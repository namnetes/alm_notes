# mkdocsinit

`mkdocsinit` configure **MkDocs Material** dans un projet avec toutes les
personnalisations standard.  L'outil est **idempotent** : relancé plusieurs
fois sur le même projet, il ne touche que ce qui manque.

**Source :** `~/alm_tools/cli/mkdocsinit`

---

## Ce que l'outil fait

| Étape | Fichier / action | Condition |
|-------|------------------|-----------|
| 1 | `git init` + branche `main` | Ignoré si `.git/` existe déjà |
| 2 | `uv add --dev` des plugins MkDocs | Ignoré si `mkdocs` déjà dans `pyproject.toml` |
| 3 | `docs/stylesheets/extra.css` | Ignoré si le fichier existe |
| 4 | `docs/javascripts/nav-dropdown.js` | Ignoré si le fichier existe |
| 5 | `docs/javascripts/mathjax.js` | Ignoré si le fichier existe |
| 6 | `mkdocs.yml` | Créé si absent ; patché si plugin problématique actif |
| 7 | `docs/index.md` (page de bienvenue) | Ignoré si le fichier existe |
| 8 | `docs/macros.py` (stub macros) | Ignoré si le fichier existe |
| 9 | `Makefile` | **Créé** si absent ; **jamais modifié** s'il existe |

!!! warning "Makefile existant"
    Si un `Makefile` est déjà présent (même vide), mkdocsinit ne le touche
    pas.  Intégrer les cibles docs manuellement si nécessaire.

---

## Installation

```bash
uv tool install --no-cache ~/alm_tools/cli/mkdocsinit
```

Réinstallation après modification du code source (toujours désinstaller
d'abord pour forcer le rebuild du wheel) :

```bash
uv tool uninstall mkdocsinit
uv tool install --no-cache ~/alm_tools/cli/mkdocsinit
```

---

## Utilisation

```bash
# Dans le répertoire courant (PATH et --yes sont optionnels)
mkdocsinit

# Confirmation interactive (défaut sans --yes)
mkdocsinit                  # affiche "Continuer ? [Y/n]:"
mkdocsinit --yes            # sans confirmation

# Répertoire explicite
mkdocsinit ~/mon-projet

# Avec le plugin mkdocstrings (projets Python avec API docs)
mkdocsinit --with-mkdocstrings
```

### Options

| Option | Description |
|--------|-------------|
| `PATH` | Répertoire cible (défaut : répertoire courant) |
| `--name / -n` | Nom du site (défaut : issu de `pyproject.toml` ou du nom du dossier) |
| `--author / -a` | Auteur (défaut : `git config user.name`) |
| `--with-mkdocstrings` | Configure le plugin `mkdocstrings[python]` sur `src/` |
| `--yes / -y` | Passer la confirmation interactive |

---

## Fichiers générés

### `docs/stylesheets/extra.css`

Cinq règles CSS au-delà des valeurs par défaut de Material :

1. **Largeur 100 %** — supprime la colonne centrée de ~1200 px
2. **Dimensions des sidebars** — nav gauche 13.068 rem, TOC droite 20.7537 rem
3. **Fix webkit** — corrige le `calc(100% - 11.5rem)` qui bloque le contenu des sidebars
4. **Ellipsis sur les titres longs** — tronque avec `…` plutôt que de wrapper sur plusieurs lignes
5. **CSS dropdown** — styles pour les menus déroulants injectés par `nav-dropdown.js`

### `docs/javascripts/nav-dropdown.js`

Ajoute un menu déroulant au survol sur les onglets qui ont des sous-sections.
Utilise `document$` de Material pour se réexécuter à chaque navigation SPA.

### `docs/javascripts/mathjax.js`

Initialise MathJax 3 pour le rendu LaTeX.  Déclaré **avant** le CDN dans
`extra_javascript` pour que MathJax lise la config au démarrage.

### `docs/macros.py`

Stub minimal pour le plugin `mkdocs-macros`.  Sans ce fichier le plugin
crashe au démarrage quand `module_name: docs/macros` est configuré.

```python
def define_env(env):
    # ajouter ici variables, filtres et macros personnalisés
    pass
```

### `mkdocs.yml`

```yaml
theme:
  language: fr       # interface en français
  font: false        # pas de Google Fonts
  features:
    - navigation.tabs / sections / indexes / expand / top
    - search.highlight / search.suggest
    - content.code.copy / content.code.annotate

plugins:
  - search (lang: fr)
  - minify
  # - git-revision-date-localized  ← commenté par défaut (requiert ≥1 commit git)
  - awesome-pages
  - include-markdown
  - macros (module_name: docs/macros)
  # - mkdocstrings  ← ajouté si --with-mkdocstrings

extra_javascript:
  - javascripts/mathjax.js
  - CDN MathJax 3
  - javascripts/nav-dropdown.js
```

Pas de section `nav:` — MkDocs auto-découvre les pages.  Utiliser des
fichiers `.pages` (awesome-pages) pour contrôler l'ordre si nécessaire.

!!! info "Plugin git-revision-date"
    Le plugin `git-revision-date-localized` est commenté par défaut car il
    requiert un dépôt git avec **au moins un commit**.  Pour l'activer :

    ```bash
    uv add --dev mkdocs-git-revision-date-localized-plugin
    ```

    Puis décommenter le bloc dans `mkdocs.yml` :

    ```yaml
    - git-revision-date-localized:
        enable_creation_date: true
        fallback_to_build_date: true
    ```

### `Makefile` (créé seulement si absent)

```makefile
.DEFAULT_GOAL := help

docs        # serveur local (premier port libre 8000–8050)
docs-start  # serveur en arrière-plan (PID dans .mkdocs.pid)
docs-stop   # arrêter le serveur arrière-plan
docs-build  # générer le site statique dans site/
help        # afficher cette aide
```

---

## Intégration avec devinit

`devinit` appelle `mkdocsinit . --with-mkdocstrings --yes` en phase
**best-effort** (après `git init` et `uv sync`).  Si `mkdocsinit` n'est pas
installé, devinit affiche un avertissement mais continue — relancer
`mkdocsinit --with-mkdocstrings` suffit.

Répartition des responsabilités :

| Artefact | Généré par |
|----------|-----------|
| `mkdocs.yml`, CSS, JS, `macros.py`, `Makefile` docs | **mkdocsinit** |
| `docs/index.md` (contenu projet-spécifique) | **devinit** — mkdocsinit le skippe |
| `docs/api.md` (autodoc mkdocstrings) | **devinit** |
| Dépendances MkDocs dans `pyproject.toml` | **devinit** — mkdocsinit skippe `uv add` |
