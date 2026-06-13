# Outils et applications

Cette page détaille la configuration de chaque application déployée par
`alm_dots` : l'invite de commandes, le terminal, le gestionnaire de fichiers,
l'éditeur, Git et Claude Code. Chaque section indique le fichier source
versionné et son emplacement cible dans `~`.

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

## Nano — `.nanorc`

Configuration de l'éditeur Nano déployée via Stow :

| Option | Effet |
|--------|-------|
| `tabstospaces` | Convertit les tabulations en espaces |
| `tabsize 2` | Indentation à 2 espaces |
| `autoindent` | Indentation automatique à la nouvelle ligne |
| `linenumbers` | Numérotation des lignes |
| `softwrap` | Retour à la ligne automatique |
| `smarthome` | La touche `Début` va en premier caractère non-blanc |
| `casesensitive` | Recherche sensible à la casse |
| `matchbrackets` | Surlignage de la parenthèse correspondante |

Nano reste disponible comme éditeur de secours lorsque Zed n'est pas installé.

---

## SSH — `.ssh/config`

Alias SSH pour le serveur SFTP local (`coruscant`) :

```
Host sftpserver
  HostName coruscant.local
  Port 2222
  User sftpuser
```

`coruscant.local` est résolu par mDNS (Avahi) sur le réseau local — l'IP peut changer (DHCP), le nom reste stable.

Connexion : `ssh sftpserver` ou `sftp sftpserver`

---

## Git — `.gitconfig`

!!! info "Fichier stowé"
    `.gitconfig` est déployé par Stow comme tous les autres dotfiles. La configuration Git (nom, email, alias) est restaurée automatiquement à la réinstallation.

Options clés :

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

Le script `change_wallpaper.sh` sélectionne aléatoirement une image dans `~/.config/my_ubuntu/wallpapers/` et l'applique via `gsettings`. La planification horaire est gérée par le service systemd `change-wallpaper.timer`, déployé automatiquement via Stow.

**Formats supportés :** `.jpg`, `.png`, `.webp`

---

## Claude Code — `.config/claude/` et `.claude/`

Trois niveaux de configuration pour Claude Code :

| Fichier | Emplacement cible | Rôle |
|---------|------------------|------|
| `global_rules.md` | `~/.config/claude/global_rules.md` → `~/.clauderc` | Règles globales (Mermaid, écriture, git) — actives sur tous les projets |
| `CLAUDE.md` (racine) | `~/CLAUDE.md` | Standards de dev : Python, Shell, MkDocs, pioinit, devinit |
| `CLAUDE_Mainframe.md` | `~/.claude/CLAUDE_Mainframe.md` | Standards IBM z/OS : COBOL 6.5, JCL, Db2, CICS — chargé dans les projets mainframe |

### Initialiser Claude Code dans un nouveau projet

Deux alias créent le `CLAUDE.md` adapté au type de projet :

```bash
# Projet Python / développement open
claude-open   # copie CLAUDE_Open.md → ./CLAUDE.md

# Projet IBM Mainframe (COBOL, JCL)
claude-z      # copie CLAUDE_Mainframe.md → ./CLAUDE.md
```

Les mêmes actions sont disponibles dans Zed via les tâches :
**"Claude: Init Open project"** et **"Claude: Init Mainframe project"**.
