# FastAPI — Concepts avancés

> Cette page détaille les mécanismes de FastAPI utilisés dans une architecture de
> production : auto-découverte des routes, exception handlers globaux, contrôle de
> types, configuration et middleware. Elle est conçue pour être lue après
> [Installation et Configuration](setup.md) et [Architecture et Code](code.md).

---

## 1. Auto-découverte des routes et `APIRouter`

### 1.1 Le problème : tout dans `main.py`

Dans les premiers exemples, toutes les routes sont définies dans `main.py`. Cela devient
rapidement ingérable :

```python
# main.py — anti-pattern dès qu'on a plus de 5 routes
app = FastAPI()

@app.get("/items/{id}")
def get_item(id: int): ...

@app.post("/items")
def create_item(): ...

@app.get("/users/{id}")
def get_user(id: int): ...

# ... 200 lignes supplémentaires
```

### 1.2 La solution : `APIRouter`

`APIRouter` est un mini-`FastAPI` — il enregistre des routes exactement comme l'objet
`app`, mais sans démarrer un serveur. On l'inclut dans l'application principale via
`include_router()`.

```mermaid
flowchart TD
    MAIN["app = FastAPI()\n(main.py)"]
    R1["router_items\n(routers/items.py)"]
    R2["router_users\n(routers/users.py)"]
    R3["router_evolutions\n(routers/evolutions.py)"]

    MAIN -->|"include_router(router_items, prefix='/api/v1')"| R1
    MAIN -->|"include_router(router_users, prefix='/api/v1')"| R2
    MAIN -->|"include_router(router_evolutions, prefix='/api/v1')"| R3

    R1 --> E1["GET /api/v1/items/{id}"]
    R1 --> E2["POST /api/v1/items"]
    R2 --> E3["GET /api/v1/users/{id}"]
    R3 --> E4["POST /api/v1/evolutions"]
    R3 --> E5["GET /api/v1/workspaces/status"]

    style MAIN fill:#e3f2fd,stroke:#1565c0
    style R1 fill:#e8f5e9,stroke:#2e7d32
    style R2 fill:#e8f5e9,stroke:#2e7d32
    style R3 fill:#e8f5e9,stroke:#2e7d32
```

### 1.3 Définir un router

```python
# routers/items.py
from fastapi import APIRouter

router = APIRouter(
    prefix="/items",       # Préfixe commun à toutes les routes de ce fichier
    tags=["Catalogue"],    # Groupe dans Swagger UI — toutes les routes sous "Catalogue"
)

@router.get("/{item_id}")           # Route complète : GET /items/{item_id}
async def get_item(item_id: int): ...

@router.post("/", status_code=201)  # Route complète : POST /items/
async def create_item(): ...
```

### 1.4 Inclure le router dans l'application

```python
# main.py
from fastapi import FastAPI
from routers import items, users, evolutions

app = FastAPI()

# FastAPI "découvre" toutes les routes définies dans chaque router
app.include_router(items.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(evolutions.router, prefix="/api/v1")
```

!!! info "Comment FastAPI 'découvre-t-il' les routes ?"
    `include_router()` parcourt toutes les routes enregistrées dans le router
    (via les décorateurs `@router.get`, `@router.post`, etc.) et les ajoute à l'arbre
    de routage interne de l'application. C'est statique — toutes les routes sont connues
    au démarrage. Il n'y a pas de scan de répertoire ou de magie — c'est un enregistrement
    explicite.

### 1.5 Dépendances au niveau du router

On peut appliquer une dépendance (ex : authentification) à **toutes** les routes d'un
router en un seul endroit :

```python
from fastapi import APIRouter, Depends
from .dependencies import require_api_key

router = APIRouter(
    prefix="/admin",
    tags=["Administration"],
    dependencies=[Depends(require_api_key)],  # Appliqué à TOUTES les routes du router
)

@router.get("/stats")   # Protégée automatiquement
async def get_stats(): ...

@router.delete("/cache")  # Protégée automatiquement
async def clear_cache(): ...
```

---

## 2. Exception handlers globaux

### 2.1 Le problème : `try/except` partout

Sans handler global, chaque endpoint doit gérer ses propres erreurs. Cela mène à du
code dupliqué et des réponses d'erreur incohérentes :

```python
# ❌ Anti-pattern : gestion locale, code dupliqué à chaque endpoint
@router.post("/evolutions")
async def create_evolution(req: CreateEvolutionRequest):
    try:
        project = gitlab.get_project(req.app_code)
    except GitlabNotFoundError:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    except GitlabConnectionError:
        raise HTTPException(status_code=502, detail="GitLab injoignable")
    # ... et ça se répète dans TOUS les endpoints
```

### 2.2 La solution : `@app.exception_handler`

Un handler global intercepte les exceptions **n'importe où** dans l'application et les
transforme en réponse HTTP uniforme :

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Router
    participant S as Service
    participant H as Exception Handler

    C->>R: POST /evolutions
    R->>S: service.create(req)
    S--xR: raise AppNotFoundError("APP_NOT_FOUND_IN_GITLAB")
    Note over R: L'exception remonte sans être attrapée
    R--xH: Exception transmise au handler global
    H-->>C: HTTP 404 {"code": "APP_NOT_FOUND_IN_GITLAB", "message": "..."}
```

```python
# exceptions.py — hiérarchie d'exceptions typées
class ZDevOpsError(Exception):
    """Exception de base pour toutes les erreurs métier."""
    def __init__(self, code: str, message: str, detail: str | dict | None = None):
        self.code = code
        self.message = message
        self.detail = detail

class AppNotFoundError(ZDevOpsError): ...
class EvolutionAlreadyExistsError(ZDevOpsError): ...

# main.py — handler global : UNE SEULE définition pour toute l'API
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

_STATUS_MAP: dict[str, int] = {
    "APP_NOT_FOUND_IN_GITLAB":  404,
    "EVOLUTION_ALREADY_EXISTS": 409,
    "CLONE_FAILED":             500,
    "GITLAB_UNREACHABLE":       502,
}

@app.exception_handler(ZDevOpsError)
async def zdevops_handler(request: Request, exc: ZDevOpsError) -> JSONResponse:
    """Convertit toute exception métier en réponse HTTP structurée.

    Le service lève des exceptions typées (sans connaître HTTP).
    Ce handler les traduit en codes HTTP et en JSON uniforme.
    """
    return JSONResponse(
        status_code=_STATUS_MAP.get(exc.code, 500),
        content={
            "code": exc.code,
            "message": exc.message,
            "detail": exc.detail,
        },
    )
```

!!! tip "Pourquoi cette séparation est importante"
    Le **service** ne connaît pas HTTP. Il lève `AppNotFoundError("APP_NOT_FOUND_IN_GITLAB")`.
    C'est le **handler** (couche HTTP) qui décide que ça donne un `404`.
    Si demain on veut changer `404` en `422` pour ce cas, on modifie `_STATUS_MAP` — une
    ligne, un seul endroit.

### 2.3 Handler pour les erreurs de validation Pydantic

FastAPI lève une `RequestValidationError` interne quand Pydantic échoue. On peut
personnaliser sa réponse :

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Reformate les erreurs Pydantic en JSON cohérent avec le reste de l'API."""
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={
            "code": "VALIDATION_ERROR",
            "message": f"{len(errors)} champ(s) invalide(s)",
            "detail": [
                {
                    "field": " → ".join(str(loc) for loc in e["loc"]),
                    "error": e["msg"],
                    "value": e.get("input"),
                }
                for e in errors
            ],
        },
    )
```

---

## 3. Contrôle de types — ce que FastAPI fait avec vos annotations

### 3.1 Les type hints ne sont pas que de la documentation

En Python standard, les annotations de type sont ignorées à l'exécution. FastAPI les
lit activement et les exploite à trois niveaux :

```mermaid
flowchart TD
    HINTS["Type hints dans votre code\n(annotations Python)"]

    subgraph FASTAPI["Ce que FastAPI en fait"]
        A["① Parsing et validation\nde la requête entrante"]
        B["② Génération du schéma\nOpenAPI / Swagger UI"]
        C["③ Validation et sérialisation\nde la réponse sortante"]
    end

    HINTS --> A
    HINTS --> B
    HINTS --> C

    A --> A1["Transforme '42' (str) en 42 (int)\nRenvoie 422 si impossible"]
    B --> B1["Documente les types, exemples,\net contraintes dans /docs"]
    C --> C1["Filtre les champs non déclarés\nConvertit les objets en JSON"]

    style FASTAPI fill:#e3f2fd,stroke:#1565c0
```

### 3.2 Parsing de la requête

FastAPI lit les type hints de la signature de votre endpoint pour savoir où chercher
chaque paramètre et comment le convertir :

```python
from fastapi import Path, Query, Body

@router.get("/items/{item_id}")
async def get_item(
    item_id: int,              # → Paramètre de chemin (path), converti en int
    active: bool = True,       # → Paramètre de query (?active=false), converti en bool
    page: int = Query(ge=1),   # → Query avec contrainte : page >= 1
) -> ItemResponse:
    ...

@router.post("/items")
async def create_item(
    item: ItemCreate,          # → Corps JSON (body), validé par Pydantic
) -> ItemResponse:
    ...
```

!!! info "Règle de localisation automatique"
    - Type simple (`int`, `str`, `bool`) dans la signature → **path parameter** si le nom
      correspond à un `{paramètre}` dans la route, sinon → **query parameter**
    - Type Pydantic `BaseModel` → **body JSON**
    - `Annotated[type, Depends(...)]` → **injection de dépendance**

### 3.3 `response_model` — validation de la réponse

`response_model` indique à FastAPI quel modèle Pydantic utiliser pour **sérialiser et
filtrer** la réponse. C'est une protection contre les fuites de données :

```python
class UserInternal(BaseModel):
    id: int
    username: str
    password_hash: str      # ← champ sensible, ne doit PAS sortir

class UserPublic(BaseModel):
    id: int
    username: str           # ← uniquement ce qui est sûr

@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int) -> UserInternal:
    # On retourne UserInternal, mais FastAPI ne sérialise
    # que les champs de UserPublic — password_hash est filtré silencieusement
    return db.get_user(user_id)
```

### 3.4 Génération OpenAPI automatique

Tout ce que vous annotez se retrouve dans `/docs` sans écrire une ligne de documentation
YAML. Chaque `Field()`, chaque `description=`, chaque `examples=[]` enrichit l'interface
Swagger UI :

```python
class CreateEvolutionRequest(BaseModel):
    app_code: str = Field(
        ...,
        description="Code application : 4 caractères commençant par 'da' ou 'dy'",
        examples=["da01", "dyab"],
        pattern=r"^d[ay][a-z0-9]{2}$",   # ← Affiché dans Swagger et validé à l'exécution
    )
```

```mermaid
flowchart LR
    CODE["Field(\n  description='...',\n  examples=['da01'],\n  pattern='...'\n)"]
    OAS["Schéma OpenAPI\n{\n  'description': '...',\n  'examples': ['da01'],\n  'pattern': '...'\n}"]
    SWAGGER["Swagger UI /docs\nFormulaire pré-rempli\navec contraintes visibles"]

    CODE -->|"FastAPI génère"| OAS
    OAS -->|"Swagger UI lit"| SWAGGER
    style CODE fill:#e8eaf6,stroke:#1a237e
    style OAS fill:#e1f5fe,stroke:#01579b
    style SWAGGER fill:#e8f5e9,stroke:#2e7d32
```

---

## 4. Configuration avec `pydantic-settings`

### 4.1 Pourquoi ne pas utiliser `os.getenv` directement

```python
# ❌ Anti-pattern : éparpillé dans le code, aucune validation, aucun typage
gitlab_url = os.getenv("GITLAB_URL")
if not gitlab_url:
    raise ValueError("GITLAB_URL est requis")

gitlab_token = os.getenv("GITLAB_TOKEN", "")
```

Avec `pydantic-settings`, la configuration est centralisée, typée, et validée
**au démarrage** — pas au moment où elle est utilisée :

```python
# ✅ Avec pydantic-settings
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Chaque champ est requis sauf s'il a une valeur par défaut
    gitlab_url: str                        # Obligatoire
    gitlab_token: str                      # Obligatoire
    gitlab_group: str                      # Obligatoire
    gitlab_params_project_id: int          # Obligatoire, converti en int automatiquement
    workspace_base_path: str               # Obligatoire
    toolchain: str = "dev"                 # Optionnel avec valeur par défaut
    git_user_name: str = "zDevOps API"     # Optionnel

    model_config = {
        "env_file": ".env",                # Lit un fichier .env si présent
        "case_sensitive": False,           # GITLAB_URL = gitlab_url = GitLab_Url
    }

@lru_cache                                 # Ne lit le .env qu'une seule fois
def get_settings() -> Settings:
    return Settings()
```

### 4.2 Fichier `.env` pour le développement

```dotenv
# .env — ne pas committer dans git (ajouter .env dans .gitignore)
GITLAB_URL=https://gitlab.example.com
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
GITLAB_GROUP=fr.lcl.zdevops.dev
GITLAB_PARAMS_PROJECT_ID=1042
WORKSPACE_BASE_PATH=/home/dev/workspace
TOOLCHAIN=dev
GIT_USER_NAME=Jean Dupont
```

### 4.3 Utiliser la config dans toute l'application via `Depends`

```python
from fastapi import Depends

def get_gitlab_service(
    settings: Settings = Depends(get_settings),
) -> GitLabService:
    return GitLabService(
        url=settings.gitlab_url,
        token=settings.gitlab_token,   # ← jamais dans les logs
        group=settings.gitlab_group,
    )
```

!!! danger "Ne jamais loguer `settings.gitlab_token`"
    `pydantic-settings` stocke les valeurs en clair en mémoire. Ne les passez jamais
    dans des logs, des messages d'erreur ou des réponses JSON. Utilisez `SecretStr`
    pour les valeurs sensibles — Pydantic les masque automatiquement dans les `repr()`.

    ```python
    from pydantic import SecretStr

    class Settings(BaseSettings):
        gitlab_token: SecretStr          # Affiché "**********" dans les logs
    
    # Récupération de la valeur brute uniquement quand nécessaire
    token = settings.gitlab_token.get_secret_value()
    ```

### 4.4 Configuration pour les tests

```python
# tests/conftest.py
from functools import lru_cache
from unittest.mock import patch

from app.config import Settings, get_settings
from app.main import app

def override_settings() -> Settings:
    return Settings(
        gitlab_url="http://mock-gitlab",
        gitlab_token="test-token",
        gitlab_group="test-group",
        gitlab_params_project_id=1,
        workspace_base_path="/tmp/test-workspace",
    )

# Remplace la config réelle par la config de test pour tous les tests
app.dependency_overrides[get_settings] = override_settings
```

---

## 5. Middleware

### 5.1 Qu'est-ce qu'un middleware ?

Un middleware est un composant qui s'exécute **avant et après** chaque requête. Il voit
toutes les requêtes sans exception, quel que soit l'endpoint.

```mermaid
sequenceDiagram
    participant C as Client
    participant MW1 as Middleware CORS
    participant MW2 as Middleware Logging
    participant R as Router + Handler

    C->>MW1: Requête entrante
    MW1->>MW2: Passe la requête (avec headers CORS ajoutés)
    MW2->>R: Passe la requête (après avoir loggué)
    R-->>MW2: Réponse
    MW2-->>MW1: Réponse (après avoir loggué la durée)
    MW1-->>C: Réponse finale (avec headers CORS)
```

### 5.2 CORS — accès depuis un navigateur

Sans middleware CORS, les navigateurs bloquent les appels depuis un domaine différent
(ex : `http://localhost:3000` → `http://localhost:8000`) :

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",    # Frontend de développement
        "https://app.example.com",  # Frontend de production
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
    allow_credentials=True,
)
```

!!! warning "`allow_origins=['*']` en production"
    Autoriser toutes les origines (`*`) est pratique en développement mais dangereux en
    production. Listez explicitement les origines autorisées.

### 5.3 Middleware personnalisé — logging des requêtes

```python
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logue chaque requête avec sa durée d'exécution."""
    start = time.perf_counter()
    response = await call_next(request)          # Exécute le handler
    duration = time.perf_counter() - start

    logger.info(
        "%s %s → %d (%.0f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration * 1000,
    )
    return response
```

---

## 6. Tâches en arrière-plan (`BackgroundTasks`)

### 6.1 Pour les opérations non-bloquantes

Certaines opérations peuvent être faites **après** que la réponse est envoyée au client :
envoi d'email, mise à jour de cache, écriture de log dans une base externe.

```python
from fastapi import BackgroundTasks

def send_notification_email(email: str, branch_name: str) -> None:
    """Envoyée après la réponse — le client n'attend pas."""
    # ... appel SMTP ou webhook
    logger.info("Notification envoyée à %s pour la branche %s", email, branch_name)

@router.post("/evolutions", status_code=201)
async def create_evolution(
    req: CreateEvolutionRequest,
    background_tasks: BackgroundTasks,              # Injecté automatiquement par FastAPI
    service: EvolutionService = Depends(get_evolution_service),
) -> CreateEvolutionResponse:
    result = await service.create(req)

    # Planifié APRÈS la réponse HTTP — le client reçoit 201 immédiatement
    background_tasks.add_task(
        send_notification_email,
        email="team@example.com",
        branch_name=result.branch_name,
    )

    return result
```

!!! warning "BackgroundTasks vs workers asynchrones"
    `BackgroundTasks` s'exécute dans le **même processus** que le serveur. Si la tâche
    plante ou prend trop longtemps, elle peut impacter les performances. Pour des tâches
    longues ou critiques, utilisez une file de messages externe (Celery, RQ, ARQ).

---

## 7. Récapitulatif des atouts FastAPI

```mermaid
mindmap
  root((FastAPI))
    Performance
      ASGI / asyncio
      Comparable à Node.js et Go
      Worker unique, milliers de requêtes simultanées
    Sécurité des types
      Type hints exploités à l'exécution
      Validation Pydantic automatique
      response_model protège les données sensibles
    Productivité développeur
      Documentation Swagger UI automatique
      Erreurs 422 détaillées par champ
      Rechargement automatique avec --reload
    Architecture
      APIRouter pour organiser les routes
      Depends pour le câblage des composants
      Exception handlers pour la cohérence des erreurs
      Middleware pour les préoccupations transversales
    Écosystème
      Pydantic v2 haute performance
      pydantic-settings pour la config
      httpx pour les appels externes async
      pytest + TestClient pour les tests
```

| Critère | Flask | Django | **FastAPI** |
|---|---|---|---|
| Validation automatique | ❌ | Partielle | ✅ Pydantic v2 |
| Documentation auto | ❌ | ❌ | ✅ OpenAPI + Swagger |
| Async natif | ❌ | Partiel | ✅ ASGI |
| Injection de dépendances | ❌ | ❌ | ✅ `Depends` |
| Contrôle de types à l'exécution | ❌ | ❌ | ✅ |
| Performance (req/s) | ~1 000 | ~1 200 | ~15 000+ |
| Courbe d'apprentissage | Faible | Élevée | Moyenne |

!!! success "FastAPI en une phrase"
    FastAPI transforme vos annotations de type Python en un système complet de validation,
    documentation et injection de dépendances — sans configuration supplémentaire.
