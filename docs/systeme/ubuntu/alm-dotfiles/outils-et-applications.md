# Outils et applications

---

## Starship — `.config/starship.toml`

Invite de commandes multilingue avec 200 lignes de configuration :

- Symboles Nerd Font Unicode
- Intégration Git (branche, état, stash)
- Indicateur de répertoire en lecture seule
- Troncature du chemin à 8 niveaux maximum
- Timeout de scan : 120 ms

---

## Terminal Kitty — `.config/kitty/`

| Fichier | Rôle |
|---------|------|
| `kitty.conf` | Configuration principale (police, couleurs, marges) |
| `current-theme.conf` | Thème de couleurs actif |
| `kittens/ssh` | Configuration SSH pour les VMs Alpine Linux |

---

## Gestionnaire de fichiers Yazi — `.config/yazi/`

| Fichier | Rôle |
|---------|------|
| `yazi.toml` | Configuration principale |
| `keymap.toml` | Raccourcis clavier personnalisés |
| `init.lua` | Initialisation des plugins Lua |

| Paramètre | Valeur |
|-----------|--------|
| Ratio d'affichage | 1 : 3 : 4 (barre latérale / principal / prévisualisation) |
| Tri | Naturel, insensible à la casse, répertoires en premier |
| Ouverture par défaut | Zed |
| Archives | `ouch` ou `unar` |

**Plugins activés :** `git`, `full-border`, `smart-filter`, `jump-to-char`, `max-preview`, `starship`, `diff`, `chmod`

---

## Éditeur Zed — `.config/zed/`

| Fichier | Rôle |
|---------|------|
| `settings.json` | 233 lignes de configuration |
| `keymap.json` | Raccourcis clavier |
| `tasks.json` | Tâches de build et d'exécution |

**Modèles IA :** Claude Sonnet 4.6 (défaut), Claude Haiku (résumés/commits).

**Police :** FiraCode Nerd Font. **Thèmes :** Catppuccin Macchiato (sombre) / One Light (clair).

### Raccourcis clés

| Raccourci | Action |
|-----------|--------|
| `Alt+Shift+G` | Ouvrir/fermer le panneau Git |
| `Alt+Shift+F` | Ouvrir/fermer le panneau projet |
| `Alt+Shift+O` | Ouvrir/fermer le plan du fichier |
| `F5` | Exécuter le fichier Python |
| `Shift+F5` | Déboguer avec pdb |
| `F8` | Ruff fix & lint |
| `Alt+Entrée` | Lancer une tâche |

**Formateurs :** Ruff (Python, 88 car.), shfmt (Shell, 80 car.). **LSP :** ruff, pyright, yaml-language-server.

---

## Git — `.gitconfig`

!!! warning "Fichier exclu de Stow"
    `.gitconfig` contient des données personnelles (email, clé GPG). Il est exclu de Stow et doit être configuré manuellement — voir [Installation](installation.md).

Options clés à reproduire depuis le dépôt :

| Option | Valeur | Effet |
|--------|--------|-------|
| `core.editor` | `zed --wait` | Ouvre Zed pour les messages de commit |
| `init.defaultBranch` | `main` | Branche par défaut |
| `push.autoSetupRemote` | `true` | Crée automatiquement la branche distante |
| `pull.rebase` | `false` | Fusion (pas de rebase) au pull |
| `fetch.prune` | `true` | Supprime les branches distantes supprimées |
| `diff.algorithm` | `histogram` | Algorithme de diff amélioré |
| `rebase.autosquash` | `true` | Applique automatiquement les `fixup!` |

---

## Fond d'écran automatique

Le script `change_wallpaper.sh` sélectionne aléatoirement une image dans `~/.config/my_ubuntu/wallpapers/` et l'applique via `gsettings`. Il installe automatiquement une tâche cron horaire au premier lancement.

**Formats supportés :** `.jpg`, `.png`, `.webp`

---

## Règles Claude Code — `.config/claude/global_rules.md`

Règles de style globales pour Claude Code : diagrammes Mermaid, écriture inclusive, commits au format Conventionnel.
