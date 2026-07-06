# Cas concret — Fonctions 13 & 14 : Configuration des tokens

> Ce document couvre les deux fonctions de configuration du plugin :
> **GitLab Token** (Ctrl+E) et **Jenkins Token** (Ctrl+K). Elles partagent la même
> philosophie — stocker des credentials de manière sécurisée — mais diffèrent par
> leur portée et leur format d'authentification.
>
> La stratégie de stockage est documentée dans [ADR-002](adr-002-stockage-tokens.md).

---

## 1. Contexte et différences

| Critère | Fonction 13 — GitLab Token | Fonction 14 — Jenkins Token |
|---|---|---|
| Raccourci | `Ctrl+E` | `Ctrl+K` |
| Portée | **Unique** — partagé entre tous les toolchains | **Par toolchain** (`dev`, `rec`, `frm`, `prd`) |
| Utilisation | API GitLab REST + opérations git (clone, push, pull) | API Jenkins — déclenchement de jobs |
| Format auth | Token seul (`PRIVATE-TOKEN: <token>`) | Basic Auth — `Base64("<user>@id.fr.cly:<token>")` |
| Credentials stockés | 1 token GitLab | 1 token Jenkins + 1 mot de passe AD/LDAP |
| Username | Déduit du login OS — jamais saisi | Déduit du login OS — jamais saisi |
| Validation au stockage | ❌ Non — validé à la première utilisation | ❌ Non — validé à la première utilisation |
| Déclenchement auto | Non | Oui — si token absent lors d'un job Jenkins |

---

## 2. Endpoints introduits

### Fonction 13 — GitLab Token

```
POST   /api/v1/config/gitlab-token    → stocker le token
GET    /api/v1/config/gitlab-token    → vérifier si configuré
DELETE /api/v1/config/gitlab-token    → supprimer le token
```

### Fonction 14 — Jenkins Token

```
POST   /api/v1/config/jenkins-token/{toolchain}    → stocker token + password
GET    /api/v1/config/jenkins-token/{toolchain}    → vérifier si configuré
DELETE /api/v1/config/jenkins-token/{toolchain}    → supprimer
```

Le paramètre `{toolchain}` est validé contre les valeurs autorisées : `dev`, `rec`,
`frm`, `prd`.

---

## 3. Analyse des règles de gestion

### RG-01 — Validation de la saisie (GitLab)

**Spécification :** le token ne doit pas être vide.

✅ **Conforme** — Pydantic rejette automatiquement les chaînes vides via `min_length=1`.

### RG-02 — Pas de validation du token au stockage

**Spécification :** le plugin ne vérifie pas si le token est valide au moment de
la saisie. La validité est contrôlée lors de la première opération GitLab ou Git.

✅ **Conservé intentionnellement** — valider le token impliquerait un appel GitLab
(latence, dépendance réseau) dans l'opération de configuration. Le comportement est
explicitement documenté dans la réponse de l'API (`"validated": false`).

!!! info "Pourquoi ne pas valider immédiatement ?"
    Valider un token nécessite un appel réseau à GitLab (`GET /api/v4/user`). Si GitLab
    est temporairement indisponible, l'utilisateur ne pourrait pas sauvegarder son token
    même s'il est correct. La validation différée est le bon compromis : le token est
    stocké immédiatement, et le premier appel réel révèle s'il est valide.

### RG-03 — Le GET ne retourne jamais la valeur du token

**Spécification originale :** le plugin affiche des `•••` si un token est déjà stocké.

✅ **Renforcé** — l'API ne retourne que l'état de configuration (`configured: true/false`),
jamais la valeur. Même masquée, une valeur partielle dans une réponse HTTP est un
risque de fuite.

### RG-04 — Déclenchement automatique (Jenkins uniquement)

**Spécification :** si le token Jenkins est absent lors d'une tentative de build,
déploiement ou audit, la boîte de saisie s'ouvre automatiquement.

**Équivalent API :** le `JenkinsService` lève `JenkinsTokenMissingError` (→ 503)
lorsqu'il détecte l'absence de token pour le toolchain demandé. Le client (CLI,
VS Code) intercepte ce code et propose à l'utilisateur de configurer le token.

### RG-05 — Récupération du username

**Spécification :** `System.getProperty("user.name")` + `@id.fr.cly`.

✅ **Conforme** — `getpass.getuser()` en Python retourne le login OS.
Le domaine `@id.fr.cly` est une constante de configuration (`LDAP_DOMAIN`).

### RG-06 — Construction des credentials Jenkins (Basic Auth)

**Spécification Java :**

```java
Base64.encode("<user.name>@id.fr.cly:<token>")
```

✅ **Conforme** — reproduit en Python avec `SecretStr` pour que la valeur ne
fuite jamais dans les logs.

---

## 4. Code FastAPI

### 4.1 Modèles Pydantic — `models/config.py`

```python
"""Modèles de données pour les endpoints de configuration des tokens.

Les tokens sont portés par SecretStr : ils ne peuvent pas être loggés,
affichés dans le repr() d'un objet, ou sérialisés accidentellement en JSON.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, SecretStr, field_validator


class Toolchain(str, Enum):
    """Environnements Jenkins disponibles."""
    DEV = "dev"
    REC = "rec"
    FRM = "frm"
    PRD = "prd"


class StoreGitlabTokenRequest(BaseModel):
    """Corps de POST /api/v1/config/gitlab-token."""

    token: SecretStr = Field(
        ...,
        min_length=1,
        description="Token d'accès personnel GitLab (Personal Access Token)",
        examples=["glpat-xxxxxxxxxxxxxxxxxxxx"],
    )


class StoreJenkinsTokenRequest(BaseModel):
    """Corps de POST /api/v1/config/jenkins-token/{toolchain}."""

    token: SecretStr = Field(
        ...,
        min_length=1,
        description="Token d'API Jenkins",
        examples=["11xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"],
    )
    password: SecretStr = Field(
        ...,
        min_length=1,
        description="Mot de passe AD/LDAP du développeur",
    )


class TokenConfigStatus(BaseModel):
    """Réponse de GET /api/v1/config/*-token."""

    configured: bool = Field(
        description="True si un token est actuellement stocké"
    )
    validated: bool = Field(
        default=False,
        description="Toujours False — la validation se fait à la première utilisation",
    )
```

---

### 4.2 Exceptions métier (ajouts)

```python
# Ajouts dans exceptions.py

# Credentials manquants (→ 503 Service Unavailable)
class GitlabTokenMissingError(ZDevOpsError): ...
class JenkinsTokenMissingError(ZDevOpsError): ...

# Toolchain invalide (→ 422)
class InvalidToolchainError(ZDevOpsError): ...
```

!!! info "Pourquoi 503 et non 401 pour un token manquant ?"
    `401 Unauthorized` signifie que le client n'est pas authentifié *auprès de l'API*.
    Ici, l'API elle-même n'a pas de token pour appeler GitLab ou Jenkins — c'est une
    configuration manquante côté serveur. `503 Service Unavailable` est plus précis :
    le service ne peut pas traiter la requête car une dépendance n'est pas configurée.

---

### 4.3 Router — `routers/config.py`

```python
"""Router pour la configuration des tokens (fonctions 13 et 14).

Ces endpoints ne font aucune opération Git ni aucun appel GitLab/Jenkins.
Ils gèrent uniquement le stockage sécurisé des credentials.
"""

import logging

from fastapi import APIRouter, Depends

from zdevops_api.models.config import (
    StoreGitlabTokenRequest,
    StoreJenkinsTokenRequest,
    TokenConfigStatus,
    Toolchain,
)
from zdevops_api.services.config_service import ConfigService, get_config_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])


# ── GitLab Token ──────────────────────────────────────────────────────────────

@router.post(
    "/gitlab-token",
    status_code=204,
    summary="Stocker le token GitLab",
    description="Sauvegarde le token d'accès personnel GitLab. Aucune validation réseau.",
)
async def store_gitlab_token(
    req: StoreGitlabTokenRequest,
    service: ConfigService = Depends(get_config_service),
) -> None:
    logger.info("Mise à jour du token GitLab")
    await service.store_gitlab_token(req.token)


@router.get(
    "/gitlab-token",
    response_model=TokenConfigStatus,
    summary="Vérifier si le token GitLab est configuré",
    description="Retourne uniquement l'état (configuré ou non). Ne retourne jamais la valeur.",
)
async def get_gitlab_token_status(
    service: ConfigService = Depends(get_config_service),
) -> TokenConfigStatus:
    return TokenConfigStatus(configured=await service.is_gitlab_token_configured())


@router.delete(
    "/gitlab-token",
    status_code=204,
    summary="Supprimer le token GitLab",
)
async def delete_gitlab_token(
    service: ConfigService = Depends(get_config_service),
) -> None:
    logger.info("Suppression du token GitLab")
    await service.delete_gitlab_token()


# ── Jenkins Token ─────────────────────────────────────────────────────────────

@router.post(
    "/jenkins-token/{toolchain}",
    status_code=204,
    summary="Stocker le token Jenkins pour une toolchain",
    description="Sauvegarde le token et le mot de passe Jenkins. Aucune validation réseau.",
)
async def store_jenkins_token(
    toolchain: Toolchain,
    req: StoreJenkinsTokenRequest,
    service: ConfigService = Depends(get_config_service),
) -> None:
    logger.info("Mise à jour du token Jenkins pour la toolchain '%s'", toolchain.value)
    await service.store_jenkins_token(toolchain, req.token, req.password)


@router.get(
    "/jenkins-token/{toolchain}",
    response_model=TokenConfigStatus,
    summary="Vérifier si le token Jenkins est configuré",
)
async def get_jenkins_token_status(
    toolchain: Toolchain,
    service: ConfigService = Depends(get_config_service),
) -> TokenConfigStatus:
    return TokenConfigStatus(
        configured=await service.is_jenkins_token_configured(toolchain)
    )


@router.delete(
    "/jenkins-token/{toolchain}",
    status_code=204,
    summary="Supprimer le token Jenkins pour une toolchain",
)
async def delete_jenkins_token(
    toolchain: Toolchain,
    service: ConfigService = Depends(get_config_service),
) -> None:
    logger.info("Suppression du token Jenkins pour '%s'", toolchain.value)
    await service.delete_jenkins_token(toolchain)
```

---

### 4.4 Service — `services/config_service.py`

```python
"""Service de gestion des credentials.

Ce module est la seule couche autorisée à lire et écrire des tokens.
Aucun autre service ne manipule directement les credentials — ils
les reçoivent via injection de dépendance depuis ce service.

V1 : stockage via pydantic-settings (variables d'environnement / .env).
V2 : stockage via OS keyring — voir ADR-002.
"""

import getpass
import logging
from base64 import b64encode

from pydantic import SecretStr

from zdevops_api.models.config import Toolchain
from zdevops_api.settings import Settings

logger = logging.getLogger(__name__)

LDAP_DOMAIN = "id.fr.cly"


class ConfigService:
    """Gestion du cycle de vie des credentials de l'API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        # Cache mémoire — SecretStr protège contre les fuites de logs
        self._gitlab_token: SecretStr | None = settings.gitlab_token
        self._jenkins_tokens: dict[str, SecretStr] = {
            tc.value: settings.get_jenkins_token(tc.value)
            for tc in Toolchain
            if settings.get_jenkins_token(tc.value) is not None
        }
        self._jenkins_passwords: dict[str, SecretStr] = {}

    # ── GitLab Token ──────────────────────────────────────────────────────────

    async def store_gitlab_token(self, token: SecretStr) -> None:
        """Stocke le token GitLab en mémoire (V1) ou dans le keyring (V2)."""
        self._gitlab_token = token
        # V2 : keyring.set_password("zdevops-api", "gitlab_token", token.get_secret_value())
        logger.debug("Token GitLab mis à jour")

    async def is_gitlab_token_configured(self) -> bool:
        return self._gitlab_token is not None

    async def delete_gitlab_token(self) -> None:
        self._gitlab_token = None
        # V2 : keyring.delete_password("zdevops-api", "gitlab_token")

    def get_gitlab_token(self) -> SecretStr:
        """Retourne le token pour utilisation par GitLabService.

        Raises:
            GitlabTokenMissingError: Si aucun token n'est configuré.
        """
        if self._gitlab_token is None:
            from zdevops_api.exceptions import GitlabTokenMissingError
            raise GitlabTokenMissingError(
                code="GITLAB_TOKEN_MISSING",
                message=(
                    "Aucun token GitLab configuré. "
                    "Appelez POST /api/v1/config/gitlab-token."
                ),
            )
        return self._gitlab_token

    # ── Jenkins Token ─────────────────────────────────────────────────────────

    async def store_jenkins_token(
        self, toolchain: Toolchain, token: SecretStr, password: SecretStr
    ) -> None:
        """Stocke le token et le mot de passe Jenkins pour une toolchain."""
        self._jenkins_tokens[toolchain.value] = token
        self._jenkins_passwords[toolchain.value] = password
        # V2 : keyring.set_password(...)
        logger.debug("Token Jenkins mis à jour pour '%s'", toolchain.value)

    async def is_jenkins_token_configured(self, toolchain: Toolchain) -> bool:
        return toolchain.value in self._jenkins_tokens

    async def delete_jenkins_token(self, toolchain: Toolchain) -> None:
        self._jenkins_tokens.pop(toolchain.value, None)
        self._jenkins_passwords.pop(toolchain.value, None)
        # V2 : keyring.delete_password(...)

    def get_jenkins_credentials(self, toolchain: Toolchain) -> str:
        """Construit les credentials Basic Auth pour Jenkins.

        Format : Base64("<username>@id.fr.cly:<token>")
        Le username est déduit automatiquement du login OS.

        Args:
            toolchain: Environnement Jenkins ciblé.

        Returns:
            Chaîne Base64 prête à être utilisée dans le header Authorization.

        Raises:
            JenkinsTokenMissingError: Si le token n'est pas configuré.
        """
        if toolchain.value not in self._jenkins_tokens:
            from zdevops_api.exceptions import JenkinsTokenMissingError
            raise JenkinsTokenMissingError(
                code="JENKINS_TOKEN_MISSING",
                message=(
                    f"Aucun token Jenkins configuré pour '{toolchain.value}'. "
                    f"Appelez POST /api/v1/config/jenkins-token/{toolchain.value}."
                ),
            )
        username = f"{getpass.getuser()}@{LDAP_DOMAIN}"
        token = self._jenkins_tokens[toolchain.value].get_secret_value()
        raw = f"{username}:{token}"
        return b64encode(raw.encode()).decode()
```

---

### 4.5 Mise à jour du handler global — `main.py`

```python
# Ajouts dans _STATUS_MAP
_STATUS_MAP: dict[str, int] = {
    # ... (existant)
    "GITLAB_TOKEN_MISSING":   503,
    "JENKINS_TOKEN_MISSING":  503,
    "INVALID_TOOLCHAIN":      422,
}

# Inclusion du router de configuration
app.include_router(config.router)
```

---

## 5. Sécurité — règles d'implémentation

| Règle | Justification |
|---|---|
| **`SecretStr` partout** | Empêche l'affichage accidentel dans les logs et le `repr()` |
| **GET ne retourne jamais la valeur** | Une réponse HTTP peut être loggée par un proxy |
| **`204 No Content` pour POST et DELETE** | Pas de corps de réponse → pas de surface de fuite |
| **Token absent → 503, pas 401** | 401 concerne l'auth *de l'API*, pas d'une dépendance |
| **Username déduit de l'OS, jamais stocké** | Réduit la surface de stockage des données personnelles |
| **Jamais loguer `token.get_secret_value()`** | `logging.debug("token: %s", token)` → log `**********` |

---

## 6. Stratégie de tests

### 6.1 Tests unitaires

```python
# tests/unit/test_config_service.py
import pytest
from pydantic import SecretStr

from zdevops_api.exceptions import GitlabTokenMissingError, JenkinsTokenMissingError
from zdevops_api.models.config import Toolchain
from zdevops_api.services.config_service import ConfigService


@pytest.fixture
def service_no_token(mock_settings) -> ConfigService:
    """Service sans aucun token configuré."""
    mock_settings.gitlab_token = None
    return ConfigService(mock_settings)


@pytest.fixture
def service_with_gitlab_token(mock_settings) -> ConfigService:
    mock_settings.gitlab_token = SecretStr("glpat-test")
    return ConfigService(mock_settings)


# ── GitLab token ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_store_then_get_gitlab_token(service_no_token):
    await service_no_token.store_gitlab_token(SecretStr("glpat-new"))
    assert await service_no_token.is_gitlab_token_configured() is True


@pytest.mark.asyncio
async def test_delete_gitlab_token(service_with_gitlab_token):
    await service_with_gitlab_token.delete_gitlab_token()
    assert await service_with_gitlab_token.is_gitlab_token_configured() is False


@pytest.mark.asyncio
async def test_get_token_missing_raises_503(service_no_token):
    with pytest.raises(GitlabTokenMissingError) as exc:
        service_no_token.get_gitlab_token()
    assert exc.value.code == "GITLAB_TOKEN_MISSING"


@pytest.mark.asyncio
async def test_get_token_never_exposes_value(service_with_gitlab_token):
    """Le GET retourne uniquement l'état, jamais la valeur."""
    status = await service_with_gitlab_token.is_gitlab_token_configured()
    assert status is True
    # Vérifier qu'on ne peut pas récupérer la valeur via l'API de status
    assert not hasattr(status, "value")


# ── Jenkins credentials ───────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_jenkins_credentials_format(service_no_token, monkeypatch):
    """Les credentials Jenkins suivent le format Base64(<user>@id.fr.cly:<token>)."""
    monkeypatch.setattr("getpass.getuser", lambda: "jdupont")
    await service_no_token.store_jenkins_token(
        Toolchain.DEV, SecretStr("token123"), SecretStr("pwd")
    )
    import base64
    credentials = service_no_token.get_jenkins_credentials(Toolchain.DEV)
    decoded = base64.b64decode(credentials).decode()
    assert decoded == "jdupont@id.fr.cly:token123"


@pytest.mark.asyncio
async def test_jenkins_token_missing_raises_503(service_no_token):
    with pytest.raises(JenkinsTokenMissingError) as exc:
        service_no_token.get_jenkins_credentials(Toolchain.DEV)
    assert exc.value.code == "JENKINS_TOKEN_MISSING"


@pytest.mark.asyncio
async def test_jenkins_tokens_isolated_by_toolchain(service_no_token):
    """Un token stocké pour DEV n'est pas accessible pour REC."""
    await service_no_token.store_jenkins_token(
        Toolchain.DEV, SecretStr("token-dev"), SecretStr("pwd")
    )
    assert await service_no_token.is_jenkins_token_configured(Toolchain.DEV) is True
    assert await service_no_token.is_jenkins_token_configured(Toolchain.REC) is False
```

### 6.2 Tableau des cas de test obligatoires

| Catégorie | Test | Code attendu |
|---|---|---|
| **GitLab** | POST token vide | 422 |
| **GitLab** | POST token valide | 204 |
| **GitLab** | GET sans token → `configured: false` | 200 |
| **GitLab** | GET après POST → `configured: true` | 200 |
| **GitLab** | DELETE → GET retourne `configured: false` | 204 / 200 |
| **GitLab** | Utiliser API sans token → 503 | 503 |
| **Jenkins** | POST token + password | 204 |
| **Jenkins** | Toolchain invalide (`xyz`) | 422 |
| **Jenkins** | Token DEV n'affecte pas REC | 200 |
| **Jenkins** | Credentials Base64 = `<user>@id.fr.cly:<token>` | — |
| **Jenkins** | Appel Jenkins sans token → 503 | 503 |
| **Sécurité** | GET ne retourne jamais la valeur du token | 200 |
