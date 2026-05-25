# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

**Wikinotes** — wiki de documentation technique personnelle, propulsé par MkDocs Material. Tout le contenu est dans `docs/` sous forme de fichiers Markdown. La structure de navigation dans `mkdocs.yml` (bloc `nav:`) est l'index autoritatif de toutes les pages.

## Langue du contenu

Toutes les pages wiki (`docs/**/*.md`) sont rédigées en **français**. Lors de la création ou modification d'une page, écrire en français — y compris les titres, les textes, les admonitions et les commentaires Markdown.

## Commandes

```bash
uv sync                       # installer / mettre à jour les dépendances
make docs                     # servir en foreground (port libre détecté entre 8000–8050)
make docs-start               # servir en arrière-plan (.mkdocs.pid)
make docs-stop                # arrêter le serveur de fond
make docs-build               # compiler vers site/
make check-deps               # vérifier uv et lsof

uv run python new-page.py     # gestionnaire interactif de pages
```

> Toujours utiliser `uv run python new-page.py` — PyYAML est disponible comme dépendance transitive de MkDocs dans l'environnement uv. Le shim `wnp` / `install.sh` est un artefact ancien, ne pas s'en servir.

## Carte du contenu (`docs/`)

| Répertoire | Thème |
|---|---|
| `systeme/ubuntu/` | Post-install Ubuntu, alm-dotfiles, alm-tools |
| `systeme/alpine/` | Alpine Linux, VMs, Docker |
| `electronique/` | PlatformIO, pioinit |
| `developpement/python/` | uv, FastAPI, concurrence, design patterns |
| `lcl/` | Mainframe / z/OS (Kafka, CICS) |
| `securite/` | TLS, AppArmor, OpenSSL, Proton |
| `outils/` | GitHub CLI, Zed, Claude Code, yt-dlp |

Chaque section a généralement un `index.md` (page d'accueil) + des pages thématiques.

## Répertoire de staging — `drafts/`

`drafts/` est la zone de dépôt pour les contenus en attente d'intégration :

- **`drafts/*.md`** — brouillons de pages pas encore placés dans `docs/` ni enregistrés dans `nav:`
- **`drafts/img/`** — images en attente de déplacement vers `docs/assets/images/`

Workflow d'intégration d'un brouillon :
1. Déplacer le `.md` dans le bon sous-répertoire de `docs/`
2. Déplacer les images associées dans `docs/assets/images/`
3. Enregistrer la page dans `mkdocs.yml` via `uv run python new-page.py` ou manuellement
4. Vérifier avec `make docs-build`

## Gestion des pages — `new-page.py`

Script interactif qui lit et écrit `mkdocs.yml`. Quatre opérations :

1. **Créer une section** — ajoute l'entrée nav et un `index.md` optionnel.
2. **Ajouter une page** — crée le `.md` et injecte l'entrée nav dans la section choisie.
3. **Supprimer une page** — analyse les liens entrants dans tous les `.md` avant de supprimer.
4. **Supprimer une section** — analyse d'impact sur les références externes avant suppression.

**Point technique critique** : le loader/dumper YAML utilise une classe `_PythonTag` pour préserver les tags `!!python/name:` (requis par `pymdownx.superfences`). Ne jamais remplacer ce loader par `yaml.safe_load` — cela corromprait `mkdocs.yml`.

## Navigation explicite

La navigation est **explicite** dans `mkdocs.yml`, pas auto-découverte. Toute nouvelle page doit être enregistrée dans `nav:` (via `new-page.py` ou manuellement). Après toute modification manuelle, vérifier avec `make docs-build`.

## Extensions MkDocs spécifiques à ce projet

- **MathJax** : rendu LaTeX via `pymdownx.arithmatex` + CDN MathJax 3, initialisé par `docs/javascripts/mathjax.js`.
- **nav-dropdown** : comportement de navigation personnalisé via `docs/javascripts/nav-dropdown.js`.
- La config MkDocs suit le standard défini dans `~/CLAUDE.md` (theme material, font: false, extra.css full-width, Makefile cibles).

## Fichiers à ne pas modifier

- `migrate.py` — script de migration one-shot TiddlyWiki → MkDocs (artefact historique). Ne fait pas partie du workflow courant.
- `site/` — sortie générée, ignorée par git.
