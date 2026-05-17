# ADR-003 — Intégration de gitpython dans FastAPI : `asyncio.to_thread()`

!!! abstract "Qu'est-ce qu'un ADR ?"
    Un **ADR** (Architecture Decision Record) documente une décision technique :
    pourquoi elle a été prise, quelles alternatives ont été écartées, et dans quelles
    conditions elle devra être réexaminée. Voir [ADR-001](adr-001-next-artifact-number.md)
    pour la définition complète.

## Statut

**Accepté — Décision définitive**

---

## Contexte

### La tension fondamentale

FastAPI est un framework **asynchrone** (`async/await`). gitpython est une bibliothèque
**synchrone** : chaque opération (clone, push, commit…) bloque le thread appelant jusqu'à
sa complétion.

Appeler du code synchrone bloquant depuis un contexte async sans précaution **fige toute
l'API** pour tous les utilisateurs simultanés pendant la durée de l'opération.

!!! info "Qu'est-ce que la boucle d'événements (event loop) ?"
    FastAPI repose sur **asyncio**, le moteur de concurrence de Python. Au cœur d'asyncio
    se trouve une **boucle d'événements** (*event loop*) : un processus unique qui gère
    toutes les requêtes en alternant entre elles aux points de suspension (`await`).

    L'analogie : un serveur au restaurant qui gère dix tables en même temps. Quand il
    attend la réponse de la cuisine pour la table 1, il va prendre la commande de la
    table 2. Il est toujours disponible car il ne reste jamais bloqué à attendre.

    Un appel **bloquant** (synchrone) correspond à un serveur qui resterait immobile
    devant le piano de la cuisine jusqu'à ce que la commande soit prête — pendant ce
    temps, les neuf autres tables attendent.

!!! info "Qu'est-ce qu'un appel bloquant ?"
    Un appel **bloquant** monopolise le thread qui l'exécute jusqu'à sa complétion. Il
    ne rend pas la main à la boucle d'événements. Tous les appels gitpython sont
    bloquants : `git.Repo.clone_from()`, `repo.git.push()`, `repo.index.commit()`…
    leur durée peut aller de quelques millisecondes à plusieurs minutes (clone d'un
    dépôt volumineux).

### Démonstration du problème

```python
# ❌ Appel bloquant dans un contexte async — fige toute l'API
@router.post("/evolutions")
async def create_evolution(req: CreateEvolutionRequest) -> CreateEvolutionResponse:
    # Cette ligne bloque la boucle d'événements pendant toute la durée du clone
    # Toutes les autres requêtes HTTP sont gelées pendant ce temps
    repo = git.Repo.clone_from(url, path)   # ← peut durer 30-60 secondes
    ...
```

Pendant le clone, l'API ne répond plus à personne — ni aux autres créations
d'évolutions, ni aux `GET /workspaces/status`, ni aux health checks.

### Comportement de python-gitlab et httpx

Les appels GitLab (API REST) peuvent être véritablement asynchrones via **httpx**
(client HTTP async) ou via le client async de **python-gitlab**. Ils ne posent donc
pas le problème de blocage.

---

## Décision

**Le service Git utilise `asyncio.to_thread()` pour déléguer les appels gitpython
à un thread du pool système.** Les méthodes du `GitService` sont déclarées `async def`
et wrappent leurs opérations synchrones gitpython dans `asyncio.to_thread()`.

```
Router (async def)
  └─ EvolutionService.create() (async def)
       ├─ GitLabService.*()  (async def + httpx)    ← vrais appels async
       └─ GitService.*()     (async def)             ← async wrapper
            └─ asyncio.to_thread(_sync_method)       ← gitpython dans thread pool
```

---

## Explication des mécanismes

### `asyncio.to_thread()` — la solution

`asyncio.to_thread()` exécute une fonction synchrone bloquante **dans un thread
séparé** du pool de threads de l'OS, tout en restant pilotable par `await`. La boucle
d'événements n'est pas bloquée : elle continue de traiter les autres requêtes pendant
que le thread exécute l'opération Git.

```
Boucle d'événements (thread principal)
  │
  ├─ Requête alice : await git_service.clone_repo("da01")
  │    └─ asyncio.to_thread → Thread-1 exécute git.clone_from(...)
  │         La boucle est libre pendant ce temps ↓
  ├─ Requête bob   : await gitlab_service.list_branches("da01")  ← traité immédiatement
  ├─ Requête carol : GET /workspaces/status                      ← traité immédiatement
  │
  │  [Thread-1 termine le clone]
  └─ Requête alice reprend : manifest écrit, commit, push...
```

### Pattern implémenté dans `GitService`

```python
"""Adapter Git — toutes les opérations gitpython sont isolées dans ce module.

Règle fondamentale : aucune méthode publique ne bloque la boucle d'événements.
Chaque opération gitpython est enveloppée dans asyncio.to_thread().
Les méthodes privées (_sync_*) sont synchrones et ne doivent jamais être
appelées directement depuis un contexte async.
"""

import asyncio
import shutil
from pathlib import Path

import git
from pydantic import SecretStr


class GitService:

    def __init__(self, workspace_base: Path, gitlab_token: SecretStr) -> None:
        self._workspace = workspace_base
        self._token = gitlab_token

    # ── Méthodes publiques async ───────────────────────────────────────────

    async def clone_repo(self, app_code: str, gitlab_url: str) -> git.Repo:
        """Clone un dépôt GitLab dans le workspace local.

        Délègue à _sync_clone_repo via asyncio.to_thread pour ne pas bloquer
        la boucle d'événements pendant la durée du clone (~10–60s selon le dépôt).
        """
        return await asyncio.to_thread(self._sync_clone_repo, app_code, gitlab_url)

    async def create_branch(self, repo: git.Repo, branch_name: str) -> None:
        """Crée et checkout une branche feature_."""
        await asyncio.to_thread(self._sync_create_branch, repo, branch_name)

    async def commit_and_push(self, repo: git.Repo, branch_name: str, message: str) -> None:
        """Commite les changements en attente et pousse vers GitLab."""
        await asyncio.to_thread(self._sync_commit_and_push, repo, branch_name, message)

    async def get_workspace_status(self, app_code: str) -> dict:
        """Retourne l'état du dépôt local — lecture seule, rapide."""
        return await asyncio.to_thread(self._sync_get_workspace_status, app_code)

    # ── Méthodes privées synchrones (gitpython) ───────────────────────────

    def _sync_clone_repo(self, app_code: str, gitlab_url: str) -> git.Repo:
        """Opération gitpython synchrone — NE PAS appeler directement depuis async."""
        local_path = self._workspace / app_code
        clone_url = self._build_authenticated_url(gitlab_url)
        return git.Repo.clone_from(clone_url, local_path)

    def _sync_create_branch(self, repo: git.Repo, branch_name: str) -> None:
        repo.git.checkout("-b", branch_name)

    def _sync_commit_and_push(
        self, repo: git.Repo, branch_name: str, message: str
    ) -> None:
        repo.git.add("-A")
        repo.index.commit(message)
        origin = repo.remote("origin")
        push_info = origin.push(branch_name)
        if push_info[0].flags & git.remote.PushInfo.ERROR:
            raise PushFailedError(
                code="PUSH_FAILED",
                message=f"Le push de '{branch_name}' a échoué.",
                detail=str(push_info[0].summary),
            )

    def _sync_get_workspace_status(self, app_code: str) -> dict:
        local_path = self._workspace / app_code
        if not local_path.exists():
            return {"local_repo_exists": False, "app_code": app_code}
        try:
            repo = git.Repo(local_path)
            return {
                "app_code": app_code,
                "local_repo_exists": True,
                "is_valid_git_repo": True,
                "current_branch": repo.active_branch.name,
                "has_uncommitted_changes": repo.is_dirty(untracked_files=True),
            }
        except git.InvalidGitRepositoryError:
            return {"local_repo_exists": True, "is_valid_git_repo": False}

    def _build_authenticated_url(self, gitlab_url: str) -> str:
        """Injecte le token dans l'URL de clone — ne jamais loguer cette URL."""
        token = self._token.get_secret_value()
        return gitlab_url.replace("https://", f"https://oauth2:{token}@")
```

### Le `GitLabService` reste véritablement async

```python
import httpx

class GitLabService:
    """Appels REST GitLab via httpx — véritablement async, pas de thread."""

    def __init__(self, base_url: str, token: SecretStr) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"PRIVATE-TOKEN": token.get_secret_value()},
        )

    async def list_branches(self, app_code: str) -> list[str]:
        response = await self._client.get(f"/api/v4/projects/{app_code}/repository/branches")
        response.raise_for_status()
        return [b["name"] for b in response.json()]

    async def get_applications_json(self) -> dict:
        response = await self._client.get(
            f"/api/v4/projects/{GITLAB_APP_PARAM_ID}/repository/files/applications.json/raw",
            params={"ref": "master"},
        )
        response.raise_for_status()
        return response.json()
```

---

## Alternatives écartées

### Option A — Tout en `def` (router synchrone)

FastAPI détecte automatiquement les route handlers `def` et les exécute dans un
thread pool. Toutes les opérations (HTTP et Git) tournent alors dans des threads.

```python
# FastAPI exécute ceci dans un thread — simple mais sous-optimal
@router.post("/evolutions")
def create_evolution(req: CreateEvolutionRequest) -> CreateEvolutionResponse:
    repo = git.Repo.clone_from(...)   # ← bloquant mais dans un thread
    response = httpx.post(...)        # ← HTTP synchrone dans le thread
    ...
```

**Pourquoi écarté :** les appels HTTP GitLab sont synchronisés dans le thread pool
alors qu'ils pourraient être véritablement async. Sous charge, le pool de threads
peut être saturé par des clones longs, retardant les requêtes qui n'impliquent
aucune opération Git (health check, `GET /config`…).

### Option B — Bibliothèque Git async alternative (pygit2, dulwich)

pygit2 (bindings libgit2) et dulwich (Git pur Python) offrent des opérations plus
bas niveau, potentiellement intégrables avec async.

**Pourquoi écarté :** gitpython est la bibliothèque de référence dans l'écosystème
Python, bien documentée et utilisée dans le plugin Java via JGit. La migration vers
une alternative introduit un risque de comportement différent sans bénéfice démontré
— `asyncio.to_thread()` résout le problème sans changer de bibliothèque.

### Option C — Processus séparé (subprocess git)

Appeler l'exécutable `git` via `asyncio.create_subprocess_exec()` — véritablement
async, sans bibliothèque tierce.

**Pourquoi écarté :** perd la validation de type et l'API objet de gitpython.
La gestion des erreurs (parsing des messages git en stderr) est fragile et
non portable. Réservé aux cas où gitpython ne couvre pas le besoin.

---

## Règles d'implémentation à respecter

1. **Toute méthode publique de `GitService` est `async def`** et délègue à une
   méthode privée `_sync_*` via `asyncio.to_thread()`.

2. **Les méthodes `_sync_*` ne contiennent que du code gitpython pur**, sans
   `await`, sans appels réseau HTTP.

3. **Ne jamais appeler une méthode `_sync_*` directement depuis un contexte async** —
   c'est exactement l'erreur qui bloque la boucle d'événements.

4. **`GitLabService` n'utilise jamais `asyncio.to_thread()`** — ses appels sont
   véritablement async via httpx.

5. **L'URL authentifiée (avec le token) ne doit jamais apparaître dans les logs** —
   utiliser `logging.debug("Clone de %s", app_code)`, pas l'URL complète.

---

## Conditions de révision

Cette décision doit être réexaminée si :

1. Une bibliothèque Git véritablement async (sans thread pool) devient stable
   et couvre le périmètre de gitpython
2. Des problèmes de saturation du thread pool sont observés en production
   (symptôme : timeouts sur des opérations non-Git sous forte charge)

---

## Liens

- [Architecture générale](architecture-generale.md)
- [ADR-001 — next_artifact_number](adr-001-next-artifact-number.md)
- [ADR-002 — Stockage des credentials](adr-002-stockage-tokens.md)
