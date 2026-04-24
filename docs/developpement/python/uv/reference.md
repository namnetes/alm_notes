# Référence

## Cheat sheet — commandes essentielles

### Installation et configuration

| Commande | Action |
|---|---|
| `curl -LsSf https://astral.sh/uv/install.sh \| sh` | Installer `uv` |
| `uv self update` | Mettre à jour `uv` |
| `uv --version` | Vérifier la version |
| `uv python list` | Lister les versions Python disponibles |
| `uv python install 3.12` | Installer Python 3.12 |
| `uv python pin 3.12` | Épingler Python 3.12 pour le projet courant |

### Projet

| Commande | Action |
|---|---|
| `uv init --app mon-projet` | Créer un projet application |
| `uv init --lib ma-lib` | Créer une bibliothèque publiable |
| `uv add requests` | Ajouter une dépendance |
| `uv add --dev pytest` | Ajouter une dépendance de développement |
| `uv remove requests` | Supprimer une dépendance |
| `uv sync` | Synchroniser le venv depuis `uv.lock` |
| `uv sync --no-dev` | Synchroniser sans les dépendances de dev |
| `uv run python script.py` | Exécuter un script |
| `uv run pytest` | Lancer les tests |
| `uv pip list` | Lister les paquets installés dans le venv |
| `uv tree` | Afficher l'arbre de dépendances |
| `uv lock` | Régénérer `uv.lock` sans modifier le venv |

### Outils globaux

| Commande | Action |
|---|---|
| `uv tool install .` | Installer le projet courant comme outil global |
| `uv tool install . --force` | Réinstaller (après modification du code) |
| `uv tool install ruff` | Installer un outil depuis PyPI |
| `uv tool list` | Lister les outils installés |
| `uv tool uninstall mon-outil` | Désinstaller un outil |
| `uv tool run ruff check .` | Exécuter un outil sans l'installer |
| `uv cache clean` | Vider le cache de téléchargement |

---

## Inventaire des chemins

```
~/.local/bin/
├── uv                          ← le binaire uv lui-même
├── mon-outil                   ← shim vers l'outil installé
└── ...

~/.local/share/uv/
├── python/                     ← versions Python gérées par uv
│   ├── cpython-3.11.x/
│   ├── cpython-3.12.x/
│   └── ...
└── tools/                      ← environnements isolés des outils
    ├── mon-outil/
    │   ├── bin/
    │   │   └── mon-outil       ← le vrai exécutable
    │   └── lib/
    └── devinit/
        └── ...

~/.cache/uv/                    ← cache des paquets téléchargés

~/mon-projet/                   ← votre projet
├── .venv/                      ← environnement virtuel du projet
├── .python-version             ← version Python épinglée
├── pyproject.toml
├── uv.lock                     ← versions exactes des dépendances
└── src/
    └── mon_projet/
        ├── __init__.py
        └── main.py
```

---

## Bonnes pratiques

### À faire

- **Versionner `uv.lock`** dans git — c'est la garantie de reproductibilité.
- **Utiliser `uv add`** pour toutes les dépendances — jamais `pip install`
  directement dans un projet `uv`.
- **Séparer les dépendances dev** avec `uv add --dev` — elles n'ont pas à
  être distribuées avec l'outil final.
- **Tester avec `uv run`** avant d'installer globalement avec `uv tool install`.
- **Vérifier `~/.local/bin` dans le PATH** après l'installation de `uv`.

### À éviter

!!! danger "Ne mélangez pas pip et uv dans le même projet"
    `pip install requests` dans un projet géré par `uv` modifie le venv
    sans mettre à jour `pyproject.toml` ni `uv.lock`. Le projet devient
    non reproductible. Utilisez toujours `uv add requests`.

!!! warning "N'activez pas le venv manuellement"
    `source .venv/bin/activate` fonctionne, mais ce n'est pas la bonne
    habitude avec `uv`. Préférez `uv run commande`. Si vous êtes dans un
    shell activé et que vous oubliez de le désactiver, vous pouvez exécuter
    du code dans le mauvais contexte.

!!! warning "Tirets vs underscores"
    Le nom du projet peut contenir des tirets (`mon-hello`), mais le nom
    du module Python doit utiliser des underscores (`mon_hello`). Un import
    `import mon-hello` est invalide en Python.

---

## Erreurs fréquentes

### `command not found : uv`

`~/.local/bin` n'est pas dans le `PATH`.

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### `command not found : mon-outil` après `uv tool install`

Le shim est créé dans `~/.local/bin/` mais ce répertoire n'est pas dans le
`PATH`, ou la session n'a pas été rechargée.

```bash
source ~/.bashrc
which mon-outil
```

### `ModuleNotFoundError` après `uv tool install`

Le point d'entrée dans `[project.scripts]` pointe vers un chemin incorrect.

Vérifiez :
```toml
[project.scripts]
# Syntaxe : "paquet.module:fonction"
# Le nom de paquet utilise des underscores, pas des tirets
mon-outil = "mon_outil.main:main"
#            ^^^^^^^^^
#            Doit correspondre au dossier dans src/
```

Vérifiez aussi que `src/mon_outil/__init__.py` existe.

### `uv run` n'utilise pas la bonne version de Python

```bash
# Voir quelle version est utilisée
uv run python --version

# Épingler la version souhaitée pour ce projet
uv python pin 3.12
```

### `uv sync` échoue avec des conflits de dépendances

```bash
# Regénérer le lock file depuis zéro
rm uv.lock
uv lock
uv sync
```

### Le venv semble corrompu

```bash
rm -rf .venv
uv sync
```

---

## Comparaison rapide avec pip

| Tâche | pip | uv |
|---|---|---|
| Installer un paquet | `pip install requests` | `uv add requests` |
| Installer depuis requirements | `pip install -r requirements.txt` | `uv sync` |
| Créer un venv | `python -m venv .venv` | automatique |
| Geler les versions | `pip freeze > requirements.txt` | `uv.lock` (auto) |
| Installer un outil global | `pipx install ruff` | `uv tool install ruff` |
| Gérer Python | `pyenv install 3.12` | `uv python install 3.12` |

!!! note "pip reste utile"
    `uv` remplace `pip` dans le contexte d'un projet géré par `uv`. Mais
    `pip` reste présent sur le système et utile dans d'autres contextes
    (scripts rapides hors projet, compatibilité avec des outils tiers qui
    appellent `pip` directement, etc.).
