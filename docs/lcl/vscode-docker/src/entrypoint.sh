#!/bin/bash
# Point d'entrée du conteneur zdev-vscode.
# Lancé automatiquement par Docker au démarrage du conteneur (ENTRYPOINT).
# Ce script est l'endroit approprié pour toute initialisation à chaque démarrage
# (ex. synchronisation de repos, installation d'extensions supplémentaires).
set -euo pipefail

# Exemple : forcer l'installation d'extensions à chaque démarrage
# (utile pour des extensions non incluses dans l'image, installées depuis un registry).
# EXTENSIONS=(
#   "IBM.zopeneditor"
#   "IBM.zowe-explorer"
#   "IBM.cics-explorer"
# )
# for ext in "${EXTENSIONS[@]}"; do
#   code-server --install-extension "$ext" || true
# done

# Lancer code-server.
# --bind-addr 0.0.0.0:8443 : écoute sur toutes les interfaces réseau du conteneur,
#   ce qui permet à Docker de router le port 8443 depuis l'hôte.
# Le point final "." ouvre le workspace (/home/zdev/workspace via le répertoire courant).
# exec remplace le processus shell par code-server — les signaux Docker (SIGTERM)
# sont ainsi transmis directement à code-server pour un arrêt propre.
exec code-server --bind-addr 0.0.0.0:8443 .
