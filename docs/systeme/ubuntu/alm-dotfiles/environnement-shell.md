# Environnement shell

---

## Point d'entrée : `.bash_env`

Tous les outils du shell sont initialisés dans `~/.bash_env`. Ce fichier est sourcé au démarrage de Bash et configure les outils dans l'ordre suivant :

| Ordre | Outil | Rôle |
|-------|-------|------|
| 1 | **Starship** | Invite de commandes visuelle avec icônes Nerd Font |
| 2 | **Éditeur par défaut** | Zed (avec fallback Nano) |
| 3 | **Jupyter** | Environnement sandbox `~/Workspaces/sandbox` |
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

Toutes les fonctions sont accessibles depuis n'importe quel répertoire. La commande `tl` (alias de `shims`) affiche l'inventaire complet des outils installés.

| Fonction | Appel | Description |
|----------|-------|-------------|
| `ve` | `ve` ou `ve chemin/` | Active le `.venv` du répertoire courant ou du chemin indiqué |
| `jl` | `jl` | Active le venv sandbox puis lance Jupyter Lab |
| `ipy` | `ipy` | Idem pour IPython |
| `fkill` | `fkill` | Sélectionne un processus via FZF et le termine |
| `path` | `path` | Affiche `$PATH` ligne par ligne, numéroté |
| `rule` | `rule` | Règle numérique alignée à la largeur du terminal (utile pour vérifier la longueur de ligne) |
| `dlvi` | `dlvi nginx redis` | Interroge Docker Hub pour la dernière version d'une ou plusieurs images |
| `gsp` | `gsp` | Statut Git de `alm_dots`, `alm_tools`, `alm_notes`, `alm_dashboard` en un coup d'œil |
| `renimg` | `renimg prefixe` | Renomme toutes les images du dossier courant en `prefixe_01.ext`, `prefixe_02.ext`… |
| `csvc` | `csvc fichier.csv` | Vérifie la cohérence du nombre de colonnes d'un fichier CSV |
| `finfo` | `finfo ~/.bash_functions` | Ouvre un sélecteur FZF sur les fonctions d'un script Bash |
| `show_ip` | `show_ip` ou `myip` | Affiche toutes les interfaces réseau avec leurs adresses IPv4/IPv6 |
| `kadm` | `kadm` | Interface TUI pour gérer les machines virtuelles KVM |
| `gpgtool` | `gpgtool` | Interface interactive pour chiffrer/déchiffrer des fichiers GPG |
| `usbboot` | `usbboot /dev/sdb` | Teste si une clé USB est bootable en la démarrant dans QEMU |
| `mkdocs-pdf` | `mkdocs-pdf chemin/page` | Exporte une page MkDocs en PDF via Brave (serveur MkDocs doit être actif) |
| `init_zed` | `init_zed` | Purge les extensions et la base de données Zed, restaure la config via `stow` |
| `shims` / `tl` | `tl` | Inventaire de tous les outils personnels installés avec statut ✓ / ✗ |
| `shim_add` | `shim_add alias cmd script proj desc` | Enregistre un nouvel outil dans le registre des shims |

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
