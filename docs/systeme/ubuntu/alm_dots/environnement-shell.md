# Environnement shell

??? info "Vocabulaire — termes récurrents dans la doc `alm_*`"
    Quelques mots reviennent souvent dans cette page et dans la documentation
    des dépôts `alm_dots` / `alm_tools`, sans toujours être définis sur place :

    | Terme | Signification |
    |-------|---------------|
    | **Shim** | Petit script "passe-plat" placé dans `~/.local/bin` (donc dans le `PATH`) qui pointe vers un outil ou projet réel ailleurs sur le disque — permet de lancer l'outil par un nom court depuis n'importe où. Voir la section [Registre des shims](#registre-des-shims-fonctionnement-et-ajout) plus bas |
    | **Idempotent** | Se dit d'une opération qui produit le même résultat qu'on l'exécute une ou plusieurs fois — la relancer ne casse rien et ne duplique rien. `stow .` ou `mkdocsinit` sont conçus pour être rejoués sans risque |
    | **Stow (GNU Stow)** | Outil qui déploie les fichiers d'un dépôt (ici `alm_dots`) vers `$HOME` via des liens symboliques, en reproduisant l'arborescence du dépôt dans `~`. Voir [Présentation d'alm_dots](presentation.md) |
    | **Best-effort** | Étape d'un script qui s'exécute "du mieux possible" : si elle échoue (outil absent, permission refusée…), un avertissement s'affiche mais le script continue plutôt que de s'arrêter en erreur |
    | **Wheel** | ⚠️ Deux sens distincts selon le contexte : un *wheel* Python est un paquet pré-compilé installé par `uv`/`pip` (le "rebuild du wheel" = recompiler le paquet après modification du code source) ; le groupe Linux `wheel` (mentionné dans la doc Alpine) est un groupe système autorisant `sudo` — sans rapport avec le précédent |

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

### Registre des shims — fonctionnement et ajout

`shims` (alias `tl`) et `shim_add` s'appuient sur un registre TSV séparé du
code, à `~/.local/share/alm_tools/shims.tsv` — une ligne par outil, au format
`alias|commande|script|projet|description`.

**`shims [filtre]`** croise ce registre avec le contenu de `~/.local/bin` et
affiche un tableau alias / commande / script / projet / statut :

- chaque entrée est marquée `✓ installé` si l'alias existe et est exécutable
  dans `~/.local/bin`, sinon `✗ manquant`
- un filtre optionnel restreint l'affichage aux lignes le contenant
- les **scripts orphelins** — exécutables détectés comme `text`/`script` par
  `file` dans `~/.local/bin` mais absents du registre — sont signalés en fin
  de sortie avec une suggestion `shim_add`. Les binaires compilés (ELF) sont
  ignorés par cette détection.

**`shim_add <alias> <commande> <script> <projet> <description>`** ajoute une
ligne au registre (création du répertoire si besoin) et refuse les doublons
d'alias déjà présents.

!!! info "État actuel (2026-06-07)"
    Le registre `~/.local/share/alm_tools/shims.tsv` n'existe pas encore —
    `tl` affiche "Aucun registre trouvé" et liste tous les scripts
    texte/script de `~/.local/bin` comme orphelins :

    | Script | Éligibilité à l'enregistrement |
    |--------|-------------------------------|
    | `wnp` | Artefact ancien (shim historique de `new-page.py`) — **à ne pas enregistrer**, voir le `CLAUDE.md` du dépôt `alm_notes` |
    | `vmforge` | Outil actif et documenté ([vmforge](../alm_tools/outils/vmforge.md)) — candidat légitime à `shim_add` |

    `uv`, `uvx`, `shai` et `mdbook` n'apparaissent pas comme orphelins : ce
    sont des binaires compilés (ELF), hors du périmètre de la détection.

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

### Raccourcis clavier FZF

`.bash_env` charge `key-bindings.bash` (fourni par le paquet `fzf`), qui
ajoute trois raccourcis globaux dans le shell — utilisables dans n'importe
quelle commande, pas seulement avec les alias `f*` ci-dessous :

| Raccourci | Effet |
|-----------|-------|
| `Ctrl+T` | Ouvre FZF et insère le(s) chemin(s) sélectionné(s) à la position du curseur |
| `Ctrl+R` | Recherche floue dans l'historique des commandes |
| `Alt+C` | Ouvre FZF sur les sous-répertoires et `cd` dans celui sélectionné |

### Alias FZF — `.bash_aliases`

| Alias | Commande | Description |
|-------|----------|-------------|
| `ff` | `fzf` | Lance FZF brut sur le répertoire courant |
| `fz` | `zed $(fzf)` | Sélectionne un fichier via FZF et l'ouvre dans Zed |
| `fn` | `nano $(fzf)` | Idem, ouverture dans Nano |
| `fh` | `history \| fzf` | Recherche floue dans l'historique (alternative à `Ctrl+R`) |
| `fcd` | `cd $(find . -type d \| fzf)` | Recherche un sous-répertoire et s'y déplace |
| `fs` | `rg --files \| fzf --preview '...'` | Recherche un fichier avec aperçu `bat` coloré |

---

## Alias Git dynamiques — `.functions/lib/git_aliases.sh`

Au démarrage, `git_aliases.sh` lit la section `[alias]` de `.gitconfig` et crée les alias Bash correspondants. Tous les alias commencent par `g` — taper `g` + `Tab` dans le terminal affiche l'ensemble des opérations disponibles.

!!! warning "Alias qui réécrivent l'historique ou perdent du travail"
    Certains alias ci-dessous ne sont pas de simples raccourcis de lecture —
    ils modifient l'historique ou suppriment des données locales. À ne pas
    taper par réflexe si vous débutez en Git :

    | Alias | Risque |
    |-------|--------|
    | `gbD` (`git branch -D`) | Supprime une branche **même si elle n'est pas mergée** — les commits qu'elle contenait deviennent orphelins et peuvent être perdus |
    | `gca` (`git commit --amend --no-edit`) | Remplace le dernier commit — dangereux s'il a déjà été poussé et partagé |
    | `grbi` (`git rebase -i`) | Réécrit l'historique des commits sélectionnés — peut créer des conflits ou perdre des modifications en cas de mauvaise manipulation |
    | `gundo` (`git reset --soft HEAD~1`) | Annule le dernier commit en gardant les modifications en attente — facile à enchaîner par erreur sur plusieurs commits |
    | `gunstage` (`git reset HEAD --`) | Désindexe les fichiers stagés — sans danger pour le contenu, mais peut surprendre si on s'attendait à un `checkout` |

    En cas de doute, `gst` (statut) et `gd` (diff) avant d'agir, et gardez à
    l'esprit que `git reflog` permet souvent de récupérer un commit "perdu"
    tant qu'il n'a pas été nettoyé par le ramasse-miettes Git.

**Status / Info**

| Alias | Commande Git |
|-------|-------------|
| `gst` | `git status -sb` |

**Branches**

| Alias | Commande Git |
|-------|-------------|
| `gb` | `git branch` |
| `gco` | `git checkout` |
| `gcb` | `git checkout -b` |
| `gbd` | `git branch -d` |
| `gbD` | `git branch -D` |

**Commit**

| Alias | Commande Git |
|-------|-------------|
| `gc` | `git commit` |
| `gcm` | `git commit -m` |
| `gca` | `git commit --amend --no-edit` |

**Diff**

| Alias | Commande Git |
|-------|-------------|
| `gd` | `git diff` |
| `gds` | `git diff --staged` |
| `gdt` | `git difftool` (visuel Kitty) |
| `gdts` | `git difftool --staged` |

**Fetch / Pull / Push**

| Alias | Commande Git |
|-------|-------------|
| `gf` | `git fetch` |
| `gfa` | `git fetch --all` |
| `gl` | `git pull` |
| `gp` | `git push` |
| `gpo` | `git push origin HEAD` |

**Log**

| Alias | Commande Git |
|-------|-------------|
| `glg` | `git log --graph` (coloré, toutes branches) |
| `glo` | `git log --oneline --decorate` |
| `glast` | `git log -1 HEAD` |

**Stash**

| Alias | Commande Git |
|-------|-------------|
| `gsta` | `git stash` |
| `gstp` | `git stash pop` |
| `gstl` | `git stash list` |

**Reset / Undo**

| Alias | Commande Git |
|-------|-------------|
| `gundo` | `git reset --soft HEAD~1` |
| `gunstage` | `git reset HEAD --` |

**Rebase**

| Alias | Commande Git |
|-------|-------------|
| `grb` | `git rebase` |
| `grbi` | `git rebase -i` |

**Maintenance**

| Alias | Commande Git |
|-------|-------------|
| `gclean` | Supprime les branches locales déjà mergées |
| `gprune` | `git remote prune origin` |

---

## Nettoyage du PATH — `.functions/lib/clean_path.sh`

Supprime les entrées dupliquées dans `$PATH` et place `~/.local/bin` et `/snap/bin` en tête.
