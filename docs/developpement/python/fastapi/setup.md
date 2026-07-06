# FastAPI — Installation et Configuration

## Création du projet avec `uv`

`uv` est le gestionnaire de projets Python recommandé — il remplace `pip`, `venv` et
`poetry` en un seul outil, écrit en Rust pour une performance maximale.

```bash
# Créer le projet
uv init my-api
cd my-api

# Ajouter FastAPI + serveur ASGI
uv add fastapi "uvicorn[standard]"

# Dépendances de développement (tests, linting)
uv add --dev pytest httpx ruff pyright
```

!!! info "Pourquoi `uvicorn[standard]` ?"

    L'extra `[standard]` installe deux bibliothèques C qui remplacent les composants
    Python pur d'Uvicorn par des équivalents natifs beaucoup plus rapides.

    **`uvloop` — boucle événementielle haute performance**

    Python asyncio s'appuie sur une boucle événementielle pour orchestrer les
    coroutines. La boucle par défaut est écrite en Python pur. `uvloop` la remplace
    par une implémentation en **Cython + C**, construite sur **libuv** — la même
    bibliothèque asynchrone utilisée par Node.js.

    - Gain mesuré : **2× à 4×** sur les benchmarks I/O intensifs.
    - Activation transparente : Uvicorn détecte `uvloop` et l'active automatiquement,
      sans aucune modification de code applicatif.
    - Limite : Linux/macOS uniquement — ignoré sur Windows (Uvicorn bascule
      silencieusement sur la boucle asyncio standard).

    **`httptools` — parseur HTTP en C**

    Par défaut, Uvicorn utilise **h11**, un parseur HTTP/1.1 écrit en Python pur.
    `httptools` le remplace par les bindings Python de **llhttp** (successeur de
    `http-parser`, lui aussi issu de l'écosystème Node.js).

    - Parsing des requêtes HTTP significativement plus rapide, surtout sous charge.
    - Activation transparente : Uvicorn bascule automatiquement sur `httptools` s'il
      est présent, sans configuration.
    - S'applique uniquement au protocole HTTP/1.1 — HTTP/2 passe par une autre pile
      (`h2`).

    **Installation**

    La façon la plus simple est l'extra `[standard]`, qui installe les deux en une
    commande :

    ```bash
    uv add "uvicorn[standard]"
    ```

    Si vous souhaitez les ajouter séparément (par exemple sur un projet existant) :

    ```bash
    uv add uvloop httptools
    ```

    Pour vérifier qu'ils sont bien pris en compte au démarrage, Uvicorn l'indique
    dans ses logs :

    ```
    INFO:     Started server process [12346]
    INFO:     Uvicorn running on http://127.0.0.1:8000
    # Aucun message d'avertissement = uvloop + httptools actifs
    ```

    Sans ces extras, Uvicorn affiche :

    ```
    WARNING:  uvloop is not installed, the default asyncio event loop will be used.
    WARNING:  httptools is not installed, the pure-Python HTTP parser will be used.
    ```

### Structure initiale générée

```
my-api/
├── .python-version   # Version Python fixée par uv
├── pyproject.toml    # Dépendances et config du projet
├── uv.lock           # Fichier de verrouillage (committer dans git)
└── main.py           # Point d'entrée (à restructurer — voir architecture)
```

---

## Premier serveur en 10 lignes

Remplacez `main.py` par ce contenu minimal pour vérifier que tout fonctionne :

```python
"""Point d'entrée FastAPI — version minimale de vérification."""

from fastapi import FastAPI

app = FastAPI(
    title="Mon API",
    description="Documentation générée automatiquement.",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Vérifie que le serveur est opérationnel."""
    return {"status": "ok"}
```

Lancez le serveur :

```bash
uv run uvicorn main:app --reload
```

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Ouvrez `http://localhost:8000/docs` — vous devriez voir Swagger UI avec un endpoint
`/health` déjà documenté et testable.

!!! tip "L'option `--reload`"
    `--reload` redémarre automatiquement le serveur à chaque modification de fichier.
    **Ne pas utiliser en production** — uniquement en développement.

---

## Configuration IDE

### VS Code

#### 1. Interpréter virtuel

VS Code doit utiliser l'environnement créé par `uv`. Ouvrez la palette
(`Ctrl+Shift+P`) → **Python: Select Interpreter** → choisissez `.venv/bin/python`.

Si l'environnement n'est pas visible, forcez sa création :

```bash
uv sync  # Crée ou met à jour .venv/
```

#### 2. Extensions recommandées

| Extension | ID | Rôle |
|-----------|----|------|
| Pylance | `ms-python.vscode-pylance` | Autocomplétion et vérification de types |
| Python | `ms-python.python` | Intégration de base |
| Ruff | `charliermarsh.ruff` | Linting et formatage |

#### 3. `.vscode/settings.json`

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoImportCompletions": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  }
}
```

### Zed Editor

Zed utilise **Pyright** nativement. Créez `pyrightconfig.json` à la racine du projet
pour pointer vers l'environnement `uv` :

```json
{
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.12",
  "typeCheckingMode": "basic",
  "reportMissingImports": true,
  "reportMissingModuleSource": false
}
```

Zed détecte automatiquement ce fichier et active l'autocomplétion complète pour FastAPI
et Pydantic, y compris les champs de modèles.

---

## Vérification complète de l'installation

```bash
# Vérifier les versions
uv run python -c "import fastapi, pydantic, uvicorn; \
    print(f'FastAPI {fastapi.__version__}'); \
    print(f'Pydantic {pydantic.__version__}'); \
    print(f'Uvicorn {uvicorn.__version__}')"
```

Sortie attendue (versions indicatives) :

```
FastAPI 0.115.x
Pydantic 2.x.x
Uvicorn 0.32.x
```

Testez l'endpoint avec `curl` :

```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/openapi.json | python -m json.tool | head -20
# Affiche le schéma OpenAPI généré automatiquement
```

---

## `pyproject.toml` de référence

Voici un `pyproject.toml` complet pour un projet FastAPI bien configuré :

```toml
[project]
name = "my-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "pydantic>=2.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "httpx>=0.27",   # Client HTTP pour les tests FastAPI
    "ruff>=0.8",
    "pyright>=1.1",
]

[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.pyright]
pythonVersion = "3.12"
venvPath = "."
venv = ".venv"
typeCheckingMode = "basic"
```

!!! note "Pourquoi `httpx` comme dépendance de test ?"
    FastAPI fournit un `TestClient` basé sur `httpx`. C'est le moyen standard de tester
    vos endpoints sans démarrer un vrai serveur — les tests s'exécutent en mémoire,
    instantanément.
