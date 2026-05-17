# ADR-001 — Gestion de `next_artifact_number` : report du verrouillage atomique

!!! abstract "Qu'est-ce qu'un ADR ?"
    Un **ADR** (Architecture Decision Record — *fiche de décision d'architecture*) est un
    document court qui trace une décision technique importante : pourquoi elle a été prise,
    quelles alternatives ont été écartées, et dans quelles conditions elle devra être
    réexaminée.

    L'objectif est de rendre les décisions **lisibles par n'importe quel développeur
    qui rejoindra le projet plus tard**, sans qu'il ait à retrouver un fil de discussion
    Slack ou interroger les personnes présentes au moment du choix.

    Un ADR n'est pas gravé dans le marbre : il a un statut (*Accepté*, *Déprécié*,
    *Remplacé par ADR-XXX*…) qui évolue avec le projet. C'est sa durée de vie explicite
    qui le distingue d'un commentaire dans le code.

## Statut

**Accepté — Décision temporaire, applicable à la V1 uniquement**

Révisable dès qu'un des déclencheurs listés en section
[Conditions de révision](#conditions-de-revision) est atteint.

---

## Contexte

### Rôle du compteur

`next_artifact_number` est un entier stocké dans `applications.json`, un fichier de
configuration hébergé dans GitLab. Il est incrémenté à chaque création d'évolution pour
une application donnée. Ce numéro sert à deux choses :

1. **Nommer le manifest** : `<app_code>_<numéro_sur_6_chiffres>_<nom_évolution>.mf.json`
2. **Tagger le load module** produit par Jenkins lors du build

La contrainte est stricte : **la bijection source ↔ load est réglementaire**. Lors d'un
audit ou d'une promotion en production, on doit être capable de retrouver le code source
exact qui a produit un load module donné. Un numéro en double brise cette traçabilité.

### Opération actuelle — plugin Java et V1 API

```
1. Lire applications.json        (GET GitLab API)
2. Extraire next_artifact_number ← lecture non atomique
3. Créer la branche + écrire le manifest avec ce numéro
4. Incrémenter next_artifact_number (PUT GitLab API)
   └─ Si le PUT échoue → WARNING, pas d'échec de la requête
```

L'opération lecture-puis-écriture n'est **pas atomique**. Entre les étapes 2 et 4, un
autre processus peut lire et utiliser le même numéro sans que personne ne le détecte.

### Contexte organisationnel

- **300 développeurs** répartis en squads
- Plusieurs squads partagent certaines applications stratégiques (`daXX` / `dyXX`)
- Les pics de création d'évolutions se concentrent : début de sprint, urgences de
  production, semaines de livraison
- Le plugin Java existant présente le même défaut. Aucun incident formel n'a été remonté
  à ce jour, mais l'absence de signalement ne prouve pas l'absence de collision silencieuse

---

## Décision

**La V1 de l'API conserve le comportement du plugin Java** : lecture non atomique de
`next_artifact_number`, sans verrouillage optimiste.

### Raisons

1. **Complexité hors périmètre MVP** — Le verrouillage optimiste nécessite une logique de
   retry (lire → vérifier → écrire → si conflit → relire → ré-essayer). Introduire cette
   logique prolonge le périmètre V1 sans valeur ajoutée immédiate pour les utilisateurs.

2. **Risque hérité, non introduit** — Le défaut existait dans le plugin Java. La V1 ne le
   corrige pas, mais ne l'aggrave pas non plus.

3. **Mitigation partielle disponible** — L'API retourne un `warning` dans la réponse
   `201` si l'incrémentation échoue (`CreateEvolutionResponse.warnings`). Les clients
   (CLI, VS Code) peuvent remonter cette information à l'utilisateur.

### Ce qui est explicitement exclu de la V1

- Optimistic locking GitLab (`last_commit_id` dans le PUT)
- Service de compteur atomique externe (Redis, PostgreSQL)
- Retry automatique en cas de conflit concurrent

---

## Conséquences

### Risques assumés

| Scénario | Probabilité | Impact |
|---|---|---|
| Deux développeurs créent simultanément une évolution sur la même application | Faible à modérée (pics de sprint) | **Élevé** — bijection cassée, charge d'audit |
| Échec du PUT → prochain `next_artifact_number` identique au précédent | Faible | **Élevé** — collision sans concurrence |
| Accumulation silencieuse de numéros dupliqués non détectés | Faible | **Très élevé** — audit impossible a posteriori |

### Garde-fous obligatoires en V1

- Le `WARNING` dans les logs est **obligatoire** — ne pas supprimer, ne pas downgrader
  en `DEBUG`. C'est le seul signal opérationnel disponible.
- Le champ `warnings` dans la réponse `201` expose l'échec au client.
- Un monitoring sur les `WARNING` liés à RG-12 doit être configuré en production avant
  le premier déploiement.

---

## Analyse du code Java original

Le plugin Java ne contient **aucun mécanisme de protection contre la race condition** :
ni retry, ni `last_commit_id`, ni bloc `synchronized`. Le problème est structurel.

### Séquence dans `GitLabService.writeBranchManifest()`

```java
// ① Lecture de applications.json — un GET GitLab sans capture du SHA
Application application = getApplicationByAppCode(project.getName());

// ② Incrément en mémoire locale — le fichier GitLab est déjà "périmé"
//    si quelqu'un d'autre a écrit entre le GET et maintenant
application.setNextArtifactNumber(application.getNextArtifactNumber() + 1);

// ③ Nommage du manifest avec le numéro incrémenté en local
String formatNextNumber = String.format("%06d", application.getNextArtifactNumber());
manifest.setManifestName(String.format("%s%s_%s",
    project.getName(), formatNextNumber, branchName));

// ... clone, création de branche, écriture du manifest, commit (RG-07 à RG-11) ...
// ← fenêtre de collision ouverte ici : plusieurs dizaines de secondes

// ④ Écriture dans GitLab — updateFile() SANS last_commit_id
//    Aucune détection de conflit. Le dernier à écrire écrase silencieusement.
pushUpdatedApplications(applications);
```

### Code de l'écriture — `pushUpdatedApplications()`

```java
private void pushUpdatedApplications(List<Application> applications) throws Exception {
    String jsonContent = objectMapper
        .writerWithDefaultPrettyPrinter()
        .writeValueAsString(applications);

    RepositoryFile repositoryFile = new RepositoryFile();
    repositoryFile.setFilePath("applications.json");
    repositoryFile.setContent(jsonContent);

    // updateFile() de gitlab4j supporte un paramètre optionnel last_commit_id.
    // Il n'est PAS passé ici → GitLab ne peut pas détecter un conflit concurrent.
    gitLabApi.getRepositoryFileApi().updateFile(
        GITLAB_APP_PARAM_ID,
        repositoryFile,
        "master",
        "📤 Mise à jour de l'applications.json"
    );
}
```

!!! note "Ce que `last_commit_id` aurait permis"
    La bibliothèque `gitlab4j` supporte bien le paramètre :
    `updateFile(projectId, file, branch, commitMessage, lastCommitId)`.
    Si passé, GitLab répond `400 Bad Request` quand le fichier a été modifié
    depuis la lecture. Sans lui, GitLab accepte l'écriture aveuglément.

### Conclusion de l'analyse Java

| Question | Réponse |
|---|---|
| Le SHA du GET est-il capturé ? | Non |
| `last_commit_id` est-il passé au PUT ? | Non |
| Y a-t-il un retry en cas de conflit ? | Non |
| Y a-t-il un bloc `synchronized` ? | Non |
| Y a-t-il un log si collision silencieuse ? | Non |

La race condition est **totalement silencieuse** : aucune exception, aucun log,
aucun indicateur. Les deux manifests sont créés, GitLab accepte les deux écritures,
et le compteur est faux sans que personne ne le sache.

!!! warning "Deux implémentations, même bug"
    Le plugin contient deux services distincts — `GitLabService.java` et `GitService.java`
    — qui implémentent tous les deux `writeBranchManifest()` avec le même code non
    atomique. Le bug a été copié-collé sans jamais être questionné. L'API Python V1
    n'a donc pas à reproduire cette structure duale : une seule implémentation, correcte.

---

## Démonstration Python de la race condition

!!! info "Qu'est-ce qu'une race condition ?"
    Une **race condition** (condition de course) est un défaut qui survient quand le
    résultat d'une opération dépend de l'ordre imprévisible dans lequel plusieurs
    processus s'exécutent simultanément.

    L'image classique : deux personnes lisent le solde d'un compte bancaire (100 €),
    retirent chacune 80 € de leur côté, et écrivent toutes les deux "nouveau solde : 20 €".
    Le compte devrait être à −60 €, mais chacune a travaillé sur sa propre copie de la
    valeur initiale. Résultat : 60 € ont disparu sans erreur visible.

    Dans notre cas, la "valeur initiale" est `next_artifact_number`, les "deux personnes"
    sont deux développeurs créant simultanément une évolution, et les "60 € disparus"
    sont des numéros d'artefacts dupliqués dans les loads modules Jenkins.

Le script suivant reproduit le scénario dans le contexte FastAPI (`asyncio`).
Avec `asyncio.gather`, trois requêtes concurrentes s'interfolient à chaque `await`,
exactement comme trois utilisateurs simultanés sur le serveur.

```python
"""
Démonstration de la race condition sur next_artifact_number.

Simule trois développeurs de la même squad qui créent simultanément
une évolution pour l'application da01.

Run: uv run python race_condition_demo.py
"""

import asyncio
import copy

# État partagé — représente applications.json sur GitLab
_gitlab_state: dict = {"da01": {"next_artifact_number": 41}}


async def gitlab_read() -> dict:
    """Simule GET /repository/files/applications.json (~50ms réseau)."""
    await asyncio.sleep(0.05)          # ← YIELD : les autres coroutines avancent
    return copy.deepcopy(_gitlab_state)


async def gitlab_write(app_code: str, new_number: int) -> None:
    """Simule PUT /repository/files/applications.json — sans last_commit_id."""
    await asyncio.sleep(0.05)          # ← YIELD : les autres coroutines avancent
    _gitlab_state[app_code]["next_artifact_number"] = new_number
    # Aucune vérification de conflit — le dernier à écrire gagne silencieusement.


async def create_evolution(user: str, app_code: str) -> str:
    # RG-05 : lecture de applications.json
    data = await gitlab_read()         # ← YIELD : les trois lisent la même valeur
    artifact_number = data[app_code]["next_artifact_number"]
    print(f"[{user:5}] READ  → next_artifact_number = {artifact_number}")

    # RG-07 à RG-11 : clone, branche, manifest, commit, push (~300ms)
    await asyncio.sleep(0.3)           # ← YIELD : fenêtre de collision ouverte

    # RG-12 : écriture du nouveau compteur
    await gitlab_write(app_code, artifact_number + 1)
    manifest_name = f"{app_code}_{artifact_number + 1:06d}_{user}"
    print(f"[{user:5}] WRITE → next_artifact_number = {artifact_number + 1}"
          f"  |  manifest = {manifest_name}")
    return manifest_name


async def main() -> None:
    print("=== Race condition sur next_artifact_number ===")
    print(f"État initial : {_gitlab_state}\n")

    # Trois requêtes concurrentes — asyncio.gather les exécute en interfoliant
    manifests = await asyncio.gather(
        create_evolution("alice", "da01"),
        create_evolution("bob",   "da01"),
        create_evolution("carol", "da01"),
    )

    artifact_numbers = {m.split("_")[1] for m in manifests}
    print(f"\nManifests créés    : {manifests}")
    print(f"État final         : {_gitlab_state}")
    print(f"Compteur attendu   : 44  (41 + 3 évolutions)")
    print(f"Compteur réel      : {_gitlab_state['da01']['next_artifact_number']}")
    if len(artifact_numbers) < len(manifests):
        print(f"⚠ Collision détectée : {len(manifests)} manifests "
              f"partagent {len(artifact_numbers)} numéro(s) : {artifact_numbers}")


asyncio.run(main())
```

### Sortie observée

```
=== Race condition sur next_artifact_number ===
État initial : {'da01': {'next_artifact_number': 41}}

[alice] READ  → next_artifact_number = 41
[bob  ] READ  → next_artifact_number = 41   ← même valeur : fenêtre ouverte
[carol] READ  → next_artifact_number = 41   ← même valeur : fenêtre ouverte
[alice] WRITE → next_artifact_number = 42  |  manifest = da01_000042_alice
[bob  ] WRITE → next_artifact_number = 42  |  manifest = da01_000042_bob
[carol] WRITE → next_artifact_number = 42  |  manifest = da01_000042_carol

Manifests créés    : ['da01_000042_alice', 'da01_000042_bob', 'da01_000042_carol']
État final         : {'da01': {'next_artifact_number': 42}}
Compteur attendu   : 44  (41 + 3 évolutions)
Compteur réel      : 42
⚠ Collision détectée : 3 manifests partagent 1 numéro(s) : {'000042'}
```

!!! danger "Ce que la sortie révèle"
    - Les trois `READ` arrivent avant le premier `WRITE` : la fenêtre entre la lecture
      GitLab et l'écriture (le temps des opérations Git) suffit pour la collision.
    - Trois loads modules seront taggés `000042` par Jenkins : **la bijection est cassée**.
    - Le compteur passe de 41 à 42 au lieu de 44 : **deux numéros sont perdus**.
    - Personne ne reçoit d'erreur. Tout semble s'être bien passé.

---

## Alternatives pour la V2

### Prérequis commun : restructurer le flow

Quelle que soit l'option retenue pour la V2, le flow doit être **inversé** par rapport au
plugin Java et à la V1 de l'API. L'incrément doit se faire **en début de workflow**,
avant toute opération Git.

=== "❌ Flow actuel (V1 — identique au plugin Java)"

    ```
    1. Lire next_artifact_number  ← lecture simple, pas de SHA
    2. Clone + branche + manifest + commit + push
       ← fenêtre de collision = durée des opérations Git (~10–60s)
    3. Écrire next_artifact_number + 1  ← aucun verrou
    ```

=== "✅ Flow cible (V2)"

    ```
    1. Réserver next_artifact_number atomiquement
       ← fenêtre de collision = ~100ms (deux appels HTTP GitLab)
       ← en cas d'échec Git après : numéro perdu (gap), pas de doublon
    2. Clone + branche + manifest nommé avec le numéro réservé
    3. Commit + push
       ← pas de second PUT sur applications.json
    ```

!!! info "Les gaps de séquence sont acceptables"
    Si les opérations Git échouent après la réservation, le numéro est définitivement
    perdu — la séquence aura un trou (ex : 41, 43, 44…). Ce comportement est identique
    à celui d'un `PostgreSQL SEQUENCE` ou d'un `Redis INCR` sur transaction annulée.
    Un trou ne casse pas la bijection ; un doublon, si.

---

### Option A — Optimistic locking GitLab *(sans nouvelle infrastructure)*

!!! info "Qu'est-ce que l'optimistic locking ?"
    Le **verrouillage optimiste** (optimistic locking) est une stratégie de concurrence
    qui part du principe que les conflits sont *rares* — on n'empêche donc personne de
    lire ou d'écrire, mais on détecte les collisions *au moment de l'écriture*.

    Concrètement : lors de la lecture, on note une **empreinte** de la donnée (un numéro
    de version, un SHA, un timestamp). Lors de l'écriture, on joint cette empreinte à la
    requête. Le système vérifie que la donnée n'a pas changé entre les deux. Si quelqu'un
    d'autre a écrit entretemps, l'écriture est **rejetée** — et on relance depuis la
    lecture (retry).

    C'est l'opposé du **verrouillage pessimiste** (mutex, `LOCK TABLE`…) qui bloque
    l'accès à la ressource dès la lecture pour être sûr que personne ne peut la modifier
    avant l'écriture. L'approche pessimiste élimine les conflits mais sérialise toutes
    les opérations, ce qui nuit aux performances sous charge.

    Dans notre contexte : GitLab joue le rôle de système de contrôle. Le paramètre
    `last_commit_id` est l'empreinte. Si `applications.json` a été modifié depuis notre
    lecture, GitLab rejette le PUT — on relance.

L'API GitLab Files supporte `last_commit_id` sur le PUT. Si le fichier a été modifié
depuis la lecture, GitLab rejette le PUT avec une erreur de conflit. Avec le flow
restructuré, la **fenêtre d'exposition est réduite à ~100ms** (temps de deux appels
HTTP), ce qui rend les conflits rares et les retries peu coûteux.

```python
async def reserve_artifact_number(self, app_code: str) -> int:
    """Réserve atomiquement le prochain numéro d'artefact.

    À appeler EN DÉBUT de workflow, avant toute opération Git.
    Si les opérations Git échouent après la réservation, le numéro
    est perdu (gap de séquence acceptable — pas un doublon).

    Args:
        app_code: Code de l'application (ex: "da01").

    Returns:
        Le numéro réservé, garanti unique pour cette application.

    Raises:
        AppNotInRegistryError: Si app_code absent de applications.json.
        ArtifactNumberUnavailableError: Si MAX_RETRIES conflits consécutifs.
    """
    for attempt in range(MAX_RETRIES):
        data, sha = await self.get_applications_json_with_sha()
        if app_code not in data:
            raise AppNotInRegistryError(
                code="APP_NOT_IN_REGISTRY",
                message=f"'{app_code}' absent de applications.json.",
            )
        reserved = data[app_code]["next_artifact_number"] + 1
        data[app_code]["next_artifact_number"] = reserved
        try:
            await self.put_applications_json(data, last_commit_id=sha)
            return reserved   # ← numéro garanti unique dès ici
        except GitlabConflictError:
            if attempt == MAX_RETRIES - 1:
                raise ArtifactNumberUnavailableError(
                    code="ARTIFACT_NUMBER_CONFLICT",
                    message=(
                        f"Impossible de réserver un numéro pour '{app_code}' "
                        f"après {MAX_RETRIES} tentatives. Réessayez."
                    ),
                )
            await asyncio.sleep(0.1 * (attempt + 1))   # backoff léger
```

Appel dans `EvolutionService.create()` :

```python
# Réservation atomique EN PREMIER — avant clone, avant toute écriture disque
artifact_number = await self.gitlab.reserve_artifact_number(req.app_code)

# Les opérations Git utilisent le numéro garanti unique
manifest_path = self.git.write_manifest(..., artifact_number=artifact_number)
# push, commit... si ça échoue : le numéro est perdu, pas dupliqué
```

**Pourquoi pas en V1 :** nécessite de restructurer le flow et de propager le SHA
dans la chaîne d'appel — périmètre non prévu dans le MVP.

---

### Option B — Service de compteur atomique (Redis / PostgreSQL SEQUENCE)

Extraire le compteur de `applications.json` vers un service dédié.
`Redis INCR` ou `PostgreSQL SEQUENCE` garantissent l'atomicité nativement, sans retry.

```python
# Avec Redis
reserved = await redis_client.incr(f"artifact_counter:{app_code}")

# Avec PostgreSQL
reserved = await db.fetchval("SELECT nextval('artifact_counter')")
```

**Pourquoi pas en V1 :** introduit une dépendance d'infrastructure nouvelle, soumise
à un processus d'approbation DSI/CMDB dans un contexte bancaire. Pertinent si l'Option A
s'avère insuffisante (charge très élevée, conflits fréquents).

---

### Comparaison Option A vs Option B pour la V2

| Critère | Option A — Optimistic locking | Option B — Redis / PostgreSQL |
|---|---|---|
| Atomicité | ✅ via retry sur `last_commit_id` | ✅ native, sans retry |
| Infrastructure | ✅ GitLab existant | ⚠️ service externe à déployer et rendre HA |
| Approbation DSI / CMDB | ✅ aucune | ⚠️ processus bancaire potentiellement long |
| Complexité code | Modérée (retry + backoff) | Faible (un seul appel) |
| Fenêtre de collision | ~100ms avec flow restructuré | Nulle |
| Retries nécessaires | Oui, mais rares | Non |
| Gaps de séquence | Oui (git fail après réservation) | Oui (SEQUENCE ne rollback pas) |
| Résilience si GitLab KO | L'API est déjà KO | ✅ Indépendant de GitLab |

**Recommandation :** Option A en V2 (flow restructuré, pas de nouvelle infra).
Option B si les conflits deviennent fréquents ou si une base de données est déjà
disponible dans l'infrastructure de l'API.

---

### Option C — Identifiant non séquentiel (timestamp ou UUID court)

Remplacer le numéro séquentiel par un identifiant basé sur le temps ou un UUID court,
éliminant tout besoin de coordination.

**Pourquoi écarté :** cassant pour le toolchain Jenkins et les conventions de nommage
des loads modules en production LCL. Nécessite une décision transverse avec les équipes
FabCI — hors périmètre de ce projet.

---

## Conditions de révision

Cette décision doit être réexaminée si l'un des déclencheurs suivants est atteint :

1. Un **incident documenté** de collision `next_artifact_number` est remonté en production
2. Le **monitoring des WARNINGs** révèle des échecs d'incrémentation récurrents
3. Un **audit de traçabilité** identifie des numéros en double dans `applications.json`
4. La **V2 du MVP est planifiée** — implémenter l'Option A avec le flow restructuré

---

## Liens

- [Cas concret POST /evolutions — RG-12](cas-concret-post-evolutions.md#rg-12-mise-à-jour-de-applicationsjson)
- [Architecture générale](architecture-generale.md)
- Spec plugin Java : `cicd_zdevops/plugin_zdevops/doc/01_demarrer_evolution/business_rules.md`
