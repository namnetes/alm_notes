# Gestion des évolutions

Les quatre fonctions de gestion des évolutions couvrent le cycle de vie d'une branche Git dans IDz : création, participation, bifurcation, et consultation en lecture seule.

---

## Démarrer une évolution

**Raccourci :** `Ctrl+1` — Menu : zDevOps > Démarrer une évolution

Crée une nouvelle branche `feature_<nom>` dans GitLab, clone le dépôt localement dans IDz et initialise le fichier manifest.

### Saisies requises

| Champ | Règles |
|---|---|
| **Code application** | Exactement 4 caractères, commence par `da` (BATCH) ou `dy` (TP) |
| **Nom de l'évolution** | Alphanumérique + `_`, sans espace, ne commence pas par `feature`, pas déjà existant sous `feature_XXX` |
| **Description** | Texte libre, obligatoire |
| **Type de composant** | `BATCH` ou `TP` (bouton radio, obligatoire) |

### Règles métier

!!! warning "Double validation du code application"
    Le code est vérifié à deux niveaux : existence dans **GitLab** (via l'API) ET référencement dans le fichier `applications.json` hébergé sur GitLab. Si l'une échoue, la création est refusée.

**Validation du nom de l'évolution**

- Interdit si la branche `feature_<nom>` existe déjà dans GitLab
- Interdit si le nom commence par `feature` (préfixe automatique)
- Interdit si le nom contient des espaces
- Autorisé : `[a-zA-Z0-9_]+` uniquement
- Coloré en **vert** si valide, **rouge** si invalide

**Gestion du dépôt local existant**

Si le dépôt est déjà cloné dans le workspace IDz, deux options sont proposées :

=== "Supprimer et recréer"
    1. Confirmation de suppression demandée
    2. Suppression physique du répertoire local
    3. Nouveau clone depuis `master`
    4. Création de `feature_<nom>` depuis `master`
    5. Écriture du manifest + commit + push
    6. Import dans IDz

=== "Mettre à jour"
    1. Commit automatique des modifications en cours
    2. Bascule sur `master`
    3. Pull de `master`
    4. Création de `feature_<nom>` depuis `master`
    5. Écriture du manifest + commit + push
    6. Import dans IDz

**Cas nominal (dépôt non existant)**

```
Clone depuis GitLab (master)
→ Création de feature_<nom> depuis master
→ Configuration du dépôt (hooks, protection master)
→ Écriture du manifest dans META-INF/
→ Commit initial + push vers GitLab
→ Import du projet dans IDz
```

### Manifest créé

Le manifest initial (`<code>_<nom>.mf.json`) contient :

```json
{
  "entity": "LCL",
  "application_code": "da01",
  "application_type": "STD",
  "component_type": "BATCH",
  "description": "Description saisie par l'utilisateur",
  "manifest_name": "da01_correction_bug_42",
  "content": {},
  "dependancies": [""]
}
```

---

## Participer à une évolution

**Raccourci :** `Ctrl+2` — Menu : zDevOps > Participer à une évolution

Rejoint une évolution déjà existante créée par un collègue ou sur un autre poste.

!!! info "Différence fondamentale avec Démarrer"
    Le nom de l'évolution est **sélectionné dans une liste** des branches existantes de GitLab (liste en lecture seule). Aucune nouvelle branche n'est créée.

### Saisies requises

| Champ | Règles |
|---|---|
| **Code application** | 4 caractères, `da` ou `dy`, doit exister dans GitLab |
| **Nom de l'évolution** | Sélection obligatoire dans la liste déroulante (READ ONLY) |

### Règles métier

**Affichage automatique des informations de l'évolution**

Quand l'utilisateur sélectionne une évolution dans la liste, le plugin lit le manifest de cette branche directement dans GitLab (sans cloner) et affiche automatiquement le **type de composant** et la **description** en champs grisés non éditables.

**Gestion du dépôt local existant**

=== "Supprimer et recréer"
    Clone complet depuis GitLab, puis checkout sur la branche sélectionnée.

=== "Mettre à jour (participateLocalEvolution)"
    Bascule directement sur `feature_XXX` dans le dépôt local existant + pull. Plus rapide — pas de re-clone.

### Comparatif

| Critère | Démarrer | Participer |
|---|---|---|
| Branche créée dans GitLab ? | Oui | Non |
| Nom de l'évolution | Saisi librement | Choisi dans la liste |
| Manifest créé ? | Oui | Non (déjà existant) |
| Type et description | Saisis | Lus depuis GitLab |

---

## Évolution depuis une évolution

**Raccourci :** `Ctrl+8` — Menu : zDevOps > Démarrer une évolution à partir d'une autre

Crée une nouvelle branche `feature_YYY` **depuis une branche `feature_XXX` existante** plutôt que depuis `master`.

!!! example "Cas d'usage"
    L'évolution B dépend fonctionnellement de l'évolution A qui n'est pas encore intégrée en `master`. On crée B depuis A pour hériter de ses modifications.

### Saisies requises

| Champ | Règles |
|---|---|
| **Code application** | 4 caractères, `da` ou `dy` |
| **Évolution de base** | Sélection dans la liste (READ ONLY) — la branche source |
| **Nom de la nouvelle évolution** | Mêmes règles que "Démarrer" : alphanumériques + `_`, pas de doublon |
| **Description** | Obligatoire |

### Règles métier

La nouvelle branche `feature_YYY` est créée au **commit HEAD de `feature_XXX`** — elle hérite de tous les changements de l'évolution de base.

!!! warning "Limitation connue"
    En cas de mise à jour (dépôt déjà cloné — Option B), la nouvelle branche est créée depuis `master` et non depuis l'évolution de base. C'est une limitation de l'implémentation actuelle.

---

## Consulter les sources

**Raccourci :** `Ctrl+9` — Menu : zDevOps > Consulter les sources d'un code application

Clone un dépôt GitLab sur la branche `master` en **lecture seule**, sans créer d'évolution.

!!! note "Usage"
    Analyse de code, revue, compréhension d'une application avant de démarrer une évolution. Le workspace reste sur `master` après l'opération.

### Saisies requises

| Champ | Règles |
|---|---|
| **Code application** | 4 caractères, `da` ou `dy`, doit exister dans GitLab ET dans `applications.json` |

### Règles métier

- Aucune branche `feature_` n'est créée
- Les hooks Git protègent `master` contre les commits accidentels
- Si le dépôt est déjà cloné : option Supprimer/Recréer ou Mettre à jour (commit courant → bascule master → pull)

### Comparatif avec les évolutions

| Critère | Démarrer / Participer | Consulter |
|---|---|---|
| Branche résultante | `feature_XXX` | `master` |
| Manifest créé ? | Oui | Non |
| Modifiable ? | Oui | Non |
| Champs requis | Code + nom + description + type | Code uniquement |

---

## Erreurs communes aux fonctions d'évolution

| Situation | Message |
|---|---|
| Code format incorrect | "Le nom du repo doit commencer par 'da' ou 'dy'" |
| Code non dans `applications.json` | "Le code application XXX n'est pas référencé..." |
| Nom d'évolution déjà existant | "L'évolution feature_XXX existe déjà dans le dépôt distant" |
| Nom avec espaces | "Le nom de l'évolution ne doit pas contenir d'espace" |
| Échec du clone | "Échec de l'opération de clone du dépôt XXX" |
