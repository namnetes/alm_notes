# Environnement VS Code Docker — Zowe & Copilot

Environnement de développement isolé sous Docker pour **Linux AMD64** et **macOS Apple Silicon (ARM64)**.  
Intègre VS Code (code-server), Zowe CLI, GitHub Copilot et les runtimes Java, Node.js et Python.  
Distribué via dépôt git — construction locale avec les scripts fournis.

## Plateformes supportées

| Plateforme | Dockerfile | Script de build | Architecture |
|---|---|---|---|
| Linux (Ubuntu, Debian…) | `Dockerfile.linux` | `build-linux.sh` | AMD64 (x86-64) |
| macOS Apple Silicon (M1/M2/M3/M4) | `Dockerfile.macos` | `build-macos.sh` | ARM64 |

Dans les deux cas, le démarrage du conteneur se fait avec `docker compose up -d`.

## Documents

| Document | Statut | Description |
|---|---|---|
| [Cahier des charges](bundle_z_vscode.md) | Implémenté | Spécifications fonctionnelles, décisions techniques et état de l'implémentation |
| [Guide technique de build](dockerfile-macos.md) | Implémenté | Construction de l'image Docker — Linux AMD64 et macOS ARM64 |

## Sources

Le dossier `src/` contient les fichiers du projet tels que livrés :

| Fichier | Rôle |
|---|---|
| `Dockerfile.linux` | Recette de l'image — Linux AMD64 |
| `Dockerfile.macos` | Recette de l'image — macOS ARM64 |
| `build-linux.sh` | Script de build Linux |
| `build-macos.sh` | Script de build macOS |
| `docker-compose.yml` | Orchestration du conteneur |
| `entrypoint.sh` | Script de démarrage du conteneur |
| `download_extensions.sh` | Téléchargement des extensions VS Code (.vsix) |
| `reset_zdev_env.sh` | Initialisation de `~/zdev/` sur l'hôte |
| `ruff.toml` | Configuration du linter Python Ruff |
| `vscode-settings.json` | Paramètres VS Code embarqués dans l'image |
