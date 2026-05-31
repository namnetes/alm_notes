# Configuration

## Structure d'un projet MkDocs

### Arborescence minimale

```
mon-projet/
├── mkdocs.yml          ← configuration MkDocs (obligatoire)
├── pyproject.toml      ← dépendances Python
├── docs/               ← dossier source par défaut (configurable)
│   ├── index.md        ← page d'accueil (obligatoire)
│   ├── guide.md
│   └── api/
│       └── reference.md
└── site/               ← généré par "mkdocs build" (ne pas versionner)
```

### Règles importantes

- `mkdocs.yml` doit se trouver à la **racine du projet**.
- `index.md` est **obligatoire** dans le dossier source — c'est la page d'accueil.
- Le répertoire `site/` est généré automatiquement. Ajoutez-le à `.gitignore` :

```bash
echo "site/" >> .gitignore
```

### Dossier source personnalisable

Par défaut, MkDocs cherche les fichiers Markdown dans `docs/`. Vous pouvez
changer ce dossier via `docs_dir` dans `mkdocs.yml` :

```yaml
docs_dir: doc   # ← utilise "doc/" au lieu de "docs/"
```

---

## Le fichier `mkdocs.yml`

`mkdocs.yml` est le cœur de la configuration. Format **YAML** : basé sur
l'indentation (comme Python).

### Configuration minimale

```yaml
site_name: Mon Projet
docs_dir: docs
```

Deux lignes suffisent pour avoir un site fonctionnel.

### Configuration complète annotée

```yaml
# ─── Métadonnées du site ────────────────────────────────────────────────────
site_name: Mon Projet — Documentation        # (1)
site_description: >                          # (2)
  Description courte du projet.
site_author: Prénom NOM                      # (3)

# ─── Répertoires ─────────────────────────────────────────────────────────────
docs_dir: doc                                # (4)

# ─── Thème ───────────────────────────────────────────────────────────────────
theme:
  name: material                             # (5)
  language: fr                               # (6)
  font: false                                # (7)
  palette:                                   # (8)
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-night
        name: Passer en mode sombre
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/weather-sunny
        name: Passer en mode clair
  features:                                  # (9)
    - navigation.tabs
    - navigation.tabs.sticky
    - navigation.sections
    - navigation.top
    - search.highlight
    - search.suggest
    - content.code.copy
    - content.code.annotate

# ─── Extensions Markdown ─────────────────────────────────────────────────────
markdown_extensions:
  - admonition                 # (10)
  - tables                     # (11)
  - attr_list                  # (12)
  - def_list                   # (13)
  - footnotes                  # (14)
  - toc:                       # (15)
      permalink: true
      title: Sur cette page
  - pymdownx.highlight:        # (16)
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.inlinehilite      # (17)
  - pymdownx.superfences:      # (18)
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:           # (19)
      alternate_style: true
  - pymdownx.details           # (20)
  - pymdownx.snippets          # (21)

# ─── Options diverses ─────────────────────────────────────────────────────────
extra:
  generator: false             # (22)

# ─── Navigation ──────────────────────────────────────────────────────────────
nav:                           # (23)
  - Accueil: index.md
  - Guide: guide.md
  - API:
      - Référence: api/reference.md
```

| N° | Clé | Effet |
|---|---|---|
| (1) | `site_name` | Titre dans l'onglet du navigateur et l'en-tête |
| (2) | `site_description` | Métadonnée HTML `<meta description>` |
| (3) | `site_author` | Métadonnée HTML `<meta author>` |
| (4) | `docs_dir` | Répertoire contenant les fichiers `.md` sources |
| (5) | `theme.name` | Thème visuel ; `material` = Material for MkDocs |
| (6) | `theme.language` | Langue de l'interface (boutons, labels de recherche…) |
| (7) | `theme.font: false` | Désactive le chargement de polices Google Fonts |
| (8) | `theme.palette` | Couleurs et mode clair/sombre automatique selon l'OS |
| (9) | `theme.features` | Fonctionnalités de navigation activées |
| (10) | `admonition` | Boîtes colorées `!!! note`, `!!! warning`, `!!! tip` |
| (11) | `tables` | Tableaux `\| col1 \| col2 \|` en Markdown standard |
| (12) | `attr_list` | Ajouter des classes CSS `{ .ma-classe }` |
| (13) | `def_list` | Listes de termes `: définition` |
| (14) | `footnotes` | Renvois `[^1]` et `[^1]: texte` |
| (15) | `toc` | Table des matières générée depuis les titres `##` |
| (16) | `pymdownx.highlight` | Coloration syntaxique avec Pygments |
| (17) | `pymdownx.inlinehilite` | Couleur sur `` `#!python code` `` dans une phrase |
| (18) | `pymdownx.superfences` | Diagrammes Mermaid dans des blocs de code |
| (19) | `pymdownx.tabbed` | Contenu en onglets `=== "Onglet 1"` |
| (20) | `pymdownx.details` | Sections `??? "Titre"` repliables au clic |
| (21) | `pymdownx.snippets` | `--8<-- "fichier.txt"` inclut un autre fichier |
| (22) | `extra.generator` | `false` = pas de mention MkDocs dans le pied de page |
| (23) | `nav` | Plan de navigation explicite du site |

---

## Navigation : avec ou sans `nav` ?

**Sans `nav`** : MkDocs découvre automatiquement tous les `.md` et les liste
par ordre alphabétique. Pratique pour démarrer.

**Avec `nav`** : vous contrôlez précisément l'ordre, les titres et la
structure. Recommandé dès que le site dépasse 3 ou 4 pages.

```yaml
nav:
  - Accueil: index.md
  - Guide utilisateur:
      - Installation: install.md
      - Configuration: config.md
      - Premier projet: quickstart.md
  - Référence technique:
      - API: api/reference.md
      - Options: api/options.md
  - Contribuer: contributing.md
```

---

## `navigation.indexes` — pages d'accueil de section cliquables

Sans configuration particulière, les sections de la nav sont des **en-têtes
non cliquables** — elles déplient juste leur sous-menu.

La fonctionnalité `navigation.indexes` rend une section cliquable en lui
associant son fichier `index.md` :

```yaml
theme:
  name: material
  features:
    - navigation.indexes    # ← rend les sections cliquables
```

**Comment ça marche :**

```yaml
nav:
  - Guide utilisateur:           # ← devient un lien vers guide/index.md
      - guide/index.md           # ← déclaré en première entrée sans titre
      - Installation: guide/install.md
      - Configuration: guide/config.md
```

!!! warning "Règle obligatoire avec `navigation.indexes`"
    Toute section qui contient des sous-sections **doit** avoir un `index.md`
    dans son répertoire. Sans cela, le lien de la section pointe dans le vide
    et MkDocs peut émettre un avertissement.

**Structure de fichiers correspondante :**

```
docs/
└── guide/
    ├── index.md        ← page d'accueil de la section "Guide utilisateur"
    ├── install.md
    └── config.md
```

!!! tip "Bonne pratique"
    Rédigez `index.md` comme une page de présentation de la section : ce
    qu'elle couvre, à qui elle s'adresse, les prérequis. Évitez d'y mettre
    le contenu détaillé — celui-ci va dans les sous-pages.
