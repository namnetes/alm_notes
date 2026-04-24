# Environnement shell

---

## Point d'entrée : `.bash_env`

Tous les outils du shell sont initialisés dans `~/.bash_env`. Ce fichier est sourcé au démarrage de Bash et configure les outils dans l'ordre suivant :

| Ordre | Outil | Rôle |
|-------|-------|------|
| 1 | **Starship** | Invite de commandes visuelle avec icônes Nerd Font |
| 2 | **Éditeur par défaut** | Zed (avec fallback Nano) |
| 3 | **Jupyter** | Environnement sandbox `~/Workspace/sandbox` |
| 4 | **fnm** | Gestionnaire de versions Node.js avec auto-switch par répertoire |
| 5 | **bat / batcat** | Remplacement de `cat` avec coloration syntaxique |
| 6 | **FZF** | Recherche floue avec raccourcis clavier |
| 7 | **ripgrep** | Recherche rapide — alias : `rg`, `rgf`, `rgv`, `rgdot`, `rgc`, `rgt`, `rgx`, `rggit` |
| 8 | **zoxide** | Remplacement intelligent de `cd` (mémorise les répertoires fréquents) |
| 9 | **eza** | Remplacement de `ls` avec informations Git intégrées |
| 10 | **uv** | Gestionnaire de paquets Python |
| 11 | **SDKMAN** | Gestionnaire de versions Java/Groovy |
| 12 | **Alias Git** | Chargés dynamiquement depuis `.gitconfig` |
| 13 | **PATH** | Déduplication — `~/.local/bin` en priorité |
| 14 | **Fond d'écran** | Lance `change_wallpaper.sh` en arrière-plan au démarrage |

---

## Alias shell — `.bash_aliases`

Plus de 100 alias définis. Exemples représentatifs :

```bash
alias ll='eza -l --git --icons --group-directories-first'
alias la='eza -la --git --icons --group-directories-first'
alias lt='eza --tree --level=2 --icons'
alias cat='bat --pager=never'
alias grep='rg'
alias cd='z'            # zoxide
alias update='update_system.sh'
```

---

## Fonctions shell — `.bash_functions`

Plus de 20 fonctions personnalisées. Le script `list_functions.sh` ouvre un sélecteur FZF interactif sur toutes les fonctions disponibles.

---

## Configuration FZF — `.fzfrc`

| Paramètre | Valeur |
|-----------|--------|
| Hauteur | 45 % |
| Disposition | Inversée (en bas de l'écran) |
| Sélection multiple | Activée |
| Navigation cyclique | Activée |
| Prévisualisation | `bat` à droite, largeur 60 % |
| Raccourci bas | `Ctrl+J` |
| Raccourci haut | `Ctrl+K` |

---

## Alias Git dynamiques — `.functions/lib/git_aliases.sh`

Au démarrage, `git_aliases.sh` lit la section `[alias]` de `.gitconfig` et crée des alias Bash équivalents :

| Alias Bash | Commande Git |
|-----------|-------------|
| `st` | `git status` |
| `co` | `git checkout` |
| `ci` | `git commit` |
| `d` | `git diff` |
| `lg` | `git log --oneline --graph --decorate` |
| `gl10` | `git log -10 --oneline` |
| `gcleanup` | Supprime les branches locales déjà mergées |

---

## Nettoyage du PATH — `.functions/lib/clean_path.sh`

Supprime les entrées dupliquées dans `$PATH` et place `~/.local/bin` et `/snap/bin` en tête.
