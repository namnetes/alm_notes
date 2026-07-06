# devinit

`devinit` génère la structure complète d'un projet Python aux standards du projet.
Il supporte six **types de projets** via l'option `--type`.

**Source :** `~/alm_tools/cli/devinit`

---

## Types de projets

| Type | Description | Dépendances ajoutées |
|------|-------------|---------------------|
| `generic` | Projet Python générique | — |
| `cli` | Outil en ligne de commande | Typer, Rich |
| `fastapi` | API REST | FastAPI, uvicorn, pydantic-settings |
| `streamlit` | Application web | Streamlit |
| `nicegui` | Application web | NiceGUI |
| `marimo` | Notebook Python réactif | Marimo |

---

## Installation

**Usage normal** — installer depuis le dépôt :

```bash
cd ~/alm_tools
uv tool install ./cli/devinit
```

**Mode développement** — les modifications du code source sont actives immédiatement :

```bash
cd ~/alm_tools/cli/devinit
uv tool install --editable .
```

!!! warning "Le flag `--force` utilise le cache"
    `uv tool install --force` réutilise un wheel en cache et ne reflète pas les
    dernières modifications du code source. Pour une réinstallation propre :

    ```bash
    uv tool uninstall devinit
    uv tool install --no-cache ~/alm_tools/cli/devinit
    ```

## Désinstallation

```bash
uv tool uninstall devinit
```

Supprime le shim `~/.local/bin/devinit` et l'environnement isolé
`~/.local/share/uv/tools/devinit/`.

---

## Utilisation

```bash
# Initialiser dans le répertoire courant (workflow standard)
mkdir mon-api && cd mon-api
devinit . --type fastapi

# Créer dans un sous-répertoire
devinit mon-api --type fastapi

# Sans prompts interactifs
devinit mon-cli --type cli --yes --no-venv

# Aide
devinit --help
```

---

## Options principales

| Option | Description |
|--------|-------------|
| `--type TYPE` | `generic`, `cli`, `fastapi`, `streamlit`, `nicegui`, `marimo` (défaut : `generic`) |
| `--description TEXT` | Description courte du projet |
| `--python VERSION` | Version Python cible (défaut : `3.12`) |
| `--no-notebooks` | Ne pas créer `notebooks/` |
| `--no-scripts` | Ne pas créer `scripts/` |
| `--no-pre-commit` | Pas de hooks pre-commit |
| `--no-pyright` | Pas de `pyrightconfig.json` |
| `--no-venv` | Ne pas créer le virtualenv (CI, tests) |
| `--yes` / `-y` | Accepter tous les défauts sans prompts |

---

## Structure générée

La **base commune** est générée pour tous les types.
Les types web (`fastapi`, `streamlit`, `nicegui`) ajoutent les fichiers Docker.

```
mon-projet/
├── pyproject.toml             # runtime + dev (MkDocs toujours inclus)
├── ruff.toml                  # linting/formatage 88 car.
├── .gitignore / .editorconfig / .gitlint
├── pyrightconfig.json
├── .pre-commit-config.yaml    # ruff + gitlint
├── .envrc                     # direnv + PYTHONPATH
├── .env.example
├── Makefile                   # install, test, lint, run*, docker-*
│                              # + docs* ajoutés par mkdocsinit
├── mkdocs.yml                 # généré par mkdocsinit
├── src/mon_projet/
│   └── main.py                # adapté au type choisi
├── tests/
├── data/
├── docs/
│   ├── index.md               # page d'accueil (contenu projet-spécifique)
│   ├── api.md                 # autodoc mkdocstrings
│   ├── stylesheets/extra.css  # généré par mkdocsinit
│   └── javascripts/           # nav-dropdown.js, mathjax.js — générés par mkdocsinit
├── .vscode/                   # settings, launch.json (debug adapté), tasks.json
└── .zed/                      # settings.json + tasks.json (toutes les cibles)
```

!!! info "mkdocsinit — source unique de vérité pour MkDocs"
    La configuration MkDocs (`mkdocs.yml`, CSS, JS, cibles Makefile) est générée
    par [`mkdocsinit`](mkdocsinit.md), appelé automatiquement en fin de `devinit`.
    Si `mkdocsinit` n'est pas installé, un avertissement est affiché mais le
    projet est créé quand même — relancer `mkdocsinit .` suffit.

**Fichiers supplémentaires par type :**

| Type | Ajouts |
|------|--------|
| `cli` | `src/*/cli.py`, `docs/cli.md` |
| `fastapi` | `src/*/routers/`, `src/*/models/`, `src/*/config.py`, `Dockerfile`, `docker-compose.yml`, `docs/endpoints.md` |
| `streamlit` | `src/*/app.py`, `src/*/pages/`, `Dockerfile`, `docker-compose.yml`, `docs/guide.md` |
| `nicegui` | `src/*/components/`, `Dockerfile`, `docker-compose.yml`, `docs/guide.md` |

---

## Cibles Makefile notables

```bash
make help          # liste toutes les cibles disponibles
make run           # lancer l'app (generic, cli, streamlit, nicegui)
make run-dev       # FastAPI : uvicorn avec hot-reload
make run-prod      # FastAPI : mode production
make docker-build  # construire l'image Docker
make docker-up     # démarrer les conteneurs
make docker-down   # arrêter les conteneurs
make docker-clean  # supprimer conteneurs, volumes et images locales
make docs          # serveur MkDocs en local (ajouté par mkdocsinit)
make docs-start    # serveur MkDocs en arrière-plan
make docs-stop     # arrêter le serveur arrière-plan
make docs-build    # générer le site statique dans site/
```

---

Documentation complète : [cli/devinit/README.md](https://github.com/namnetes/alm_tools/blob/main/cli/devinit/README.md)
