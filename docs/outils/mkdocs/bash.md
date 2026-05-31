# Script Bash & CI

## Cas d'usage typiques

Un script Bash pour MkDocs est utile pour :

- **Automatiser** la génération avant un déploiement.
- **Centraliser** les paramètres (répertoire de destination, URL de base…).
- **Intégrer** la documentation dans un pipeline CI/CD.
- **Contrôler** que les prérequis sont respectés avant de lancer la génération.

---

## Script de génération et déploiement local

```bash
#!/usr/bin/env bash
# =============================================================================
# build_docs.sh — Génère la documentation HTML du projet avec MkDocs.
#
# Usage :
#   bash build_docs.sh [--serve] [--strict] [--output DIR]
#
# Options :
#   --serve        Lance le serveur de développement (port 8000).
#   --strict       Traite les liens brisés comme des erreurs.
#   --output DIR   Répertoire de sortie (défaut : site/).
#
# Codes de sortie :
#   0  Succès
#   1  Prérequis manquant
#   2  Erreur de génération MkDocs
# =============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

SERVE=false
STRICT=false
OUTPUT_DIR="site"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

info()    { echo -e "${BLUE}[INFO]${RESET}  $*"; }
success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --serve)  SERVE=true;  shift ;;
        --strict) STRICT=true; shift ;;
        --output) OUTPUT_DIR="$2"; shift 2 ;;
        *)
            error "Option inconnue : $1"
            echo "Usage : $0 [--serve] [--strict] [--output DIR]"
            exit 1
            ;;
    esac
done

info "Vérification des prérequis..."
if ! command -v uv &>/dev/null; then
    error "uv introuvable. Installez-le avec :"
    error "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

cd "${PROJECT_ROOT}"

if [[ ! -f "mkdocs.yml" ]]; then
    error "mkdocs.yml introuvable dans : ${PROJECT_ROOT}"
    exit 1
fi

success "Prérequis validés"

info "Synchronisation de l'environnement Python..."
uv sync --quiet
success "Environnement synchronisé"

if [[ "${SERVE}" == "true" ]]; then
    info "Démarrage du serveur — http://127.0.0.1:8000"
    uv run mkdocs serve
    exit 0
fi

info "Génération de la documentation HTML..."
MKDOCS_ARGS=("build" "--site-dir" "${OUTPUT_DIR}")
[[ "${STRICT}" == "true" ]] && MKDOCS_ARGS+=("--strict")

if uv run mkdocs "${MKDOCS_ARGS[@]}"; then
    success "Documentation générée dans : ${PROJECT_ROOT}/${OUTPUT_DIR}"
    info "  xdg-open ${OUTPUT_DIR}/index.html"
else
    error "Échec de la génération MkDocs"
    exit 2
fi
```

### Utilisation

```bash
chmod +x script/build_docs.sh

bash script/build_docs.sh               # générer dans site/
bash script/build_docs.sh --serve       # serveur de développement
bash script/build_docs.sh --strict      # CI/CD — échoue si lien brisé
bash script/build_docs.sh --output /var/www/html/mon-projet
```

---

## Intégration GitHub Actions

```yaml
# .github/workflows/docs.yml
name: Documentation

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Installer uv
        uses: astral-sh/setup-uv@v4

      - name: Installer les dépendances
        run: uv sync

      - name: Générer la documentation (mode strict)
        run: uv run mkdocs build --strict

      - name: Déployer sur GitHub Pages
        if: github.ref == 'refs/heads/main'
        uses: peaceiris/actions-gh-pages@v4
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./site
```

!!! note "Alternative : `mkdocs gh-deploy`"
    MkDocs intègre une commande dédiée au déploiement sur GitHub Pages :
    ```bash
    uv run mkdocs gh-deploy
    ```
    Elle génère le site et le pousse automatiquement sur la branche `gh-pages`.

---

## Vérification des liens depuis un script

```bash
#!/usr/bin/env bash
# check_links.sh — Vérifie que tous les liens internes sont valides.
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

echo "Vérification des liens (mode strict)..."
if uv run mkdocs build --strict --quiet; then
    echo "✓ Aucun lien brisé détecté"
    exit 0
else
    echo "✗ Des liens brisés ont été détectés"
    exit 1
fi
```
