#!/bin/bash
# Crée (ou recrée) l'arborescence ~/zdev/ sur la machine hôte.
# Ces dossiers sont montés comme volumes Docker dans le conteneur zdev-vscode
# pour assurer la persistance des projets, paramètres et caches entre les lancements.
#
# Usage : ./reset_zdev_env.sh
#
# ATTENTION : si ~/zdev/ existe déjà, il est supprimé entièrement avant recréation.
# Vos projets dans ~/zdev/projets/ seront perdus. Faites une sauvegarde si nécessaire.
set -euo pipefail

ZDEV_DIR="$HOME/zdev"

# Suppression complète pour repartir d'un état propre (volumes corrompus, droits incorrects, etc.)
if [ -d "$ZDEV_DIR" ]; then
    echo "Suppression de $ZDEV_DIR..."
    rm -rf "$ZDEV_DIR"
fi

# --- Dossiers de données et de caches ---
mkdir -p "$ZDEV_DIR/projets"            # espace de travail monté dans /home/zdev/workspace
mkdir -p "$ZDEV_DIR/vscode-npm-cache"   # accélère npm install entre les sessions
mkdir -p "$ZDEV_DIR/vscode-pip-cache"   # accélère pip install entre les sessions

# --- Dossiers de configuration VS Code ---
mkdir -p "$ZDEV_DIR/vscode-settings"    # paramètres utilisateur (settings.json, keybindings…)
mkdir -p "$ZDEV_DIR/vscode-extensions"  # extensions installées manuellement depuis VS Code

# --- Fichiers de configuration shell et git ---
# touch crée les fichiers vides s'ils n'existent pas encore.
# Docker exige que les fichiers montés existent sur l'hôte avant le démarrage du conteneur.
touch "$ZDEV_DIR/.zshrc"
touch "$ZDEV_DIR/.gitconfig"

# --- Droits d'accès ---
# chmod 755 : lecture/exécution par tous, écriture réservée au propriétaire.
# chown : s'assure que les fichiers appartiennent à l'utilisateur courant, pas à root.
chmod 755 "$ZDEV_DIR"
chown "$(id -u):$(id -g)" "$ZDEV_DIR"

for d in projets vscode-npm-cache vscode-pip-cache vscode-settings vscode-extensions; do
    chmod 755 "$ZDEV_DIR/$d"
    chown "$(id -u):$(id -g)" "$ZDEV_DIR/$d"
done

chmod 644 "$ZDEV_DIR/.zshrc" "$ZDEV_DIR/.gitconfig"
chown "$(id -u):$(id -g)" "$ZDEV_DIR/.zshrc" "$ZDEV_DIR/.gitconfig"

echo "Environnement $ZDEV_DIR réinitialisé avec succès."

