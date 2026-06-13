# Stack de référence

Cette page rassemble le **stack MkDocs complet** utilisé par ce wiki. C'est
exactement celui défini comme standard dans `~/.claude/CLAUDE.md` et généré
automatiquement par l'outil [`mkdocsinit`](../../systeme/ubuntu/alm_tools/outils/mkdocsinit.md) :
les deux sont **identiques**.

!!! info "Source de vérité : `mkdocsinit`"
    Pour un nouveau projet, ne recopiez pas ce bloc à la main — lancez
    `mkdocsinit .`. Cette page sert de référence lisible et doit rester
    synchronisée avec le template du générateur.

---

## Plugins obligatoires

Les six plugins du stack, à installer en dépendances de développement :

```bash
uv add --dev \
    mkdocs-material \
    mkdocs-minify-plugin \
    mkdocs-git-revision-date-localized-plugin \
    mkdocs-awesome-pages-plugin \
    mkdocs-include-markdown-plugin \
    mkdocs-macros-plugin
```

| Plugin | Rôle |
|---|---|
| `mkdocs-material` | Thème Material : navigation, recherche, mode sombre, onglets de code |
| `mkdocs-minify-plugin` | Compresse le HTML généré |
| `mkdocs-git-revision-date-localized-plugin` | Date de dernière modification sur chaque page (issue de Git) |
| `mkdocs-awesome-pages-plugin` | Contrôle de l'ordre des pages via des fichiers `.pages` |
| `mkdocs-include-markdown-plugin` | Inclure un fichier Markdown dans un autre |
| `mkdocs-macros-plugin` | Variables et macros Jinja2 dans les pages |

!!! note "Mermaid n'est pas un plugin tiers"
    Le rendu des diagrammes Mermaid est assuré nativement par
    `pymdownx.superfences` (fourni avec `mkdocs-material`) — aucun plugin
    supplémentaire n'est requis.

---

## `mkdocs.yml` complet

```yaml
site_name: Nom du projet
docs_dir: docs
site_dir: site

theme:
  name: material
  language: fr
  font: false
  palette:
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
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.indexes
    - navigation.expand
    - navigation.top
    - search.highlight
    - search.suggest
    - content.code.copy
    - content.code.annotate

markdown_extensions:
  - admonition
  - tables
  - attr_list
  - def_list
  - footnotes
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.inlinehilite
  - pymdownx.keys
  - pymdownx.snippets
  - pymdownx.emoji:
      emoji_index: !!python/name:material.extensions.emoji.twemoji
      emoji_generator: !!python/name:material.extensions.emoji.to_svg
  - pymdownx.tasklist:
      custom_checkbox: true
  - pymdownx.highlight:
      anchor_linenums: true
      line_spans: __span
      pygments_lang_class: true
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.arithmatex:
      generic: true

plugins:
  - search:
      lang: fr
  - minify:
      minify_html: true
  # Décommenter une fois le dépôt git initialisé avec au moins un commit :
  # - git-revision-date-localized:
  #     enable_creation_date: true
  #     fallback_to_build_date: true
  - awesome-pages
  - include-markdown
  - macros

extra_css:
  - stylesheets/extra.css

extra_javascript:
  - javascripts/mathjax.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
  - javascripts/nav-dropdown.js

extra:
  generator: false
```

!!! tip "Activer `git-revision-date-localized`"
    Le plugin est commenté par défaut car il exige un dépôt Git avec **au
    moins un commit**. Une fois le dépôt initialisé, décommentez le bloc en
    **conservant** `fallback_to_build_date: true`. C'est ce que fait ce
    wiki, dont le dépôt est versionné.

---

## Ce que chaque extension apporte

| Extension | Apport dans les pages |
|---|---|
| `admonition` + `pymdownx.details` | Encadrés `!!! note` et blocs repliables `??? ` |
| `pymdownx.superfences` | Diagrammes **Mermaid** et blocs de code imbriqués |
| `pymdownx.tabbed` | Onglets de contenu `=== "Onglet"` |
| `pymdownx.highlight` + `inlinehilite` | Coloration syntaxique, ligne par ligne |
| `pymdownx.emoji` | Icônes `:material-*:` (utilisées par les grilles de cartes) |
| `pymdownx.arithmatex` | Formules LaTeX rendues via MathJax 3 |
| `pymdownx.keys` | Touches clavier `++ctrl+c++` |
| `attr_list` + `md_in_html` | Grilles de cartes `<div class="grid cards" markdown>` |
| `pymdownx.tasklist` | Cases à cocher `- [ ]` |
| `toc` | Table des matières et ancres permanentes |

---

## Compléments

- **CSS pleine largeur et sidebars** : voir [Personnalisations](personnalisation.md).
- **Cibles Makefile** (`docs`, `docs-start`, `docs-stop`, `docs-build`) : voir [Commandes](commandes.md).
- **Génération automatique** de tout ce stack : [`mkdocsinit`](../../systeme/ubuntu/alm_tools/outils/mkdocsinit.md).
