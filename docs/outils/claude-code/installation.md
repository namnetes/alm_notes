# Installation & Authentification

---

## Les deux modes de facturation

Anthropic propose deux modèles de facturation totalement distincts.
Il faut les distinguer avant toute configuration.

| Mode | Adapté à | Facturation | Authentification |
|------|----------|-------------|-----------------|
| **Abonnement Claude Pro / Max** | Usage régulier, prix fixe | Forfait mensuel | OAuth via `/login` |
| **API Console** | Scripts, automatisation, CI | À l'usage (par jeton) | Clé API `sk-ant-…` |

!!! info "Choix par défaut"
    Pour un usage interactif quotidien dans le terminal et Zed,
    l'**abonnement Pro ou Max** est généralement le plus économique.
    L'**API** reste utile pour les scripts ou pour un budget de jetons indépendant.

### Souscription Claude Pro

1. Se rendre sur [claude.com/pricing](https://claude.com/pricing)
2. Choisir **Pro** (offre individuelle) ou **Max** (limites élargies)
3. L'abonnement Pro/Max **inclut l'accès à Claude Code** — l'offre gratuite ne le permet pas

---

## Installation sur Ubuntu

La méthode recommandée est **l'installateur natif** — le binaire se met à jour
automatiquement en arrière-plan.

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Le binaire est placé dans `~/.local/bin/claude`. Vérifier que ce répertoire
est dans le `PATH`, puis contrôler l'installation :

```bash
claude --version
claude doctor
```

!!! info "État sur cette machine (juillet 2026)"
    - Version installée : **2.1.201**, via l'installateur natif
      (`installMethod: native` dans `~/.claude.json`).
    - `~/.local/bin/claude` est un **symlink** vers le binaire versionné
      `~/.local/share/claude/versions/<version>`.
    - Mises à jour automatiques désactivées ici (`autoUpdates: false` dans
      `~/.claude.json`) — mise à jour manuelle : `claude update`.
    - Authentification active : **abonnement Claude Pro** (OAuth), mode `sub`
      mémorisé dans `~/.config/claude/mode` (voir `claude-switch` plus bas).

??? details "Autres méthodes d'installation"
    **Dépôt APT signé (pas de mise à jour automatique) :**

    ```bash
    sudo install -d -m 0755 /etc/apt/keyrings
    sudo curl -fsSL https://downloads.claude.ai/keys/claude-code.asc \
      -o /etc/apt/keyrings/claude-code.asc
    echo "deb [signed-by=/etc/apt/keyrings/claude-code.asc] \
      https://downloads.claude.ai/claude-code/apt/stable stable main" \
      | sudo tee /etc/apt/sources.list.d/claude-code.list
    sudo apt update && sudo apt install claude-code
    ```

    **npm (nécessite Node.js 18+) :**

    ```bash
    npm install -g @anthropic-ai/claude-code
    ```

    Ne **jamais** utiliser `sudo npm install -g`.

---

## Authentification

### Abonnement Pro/Max

```bash
claude
```

Au premier démarrage, Claude Code ouvre le navigateur. Choisir
**Claude.ai (Pro/Max subscription)** et valider. Les jetons OAuth sont
enregistrés dans `~/.claude/.credentials.json` (permissions `0600`).

### Clé API Anthropic

1. Créer une clé sur [console.anthropic.com](https://console.anthropic.com) → *API Keys*
2. L'exporter avant de lancer Claude Code :

```bash
export ANTHROPIC_API_KEY="sk-ant-…"
claude
```

Au premier lancement avec une clé en environnement, Claude Code demande une
approbation interactive — la décision est mémorisée.

### Commandes utiles

Deux familles de commandes coexistent : des **sous-commandes CLI** (tapées
directement dans le shell, hors session) et des **commandes slash** (tapées
*à l'intérieur* d'une session `claude` déjà lancée).

```bash
# Depuis le shell (hors session)
claude auth login     # (re)connexion — options --email, --sso, --console
claude auth logout    # déconnexion
claude auth status    # statut d'authentification en JSON (--text pour du lisible)
```

```text
# Depuis une session claude déjà lancée
/login    # (re)connexion ou changement de compte
/logout   # déconnexion
/status   # compte et mode d'authentification actifs
/config   # menu de configuration (modèle, canal de mise à jour…)
```

!!! note "`claude /login` fonctionne aussi, mais n'est pas la forme documentée"
    `claude "texte"` démarre une session interactive avec ce texte comme
    premier message ; `claude /login` fonctionne donc dans la pratique en
    passant `/login` comme prompt initial. La documentation officielle
    recommande toutefois `claude auth login` pour un usage scriptable
    (CI, alias, vérifications automatisées) — c'est ce que `claude-switch`
    ci-dessous devrait utiliser pour un contrôle fiable et non interactif.

### Précédence des authentifications

!!! warning "Ordre d'évaluation"
    Si plusieurs méthodes sont présentes, Claude Code les évalue dans cet ordre :

    1. Identifiants cloud (Bedrock, Vertex, Foundry)
    2. `ANTHROPIC_AUTH_TOKEN` (proxies)
    3. **`ANTHROPIC_API_KEY`** — prend le pas sur l'abonnement après approbation
    4. Script `apiKeyHelper`
    5. `CLAUDE_CODE_OAUTH_TOKEN` (CI)
    6. Identifiants OAuth de l'abonnement (`/login`)

    Tant que `ANTHROPIC_API_KEY` est définie et approuvée, c'est elle qui est
    facturée — **pas l'abonnement**.

---

## Basculer entre abonnement et clé API

### Méthode manuelle

```bash
# Utiliser l'abonnement Pro/Max
unset ANTHROPIC_API_KEY
claude

# Utiliser la clé API
export ANTHROPIC_API_KEY="sk-ant-…"
claude
```

### Script `claude-switch`

Mémorise le mode actif et lance Claude Code avec la bonne authentification.

!!! info "Déjà déployé via alm_dots"
    Le script vit dans `alm_dots/.functions/bin/claude-switch` (versionné,
    stowé vers `~/.functions/bin/claude-switch`) ; `~/.bash_env` recrée
    automatiquement le lien `~/.local/bin/claude-switch` à chaque démarrage de
    shell — voir [Assistant terminal](terminal.md#fichiers-deployes). Le bloc
    ci-dessous reste la référence pour comprendre ou reproduire le mécanisme
    ailleurs.

Créer `~/.local/bin/claude-switch` (ou, comme ici, un script versionné
symlinké vers cet emplacement) :

```bash
#!/usr/bin/env bash
# Bascule entre abonnement Pro/Max et clé API.
# Usage : claude-switch [sub|api]

set -euo pipefail

API_ENV_FILE="${HOME}/.config/claude/api.env"
STATE_FILE="${HOME}/.config/claude/mode"
mkdir -p "$(dirname "${STATE_FILE}")"

mode="${1:-}"

case "${mode}" in
  sub|subscription)
    shift   # sinon "sub"/"api" est repassé à claude comme prompt initial
    echo "sub" > "${STATE_FILE}"
    echo "Mode : abonnement Pro/Max."
    ;;
  api)
    shift
    [[ -f "${API_ENV_FILE}" ]] || {
      echo "Erreur : ${API_ENV_FILE} introuvable." >&2
      echo "Créer ce fichier avec : ANTHROPIC_API_KEY=sk-ant-…" >&2
      exit 1
    }
    echo "api" > "${STATE_FILE}"
    echo "Mode : clé API Console."
    ;;
  "") : ;;
  *) echo "Usage : claude-switch [sub|api]" >&2; exit 2 ;;
esac

current="$(cat "${STATE_FILE}" 2>/dev/null || echo sub)"

if [[ "${current}" == "api" ]]; then
  set -a; source "${API_ENV_FILE}"; set +a
  echo "→ Lancement avec la clé API."
else
  unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN
  echo "→ Lancement avec l'abonnement."
fi

exec claude "$@"
```

```bash
chmod +x ~/.local/bin/claude-switch

mkdir -p ~/.config/claude
cat > ~/.config/claude/api.env <<'EOF'
ANTHROPIC_API_KEY=sk-ant-VOTRE_CLE_ICI
EOF
chmod 600 ~/.config/claude/api.env
```

```bash
claude-switch sub   # bascule en mode abonnement et lance claude
claude-switch api   # bascule en mode API et lance claude
claude-switch       # relance avec le dernier mode mémorisé
```

!!! note "Pourquoi un fichier `.env` séparé ?"
    Stocker la clé en mode `0600` évite de l'exporter dans `.bashrc` pour
    tous les processus. Le script ne la charge qu'au moment d'exécuter `claude`.

---

## Tableau des fichiers et variables

| Élément | Emplacement |
|---------|-------------|
| Binaire | `~/.local/bin/claude` → symlink vers `~/.local/share/claude/versions/<version>` |
| Identifiants OAuth | `~/.claude/.credentials.json` (mode `0600`) |
| Configuration utilisateur | `~/.claude.json`, `~/.claude/` |
| Variable clé API | `ANTHROPIC_API_KEY` |
| Variable token OAuth (CI) | `CLAUDE_CODE_OAUTH_TOKEN` |
| Script de bascule | `~/.local/bin/claude-switch` |
| Fichier clé API | `~/.config/claude/api.env` (mode `0600`) |
| Mode actif mémorisé | `~/.config/claude/mode` (`sub` ou `api`) |
