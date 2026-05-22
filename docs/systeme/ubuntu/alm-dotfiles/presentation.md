# Présentation

`alm_dots` est un dépôt personnel qui centralise tous les fichiers de configuration (dotfiles) de l'environnement de travail. Grâce à [GNU Stow](https://www.gnu.org/software/stow/), chaque fichier est déployé via un lien symbolique dans le répertoire personnel (`~`). La structure du dépôt reflète exactement celle de `~`.

---

## Avantages

| Propriété | Description |
|-----------|-------------|
| **Reproductibilité** | Un seul dépôt git pour reconfigurer un poste après une installation fraîche |
| **Versionnage** | L'historique git trace toutes les modifications de configuration |
| **Idempotence** | `stow .` peut être relancé sans risque |
| **Portabilité** | La structure du dépôt reflète exactement la structure de `~` |

---

## Fichiers et répertoires gérés

| Élément | Emplacement cible | Rôle |
|---------|------------------|------|
| `.bash_env` | `~/.bash_env` | Point d'entrée principal de l'environnement shell |
| `.bash_aliases` | `~/.bash_aliases` | Alias shell (100+ entrées) |
| `.bash_functions` | `~/.bash_functions` | Fonctions shell personnalisées |
| `.nanorc` | `~/.nanorc` | Configuration de Nano |
| `.fzfrc` | `~/.fzfrc` | Configuration de FZF |
| `.config/starship.toml` | `~/.config/starship.toml` | Invite de commandes Starship |
| `.config/kitty/` | `~/.config/kitty/` | Terminal Kitty (config + thème + SSH Alpine) |
| `.config/yazi/` | `~/.config/yazi/` | Gestionnaire de fichiers TUI Yazi |
| `.config/zed/` | `~/.config/zed/` | Éditeur Zed (settings, keymap, tasks) |
| `.config/claude/` | `~/.config/claude/` | Règles globales Claude Code |
| `.config/my_ubuntu/` | `~/.config/my_ubuntu/` | Fonds d'écran + raccourcis Ubuntu |
| `.config/systemd/` | `~/.config/systemd/` | Unités systemd utilisateur |
| `.functions/bin/` | `~/.functions/bin/` | Scripts exécutables dans le PATH |
| `.functions/lib/` | `~/.functions/lib/` | Librairies shell (sourcées au démarrage) |
| `.functions/tools/` | `~/.functions/tools/` | Utilitaires Python |
| `.gitconfig` | `~/.gitconfig` | Configuration Git (alias, éditeur, options) |
| `.claudecodeignore` | `~/.claudecodeignore` | Fichiers ignorés par Claude Code |
| `.ssh/config` | `~/.ssh/config` | Alias SSH pour le serveur SFTP local |
| `CLAUDE.md` | `~/CLAUDE.md` | Règles globales Claude Code (tous projets) |
| `.claude/` | `~/.claude/` | Templates CLAUDE.md + règles Claude |

---

## Fichiers exclus de Stow

Le fichier `.stow-local-ignore` exclut du déploiement les éléments suivants :

```
.git/
.gitignore
system-config/
settings.local.json
.github/
.editorconfig
README.md
```

!!! info "`.gitconfig` est stowé"
    Contrairement à ce que l'on pourrait croire, `.gitconfig` **est bien déployé par Stow** (`~/.gitconfig → alm_dots/.gitconfig`). La configuration Git (nom, email, alias) est donc restaurée automatiquement à la réinstallation.

!!! info "`settings.local.json` non stowé"
    Ce fichier contient les permissions accordées à Claude Code session par session. Il est exclu de Stow et n'est pas versionné — Claude Code le recrée automatiquement.
