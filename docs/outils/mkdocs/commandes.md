# Commandes quotidiennes

## Tableau récapitulatif

| Commande | Effet | Quand l'utiliser |
|---|---|---|
| `uv sync` | Installe / met à jour les dépendances | Après `git pull` ou ajout de paquet |
| `uv run mkdocs serve` | Serveur local avec rechargement automatique | Pendant l'écriture |
| `uv run mkdocs build` | Génère `site/` en HTML statique | Avant déploiement |
| `uv run mkdocs build --strict` | Idem + erreur si lien brisé | En CI/CD |
| `uv run mkdocs --help` | Aide complète | En cas de doute |

---

## Serveur local de développement

```bash
uv run mkdocs serve
```

Ouvrez votre navigateur à l'adresse affichée (par défaut
`http://127.0.0.1:8000`). Chaque sauvegarde d'un fichier `.md` ou de
`mkdocs.yml` **recharge automatiquement** la page dans le navigateur.

```
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 0.42 seconds
INFO    -  [HH:MM:SS] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO    -  [HH:MM:SS] Serving on http://127.0.0.1:8000/
```

Arrêtez le serveur avec `Ctrl+C`.

### Servir sur une adresse personnalisée

```bash
# Accessible depuis d'autres machines sur le réseau local
uv run mkdocs serve --dev-addr 0.0.0.0:8080

# Port personnalisé en local
uv run mkdocs serve --dev-addr 127.0.0.1:9000
```

---

## Générer le HTML statique

```bash
uv run mkdocs build
```

Le répertoire `site/` contient le site complet. Vous pouvez l'ouvrir
directement dans un navigateur ou le déployer sur n'importe quel hébergement.

```bash
# Ouvrir le site généré localement
xdg-open site/index.html
```

---

## Mode strict (recommandé en CI)

```bash
uv run mkdocs build --strict
```

En mode strict, MkDocs retourne le code d'erreur `1` si la documentation
contient des **liens brisés** (vers des pages ou des ancres inexistantes).
C'est la commande à utiliser dans un pipeline CI/CD.

---

## Makefile — cibles recommandées

Le standard du projet (défini dans `~/.claude/CLAUDE.md`) utilise ces cibles :

```makefile
PORT     := $(shell \
    for p in $$(seq 8000 8050); do \
        lsof -ti:$$p >/dev/null 2>&1 || { echo $$p; break; }; \
    done)
HOST     := 127.0.0.1
PID_FILE := .mkdocs.pid
LOG_FILE := .mkdocs.log

docs:
    uv run mkdocs serve --dev-addr $(HOST):$(PORT)

docs-start:
    @if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
        echo "MkDocs tourne déjà (PID $$(cat $(PID_FILE)))"; \
    else \
        uv run mkdocs serve --dev-addr $(HOST):$(PORT) > $(LOG_FILE) 2>&1 & \
        echo $$! > $(PID_FILE); \
    fi

docs-stop:
    @PID=$$(cat $(PID_FILE)); kill $$PID && rm $(PID_FILE)

docs-build:
    uv run mkdocs build
```

La détection de port dynamique (`lsof` sur 8000–8050) permet de faire
tourner plusieurs projets docs en parallèle sans conflit.
