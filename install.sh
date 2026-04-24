#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python"
SHIM_DIR="$HOME/.local/bin"
SHIM_NAME="wnp"
SHIM_PATH="$SHIM_DIR/$SHIM_NAME"

echo "=== Installation de new-page.py ==="
echo ""

# Vérification du venv
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "[!] Python venv introuvable : $VENV_PYTHON"
    echo "    Créez-le avec : python3 -m venv .venv && .venv/bin/pip install pyyaml"
    exit 1
fi
echo "[✓] Venv Python : $VENV_PYTHON"

# Vérification de PyYAML
if ! "$VENV_PYTHON" -c "import yaml" 2>/dev/null; then
    echo "[!] PyYAML absent du venv — installation..."
    "$SCRIPT_DIR/.venv/bin/pip" install pyyaml --quiet
    echo "[✓] PyYAML installé"
else
    echo "[✓] PyYAML disponible"
fi

# Rendre new-page.py exécutable
chmod +x "$SCRIPT_DIR/new-page.py"
echo "[✓] new-page.py marqué exécutable"

# Créer ~/.local/bin si besoin
mkdir -p "$SHIM_DIR"

# Créer le shim
cat > "$SHIM_PATH" << EOF
#!/usr/bin/env bash
exec "$VENV_PYTHON" "$SCRIPT_DIR/new-page.py" "\$@"
EOF
chmod +x "$SHIM_PATH"
echo "[✓] Shim créé : $SHIM_PATH"

# Vérifier que ~/.local/bin est dans le PATH
if [[ ":$PATH:" != *":$SHIM_DIR:"* ]]; then
    SHELL_RC=""
    if [[ -f "$HOME/.bashrc" ]]; then
        SHELL_RC="$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        SHELL_RC="$HOME/.zshrc"
    fi

    if [[ -n "$SHELL_RC" ]]; then
        if ! grep -q 'local/bin' "$SHELL_RC"; then
            {
                echo ''
                echo '# wikinotes'
                echo 'export PATH="$HOME/.local/bin:$PATH"'
            } >> "$SHELL_RC"
            echo "[✓] PATH mis à jour dans $SHELL_RC"
        fi
        echo "    Rechargez votre shell : source $SHELL_RC"
    else
        echo "[!] Ajoutez manuellement : export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
else
    echo "[✓] ~/.local/bin déjà dans \$PATH"
fi

echo ""
echo "=== Terminé ==="
echo "Commande disponible : $SHIM_NAME"
echo "Usage              : $SHIM_NAME"
