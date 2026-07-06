# Gestion du manifest

Le manifest (`.mf.json` dans `META-INF/`) est le fichier central de l'évolution. Il déclare quels fichiers doivent être buildés et vers quelles autres évolutions l'application dépend. Ces trois fonctions permettent de le maintenir.

---

## Structure du manifest

```json
{
  "entity": "LCL",
  "application_code": "da01",
  "application_type": "STD",
  "manifest_object": "Objet du projet",
  "manifest_number": "20250401-001",
  "manifest_name": "da01_correction_bug_42",
  "description": "Description de l'évolution",
  "component_type": "BATCH",
  "content": {
    "src": ["MONPROG.cbl"],
    "cpy": ["MACOPIE.cpy"],
    "asm": []
  },
  "dependancies": ["da02_evolution_partagee"]
}
```

| Champ | Description |
|---|---|
| `application_code` | Code à 4 caractères (`da`/`dy` + 2 chars) |
| `application_type` | `STD` (batch standard), `CRF` (crédit), etc. |
| `manifest_number` | Numéro de version (date + séquence) |
| `manifest_name` | `<code>_<nom_evolution>` |
| `component_type` | `BATCH` ou `TP` |
| `content` | Fichiers à builder, organisés par répertoire |
| `dependancies` | Noms de manifests d'autres évolutions dont on dépend |

---

## Mettre à jour les copybooks

**Raccourci :** `Ctrl+4` — Menu : zDevOps > Mettre à jour les copybooks

Synchronise les copybooks COBOL externes nécessaires au projet depuis les dépôts GitLab partagés, et les dépose dans `dex_read_only/`.

### Concepts

!!! abstract "Copybooks internes vs externes"
    - **Internes** : présents dans `cpy/`, `dcl/`, `in2/` du projet lui-même
    - **Externes** : utilisés par les programmes mais définis dans d'autres dépôts GitLab
    - **Participating** : copybooks des évolutions déclarées dans `dependancies`

!!! abstract "dex_read_only/"
    Répertoire local du projet (`dex_read_only/cpy/`, `dex_read_only/dcl/`, `dex_read_only/in2/`) contenant les copybooks externes téléchargés. **Ne pas modifier manuellement** — régénéré à chaque exécution.

### Séquence d'exécution

```
1. Nettoyage de dex_read_only/ (suppression des anciens fichiers)
2. Scan des sources du manifest (.cob, .cbl) pour extraire les COPY / EXEC SQL INCLUDE
3. Comparaison avec les copybooks internes (cpy/, dcl/, in2/)
4. Téléchargement des copybooks manquants depuis GitLab (partagés + publiés)
5. Téléchargement des copybooks participating (dépendances du manifest)
6. Génération des fichiers de rapport dans META-INF/
7. Rafraîchissement du projet IDz
```

### Rapports générés dans `META-INF/`

| Fichier | Contenu |
|---|---|
| `dependancies.txt` | Tous les copybooks référencés, par programme |
| `dex_read_only_cpy.txt` | Copybooks `.cpy` présents + programmes qui les utilisent |
| `dex_read_only_dcl.txt` | Idem pour `.dcl` |
| `dex_read_only_in2.txt` | Idem pour `.in2` |
| `manifest_dependancies.txt` | Pour chaque programme du manifest : ses copybooks inclus |
| `errors.txt` | Copybooks non trouvés (si des erreurs ont eu lieu) |

!!! tip "Quand l'utiliser"
    - Après avoir modifié le manifest (nouveaux composants ajoutés)
    - Quand un collègue a modifié un copybook partagé
    - Avant un build, pour éviter des erreurs de compilation

---

## Gérer les composants du manifest

**Raccourci :** `Ctrl+5` — Menu : zDevOps > Gérer les composants du manifest

Sélectionne les fichiers sources à inclure dans la section `content` du manifest via une interface arborescente à cases à cocher.

### Répertoires selon le type d'application

=== "BATCH"
    | Répertoire | Contenu |
    |---|---|
    | `asm` | Fichiers assembleur |
    | `par` | Paramètres |
    | `skl` | Squelettes JCL |
    | `src` | Sources COBOL principaux |
    | `srx` | Sources COBOL étendus |
    | `cli` | Clients CICS |
    | `srp` | Sous-routines |
    | `cpy` | Copybooks internes |
    | `dcl` | Déclarations |
    | `in2` | Includes de niveau 2 |

=== "TP (Transactionnel CICS)"
    | Répertoire | Contenu |
    |---|---|
    | `ast` | Assets CICS |
    | `mps` | Maps CICS |
    | `msk` | Masques d'écran |
    | `poe` | Procédures opérationnelles |
    | `spn` | Sources de spanning |
    | `srt` | Sorties |
    | `cpy` | Copybooks internes |
    | `dcl` | Déclarations |
    | `in2` | Includes de niveau 2 |

Seuls les répertoires **réellement présents** dans le projet local sont affichés.

### Règles métier

- Les fichiers déjà dans le manifest sont **pré-cochés** à l'ouverture
- Le filtre texte permet de chercher un fichier — les cases cochées sont **conservées pendant le filtrage**
- La sauvegarde n'a lieu que sur **"Valider"** — "Quitter" sans valider ne modifie rien
- Un seul manifest doit exister dans `META-INF/` (erreur si absent ou multiple)

### Interface

```
┌─ Métadonnées (lecture seule) ──────┬─ Sélection ─────────────────────┐
│ Code application : da01            │ [Filtre]          [Reset]        │
│ Objet : Mon projet                 │                                  │
│ Évolution : correction_bug_42      │ ▼ src                            │
│ Type composant : BATCH             │   ☑ MONPROG.cbl                  │
│ Type application : STD             │   ☐ AUTREPROG.cbl                │
│ Description : ...                  │ ▼ cpy                            │
│                                    │   ☑ MACOPIE.cpy                  │
├────────────────────────────────────┴──────────────────────────────────┤
│ src = [MONPROG.cbl]   cpy = [MACOPIE.cpy]   asm = []                 │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Gérer les dépendances du manifest

**Raccourci :** `Ctrl+7` — Menu : zDevOps > Gérer les dépendances du manifest

Déclare des dépendances vers des évolutions d'**autres applications** dans le champ `dependancies` du manifest.

!!! abstract "Pourquoi déclarer une dépendance ?"
    Si votre application utilise un copybook développé dans une autre application dont la version en cours n'est pas encore en `master`, il faut déclarer cette dépendance. La fonction "Mettre à jour les copybooks" ira alors télécharger les copybooks de ces évolutions dépendantes.

### Format d'une dépendance

Une dépendance est stockée comme le **nom du manifest** de l'évolution cible (pas le nom de la branche) :

```
Branche GitLab : feature_evolution_partagee
Manifest name  : da02_evolution_partagee   ← valeur stockée dans dependancies
```

Le plugin fait la correspondance automatiquement en interrogeant GitLab.

### Règles métier

- Saisir un code application (4 chars, `da`/`dy`) dans le champ de filtre → les branches de cette application sont chargées **en arrière-plan** (Job Eclipse asynchrone)
- La branche courante du projet actif est **exclue** de la liste
- Les branches déjà déclarées en dépendance sont **pré-cochées**
- Cocher une branche → récupération automatique du nom du manifest via l'API GitLab
- Le bouton **Valider** est désactivé si le code saisi est invalide

### Résumé en temps réel

La zone basse affiche la liste des dépendances sélectionnées :

```
dépendances = [da02_evolution_partagee, da03_autre_dep]
```

!!! warning "Sauvegarde"
    Comme pour les composants, la sauvegarde n'a lieu que sur **"Valider"**.
