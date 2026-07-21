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
uv run ruff check new-page.py --fix   # linter new-page.py (ruff.toml à la racine)
```

> `ruff` n'est **pas** une dépendance du projet (absent de `uv.lock`) — il provient de l'installation globale (`uv tool`) et `uv run` le trouve via le PATH. Ne pas l'ajouter à `pyproject.toml`.

> Toujours utiliser `uv run python new-page.py` — PyYAML est disponible comme dépendance transitive de MkDocs dans l'environnement uv. Le shim `wnp` / `install.sh` est un artefact ancien, ne pas s'en servir.

> **Conflit de port** : ce dépôt est aussi servi en permanence par un service systemd utilisateur `mkdocs.service` (défini dans le dépôt `alm_dots`) sur `127.0.0.1:8000` — piloté par les alias `mkr`/`mks`/`mkl`. Lancer `make docs` pendant que le service tourne fait basculer le serveur de dev sur le premier port libre (8001+). Pour servir sur 8000 en dev, arrêter d'abord le service (`mks` pour vérifier l'état).

## Carte du contenu (`docs/`)

| Répertoire | Onglet nav | Thème |
|---|---|---|
| racine `docs/` | Accueil | Page d'accueil, matériel, BIOS/EC |
| `systeme/ubuntu/` | Ubuntu | Post-install Ubuntu, alm_dots, alm_tools |
| `systeme/alpine/` | Alpine | Alpine Linux, VMs, Docker |
| `electronique/` | Électronique | PlatformIO, pioinit |
| `developpement/python/` | Développement | uv, FastAPI, concurrence, design patterns |
| `lcl/` | LCL | Mainframe / z/OS (Kafka, CICS, zDevOps plugin) |
| `securite/` | Sécurité | TLS, AppArmor, OpenSSL, Proton |
| `outils/` | Outils | CLI modernes (eza…), Kitty, yt-dlp, Claude Code, MkDocs |

Chaque section utilise `navigation.indexes` : le `index.md` du répertoire est la page d'accueil cliquable de la section dans la nav. Toute section créée avec des sous-sections **doit** avoir un `index.md`.

**Cross-référence pioinit** : `electronique/pioinit/index.md` apparaît à la fois sous l'onglet Électronique et sous Ubuntu > alm_tools > Outils spécialisés. C'est intentionnel — ne pas dupliquer le fichier.

## Répertoire de staging — `drafts/`

`drafts/` est la zone de dépôt pour les contenus en attente d'intégration :

- **`drafts/*.md`** — brouillons de pages pas encore placés dans `docs/` ni enregistrés dans `nav:`
- **`drafts/img/`** — images en attente de déplacement vers `docs/assets/images/`

Brouillons actuellement en attente :
- `drafts/cics_event_processing.md` (à intégrer dans `lcl/`).
- `drafts/smartphone-linux-pistes-a-explorer.md` — point ouvert, liste
  d'outils smartphone↔Linux à tester avant rédaction (pas une page finie à
  intégrer telle quelle).

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

## Assets statiques

- **Images** : toutes les images référencées dans les pages vont dans `docs/assets/images/`. Ne pas créer de sous-dossiers images dans les répertoires de sections.
- **JS custom** (`docs/javascripts/`) :
  - `mathjax.js` — initialise MathJax 3 pour `pymdownx.arithmatex` (LaTeX dans les pages)
  - `nav-dropdown.js` — comportement de navigation personnalisé
- **CSS** : `docs/stylesheets/extra.css` — mise en page 100 % largeur + sidebars (voir standard dans `~/.claude/CLAUDE.md`)

## Extensions MkDocs spécifiques à ce projet

- **MathJax** : rendu LaTeX via `pymdownx.arithmatex` + CDN MathJax 3.
- La config MkDocs suit le standard défini dans `~/.claude/CLAUDE.md` (theme material, font: false, extra.css full-width, Makefile cibles).
- **Écart volontaire avec le standard global** : le plugin `macros` est déclaré **sans** `module_name` et le projet n'a ni `main.py` ni `docs/macros.py`. Ne pas ajouter `module_name: docs/macros` (référence du CLAUDE.md global) sans créer le fichier — cela casserait le build.

## Fichiers à ne pas modifier

- `migrate.py` — script de migration one-shot TiddlyWiki → MkDocs (artefact historique).
- `install.sh` — ancien shim d'installation pour `new-page.py`, remplacé par `uv run python new-page.py`.
- `site/` — sortie générée par `make docs-build`, ignorée par git.
