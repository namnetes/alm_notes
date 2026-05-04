#!/usr/bin/env bash
# Télécharge les extensions VS Code (.vsix) depuis le Marketplace Microsoft.
# Usage : ./download_extensions.sh [--proxy http://host:port]
set -euo pipefail

OUTDIR="extensions"
# Au bureau : décommenter la ligne ci-dessous (ou exporter HTTP_PROXY avant d'appeler le script)
# PROXY="${HTTP_PROXY:-http://10.179.250.164:3128}"
PROXY="${HTTP_PROXY:-}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --proxy) PROXY="$2"; shift 2 ;;
        --no-proxy) PROXY=""; shift ;;
        *) echo "Option inconnue : $1"; exit 1 ;;
    esac
done

CURL_OPTS=(-fsSL --compressed)
[[ -n "$PROXY" ]] && CURL_OPTS+=(--proxy "$PROXY")

mkdir -p "$OUTDIR"

# Tableau récapitulatif rempli par download_vsix
declare -a DOWNLOADED=()

# Récupère la dernière version depuis l'API du Marketplace, puis télécharge le .vsix
download_vsix() {
    local id="$1"
    local publisher="${id%%.*}"
    local name="${id#*.}"

    printf "  ↓ %-45s " "$id"

    local version
    version=$(curl "${CURL_OPTS[@]}" \
        -X POST \
        "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery?api-version=3.0-preview.1" \
        -H "Content-Type: application/json" \
        -H "Accept: application/json;api-version=3.0-preview.1" \
        -d "{\"filters\":[{\"criteria\":[{\"filterType\":7,\"value\":\"${id}\"}]}],\"flags\":914}" \
        | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['results'][0]['extensions'][0]['versions'][0]['version'])")

    curl "${CURL_OPTS[@]}" \
        -o "${OUTDIR}/${id}-${version}.vsix" \
        "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/${publisher}/vsextensions/${name}/${version}/vspackage"

    echo "v${version}"
    DOWNLOADED+=("${id}|${version}")
}

echo "=== Téléchargement des extensions VS Code ==="
echo "Proxy : ${PROXY:-aucun}"
echo "Dossier de sortie : ${OUTDIR}/"
echo ""

# ── Python ────────────────────────────────────────────────────────────────────
download_vsix "ms-python.python"
download_vsix "ms-python.debugpy"
download_vsix "charliermarsh.ruff"
download_vsix "donjayamanne.python-environment-manager"

# ── Formats de données ────────────────────────────────────────────────────────
download_vsix "tamasfe.even-better-toml"      # TOML — référence absolue
download_vsix "ZainChen.json"                  # JSON — validation + schéma
download_vsix "redhat.vscode-yaml"             # YAML — Red Hat
download_vsix "mechatroner.rainbow-csv"        # CSV Rainbow

# ── Interface ─────────────────────────────────────────────────────────────────
download_vsix "PKief.material-icon-theme"      # Icônes fichiers/dossiers
download_vsix "PKief.material-product-icons"   # Icônes UI VS Code
download_vsix "Catppuccin.catppuccin-vsc"      # Thème Catppuccin (Latte, Frappé, Macchiato, Mocha)

# ── IA (GitHub Copilot — abonnement requis) ───────────────────────────────────
download_vsix "GitHub.copilot"                 # Copilot — complétion de code IA inline
download_vsix "GitHub.copilot-chat"            # Copilot Chat — assistant IA conversationnel

# ── Documentation ─────────────────────────────────────────────────────────────
download_vsix "yzhang.markdown-all-in-one"     # Markdown All in One

# ── IBM ADFz Extension Pack ───────────────────────────────────────────────────
# Le pack IBM.application-delivery-foundation-for-zos-vscode-extension-pack est
# une meta-extension (package.json uniquement, pas de code). Pour une installation
# .vsix hors-ligne (Dockerfile), chaque extension membre doit être téléchargée
# individuellement ci-dessous.
# Licence IBM requise à l'exécution pour : zopendebug, compiledcodecoverage,
# zfilemanager, zfaultanalyzer, apa-extension.
download_vsix "IBM.zopeneditor"              # Z Open Editor  — COBOL, PL/I, JCL, HLASM, REXX
download_vsix "IBM.zopendebug"              # Z Open Debug   — DAP client pour IBM z/OS Debugger
download_vsix "IBM.compiledcodecoverage"    # Compiled Code Coverage
download_vsix "Zowe.vscode-extension-for-zowe"   # Zowe Explorer  — datasets, USS, JES
download_vsix "Zowe.cics-extension-for-zowe"     # Zowe CICS Explorer
download_vsix "IBM.zfilemanager"            # File Manager for z/OS
download_vsix "IBM.zfaultanalyzer"          # Fault Analyzer for z/OS
download_vsix "IBM.apa-extension"           # Application Performance Analyzer for z/OS
download_vsix "IBM.db2forzosdeveloperextension"  # IBM Db2 for z/OS Developer Extension
