# ADR-002 — Stockage des credentials : report du keyring OS en V1

!!! abstract "Qu'est-ce qu'un ADR ?"
    Un **ADR** (Architecture Decision Record) documente une décision technique :
    pourquoi elle a été prise, quelles alternatives ont été écartées, et dans quelles
    conditions elle devra être réexaminée. Voir [ADR-001](adr-001-next-artifact-number.md)
    pour la définition complète.

## Statut

**Accepté — Décision temporaire, applicable à la V1 uniquement**

Révisable dès qu'un des déclencheurs listés en section
[Conditions de révision](#conditions-de-revision) est atteint.

---

## Contexte

### Les trois credentials gérés par le plugin

Le plugin Eclipse gère **trois credentials distincts**, pas deux :

| Credential | Rôle | Portée |
|---|---|---|
| `gitlab_token` | Token d'accès personnel GitLab (PAT) | Unique par développeur |
| `jenkins_token` | Token d'API Jenkins | Un par toolchain (`dev`, `rec`, `frm`, `prd`) |
| `user_password` | Mot de passe AD/LDAP du développeur | Unique par développeur, requis par Jenkins |

Les trois sont marqués `encrypt=true` dans le code Java — ils ne transitent jamais en clair
dans le Secure Store.

### Ce que fait le plugin Eclipse

Le plugin utilise **Eclipse Secure Storage** (`org.eclipse.equinox.security.storage`),
une couche d'abstraction qui délègue au keyring de l'OS selon la plateforme :

| OS | Backend Eclipse Secure Storage |
|---|---|
| Windows | Windows Data Protection API (DPAPI) |
| macOS | macOS Keychain |
| Linux | GNOME Keyring / fichier chiffré par mot de passe |

```java
// Stockage du token GitLab (dans le chemin standard EGit)
ISecurePreferences securePreferences = SecurePreferencesFactory.getDefault();
ISecurePreferences gitNode = securePreferences.node("/GIT/https\\2f\\2fscm.saas.cagip.group.gca:443");
gitNode.put("password", token, true);   // true = chiffré par l'OS

// Stockage du token Jenkins (partitionné par toolchain)
ISecurePreferences root = SecurePreferencesFactory.getDefault().node(toolchain);
ISecurePreferences node = root.node("fr.lcl.zdevops.jenkins.auth");
node.put("jenkins_token", token, true);
```

!!! info "Le chemin EGit"
    Le token GitLab est délibérément stocké dans le chemin standard d'EGit
    (`/GIT/https://...`). Cela permet à EGit d'utiliser les mêmes credentials
    que le plugin pour les opérations Git. L'API Python n'a pas besoin de
    reproduire ce comportement : gitpython reçoit le token directement en
    paramètre à chaque appel.

### Contexte de déploiement

L'API tourne **localement sur le poste de chaque développeur** — identique au plugin
Eclipse qu'elle remplace. Le token appartient au développeur et reste sur son poste.

Le parc est majoritairement **Windows**, avec une adoption croissante de **macOS**.

---

## Décision

**La V1 utilise les variables d'environnement + `SecretStr` Pydantic.**

pydantic-settings charge les credentials depuis l'environnement (ou un fichier `.env`
gitignored). `SecretStr` garantit que les valeurs ne fuient jamais dans les logs ni dans
le `repr()` des objets.

```python
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration de l'API chargée depuis l'environnement.

    En V1, les credentials sont fournis via des variables d'environnement
    ou un fichier .env gitignored. Ils ne sont jamais loggés ni affichés
    grâce au type SecretStr.
    """

    gitlab_token: SecretStr

    jenkins_token_dev: SecretStr | None = None
    jenkins_token_rec: SecretStr | None = None
    jenkins_token_frm: SecretStr | None = None
    jenkins_token_prd: SecretStr | None = None

    user_password: SecretStr | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    def get_jenkins_token(self, toolchain: str) -> SecretStr | None:
        """Retourne le token Jenkins pour la toolchain demandée."""
        return getattr(self, f"jenkins_token_{toolchain}", None)
```

Fichier `.env` (gitignored, sur le poste du développeur) :

```bash
GITLAB_TOKEN=glpat-xxxxxxxxxxxxxxxxxxxx
JENKINS_TOKEN_DEV=11xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
JENKINS_TOKEN_REC=11xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
USER_PASSWORD=monMotDePasse
```

### Raisons du choix V1

1. **Zéro dépendance supplémentaire** — pydantic-settings est déjà dans la stack
2. **Implémentation immédiate** — aucune logique de keyring à écrire pour le MVP
3. **Comportement prévisible** — les variables d'environnement sont le standard
   de facto des applications 12-factor et sont bien comprises par tous les développeurs

### Limitation assumée

Si le développeur opte pour un fichier `.env`, le token est en clair sur disque.
Ce risque est atténué par :

- Le fichier `.env` doit être ajouté à `.gitignore` dès l'init du projet
- Le fichier doit avoir des permissions restrictives (`chmod 600 .env` sur Linux/macOS)
- Ce comportement est documenté dans le guide d'installation

---

## Analyse du code Java original

### Points forts à conserver

- Les trois credentials sont **distincts** : pas de token "fourre-tout"
- Le Jenkins token est **partitionné par toolchain** — l'API reproduit ce découpage
  via `jenkins_token_dev`, `jenkins_token_rec`, etc.

### Points à ne pas reproduire

- Le token GitLab est stocké dans le chemin EGit pour permettre son réutilisation
  par EGit. **L'API n'a pas ce besoin** : gitpython reçoit le token directement.
  Reproduire ce couplage introduirait une dépendance à la convention de nommage EGit.
- `System.out.println` utilisé pour le debug des valeurs récupérées → remplacé par
  le module `logging` Python avec niveau `DEBUG` (jamais la valeur elle-même).

---

## Architecture cible V2 — OS Keyring + SecretStr

!!! info "Qu'est-ce que le keyring OS ?"
    Le **keyring** (ou trousseau de clés) est un composant sécurisé de l'OS qui stocke
    des credentials chiffrés, déverrouillés par la session de l'utilisateur. Ni le mot
    de passe de chiffrement ni les credentials ne transitent en clair sur le disque.

    - **Windows** : Windows Credential Manager (accessible via Panneau de configuration
      → Gestionnaire d'identification)
    - **macOS** : Keychain (accessible via l'application Trousseau d'accès)
    - **Linux** : GNOME Keyring ou KWallet selon l'environnement de bureau

    C'est exactement ce qu'utilise Eclipse Secure Storage en coulisses — la bibliothèque
    Python `keyring` cible les **mêmes backends** sur les mêmes OS.

La bibliothèque `keyring` (maintenue, stable, sans dépendance système à installer)
abstrait les trois plateformes derrière une interface identique :

```python
import keyring
from pydantic import SecretStr

SERVICE_NAME = "zdevops-api"


def store_gitlab_token(token: str) -> None:
    """Stocke le token GitLab dans le keyring de l'OS."""
    keyring.set_password(SERVICE_NAME, "gitlab_token", token)


def get_gitlab_token() -> SecretStr | None:
    """Lit le token GitLab depuis le keyring de l'OS."""
    value = keyring.get_password(SERVICE_NAME, "gitlab_token")
    return SecretStr(value) if value else None


def store_jenkins_token(toolchain: str, token: str) -> None:
    """Stocke le token Jenkins pour une toolchain dans le keyring de l'OS."""
    keyring.set_password(SERVICE_NAME, f"jenkins_token_{toolchain}", token)


def get_jenkins_token(toolchain: str) -> SecretStr | None:
    """Lit le token Jenkins pour une toolchain depuis le keyring de l'OS."""
    value = keyring.get_password(SERVICE_NAME, f"jenkins_token_{toolchain}")
    return SecretStr(value) if value else None
```

### Flow V2 au démarrage de l'API

```
Démarrage
  └─ pour chaque credential attendu :
       ├─ keyring.get_password("zdevops-api", clé)
       │    ├─ Trouvé  → SecretStr en mémoire → utilisation silencieuse
       │    └─ Absent  → credential manquant → loggé en WARNING
       │                  l'API démarre sans ce credential
       │                  les endpoints concernés retournent 503
       │
       └─ POST /api/v1/config/gitlab-token
            → keyring.set_password(...)
            → rechargement du SecretStr en mémoire
            → 204 No Content
```

### Endpoints de configuration (fonctions 13 et 14 dans la V2)

| Méthode | Endpoint | Action |
|---|---|---|
| `POST` | `/api/v1/config/gitlab-token` | Stocke dans le keyring + charge en mémoire |
| `GET` | `/api/v1/config/gitlab-token` | Retourne `{"configured": true/false}` (jamais la valeur) |
| `DELETE` | `/api/v1/config/gitlab-token` | Supprime du keyring + vide la mémoire |
| `POST` | `/api/v1/config/jenkins-token/{toolchain}` | Idem pour Jenkins |
| `GET` | `/api/v1/config/jenkins-token/{toolchain}` | Idem |
| `DELETE` | `/api/v1/config/jenkins-token/{toolchain}` | Idem |

### Comparaison V1 vs V2

| Critère | V1 — Variables d'env | V2 — OS Keyring |
|---|---|---|
| Token en clair sur disque | ⚠️ Si fichier `.env` | ✅ Jamais |
| Dépendance supplémentaire | ✅ Aucune | ✅ `keyring` (léger) |
| Cohérence avec Eclipse | ⚠️ Différent | ✅ Même backend OS |
| Complexité implémentation | Très faible | Faible |
| API de configuration (13/14) | Non (env seulement) | ✅ Endpoints dédiés |
| Protection mémoire (`SecretStr`) | ✅ | ✅ |

---

## Conditions de révision

Cette décision doit être réexaminée si l'un des déclencheurs suivants est atteint :

1. Un **incident de sécurité** impliquant un token exposé dans un `.env` commité
2. La **V2 du MVP est planifiée** — c'est le moment naturel d'implémenter le keyring
3. Une **exigence de sécurité** de la DSI impose le stockage dans le keyring OS

---

## Liens

- [Architecture générale](architecture-generale.md)
- [ADR-001 — next_artifact_number](adr-001-next-artifact-number.md)
- Code Java : `EclipsePluginHelper.java` — méthodes `store*Securely()` et `retrieve*Securely()`
