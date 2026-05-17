# ADR-004 — Stratégie de tests : pyramide à 4 niveaux sans testcontainers

!!! abstract "Qu'est-ce qu'un ADR ?"
Un **ADR** (Architecture Decision Record) documente une décision technique :
pourquoi elle a été prise, quelles alternatives ont été écartées, et dans quelles
conditions elle devra être réexaminée. Voir [ADR-001](adr-001-next-artifact-number.md)
pour la définition complète.

## Statut

**Accepté — Décision définitive pour la V1**

---

## Contexte

### Le défi de ce projet

Tester cette API pose deux difficultés spécifiques :

1. **Les opérations sont asynchrones** (`async def`, `await`) — les tests doivent
   savoir gérer ce modèle d'exécution.
2. **Les adapters dépendent de services externes** (GitLab distant, système de fichiers
   local, git) — les tests doivent pouvoir s'exécuter sans réseau, sans credentials,
   sans infrastructure.

!!! info "Qu'est-ce que la pyramide de tests ?"
La **pyramide de tests** est un modèle qui organise les tests en couches selon
leur vitesse, leur coût et leur portée.

    ```
               ▲
             /   \
            / E2E \        ← peu nombreux, lents, coûteux
           /───────\
          /  Intég  \      ← tests d'assemblage des couches
         /───────────\
        /  Unitaires  \    ← nombreux, rapides, isolés
       /───────────────\
    ```

    La règle : **plus le test est bas dans la pyramide, plus il doit être nombreux**.
    Les tests unitaires sont écrits en premier et constituent la majorité. Les tests
    d'intégration viennent ensuite, en nombre plus faible. Les tests E2E sont rares
    et réservés aux chemins critiques.

!!! info "Qu'est-ce qu'un mock ?"
Un **mock** est un objet factice qui remplace une dépendance réelle pendant un test.
Il simule le comportement de la dépendance (retourner une valeur, lever une
exception) sans déclencher les effets de bord réels (appels réseau, écriture disque).

    Exemple : au lieu d'appeler le vrai GitLab (réseau, credentials, état du dépôt),
    on passe un mock qui retourne immédiatement `["feature_tva", "master"]` quand
    on lui demande la liste des branches. Le test vérifie la logique du service,
    pas le comportement de GitLab.

### Stack de test retenue

| Outil                                      | Rôle                                                |
| ------------------------------------------ | --------------------------------------------------- |
| `pytest`                                   | Runner, fixtures, assertions                        |
| `pytest-asyncio`                           | Support des tests `async def`                       |
| `unittest.mock` (`MagicMock`, `AsyncMock`) | Mocks pour la couche service                        |
| `respx`                                    | Mock du transport HTTP pour `httpx` (couche GitLab) |
| `tmp_path` (fixture pytest)                | Dépôts Git locaux temporaires (couche Git)          |

---

## Décision

**La V1 applique une pyramide à 4 niveaux.** Chaque niveau teste une couche
distincte de l'architecture avec l'outil le plus adapté à sa nature.

```
Niveau 4 — E2E            (hors V1 — contre un environnement réel)
Niveau 3 — Git adapter    (respx + tmp_path — dépôts git locaux réels)
Niveau 2 — GitLab adapter (respx — transport HTTP mocké)
Niveau 1 — Service + Modèles (AsyncMock / MagicMock — zéro I/O)
```

---

## Implémentation par niveau

### Niveau 1 — Modèles Pydantic et couche service

Les tests les plus rapides et les plus nombreux. Aucun I/O — ni réseau,
ni disque, ni git. Les adapters (GitLab, Git) sont remplacés par des mocks.

Ce niveau est **déjà documenté** en détail dans
[Cas concret : POST /evolutions](cas-concret-post-evolutions.md#5-strategie-de-tests).
En voici le rappel de structure :

```python
# tests/unit/test_evolution_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock

from zdevops_api.services.evolution_service import EvolutionService
from zdevops_api.exceptions import EvolutionAlreadyExistsError


@pytest.fixture
def mock_gitlab() -> AsyncMock:
    """Adapter GitLab factice — aucun appel réseau."""
    m = AsyncMock()
    m.list_branches.return_value = []
    m.get_applications_json.return_value = {
        "da01": {"next_artifact_number": 41}
    }
    return m


@pytest.fixture
def mock_git() -> MagicMock:
    """Adapter Git factice — aucune écriture disque."""
    m = MagicMock()
    m.get_local_repo_if_exists.return_value = None
    m.clone_repo = AsyncMock(return_value=MagicMock())
    m.write_manifest.return_value = "META-INF/da01_correction_tva.mf.json"
    m.get_local_path.return_value = "/workspace/da01"
    return m


@pytest.mark.asyncio
async def test_evolution_already_exists_raises_409(mock_gitlab, mock_git):
    mock_gitlab.list_branches.return_value = ["feature_correction_tva"]
    service = EvolutionService(gitlab=mock_gitlab, git=mock_git)

    with pytest.raises(EvolutionAlreadyExistsError) as exc:
        await service.create(make_request())

    assert exc.value.code == "EVOLUTION_ALREADY_EXISTS"
```

---

### Niveau 2 — Adapter GitLab (`respx`)

`respx` intercepte les appels HTTP au niveau du **transport httpx**, sans démarrer
de serveur. Il simule les réponses GitLab exactement comme le ferait le vrai serveur,
ce qui permet de tester la logique de désérialisation, de gestion d'erreur et de
retry de `GitLabService`.

!!! info "Pourquoi `respx` plutôt qu'un mock de la classe ?"
Mocker `GitLabService` directement (niveau 1) teste la logique du _service_.
Mocker au niveau du transport HTTP (niveau 2) teste le _code de `GitLabService`
lui-même_ : est-ce qu'il appelle la bonne URL ? Est-ce qu'il désérialise
correctement le JSON ? Est-ce qu'il gère les 404 de GitLab ?

    `respx` reproduit exactement les réponses HTTP sans exiger de serveur réel.

```python
# tests/integration/test_gitlab_service.py
import pytest
import respx
import httpx
from pydantic import SecretStr

from zdevops_api.services.gitlab_service import GitLabService


GITLAB_URL = "https://gitlab.example.com"


@pytest.fixture
def gitlab_service() -> GitLabService:
    return GitLabService(base_url=GITLAB_URL, token=SecretStr("test-token"))


@pytest.mark.asyncio
async def test_list_branches_deserializes_correctly(gitlab_service):
    """GitLabService extrait les noms de branches depuis la réponse JSON GitLab."""
    with respx.mock:
        respx.get(
            f"{GITLAB_URL}/api/v4/projects/da01/repository/branches"
        ).mock(return_value=httpx.Response(
            200,
            json=[{"name": "feature_tva"}, {"name": "master"}],
        ))

        branches = await gitlab_service.list_branches("da01")

    assert branches == ["feature_tva", "master"]


@pytest.mark.asyncio
async def test_project_not_found_raises_404(gitlab_service):
    """Un projet absent de GitLab lève AppNotFoundInGitlabError (→ 404 API)."""
    with respx.mock:
        respx.get(
            f"{GITLAB_URL}/api/v4/projects/da99"
        ).mock(return_value=httpx.Response(404))

        from zdevops_api.exceptions import AppNotFoundInGitlabError
        with pytest.raises(AppNotFoundInGitlabError):
            await gitlab_service.assert_project_exists("da99")


@pytest.mark.asyncio
async def test_gitlab_unreachable_raises_502(gitlab_service):
    """Une erreur réseau GitLab lève GitlabUnreachableError (→ 502 API)."""
    with respx.mock:
        respx.get(
            f"{GITLAB_URL}/api/v4/projects/da01/repository/branches"
        ).mock(side_effect=httpx.ConnectError("Connection refused"))

        from zdevops_api.exceptions import GitlabUnreachableError
        with pytest.raises(GitlabUnreachableError):
            await gitlab_service.list_branches("da01")
```

---

### Niveau 3 — Adapter Git (`tmp_path` + dépôts locaux)

Le `GitService` fait des opérations réelles sur le système de fichiers et sur git.
On peut tester ces opérations **sans serveur GitLab** en utilisant :

- `tmp_path` — fixture pytest qui crée un répertoire temporaire nettoyé après le test
- Un **dépôt bare local** jouant le rôle de "remote GitLab"

!!! info "Qu'est-ce qu'un dépôt bare ?"
Un dépôt bare (`git init --bare`) est un dépôt git **sans répertoire de travail** —
il contient uniquement l'historique (les objets git). C'est le format utilisé par
les serveurs git (GitHub, GitLab…). On peut pousser vers un bare repo exactement
comme vers un remote réel, sans réseau.

```python
# tests/integration/test_git_service.py
import pytest
import git
from pathlib import Path
from pydantic import SecretStr

from zdevops_api.services.git_service import GitService


@pytest.fixture
def bare_remote(tmp_path: Path) -> Path:
    """Crée un dépôt bare local jouant le rôle de 'remote GitLab'."""
    remote_path = tmp_path / "remote.git"
    repo = git.Repo.init(remote_path, bare=True)
    # Commit initial pour avoir une branche master
    with git.Repo.init(tmp_path / "_init") as init_repo:
        (tmp_path / "_init" / "README.md").write_text("init")
        init_repo.index.add(["README.md"])
        init_repo.index.commit("Initial commit")
        init_repo.create_remote("origin", str(remote_path))
        init_repo.remotes.origin.push("master")
    return remote_path


@pytest.fixture
def git_service(tmp_path: Path) -> GitService:
    return GitService(
        workspace_base=tmp_path / "workspace",
        gitlab_token=SecretStr("fake-token"),
    )


@pytest.mark.asyncio
async def test_clone_creates_local_directory(git_service, bare_remote, tmp_path):
    """Après un clone, le répertoire local existe et est un dépôt git valide."""
    repo = await git_service.clone_repo("da01", str(bare_remote))

    local_path = tmp_path / "workspace" / "da01"
    assert local_path.exists()
    assert not repo.bare


@pytest.mark.asyncio
async def test_create_branch_checkouts_new_branch(git_service, bare_remote, tmp_path):
    """Après create_branch, le dépôt local est sur la nouvelle branche."""
    repo = await git_service.clone_repo("da01", str(bare_remote))
    await git_service.create_branch(repo, "feature_correction_tva")

    assert repo.active_branch.name == "feature_correction_tva"


@pytest.mark.asyncio
async def test_dirty_repo_detected(git_service, bare_remote, tmp_path):
    """is_dirty renvoie True si un fichier est modifié non commité."""
    repo = await git_service.clone_repo("da01", str(bare_remote))
    (tmp_path / "workspace" / "da01" / "new_file.txt").write_text("contenu")

    assert repo.is_dirty(untracked_files=True)
```

---

## Alternatives écartées

### testcontainers — un vrai GitLab en Docker

`testcontainers-python` peut démarrer un conteneur **GitLab CE** pour des tests
d'intégration contre une instance réelle.

!!! info "Qu'est-ce que testcontainers ?"
`testcontainers` est une bibliothèque qui lance des conteneurs Docker
(base de données, message broker, serveur web…) pendant l'exécution des tests,
puis les détruit automatiquement. Elle est utilisée pour tester le comportement
réel d'une dépendance externe sans se connecter à un environnement partagé.

**Pourquoi écarté pour la V1 :**

| Problème                          | Impact                                       |
| --------------------------------- | -------------------------------------------- |
| Image GitLab CE : ~3–4 Go         | Téléchargement long au premier `docker pull` |
| Démarrage du conteneur : 2–3 min  | Chaque `pytest` complet dure 3 min minimum   |
| Requiert Docker en fonctionnement | Friction sur les postes développeurs Windows |
| Instabilité des tests (timing)    | GitLab met du temps à être prêt → flakiness  |

**Bilan :** testcontainers est pertinent pour tester des **migrations de base de
données** ou des **comportements spécifiques au SGBD**. Pour une API REST dont on
maîtrise le contrat, `respx` donne les mêmes garanties de désérialisation en
quelques millisecondes. Le rapport coût/bénéfice ne justifie pas le poids de GitLab CE.

Laissé en option pour un pipeline CI/CD dédié aux tests d'intégration longue durée,
hors cycle de développement quotidien.

### Instance GitLab de test partagée

Utiliser un projet GitLab dédié aux tests dans l'infrastructure LCL existante.

**Pourquoi écarté :** fragilité — les tests dépendent d'un état externe modifiable
par d'autres, d'une connectivité réseau, et de credentials de test à distribuer.
Les tests deviennent non reproductibles et difficiles à exécuter hors LAN.

---

## Règles d'implémentation

1. **Niveau 1 uniquement pour la logique métier** — ne jamais tester le comportement
   HTTP dans les tests unitaires du service.

2. **`respx` uniquement pour `GitLabService`** — ne pas utiliser `respx` pour
   mocker des appels qui devraient être testés avec un mock de classe (niveau 1).

3. **Fixtures `bare_remote` réutilisables** — factoriser dans `conftest.py` pour
   éviter la duplication entre les tests Git.

4. **Chaque test vérifie une seule chose** — un test qui échoue doit immédiatement
   indiquer ce qui est cassé sans avoir à lire le détail de l'assertion.

5. **Les tests async sont marqués `@pytest.mark.asyncio`** — configurer
   `asyncio_mode = "auto"` dans `pytest.ini` pour éviter la répétition du décorateur.

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
testpaths = tests
```

---

## Conditions de révision

Cette décision doit être réexaminée si :

1. Un **bug de production** n'est pas reproductible sans une vraie instance GitLab
   — signal que `respx` ne couvre pas ce comportement spécifique
2. Le **pipeline CI/CD** dispose d'un environnement Docker adapté — envisager alors
   testcontainers pour un job d'intégration séparé, pas pour les tests unitaires

---

## Liens

- [Cas concret : POST /evolutions — section Tests](cas-concret-post-evolutions.md#5-strategie-de-tests)
- [ADR-003 — Async/sync gitpython](adr-003-async-sync-gitpython.md)
- [Architecture générale](architecture-generale.md)
