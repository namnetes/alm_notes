# Dockerfile — Environnement VS Code Docker pour macOS ARM64

Image Docker isolée pour macOS Apple Silicon (M4 / ARM64).  
Voir l'[expression de besoin](bundle_z_vscode.md) pour le contexte complet.

## Fichiers du build context

| Fichier | Rôle |
|---------|------|
| `Dockerfile` | Construction de l'image |
| `entrypoint.sh` | Génère `settings.json` au démarrage et lance code-server |
| `ruff.toml` | Configuration Ruff (linting et formatage Python) |

## Construction

```bash
docker build \
  --platform linux/arm64 \
  --build-arg PROXY_HOST=1111.1111.1111.1111:8080 \
  -t zdev-vscode:latest .
```

Surcharger les arguments disponibles si besoin :

| `--build-arg` | Défaut | Description |
|---|---|---|
| `PROXY_HOST` | `1111.1111.1111.1111:8080` | Adresse du proxy d'entreprise |
| `NO_PROXY` | `localhost,127.0.0.1` | Exclusions proxy |
| `NODE_VERSION` | `24.15.0` | Version Node.js |
| `CODESERVER_VERSION` | `4.96.4` | Version code-server |

## Lancement

```bash
docker run -d \
  --name zdev \
  -e PASSWORD=<mot_de_passe> \
  -v ~/projets:/home/zdev/workspace \
  -v ~/.ssh:/home/zdev/.ssh:ro \
  -p 8443:8443 \
  zdev-vscode:latest
```

Accès VS Code : **http://localhost:8443**

| Variable `-e` | Obligatoire | Description |
|---|---|---|
| `PASSWORD` | Oui | Mot de passe d'accès à code-server |
| `HTTP_PROXY` | Non | Surcharge le proxy sans reconstruire l'image |
| `HTTPS_PROXY` | Non | Idem pour HTTPS |

## Architecture des couches Docker

```
debian:bookworm-slim (ARM64)
 ├── 1. Paquets système  (curl, git, zsh, python3…)
 ├── 2. Java JDK 25 LTS  (Eclipse Temurin — couche lourde, cache prioritaire)
 ├── 3. Node.js 24.15.0  (binaire officiel ARM64)
 ├── 4. Zowe CLI v3-LTS  (npm install -g)
 ├── 5. code-server
 ├── 6. USER zdev (non-root, shell zsh)
 ├── 7. Plugins Zowe     (CICS · MQ · z/OS FTP — dans /home/zdev/.zowe)
 ├── 8. Extensions VS Code (Microsoft Marketplace via EXTENSIONS_GALLERY)
 └── 9. Fichiers de config (ruff.toml, entrypoint.sh)
```

Les couches lourdes (Java, Node.js) sont placées en tête pour maximiser le cache Docker entre les rebuilds.

## Extensions VS Code installées

| Extension | ID Marketplace |
|-----------|---------------|
| Language Support for Java (Red Hat) | `redhat.java` |
| Debugger for Java (Microsoft) | `vscjava.vscode-java-debug` |
| ESLint | `dbaeumer.vscode-eslint` |
| Even Better TOML | `tamasfe.even-better-toml` |
| JSON Tools | `eriklynd.json-tools` |
| Ruff | `charliermarsh.ruff` |
| Python Environment Manager | `donjayamanne.python-environment-manager` |
| Python Debugger | `ms-python.debugpy` |
| Python | `ms-python.python` |
| GitHub Copilot | `github.copilot` |
| GitHub Copilot Chat | `github.copilot-chat` |
| Rainbow CSV | `mechatroner.rainbow-csv` |
| YAML (Red Hat) | `redhat.vscode-yaml` |

!!! warning "Microsoft Marketplace"
    Les extensions `github.copilot*` et `ms-python.*` ne sont pas disponibles sur Open VSX (registry par défaut de code-server).  
    La variable `EXTENSIONS_GALLERY` dans le Dockerfile redirige vers le Marketplace Microsoft pendant le build.

## Points ouverts

Voir le tableau en bas de l'[expression de besoin](bundle_z_vscode.md#points-ouverts-à-confirmer-avant-construction).
