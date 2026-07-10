# 6. Où trouver quoi

Cette dernière page sert d'index rapide, à consulter une fois le reste du
guide déjà lu — pas à apprendre par cœur.

## 6.1 Fichiers du projet pass-tool

| Fichier | Rôle |
|---|---|
| `src/pass_tool/cli.py` | Toute la logique métier — voir [chapitre 2](lecture-du-code.md) |
| `src/pass_tool/main.py` | Point d'entrée trivial, appelle simplement `app()` |
| `src/pass_tool/__init__.py` | Déclare `__version__` |
| `tests/test_cli.py` | Aide générale, `--help`, cas de base de `gen` |
| `tests/test_password.py` | `_generate_password` en isolation |
| `tests/test_clipboard.py` | Presse-papier réel (pas de mock) |
| `tests/test_vault_entry.py` | `vault list` / `entry list`, définit le mock `pass-cli` |
| `tests/test_interactive.py` | Menu interactif, réutilise le mock ci-dessus |
| `pyproject.toml` | Dépendances, config `pytest`/`ruff`/`mypy`, point d'entrée CLI |
| `ruff.toml` | Configuration détaillée du lint |
| `uv.lock` | Versions exactes verrouillées des dépendances |
| `Makefile` | Raccourcis `make check`, `make test`, etc. — voir [chapitre 5](workflow-et-exercice.md) |
| `.pre-commit-config.yaml` | Config des vérifications automatiques au commit — voir [chapitre 5](workflow-et-exercice.md) |
| `README.md` | Doc de référence utilisateur, à jour |
| `.dev-notes.md` | Notes de reprise personnelles, **non committées** (gitignored) — ne pas s'y fier comme documentation pérenne |
| `docs/` (MkDocs local) | ⚠️ Désynchronisé du code réel (ex. option `--name` fictive) — ne pas utiliser comme référence, voir 6.3 |

## 6.2 Documentation existante dans `~/alm_notes`

| Fichier | Contenu | Angle |
|---|---|---|
| [`outils/pass-tool.md`](../../../systeme/ubuntu/alm_tools/outils/pass-tool.md) | Installation, usage de chaque commande, sécurité | Utilisateur final |
| [`outils/index.md`](../../../systeme/ubuntu/alm_tools/outils/index.md) | Carte de présentation dans la grille des outils | Découverte |
| [`postinstall/post-installation.md`](../../../systeme/ubuntu/alm_tools/postinstall/post-installation.md) (étape 41) | Installation via `uv tool install --force` | Déploiement machine |
| [`securite/proton/ecosysteme.md`](../../../securite/proton/ecosysteme.md) | Renvois croisés (PAT vs auth interactive), exemples `pass-cli` en ligne de commande | Sécurité/écosystème Proton |
| [`pass-cli-subprocess.md`](../pass-cli-subprocess.md) | Patterns génériques subprocess + pass-cli (gestion des codes de sortie, exposition de secrets) | Développeur — référence générique, pas spécifique à pass-tool |
| [`cli/index.md`](../cli/index.md) | Typer, callbacks, pattern décorateur + registre — approfondissement du chapitre 3 | Développeur — générique, illustré par pass-tool |
| **ce guide** | Prise en main technique pour contribuer à un petit projet Python | Développeur — méthode, illustrée par pass-tool |

Ce guide est donc complémentaire à `pass-tool.md` (qui reste la référence
pour un usage courant de l'outil), à `pass-cli-subprocess.md` (qui explique
les patterns génériques repris dans `_run_pass_cli`) et à `cli/` (qui
approfondit les mécanismes Typer évoqués au chapitre 3).

## 6.3 Une incohérence connue, à ne pas reproduire

Le dossier `docs/` interne au dépôt `pass-tool` (scaffolding MkDocs généré
à l'origine par un outil de création de projet) documente une option
`--name` qui n'existe pas dans le code réel — reste d'un modèle générique
jamais mis à jour. Si vous consultez ce dossier par erreur en cherchant de
la documentation, sachez qu'il n'est pas fiable : le `README.md` à la
racine du projet est la seule source à jour côté dépôt.

## 6.4 Pistes de cross-référencement futur

Certaines pages de `~/alm_notes` pourraient utilement compléter ce guide,
sans que ce soit nécessaire dès maintenant :

- **[uv — Gestionnaire de projets](../uv/index.md)** — pourrait enrichir
  [le chapitre 1](mise-en-route.md) avec plus de détail sur `uv sync`/`uv
  run`.
- **[Concurrence — Sync, Threads & Async](../concurrence/index.md)** —
  pourrait éclairer davantage
  [2.5.1](lecture-du-code.md#251-comprendre-_spawn_clipboard_clearer)
  (processus détaché du presse-papier), si son contenu couvre la gestion de
  processus.
- **[Design Patterns](../patterns/index.md)** (Policy Pattern, Ports &
  Adapters) — pass-tool n'utilise pas ces patterns actuellement (pas
  d'architecture en couches, voir [l'index de ce guide](index.md)), donc
  pas de lien pertinent pour l'instant. À reconsidérer si le projet grossit
  ou si un autre projet illustrant ces patterns sert de fil rouge pour une
  future méthode similaire.

Ces liens ne sont pas encore posés dans ce guide — à évaluer plus tard, une
fois ces pages elles-mêmes plus complètes.
