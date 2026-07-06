# FastAPI — Introduction et Concepts

FastAPI est un framework web Python moderne conçu pour construire des **API performantes**
avec un minimum de code et un maximum de robustesse. Ce guide vous accompagne de zéro
jusqu'à une architecture de production.

---

## Qu'est-ce qu'un framework ?

Avant d'écrire la moindre ligne, posons une question fondamentale.

Un **framework** (cadre de travail) est un ensemble de composants pré-construits qui
impose une structure et résout les problèmes communs à votre place. Il vous dit
*où* mettre votre code et *comment* il sera exécuté.

### Analogie : construire une maison

```mermaid
flowchart LR
    subgraph "Sans framework — tout à la main"
        direction TB
        S1["🪨 Couler les fondations"]
        S2["🧱 Monter les murs"]
        S3["🪟 Installer les fenêtres"]
        S4["⚡ Tirer l'électricité"]
        S5["🚿 Plomberie"]
        S1 --> S2 --> S3 --> S4 --> S5
    end

    subgraph "Avec framework — sur ossature existante"
        direction TB
        F1["🏗️ Ossature fournie\n(routing, parsing, sérialisation)"]
        F2["🎨 Vous décorez\nvos pièces\n(logique métier)"]
        F1 --> F2
    end

    style F1 fill:#e1f5fe,stroke:#01579b
    style F2 fill:#e8f5e9,stroke:#2e7d32
```

Sans framework, chaque projet repart de zéro : gérer les sockets réseau, parser les
requêtes HTTP, sérialiser les réponses JSON... Des centaines de lignes avant d'écrire
la moindre règle métier. Le framework prend en charge toute cette plomberie.

!!! info "Différence framework / bibliothèque"
    - **Bibliothèque** : vous l'appelez quand vous voulez (`import requests`). Vous
      gardez le contrôle du flux.
    - **Framework** : *il vous appelle*. Vous branchez votre code dans ses points
      d'extension (routes, middlewares, hooks). C'est le principe
      d'**inversion de contrôle**.

---

## La famille des frameworks web Python

```mermaid
flowchart TD
    PY["🐍 Python Web Frameworks"]
    PY --> FLASK["Flask\n🪶 Micro-framework"]
    PY --> DJANGO["Django\n🏭 Full-stack"]
    PY --> FASTAPI["FastAPI\n⚡ Async + Typé"]

    FLASK --> FL1["✅ Liberté totale"]
    FLASK --> FL2["❌ Tout à configurer"]
    FLASK --> FL3["❌ Pas de validation intégrée"]

    DJANGO --> DJ1["✅ Batterie incluse\n(ORM, Admin, Auth)"]
    DJANGO --> DJ2["❌ Lourd pour une API pure"]
    DJANGO --> DJ3["❌ Synchrone par défaut"]

    FASTAPI --> FA1["✅ Async natif"]
    FASTAPI --> FA2["✅ Validation Pydantic"]
    FASTAPI --> FA3["✅ Doc auto OpenAPI"]
    FASTAPI --> FA4["✅ Performances élevées"]

    style FASTAPI fill:#e8eaf6,stroke:#1a237e
    style FA1 fill:#e8f5e9,stroke:#2e7d32
    style FA2 fill:#e8f5e9,stroke:#2e7d32
    style FA3 fill:#e8f5e9,stroke:#2e7d32
    style FA4 fill:#e8f5e9,stroke:#2e7d32
```

| Critère | Flask | Django | FastAPI |
|---------|-------|--------|---------|
| Courbe d'apprentissage | Faible | Élevée | Moyenne |
| Performance (req/s) | ~1 000 | ~1 200 | ~15 000+ |
| Validation intégrée | ❌ | ✅ (basique) | ✅ (Pydantic) |
| Asynchrone natif | ❌ | Partiel | ✅ |
| Documentation auto | ❌ | ❌ | ✅ OpenAPI |
| Type hints exploités | ❌ | ❌ | ✅ |
| Idéal pour | Prototypes | Applications complètes | APIs modernes |

---

## Pourquoi FastAPI change la donne

### 1. Le typage Python comme contrat

Python 3.5+ introduit les **type hints** — des annotations optionnelles qui précisent
le type attendu de chaque variable. FastAPI les utilise non pas comme documentation,
mais comme **spécification exécutable** de votre API.

```python
# Sans type hints — aucune garantie
@app.get("/users")
def get_user(user_id):
    ...

# Avec type hints — FastAPI génère parsing + validation + doc
@app.get("/users/{user_id}")
def get_user(user_id: int) -> UserResponse:
    ...
```

Avec la deuxième version, FastAPI :

1. **Parse** `user_id` en entier (retourne 422 si ce n'est pas possible)
2. **Génère** l'entrée dans la doc Swagger avec le bon type
3. **Valide** le modèle de réponse `UserResponse`

### 2. Performance : ASGI vs WSGI

Les frameworks traditionnels (Flask, Django) utilisent **WSGI** — un protocole synchrone
qui traite une requête à la fois par worker.

FastAPI utilise **ASGI** (Asynchronous Server Gateway Interface), qui permet à un seul
worker de traiter des milliers de requêtes en parallèle grâce à la programmation
asynchrone.

```mermaid
flowchart LR
    subgraph "WSGI — Synchrone"
        direction TB
        WW1["Worker 1\n🔴 Bloqué (attente DB)"]
        WW2["Worker 2\n🔴 Bloqué (attente API)"]
        WW3["Worker 3\n🟢 Actif"]
        WR["Requêtes\nen file"]
        WR --> WW1
        WR --> WW2
        WR --> WW3
    end

    subgraph "ASGI — Asynchrone"
        direction TB
        AW["Worker unique\n🟢 Toujours actif"]
        AT1["Tâche 1\n(attend DB)"]
        AT2["Tâche 2\n(attend API)"]
        AT3["Tâche 3\n(calcul)"]
        AW --> AT1
        AW --> AT2
        AW --> AT3
    end

    style AW fill:#e8f5e9,stroke:#2e7d32
    style WW1 fill:#ffebee,stroke:#c62828
    style WW2 fill:#ffebee,stroke:#c62828
```

---

## Pydantic : le gardien de vos données

**Pydantic** est la bibliothèque de validation de données sur laquelle FastAPI est bâti.
Elle transforme vos classes Python en validateurs automatiques.

### Analogie : le videur de discothèque

```mermaid
sequenceDiagram
    participant C as Client
    participant P as Pydantic 🕴️<br/>(videur)
    participant S as Service métier

    C->>P: POST /users {name: "Alice", age: "vingt"}
    P-->>C: 422 Unprocessable Entity<br/>{"age": "must be integer"}

    C->>P: POST /users {name: "Alice", age: 25}
    P->>S: User(name="Alice", age=25) ✅
    S-->>C: 201 Created
```

Sans Pydantic, vous écririez pour chaque endpoint :

```python
# Validation manuelle — fastidieux et source d'erreurs
@app.post("/users")
def create_user(data: dict):
    if "name" not in data:
        return {"error": "name is required"}, 400
    if not isinstance(data.get("age"), int):
        return {"error": "age must be an integer"}, 400
    if data["age"] < 0:
        return {"error": "age must be positive"}, 400
    # ... et ça continue
```

Avec Pydantic :

```python
from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    name: str
    age: int = Field(ge=0, description="Âge en années révolues")

@app.post("/users")
def create_user(user: UserCreate):
    # Ici, user.name est garanti str et user.age est garanti int >= 0
    ...
```

Pydantic v2 (inclus dans FastAPI 0.100+) valide à la vitesse du C grâce à son core
réécrit en Rust.

### Ce que Pydantic génère automatiquement

À partir d'un simple modèle Python, Pydantic produit :

- Un **schéma JSON** conforme OpenAPI 3.1
- Des **messages d'erreur explicites** par champ invalide
- La **conversion de types** (une string `"42"` devient l'entier `42` si attendu)
- La **sérialisation** vers dict/JSON pour les réponses

---

## La documentation interactive (Swagger UI)

FastAPI génère automatiquement deux interfaces de documentation :

| URL | Interface | Usage |
|-----|-----------|-------|
| `/docs` | **Swagger UI** | Tester les endpoints interactivement |
| `/redoc` | **ReDoc** | Documentation de référence lisible |
| `/openapi.json` | JSON brut | Importation dans Postman, client SDK |

```mermaid
flowchart LR
    CODE["Votre code Python\n(type hints + Pydantic)"]
    SCHEMA["Schéma OpenAPI\n/openapi.json"]
    SWAGGER["Swagger UI\n/docs"]
    REDOC["ReDoc\n/redoc"]
    POSTMAN["Postman\nInsomnia\nClients générés"]

    CODE -->|"génère automatiquement"| SCHEMA
    SCHEMA --> SWAGGER
    SCHEMA --> REDOC
    SCHEMA --> POSTMAN

    style CODE fill:#e8eaf6,stroke:#1a237e
    style SCHEMA fill:#e1f5fe,stroke:#01579b
```

!!! tip "Pas besoin de Postman en développement"
    `/docs` offre une interface complète pour tester chaque endpoint avec des formulaires
    pré-remplis selon vos modèles Pydantic. En développement, c'est votre outil principal.

---

## Prérequis pour ce guide

- Python **3.12+** (vérifier avec `python --version`)
- `uv` installé (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Notions de base Python : fonctions, classes, exceptions
- Connaissance de HTTP basique : méthodes GET/POST, codes de statut

!!! note "Notions HTTP rappelées dans ce guide"
    Chaque fois qu'un concept HTTP est utilisé (code 422, header, body), il est expliqué
    en contexte. Aucune connaissance préalable n'est supposée.
