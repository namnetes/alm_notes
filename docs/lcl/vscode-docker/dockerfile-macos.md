# Guide technique — Construction de l'image Docker

Ce document s'adresse aux développeurs et aux administrateurs qui souhaitent comprendre comment l'image Docker est construite, la modifier ou la reconstruire.

> **Débutant ?** Vous n'avez pas besoin de lire ce fichier pour utiliser l'environnement. Consultez la [page d'accueil de la section](index.md) pour le démarrage rapide.

Voir aussi le [cahier des charges initial](bundle_z_vscode.md) pour le contexte complet du projet.

---

## Variantes par plateforme

Le projet fournit deux Dockerfiles selon la plateforme cible :

| Fichier | Plateforme | Architecture | Binaires spécifiques |
|---|---|---|---|
| `Dockerfile.linux` | Linux (Ubuntu, Debian…) | AMD64 (x86-64) | Java `x64`, code-server `amd64` |
| `Dockerfile.macos` | macOS Apple Silicon | ARM64 | Java `aarch64`, code-server `arm64`, proxy npm |

Les deux variantes partagent la même structure de couches et les mêmes versions logicielles. Seuls les binaires dépendants de l'architecture et la configuration proxy npm diffèrent.

---

## Qu'est-ce qu'un Dockerfile ?

Un Dockerfile est un fichier texte qui décrit, étape par étape, comment construire une image Docker. Chaque instruction (`RUN`, `COPY`, `ENV`…) crée une **couche** (layer). Docker met ces couches en cache : si une couche n'a pas changé depuis le dernier build, elle est réutilisée directement, ce qui accélère les reconstructions.

---

## Fichiers du build context

| Fichier | Rôle |
|---|---|
| `Dockerfile.linux` | Recette de l'image pour Linux AMD64 |
| `Dockerfile.macos` | Recette de l'image pour macOS ARM64 |
| `build-linux.sh` | Script de build Linux (nettoie le cache puis lance le build) |
| `build-macos.sh` | Script de build macOS (idem + `--platform linux/arm64` + proxy) |
| `entrypoint.sh` | Script lancé au démarrage du conteneur — démarre code-server |
| `vscode-settings.json` | Paramètres VS Code copiés dans l'image |
| `ruff.toml` | Configuration du linter Python Ruff |
| `copilot/` | Instructions GitHub Copilot copiées dans l'image |
| `extensions/` | Fichiers `.vsix` des extensions VS Code (à télécharger au préalable) |

---

## Avant de construire — télécharger les extensions

Les extensions VS Code ne sont pas versionnées dans le dépôt. Téléchargez-les avec le script fourni :

```bash
# Sans proxy
./download_extensions.sh

# Avec proxy d'entreprise
./download_extensions.sh --proxy http://adresse-proxy:port
```

Le script interroge l'API du Marketplace Microsoft, récupère la dernière version de chaque extension et enregistre les fichiers `.vsix` dans le dossier `extensions/`. Un tableau récapitulatif s'affiche à la fin.

> **Connexion requise :** le script contacte `marketplace.visualstudio.com`. En environnement sans accès internet, les `.vsix` doivent être fournis manuellement.

---

## Construction de l'image

La méthode recommandée est d'utiliser les scripts fournis. Ils nettoient le cache Docker avant chaque build pour garantir une construction propre.

### Sur Linux

```bash
./build-linux.sh
```

Équivalent manuel :

```bash
docker builder prune -a -f
docker build -f Dockerfile.linux -t zdev-vscode:latest .
```

### Sur macOS Apple Silicon

```bash
./build-macos.sh
```

Le proxy est lu depuis la variable d'environnement `HTTP_PROXY`. Pour le surcharger :

```bash
HTTP_PROXY=http://adresse-proxy:port ./build-macos.sh
```

Équivalent manuel :

```bash
docker builder prune -a -f
docker build \
  --platform linux/arm64 \
  -f Dockerfile.macos \
  --build-arg HTTP_PROXY=http://adresse-proxy:port \
  --build-arg HTTPS_PROXY=http://adresse-proxy:port \
  --build-arg PROXY_HOST=http://adresse-proxy:port \
  -t zdev-vscode:latest .
```

### Démarrer le conteneur (Linux et macOS)

Après le build, la commande de démarrage est identique sur les deux plateformes :

```bash
docker compose up -d
```

---

## Arguments de build disponibles

Ces valeurs peuvent être surchargées avec `--build-arg` sans modifier le Dockerfile.

### Communs aux deux variantes

| Argument | Valeur par défaut | Description |
|---|---|---|
| `NODE_VERSION` | `24.15.0` | Version de Node.js installée |
| `CODESERVER_VERSION` | `4.117.0` | Version de code-server installée |

### Spécifiques à `Dockerfile.macos`

| Argument | Valeur par défaut | Description |
|---|---|---|
| `PROXY_HOST` | `http://??????` | Adresse du proxy d'entreprise utilisée à l'intérieur du build |
| `NO_PROXY` | `localhost,127.0.0.1,10.0.0.0/8` | Adresses qui contournent le proxy |

> **`PROXY_HOST` vs `HTTP_PROXY`** : `PROXY_HOST` configure le proxy à l'intérieur du build (apt, curl, npm). `HTTP_PROXY` est une variable d'environnement standard passée en complément.

---

## Lancement du conteneur

La méthode recommandée est Docker Compose (voir la [page d'accueil de la section](index.md)). La commande `docker run` manuelle est donnée ici à titre de référence :

```bash
docker run -d \
  --name zdev \
  -e PASSWORD=mon-mot-de-passe \
  -e TZ=Europe/Paris \
  -v ~/zdev/projets:/home/zdev/workspace \
  -v ~/zdev/vscode-settings:/home/zdev/.local/share/code-server/User \
  -v ~/zdev/vscode-extensions:/home/zdev/.local/share/code-server/extensions \
  -v ~/zdev/.zshrc:/home/zdev/.zshrc \
  -v ~/zdev/.gitconfig:/home/zdev/.gitconfig \
  -v ~/.ssh:/home/zdev/.ssh:ro \
  -p 8443:8443 \
  zdev-vscode:latest
```

Accès VS Code : **http://localhost:8443**

### Variables d'environnement à l'exécution

| Variable | Obligatoire | Valeur par défaut | Description |
|---|---|---|---|
| `PASSWORD` | Oui | *(aucune)* | Mot de passe d'accès à code-server |
| `TZ` | Non | `UTC` | Fuseau horaire du conteneur |
| `HTTP_PROXY` | Non | *(aucune)* | Surcharge le proxy sans reconstruire l'image |
| `HTTPS_PROXY` | Non | *(aucune)* | Idem pour HTTPS |

---

## Architecture des couches Docker

L'ordre des couches est optimisé pour maximiser les hits de cache lors des rebuilds. Les couches les plus stables (et les plus lourdes) sont placées en premier.

```
debian:bookworm-slim
 │   Linux : AMD64     macOS : ARM64 (--platform linux/arm64)
 │
 ├──  1. Paquets système
 │        curl, git, zsh, python3, pip, ca-certificates, unzip
 │        libcairo2, libpangocairo-1.0-0, libgdk-pixbuf-2.0-0, fonts-dejavu-core
 │        └── librairies Cairo nécessaires aux social cards MkDocs Material
 │
 ├──  2. Java JDK 21 LTS (Eclipse Temurin — ~180 Mo)
 │        Linux : binaire x64      macOS : binaire aarch64
 │        Stable — rarement modifié → cache prioritaire
 │
 ├──  3. Node.js 24 LTS (~60 Mo)
 │        Source : nodesource.com
 │        macOS uniquement : configuration proxy npm
 │
 ├──  4. Zowe CLI v3-LTS
 │        npm install -g @zowe/cli
 │        + plugins : CICS · MQ · z/OS FTP
 │
 ├──  5. code-server 4.117.0
 │        Linux : binaire linux-amd64      macOS : binaire linux-arm64
 │
 ├──  6. Utilisateur zdev (non-root, shell zsh)
 │        Création de /home/zdev/workspace
 │
 ├──  7. uv  (~10 Mo)
 │        Gestionnaire de paquets Python — installé via script officiel
 │        Disponible à /home/zdev/.local/bin/uv
 │
 ├──  8. MkDocs Material
 │        uv tool install mkdocs
 │          + mkdocs-material[imaging]   ← social cards, thème complet
 │          + mkdocs-minify-plugin       ← minification HTML/CSS/JS
 │          + mkdocs-redirects           ← redirections d'URLs
 │          + mkdocs-git-revision-date-localized-plugin ← dates git par page
 │
 ├──  9. Fichiers de configuration
 │        ruff.toml, vscode-settings.json, copilot/
 │
 ├── 10. Extensions VS Code
 │        Installation des .vsix depuis extensions/
 │        → couche fréquemment modifiée, placée en fin pour éviter
 │          d'invalider le cache des couches stables ci-dessus
 │
 └── 11. Entrypoint
          entrypoint.sh → lance code-server sur 0.0.0.0:8443
```

**Règle clé :** modifier une couche invalide toutes les couches suivantes. C'est pourquoi Java, Node.js, uv et MkDocs (lourds et stables) sont placés avant les fichiers de config et les extensions (légers et changeants).

---

## Extensions VS Code installées

Les extensions suivantes sont téléchargées par `download_extensions.sh` et installées dans l'image lors du build.

### Python

| ID Marketplace | Extension |
|---|---|
| `ms-python.python` | Python (Microsoft) |
| `ms-python.debugpy` | Python Debugger (Microsoft) |
| `charliermarsh.ruff` | Ruff |
| `donjayamanne.python-environment-manager` | Python Environment Manager |

### Formats de données

| ID Marketplace | Extension |
|---|---|
| `tamasfe.even-better-toml` | Even Better TOML |
| `ZainChen.json` | JSON |
| `redhat.vscode-yaml` | YAML (Red Hat) |
| `mechatroner.rainbow-csv` | Rainbow CSV |

### Interface et thème

| ID Marketplace | Extension |
|---|---|
| `PKief.material-icon-theme` | Material Icon Theme |
| `PKief.material-product-icons` | Material Product Icons |
| `Catppuccin.catppuccin-vsc` | Catppuccin (thème) |
| `yzhang.markdown-all-in-one` | Markdown All in One |

### Intelligence artificielle

| ID Marketplace | Extension |
|---|---|
| `GitHub.copilot` | GitHub Copilot |
| `GitHub.copilot-chat` | GitHub Copilot Chat |

### IBM ADFz (Application Delivery Foundation for z/OS)

Ces extensions font partie du pack IBM ADFz. Chacune est installée individuellement en `.vsix` car les méta-paquets ne sont pas installables hors ligne.

| ID Marketplace | Extension | Licence IBM requise |
|---|---|---|
| `IBM.zopeneditor` | Z Open Editor (COBOL, JCL, PL/I…) | Non |
| `Zowe.vscode-extension-for-zowe` | Zowe Explorer | Non |
| `Zowe.cics-extension-for-zowe` | Zowe CICS Explorer | Non |
| `IBM.zopendebug` | Z Open Debug | Oui |
| `IBM.compiledcodecoverage` | Compiled Code Coverage | Oui |
| `IBM.zfilemanager` | File Manager for z/OS | Oui |
| `IBM.zfaultanalyzer` | Fault Analyzer for z/OS | Oui |
| `IBM.apa-extension` | Application Performance Analyzer | Oui |

> **Note sur les extensions Microsoft et GitHub :** les extensions `ms-python.*`, `GitHub.copilot*` ne sont pas disponibles sur Open VSX (registry par défaut de code-server). Elles sont téléchargées directement depuis le Marketplace Microsoft par `download_extensions.sh` et installées via `.vsix`, ce qui contourne cette limitation.

---

## Modifier les extensions

Pour ajouter ou retirer une extension :

1. Modifiez `download_extensions.sh` (ajoutez ou supprimez un appel `download_vsix "publisher.extension"`).
2. Relancez le téléchargement : `./download_extensions.sh`.
3. Reconstruisez l'image : `docker compose build`.

Seule la dernière couche (installation des extensions) est reconstruite. Le reste du cache Docker est conservé.

---

## Modifier l'image

### Ajouter un paquet système

Dans le Dockerfile, ajoutez le paquet à la couche `apt-get` (étape 1) :

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git zsh python3 python3-pip python3-venv ca-certificates unzip \
    mon-nouveau-paquet \
    && rm -rf /var/lib/apt/lists/*
```

> Attention : modifier la couche 1 invalide toutes les couches suivantes. Le build sera long.

### Changer la version de Node.js ou de code-server

Modifiez l'argument par défaut dans le Dockerfile ou passez `--build-arg` :

```bash
docker compose build --build-arg NODE_VERSION=22.0.0
```

### Changer la version de Java

Java JDK 21 LTS (Eclipse Temurin) est téléchargé depuis GitHub Adoptium. Pour changer de version, modifiez l'URL dans la couche 3 du Dockerfile.

---

## Sécurité

- Le conteneur s'exécute avec l'utilisateur non-root `zdev` (UID aléatoire).
- Les clés SSH sont montées en **lecture seule** (`~/.ssh:/home/zdev/.ssh:ro`).
- Le mot de passe code-server est transmis via variable d'environnement — ne le committez jamais dans le dépôt.
- Le port 8443 n'est exposé que localement (`127.0.0.1:8443` par défaut avec Docker Desktop).
