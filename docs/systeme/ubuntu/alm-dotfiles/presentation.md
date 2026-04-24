# Présentation

`alm-dotfiles` est un dépôt personnel qui centralise tous les fichiers de configuration (dotfiles) de l'environnement de travail. Grâce à [GNU Stow](https://www.gnu.org/software/stow/), chaque fichier est déployé via un lien symbolique dans le répertoire personnel (`~`). La structure du dépôt reflète exactement celle de `~`.

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
| `.local/share/applications/` | `~/.local/share/applications/` | Raccourcis bureau |

---

## Fichiers exclus de Stow

Le fichier `.stow-local-ignore` exclut du déploiement les éléments suivants :

```
.git
.gitconfig
.gitignore
CLAUDE.md
.claudecodeignore
.editorconfig
.github
system-config
README.md
```

!!! warning "`.gitconfig` non déployé"
    `.gitconfig` est exclu car il contient des données personnelles (email, clé GPG). Il doit être configuré manuellement après le déploiement — voir [Installation](installation.md).
