# Configuration

Claude Code charge des **instructions contextuelles** depuis des fichiers
`CLAUDE.md` selon une hiérarchie précise, et gère les **permissions** par
projet via `settings.local.json`.

---

## Hiérarchie des CLAUDE.md

Claude Code charge les fichiers `CLAUDE.md` de façon additive (ils se
concatènent, aucun n'écrase l'autre) — du plus général au plus spécifique :

| Portée | Emplacement | Chargement |
|---|---|---|
| Politique managée (entreprise) | `/etc/claude-code/CLAUDE.md` (Linux/WSL) | Toujours chargé en premier — non désactivable |
| Utilisateur | `~/.claude/CLAUDE.md` | Toujours chargé, tous les projets |
| Projet | `<projet>/CLAUDE.md` **ou** `<projet>/.claude/CLAUDE.md` | Si le CWD est dans ce projet |
| Local (perso, non versionné) | `<projet>/CLAUDE.local.md` | Idem, à ajouter au `.gitignore` |

Claude Code remonte l'arborescence depuis le répertoire courant : lancé dans
`foo/bar/`, il charge `foo/bar/CLAUDE.md` **et** `foo/CLAUDE.md` (le plus
proche du CWD est lu en dernier, donc prioritaire en cas d'instructions
contradictoires). Les `CLAUDE.md` situés dans des **sous-répertoires** du CWD
ne sont chargés qu'à la demande, quand Claude lit un fichier de ce
sous-répertoire — pas au démarrage.

!!! info "`.claude/CLAUDE.md` dans un projet est bien chargé"
    Les deux emplacements `<projet>/CLAUDE.md` et `<projet>/.claude/CLAUDE.md`
    sont **équivalents** et documentés comme tels par Anthropic. (Correction :
    une version précédente de cette page affirmait le contraire — vérifié en
    juillet 2026 contre la documentation officielle.)

!!! tip "Nouveau depuis 2026 : `.claude/rules/` et la mémoire automatique"
    - **`.claude/rules/*.md`** découpe un `CLAUDE.md` trop long en fichiers
      thématiques, éventuellement **scopés par chemin** (frontmatter
      `paths: ["src/api/**/*.ts"]`) — chargés seulement quand Claude touche
      un fichier correspondant.
    - **Mémoire automatique** (`~/.claude/projects/<projet>/memory/`,
      fichier `MEMORY.md` + notes thématiques) : Claude y consigne lui-même
      ce qu'il apprend de vos corrections, sans intervention manuelle.
      Activée par défaut depuis la v2.1.59 ; se gère via `/memory`.
    - Taille recommandée d'un `CLAUDE.md` : **moins de 200 lignes** — au-delà,
      l'adhérence aux instructions diminue.

---

## Le fichier `AGENTS.md`

`AGENTS.md` est un **format ouvert et standardisé** (voir
[agents.md](https://agents.md)) : un fichier Markdown placé à la racine d'un
dépôt qui donne aux agents de code IA les instructions techniques du projet —
commandes de build et de test, conventions de code, structure, règles de
commit. C'est en quelque sorte un « README pour les agents », qui garde le
`README.md` centré sur les humains.

Son intérêt : **un seul fichier** lu par de nombreux outils (Claude, Codex,
Cursor, GitHub Copilot, Aider, Devin…) au lieu d'un fichier propriétaire par
outil (`CLAUDE.md`, `.cursorrules`, `.github/copilot-instructions.md`…).

### Sections typiques d'un `AGENTS.md`

```markdown
# AGENTS.md

## Setup / Build
Commandes pour installer les dépendances et compiler.

## Tests
Comment lancer les tests, et lesquels lancer avant un commit.

## Conventions de code
Style, nommage, formatage.

## Commits / PR
Format des messages de commit, règles de revue.
```

Dans un monorepo, on peut placer un `AGENTS.md` par sous-projet : l'agent lit
**le plus proche** dans l'arborescence.

!!! warning "Claude Code lit `CLAUDE.md`, pas `AGENTS.md`"
    Claude Code ne lit **pas** `AGENTS.md` directement. Si votre dépôt en
    possède déjà un (pour d'autres agents), créez un `CLAUDE.md` qui
    **l'importe** afin que les deux outils partagent les mêmes instructions
    sans duplication :

    ```markdown
    @AGENTS.md

    ## Claude Code
    Instructions spécifiques à Claude ajoutées sous l'import.
    ```

    Un lien symbolique fonctionne aussi si aucun ajout Claude n'est nécessaire :

    ```bash
    ln -s AGENTS.md CLAUDE.md
    ```

    Sous Windows, le symlink exige les droits administrateur — préférez alors
    l'import `@AGENTS.md`.

!!! tip "`/init` récupère un `AGENTS.md` existant"
    Lancé dans un dépôt qui contient déjà un `AGENTS.md`, la commande `/init`
    le lit et intègre les parties pertinentes dans le `CLAUDE.md` généré (elle
    lit aussi `.cursorrules`, `.devin/rules/` et `.windsurfrules`).

---

## Architecture avec alm_dots (GNU Stow)

Les fichiers CLAUDE.md sont **versionnés dans `alm_dots`** et déployés via
GNU Stow :

```
alm_dots/.claude/CLAUDE.md  ──stow──►  ~/.claude/CLAUDE.md   (GLOBAL)
alm_dots/CLAUDE.md               ──►  ~/alm_dots/CLAUDE.md   (PROJET)
```

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff"}}}%%
flowchart LR
    classDef startStop fill:#e1f5fe,stroke:#01579b,color:#000
    classDef logic     fill:#e8eaf6,stroke:#1a237e,color:#000
    classDef data      fill:#fff3e0,stroke:#e65100,color:#000

    subgraph alm_dots["~/alm_dots (versionné Git)"]
        SRC_G[/.claude/CLAUDE.md\nStandards globaux/]:::data
        SRC_P[/CLAUDE.md\nGuide alm_dots/]:::data
    end

    subgraph home["$HOME"]
        GLOBAL["~/.claude/CLAUDE.md\nToujours chargé"]:::logic
        PROJ["~/alm_dots/CLAUDE.md\nChargé dans alm_dots"]:::logic
        OTHER["~/alm_tools/CLAUDE.md\n~/alm_notes/CLAUDE.md\n…"]:::logic
    end

    SRC_G -->|stow .| GLOBAL
    SRC_P -->|non stowé| PROJ

    CC([Claude Code]):::startStop
    CC -->|charge| GLOBAL
    CC -->|"CWD dans alm_dots"| PROJ
    CC -->|"CWD dans le projet"| OTHER

    subgraph Legend["Légende"]
        direction LR
        L1([Acteur]):::startStop
        L2[Fichier actif]:::logic
        L3[/Source versionnée/]:::data
    end
```

**Contenu de `~/.claude/CLAUDE.md` (global)** : langue (français), standards
Python/Shell/MkDocs, conventions de nommage, initialisation projets, palette
Mermaid.

**Contenu de `~/alm_dots/CLAUDE.md` (projet)** : objectif du dépôt (GNU Stow,
Ubuntu 20.04), contraintes de compatibilité, structure et patterns clés.

---

## Déploiement du CLAUDE.md global via Stow

Le fichier `~/.claude/CLAUDE.md` est un **symlink stow**, pas un fichier
éditable directement.

### Prérequis — `~/.claude/` doit exister avant de stower

Si `~/.claude/` n'existe pas, Stow crée un **symlink sur le dossier entier**
(`~/.claude/ → alm_dots/.claude/`), ce qui écraserait `.credentials.json`
et `settings.local.json`.

Claude Code crée `~/.claude/` au premier lancement. Sur une machine fraîche :

```bash
mkdir -p ~/.claude
stow .
```

!!! danger "Le même piège existe pour `~/.config/claude/`"
    `~/.config/claude/` mélange lui aussi un fichier versionné
    (`global_rules.md`) et des fichiers machine (`api.env` — la clé API,
    `mode` — voir [Installation & Authentification](installation.md#basculer-entre-abonnement-et-cle-api)).
    Si `~/.config/claude/` n'existe pas avant `stow .`, Stow le symlinke en
    entier vers `alm_dots/.config/claude/` — tout `api.env` créé *après coup*
    atterrit alors **physiquement dans le dépôt git**, clé en clair incluse.
    Incident réel rencontré et corrigé en juillet 2026 sur ce dépôt (le
    fichier n'avait heureusement jamais été commité). Prémunition :

    ```bash
    mkdir -p ~/.claude ~/.config/claude
    stow .
    ```

    Si le dossier existe déjà comme symlink de dossier entier (vérifier avec
    `ls -la ~/.config/claude` — absence de flèche `->` sur les fichiers
    individuels), le corriger :

    ```bash
    rm ~/.config/claude                # supprime uniquement le lien
    mkdir -p ~/.config/claude
    mv ~/alm_dots/.config/claude/{api.env,mode} ~/.config/claude/ 2>/dev/null
    cd ~/alm_dots && stow --restow .   # relie individuellement les fichiers versionnés
    ```

### Workflow de mise à jour

```bash
# 1. Éditer la source dans alm_dots
zed ~/alm_dots/.claude/CLAUDE.md

# 2. Le symlink est immédiatement actif — pas besoin de re-stower

# 3. Committer
cd ~/alm_dots
git add .claude/CLAUDE.md
git commit -m "docs: update global Claude Code instructions"
```

### Vérifier les symlinks

```bash
ls -la ~/.claude/CLAUDE.md
# ~/.claude/CLAUDE.md -> ../alm_dots/.claude/CLAUDE.md  ✓
```

Si `~/CLAUDE.md` existe (ancien symlink de l'architecture précédente) :

```bash
rm ~/CLAUDE.md
```

---

## CLAUDE.md par projet

Chaque dépôt dispose de son propre `CLAUDE.md` à la racine. Les standards
globaux sont automatiquement hérités — ne pas les répéter.

**Initialiser rapidement avec les alias `alm_dots` :**

```bash
claude-open   # copie CLAUDE_Open.md comme CLAUDE.md dans le projet courant
claude-z      # copie CLAUDE_Mainframe.md (contexte IBM z/OS)
```

**Structure minimale d'un `CLAUDE.md` projet :**

```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working
with code in this repository.

## Project

Description courte du projet et de son contexte.

## Commands

\`\`\`bash
make install   # installer les dépendances
make test      # lancer les tests
make lint      # linter
\`\`\`

## Architecture

Points non-évidents sur la structure ou les patterns du projet.
```

---

## Réglages globaux — `~/.claude/settings.json`

Fichier de réglages qui s'applique à **tous les projets**. Contenu actuel sur
cette machine (juillet 2026) :

```json
{
  "permissions": {
    "allow": [
      "Write",
      "Edit"
    ]
  },
  "skipDangerousModePermissionPrompt": true,
  "model": "claude-fable-5[1m]"
}
```

- **`model`** — modèle par défaut de toute session. Ici **Claude Fable 5**
  (famille Claude 5, tier Mythos, sortie 2026) ; le suffixe **`[1m]`** active
  la fenêtre de contexte étendue à **1 million de jetons**. Se change aussi en
  session via `/model`.
- **`permissions.allow`** — `Write` et `Edit` pré-autorisés partout : Claude
  édite les fichiers sans confirmation. Le reste (Bash, WebFetch…) est géré
  projet par projet via `settings.local.json` (section suivante).
- **`skipDangerousModePermissionPrompt`** — supprime la confirmation
  interactive à l'activation du mode `--dangerously-skip-permissions`.

!!! note "Fable 5 réfléchit toujours"
    Fable 5 utilise en permanence la réflexion étendue (*extended thinking*) —
    le raccourci ++alt+t++ (bascule de la réflexion) est sans effet sur ce
    modèle. Voir [Raccourcis clavier](raccourcis-windows-linux.md).

---

## Permissions locales — `settings.local.json`

**Emplacement :** `<projet>/.claude/settings.local.json`

Pré-autorise des outils et commandes spécifiques au projet, évitant les
prompts de confirmation répétitifs.

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(make *)",
      "Read(/home/galan/**)",
      "WebSearch"
    ]
  }
}
```

- Portée **locale uniquement** — ne s'applique qu'au projet courant
- Géré via le skill `/fewer-permission-prompts` ou manuellement
- **Ne pas stower** : contient des données spécifiques à la machine
- Complète (sans remplacer) `~/.claude/settings.json`

---

## Résumé de la hiérarchie

```
~/.claude/CLAUDE.md                    ← instructions globales (stowé)
~/.claude/settings.json                ← réglages globaux (modèle, permissions)
    +
<projet>/CLAUDE.md                     ← instructions projet
<projet>/.claude/settings.local.json   ← permissions projet
```

---

## Bonnes pratiques

- Ne jamais committer `ANTHROPIC_API_KEY` dans Git — même dans un dépôt privé
- Vérifier régulièrement le mode actif : `claude /status`
- Préférer la saisie de clé via l'**UI Zed** (trousseau système) plutôt que
  `api_key` en clair dans `settings.json`
- Canal `stable` (`autoUpdatesChannel: "stable"`) recommandé en environnement professionnel
