# Workflow projet

Cette page couvre le cycle de vie complet d'un projet Python géré avec `uv` :
de la création jusqu'à l'exécution, en passant par la gestion des dépendances.

---

## Créer un projet

### Les différents types de projets

| Commande | Usage |
|---|---|
| `uv init mon-projet` | Projet minimaliste, fichier unique (`hello.py`) |
| `uv init --app mon-projet` | Application avec structure `src/` |
| `uv init --lib mon-projet` | Bibliothèque publiable, structure `src/` |

Pour un script ou un outil en ligne de commande, utilisez `--app`.

### Initialisation

```bash
uv init --app mon-hello
cd mon-hello
```

`uv` crée la structure suivante :

```
mon-hello/
├── .python-version     ← version Python épinglée pour ce projet
├── README.md
├── pyproject.toml      ← cerveau du projet
└── src/
    └── mon_hello/
        ├── __init__.py
        └── main.py
```

!!! warning "Tirets et underscores"
    Le nom du projet (`mon-hello`) peut contenir des tirets, mais le nom du
    **dossier Python** utilise des underscores (`mon_hello`). Python n'accepte
    pas les tirets dans les noms de modules. `uv` gère cette conversion
    automatiquement, mais il faut le savoir pour écrire les imports correctement.

---

## Comprendre `pyproject.toml`

C'est le fichier central du projet. Il contient toutes les métadonnées et
la configuration.

```toml
[project]
name = "mon-hello"
version = "0.1.0"
description = "Mon premier projet uv"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []          # ← les dépendances s'ajoutent ici automatiquement

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

| Champ | Rôle |
|---|---|
| `name` | Nom du projet (avec tirets) |
| `version` | Version sémantique |
| `requires-python` | Version minimale de Python |
| `dependencies` | Liste des paquets nécessaires |

---

## L'environnement virtuel

`uv` crée automatiquement un `.venv` à la racine du projet lors de la première
commande `uv add` ou `uv sync`. **Vous n'avez jamais besoin de l'activer.**

```
mon-hello/
├── .venv/          ← créé automatiquement par uv
│   ├── bin/
│   ├── lib/
│   └── ...
├── pyproject.toml
└── ...
```

!!! tip "Ignorer `.venv` dans git"
    Le `.venv` ne doit pas être versionné. Vérifiez que `.venv` est dans
    votre `.gitignore` :
    ```bash
    echo ".venv" >> .gitignore
    ```
    `uv init` l'y ajoute automatiquement.

---

## Exécuter du code

### Avec `uv run`

`uv run` exécute une commande dans le contexte du projet (avec le bon Python
et les bonnes dépendances), sans avoir à activer le venv manuellement.

```bash
# Exécuter un fichier Python
uv run python src/mon_hello/main.py

# Exécuter un module
uv run python -m mon_hello

# Exécuter un outil de développement (ex: un linter)
uv run ruff check .

# Lancer les tests
uv run pytest
```

!!! info "uv run vs activation manuelle"
    `source .venv/bin/activate` fonctionne aussi, mais `uv run` est préférable :
    il vérifie que les dépendances sont synchronisées avant d'exécuter, et il
    n'affecte pas votre shell courant.

### Premier test

Ouvrez `src/mon_hello/main.py` et remplacez son contenu par :

```python
def main() -> None:
    print("Bonjour depuis mon-hello !")

if __name__ == "__main__":
    main()
```

Exécutez :

```bash
uv run python src/mon_hello/main.py
```

```
Bonjour depuis mon-hello !
```

---

## Gérer les dépendances

### Ajouter un paquet

```bash
uv add requests
uv add rich typer          # plusieurs paquets à la fois
uv add "requests>=2.28"    # avec contrainte de version
```

`uv add` met automatiquement à jour `pyproject.toml` et `uv.lock`.

### Dépendances de développement

Les dépendances de développement (tests, linters, formateurs) ne doivent pas
être incluses dans le programme final distribué. Ajoutez-les avec `--dev` :

```bash
uv add --dev pytest ruff
```

Elles apparaissent dans `pyproject.toml` sous `[tool.uv]` ou
`[dependency-groups]`, séparément des dépendances de production.

!!! note "dev vs production"
    Quand un utilisateur installe votre outil avec `uv tool install`, seules
    les dépendances de production (sans `--dev`) sont incluses. `pytest` et
    `ruff` restent sur votre machine de développement.

### Supprimer un paquet

```bash
uv remove requests
```

### Voir les dépendances installées

```bash
uv pip list        # liste les paquets du venv
uv tree            # arbre de dépendances
```

---

## Le fichier `uv.lock`

`uv.lock` est généré automatiquement à chaque `uv add`, `uv remove` ou
`uv sync`. Il enregistre la version exacte de chaque paquet et de toutes
leurs dépendances transitives.

```
# uv.lock (extrait)
[[package]]
name = "requests"
version = "2.31.0"
source = { registry = "https://pypi.org/simple" }
dependencies = [
  { name = "certifi" },
  { name = "charset-normalizer" },
  ...
]
```

!!! warning "Ne jamais modifier `uv.lock` à la main"
    Ce fichier est géré exclusivement par `uv`. Toute modification manuelle
    sera écrasée. Pour changer les dépendances, utilisez toujours `uv add`
    ou `uv remove`.

---

## Synchroniser l'environnement : `uv sync`

Quand vous clonez un projet existant ou revenez dessus après un `git pull`,
utilisez `uv sync` pour reconstituer l'environnement exactement comme défini
dans `uv.lock` :

```bash
git clone https://github.com/example/mon-hello
cd mon-hello
uv sync               # installe toutes les dépendances
uv run python src/mon_hello/main.py
```

`uv sync` sans arguments installe les dépendances de production et de
développement. Pour la production uniquement :

```bash
uv sync --no-dev
```

---

## Exercice guidé — projet complet

Cet exercice crée un projet qui récupère la météo depuis une API publique.

**Étape 1 : Créer le projet**

```bash
uv init --app meteo-cli
cd meteo-cli
```

**Étape 2 : Ajouter les dépendances**

```bash
uv add requests rich
uv add --dev ruff
```

Vérifiez que `pyproject.toml` contient maintenant `requests` et `rich` dans
`dependencies`.

**Étape 3 : Écrire le code**

Ouvrez `src/meteo_cli/main.py` et remplacez son contenu :

```python
import requests
from rich.console import Console
from rich.table import Table


def get_meteo(ville: str) -> dict:
    url = f"https://wttr.in/{ville}?format=j1"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    console = Console()
    ville = "Paris"

    console.print(f"[bold]Météo pour {ville}[/bold]")

    try:
        data = get_meteo(ville)
        temp = data["current_condition"][0]["temp_C"]
        desc = data["current_condition"][0]["weatherDesc"][0]["value"]

        table = Table()
        table.add_column("Mesure")
        table.add_column("Valeur")
        table.add_row("Température", f"{temp} °C")
        table.add_row("Conditions", desc)
        console.print(table)

    except Exception as e:
        console.print(f"[red]Erreur : {e}[/red]")


if __name__ == "__main__":
    main()
```

**Étape 4 : Tester**

```bash
uv run python src/meteo_cli/main.py
```

**Étape 5 : Simuler un clone sur une autre machine**

```bash
# Supprimer le venv local
rm -rf .venv

# Reconstituer depuis uv.lock
uv sync

# Vérifier que tout fonctionne toujours
uv run python src/meteo_cli/main.py
```

Si le résultat est identique, votre projet est reproductible.

!!! tip "Prochaine étape"
    Pour transformer ce projet en commande globale (`meteo` accessible depuis
    n'importe quel dossier), consultez la page [Outils CLI](outils.md).
