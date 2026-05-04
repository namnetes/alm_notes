# Cahier des charges — Environnement de développement isolé sous Docker

> **Nature de ce document**
> Il s'agit du cahier des charges initial rédigé avant la construction de l'image, complété par les décisions techniques prises lors de l'implémentation. Les sections marquées **[Implémenté]** décrivent l'état réel du projet. Les informations originales qui ont évolué sont annotées.
>
> Pour démarrer rapidement, consultez la [page d'accueil de la section](index.md).

---

## État de l'implémentation

Le tableau suivant résume les composants livrés et les décisions prises sur les points qui étaient ouverts lors de la rédaction initiale.

| Composant | Spécification initiale | Implémenté |
|---|---|---|
| Hôte cible | macOS M4 (ARM64) | Linux AMD64 (`Dockerfile.linux`) et macOS ARM64 (`Dockerfile.macos`) |
| Image de base | Debian (ARM64) | `debian:bookworm-slim` (AMD64 ou ARM64 selon la variante) |
| Java | JDK 25 LTS *(non disponible à la rédaction)* | JDK 21 LTS — Eclipse Temurin (`x64` ou `aarch64`) |
| Node.js | 24.15.0 LTS | 24.15.0 LTS |
| Zowe CLI | v3-LTS | v3-LTS |
| Plugins Zowe | CICS, MQ, z/OS FTP | CICS, MQ, z/OS FTP |
| IDE | code-server | code-server 4.96.4 |
| Extensions VS Code | 12 extensions | 22 extensions (liste étendue, voir ci-dessous) |
| Utilisateur | non-root `zdev` + zsh | `zdev` + zsh |
| Gestionnaire de paquets Python | *(non spécifié)* | `uv` — disponible dans le terminal VS Code et sur macOS |
| Documentation statique | *(non spécifié)* | MkDocs Material + 4 plugins (`imaging`, `minify`, `redirects`, `git-revision-date`) |
| Proxy | Paramétrable | Paramétrable via `--build-arg` et variable d'env. |
| Clés SSH | À définir | Montage en lecture seule depuis `~/.ssh` de l'hôte |
| Profils Zowe | À définir | Gérés via l'extension Zowe Explorer (non gravés dans l'image) |
| Mot de passe code-server | À définir | Variable d'environnement `PASSWORD` dans `docker-compose.yml` |
| Distribution | SCCM *(prévu)* | Docker Compose — distribution via dépôt git |

---

## 1. Contexte du projet

L'objectif est de mettre en place un environnement de développement complet, portable et totalement isolé. Cet environnement doit permettre le développement mainframe IBM z/OS sans installer de dépendances directement sur le système d'exploitation de l'utilisateur.

**Avantages du conteneur Docker :**

- **Isolation stricte** : aucune dépendance installée sur la machine hôte.
- **Portabilité** : l'environnement est identique sur toutes les machines qui exécutent le conteneur.
- **Zéro résidu** : supprimer le conteneur supprime tous les outils. Les données utilisateur sont préservées via des volumes.
- **Reconstructible** : en cas de problème, on repart d'une image propre sans perdre les projets.

---

## 2. Objectifs techniques

- **Isolation stricte :** toutes les couches logicielles (IDE, runtimes, outils CLI) sont encapsulées dans l'image Docker.
- **Multi-plateforme :** deux variantes de l'image sont fournies — `Dockerfile.linux` pour Linux AMD64, `Dockerfile.macos` pour macOS Apple Silicon (ARM64).
- **Zéro résidu :** la suppression du conteneur entraîne la disparition de tous les outils de développement sur l'hôte. Les projets et paramètres utilisateur sont préservés via des volumes Docker.
- **Proxy d'entreprise :** l'environnement fonctionne derrière un proxy HTTP d'entreprise, sans modification de la machine hôte.

---

## 3. Spécifications fonctionnelles

### A. Runtimes et outils

**Java** **[Implémenté : JDK 21 LTS]**

Java est requis pour les extensions VS Code de développement Java (Language Support, Debugger). Aucun outil de build (Maven, Gradle) n'est nécessaire.

La spécification initiale mentionnait Java 25 LTS, qui n'était pas disponible lors de la construction. La version retenue est **Java 21 LTS** (Eclipse Temurin, binaire `aarch64`), dernière version LTS disponible.

**Python** **[Implémenté : Python 3 + uv]**

Python est installé depuis les paquets système Debian (`python3`, `python3-pip`, `python3-venv`). Un fichier de configuration **`ruff.toml`** est inclus dans l'image, positionné dans `/home/zdev/` et référencé par l'extension Ruff dans VS Code.

**uv** est installé comme gestionnaire de paquets Python de référence (`~/.local/bin/uv`). Il remplace `pip`, `venv` et `poetry` pour la création de projets, la gestion des dépendances et l'exécution de scripts. Il est également installable sur macOS pour travailler hors conteneur sur les mêmes fichiers.

**MkDocs Material** est installé via `uv tool install` pour la génération de documentation statique. Plugins inclus : `imaging` (social cards), `minify`, `redirects`, `git-revision-date-localized`.

**Node.js** **[Implémenté : 24.15.0 LTS]**

Installé depuis `nodesource.com`. La configuration proxy npm est appliquée automatiquement lors du build.

**Zowe CLI** **[Implémenté : v3-LTS + 3 plugins]**

```
zowe plugins install @zowe/cics-for-zowe-cli@zowe-v3-lts
zowe plugins install @zowe/mq-for-zowe-cli@zowe-v3-lts
zowe plugins install @zowe/zos-ftp-for-zowe-cli@zowe-v3-lts
```

### B. Environnement de développement (IDE)

**VS Code intégré via code-server** **[Implémenté : code-server 4.96.4]**

code-server expose VS Code sur le port 8443 en HTTP local. Accès via navigateur sur `http://localhost:8443`.

**Extensions pré-configurées** **[Implémenté : 22 extensions]**

Les extensions ne sont pas téléchargées depuis internet lors du build (contrainte de proxy et de reproductibilité). Elles sont fournies sous forme de fichiers `.vsix` et installées pendant le build.

Le script `download_extensions.sh` automatise leur téléchargement depuis le Marketplace Microsoft.

Extensions installées (liste complète) :

| Catégorie | Extension | ID |
|---|---|---|
| Python | Python | `ms-python.python` |
| Python | Python Debugger | `ms-python.debugpy` |
| Python | Ruff | `charliermarsh.ruff` |
| Python | Python Environment Manager | `donjayamanne.python-environment-manager` |
| Données | Even Better TOML | `tamasfe.even-better-toml` |
| Données | JSON | `ZainChen.json` |
| Données | YAML | `redhat.vscode-yaml` |
| Données | Rainbow CSV | `mechatroner.rainbow-csv` |
| Interface | Material Icon Theme | `PKief.material-icon-theme` |
| Interface | Material Product Icons | `PKief.material-product-icons` |
| Interface | Catppuccin | `Catppuccin.catppuccin-vsc` |
| Documentation | Markdown All in One | `yzhang.markdown-all-in-one` |
| IA | GitHub Copilot | `GitHub.copilot` |
| IA | GitHub Copilot Chat | `GitHub.copilot-chat` |
| Mainframe | Z Open Editor | `IBM.zopeneditor` |
| Mainframe | Z Open Debug | `IBM.zopendebug` |
| Mainframe | Compiled Code Coverage | `IBM.compiledcodecoverage` |
| Mainframe | Zowe Explorer | `Zowe.vscode-extension-for-zowe` |
| Mainframe | Zowe CICS Explorer | `Zowe.cics-extension-for-zowe` |
| Mainframe | File Manager for z/OS | `IBM.zfilemanager` |
| Mainframe | Fault Analyzer for z/OS | `IBM.zfaultanalyzer` |
| Mainframe | Application Performance Analyzer | `IBM.apa-extension` |

**Utilisateur dédié** **[Implémenté]**

Utilisateur non-root `zdev` avec `zsh` comme shell par défaut.

### C. Gestion réseau et proxy

**[Implémenté]**

Le proxy est configurable à deux niveaux :

- **Au build** : `--build-arg HTTP_PROXY=...` et `--build-arg HTTPS_PROXY=...` (ou `PROXY_HOST` pour l'adresse interne au build).
- **À l'exécution** : variables d'environnement `HTTP_PROXY` et `HTTPS_PROXY` dans `docker-compose.yml`.

L'adresse proxy par défaut dans le Dockerfile est `http://10.179.250.164:3128`. Elle peut être surchargée sans modifier le Dockerfile.

GitHub Copilot utilise le proxy VS Code configuré via le paramètre `http.proxy` dans `vscode-settings.json`.

---

## 4. Gestion des données et déploiement

### Persistance locale **[Implémenté]**

Les données utilisateur sont stockées sur la machine hôte via des volumes Docker. Le conteneur est **stateless** : sa suppression ne supprime aucune donnée utilisateur.

| Volume hôte | Montage conteneur | Contenu |
|---|---|---|
| `~/zdev/projets` | `/home/zdev/workspace` | Projets et fichiers de travail |
| `~/zdev/vscode-settings` | `~/.local/share/code-server/User` | Paramètres VS Code |
| `~/zdev/vscode-extensions` | `~/.local/share/code-server/extensions` | Extensions installées |
| `~/zdev/.zshrc` | `/home/zdev/.zshrc` | Configuration shell |
| `~/zdev/.gitconfig` | `/home/zdev/.gitconfig` | Configuration git |
| `~/zdev/vscode-npm-cache` | `/home/zdev/.npm` | Cache npm |
| `~/zdev/vscode-pip-cache` | `/home/zdev/.cache/pip` | Cache pip |

### Clés SSH **[Implémenté : montage en lecture seule]**

Les clés SSH existantes de l'utilisateur sont montées depuis `~/.ssh` en lecture seule :

```yaml
- ~/.ssh:/home/zdev/.ssh:ro
```

Aucune génération de clé dans le conteneur. Les clés sont gérées sur la machine hôte.

### Profils Zowe **[Implémenté : gestion via Zowe Explorer]**

Les profils de connexion z/OS (hostname, port, credentials) ne sont pas gravés dans l'image. Ils sont créés et gérés via l'extension **Zowe Explorer** dans VS Code, qui les stocke dans `~/.zowe/` — répertoire persisté via le volume `vscode-settings`.

### Mot de passe code-server **[Implémenté : variable d'environnement]**

Le mot de passe est transmis via la variable d'environnement `PASSWORD` dans `docker-compose.yml`. Valeur par défaut : `zdev`. À modifier avant tout déploiement en production.

### Distribution **[Implémenté : Docker Compose + dépôt git]**

L'image est construite localement avec `docker compose build`. La distribution se fait par partage du dépôt git (l'image elle-même n'est pas publiée sur un registry à ce stade).

---

## 5. Contraintes de performance

- Image basée sur `debian:bookworm-slim` — empreinte minimale.
- Couches Docker ordonnées pour maximiser le cache : les couches lourdes et stables (Java, Node.js) sont placées en début de Dockerfile.
- Volumes montés en natif avec VirtioFS (macOS Docker Desktop) — accès fichiers performant.
- Caches npm et pip montés en volume pour éviter le re-téléchargement des dépendances.

---

## Résumé des composants

| Composant | Technologie retenue |
|---|---|
| **Image de base** | `debian:bookworm-slim` (AMD64 — Linux / ARM64 — macOS) |
| **IDE** | code-server 4.117.0 (VS Code dans le navigateur) |
| **Java** | JDK 21 LTS — Eclipse Temurin (`x64` Linux / `aarch64` macOS) |
| **Node.js** | 24.15.0 LTS |
| **CLI Mainframe** | Zowe CLI v3-LTS + plugins CICS, MQ, z/OS FTP |
| **Python (packaging)** | uv — gestionnaire de paquets et environnements virtuels |
| **Documentation** | MkDocs Material + plugins imaging, minify, redirects, git-date |
| **Shell utilisateur** | zsh (utilisateur `zdev`, non-root) |
| **Proxy** | Paramétrable via `--build-arg` et variable d'env. |
| **Accès** | Navigateur web — http://localhost:8443 |
| **Persistance** | Volumes Docker dans `~/zdev/` sur l'hôte |
| **Clés SSH** | Montage lecture seule depuis `~/.ssh` de l'hôte |
| **Distribution** | Docker Compose — dépôt git |
