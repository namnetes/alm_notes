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

## Arborescence commentée

Le dépôt reproduit exactement la structure de `~` — chaque chemin ci-dessous
est donc, une fois `stow .` exécuté, à la fois un fichier du dépôt et un
lien symbolique dans `$HOME`. Les commentaires indiquent le **rôle**, pas
seulement l'emplacement.

```text
alm_dots/
├── .bash_aliases            # Alias statiques génériques (~30) : navigation,
│                            # presse-papiers, raccourcis système. Sourcé en
│                            # PREMIER par .bashrc (voir Environnement shell).
├── .bash_env                # Point d'entrée de la config shell : initialise
│                            # chaque outil CLI (starship, fzf, zoxide, fnm,
│                            # eza, uv...) dans un ordre précis. Sourcé en
│                            # DEUXIÈME.
├── .bash_functions          # Fonctions bash personnalisées (ve, gsp, csvc,
│                            # shims...). Sourcé en DERNIER — certaines
│                            # fonctions dépendent de variables exportées
│                            # par .bash_env (voir Environnement shell).
├── .nanorc                  # Configuration de Nano
├── .fzfrc                   # Options par défaut de fzf (FZF_DEFAULT_OPTS_FILE)
├── .gitconfig                # Alias [alias], éditeur, diff/difftool — lu à
│                            # la fois par git et par .functions/lib/git_aliases.sh
├── .tigrc                    # Config tig (TUI Git) — couleurs cursor/status/title
├── .claudecodeignore         # Fichiers ignorés par Claude Code
├── .clauderc                 # Règles Claude (copie de .config/claude/global_rules.md)
├── .stow-local-ignore        # Liste blanche : fichiers que Stow ne déploie PAS
│
├── .claude/                  # → ~/.claude/ — règles globales Claude Code
│   ├── CLAUDE.md              #   Règles appliquées à TOUS les projets
│   ├── CLAUDE_Open.md          #   Template : projets grand public (alias claude-open)
│   └── CLAUDE_Mainframe.md     #   Template : projets mainframe/z/OS (alias claude-z)
│
├── .config/                  # → ~/.config/ (miroir exact)
│   ├── starship.toml          #   Invite de commande
│   ├── kitty/                  #   Terminal : kitty.conf, thème, script SSH Alpine
│   ├── zed/                    #   Éditeur : settings.json, keymap.json, tasks.json
│   ├── bat/                    #   Thème et style par défaut de bat
│   ├── ripgrep/                 #   Config lue via RIPGREP_CONFIG_PATH
│   ├── Code/                    #   Réglages utilisateur VS Code
│   ├── claude/                  #   global_rules.md — source de .clauderc
│   ├── my_ubuntu/wallpapers/    #   Images piochées par change_wallpaper.sh
│   └── systemd/user/            #   Unités : mkdocs.service, change-wallpaper.timer
│
├── .ssh/
│   └── config                 # Alias SSH (serveur SFTP local)
│
└── .functions/                # → ~/.functions/ — trois rôles disjoints,
    │                          # jamais mélangés (détail : Environnement shell
    │                          # > Convention .functions)
    ├── bin/                    # Exécutables AUTONOMES, dans le PATH
    │   ├── update_system.sh     #   sudo apt update/upgrade/autoremove + snap
    │   ├── update_hostname.sh    #   change /etc/hostname et /etc/hosts
    │   ├── vid2mp3.sh            #   extrait l'audio d'un .mp4/.webm en .mp3
    │   ├── change_wallpaper.sh   #   tire un fond d'écran au hasard (gsettings)
    │   ├── init_zed.sh           #   purge extensions/DB Zed, restaure via stow
    │   ├── list_functions.sh     #   sélecteur FZF sur les fonctions d'un script
    │   └── claude-switch         #   bascule abonnement / clé API Claude Code
    ├── lib/                    # Bibliothèques à SOURCER — jamais exécutées seules
    │   ├── clean_path.sh         #   fonction clean_path() — dédoublonne le PATH
    │   └── git_aliases.sh        #   fonction load_git_aliases() — alias Git dynamiques
    └── tools/                  # Scripts Python, invoqués via `uv run python3`
        ├── check_csv.py          #   derrière la fonction csvc()
        ├── rename_images.py      #   derrière la fonction renimg()
        ├── encrypt_gpg.py        #   derrière la fonction gpgtool()
        └── manage_kvm.py         #   derrière la fonction kadm()
```

!!! danger "`~/.bashrc` n'est PAS dans ce dépôt"
    Aucun `.bashrc` ne figure dans `alm_dots` — c'est volontairement le
    fichier squelette standard d'Ubuntu (`/etc/skel/.bashrc`), présent par
    défaut sur toute installation. Or c'est justement lui qui source, dans
    l'ordre, `.bash_aliases`, `.bash_env` puis `.bash_functions` — la
    chaîne de chargement entière dépend donc d'un fichier **non versionné,
    non déployé par `stow`**, dans lequel ces trois blocs `source` ont été
    ajoutés à la main. Détail complet et risque associé sur une
    réinstallation :
    [Environnement shell — Chaîne de chargement](environnement-shell.md#chaine-de-chargement).

---

## Fichiers exclus de Stow

Le fichier `.stow-local-ignore` exclut du déploiement les éléments suivants :

```
.git/
.gitignore
system-config/
settings.local.json
^CLAUDE\.md$
.github/
.editorconfig
README.md
.steampath
.steampid
```

!!! warning "Le `CLAUDE.md` racine n'est **pas** stowé"
    Le `CLAUDE.md` à la racine du dépôt est le guide du dépôt `alm_dots`
    lui-même (lu par Claude Code quand on travaille *dans* le dépôt). Il est
    exclu par le motif `^CLAUDE\.md$`. Les règles globales déployées dans
    `~` sont celles de `.claude/CLAUDE.md → ~/.claude/CLAUDE.md`.

!!! info "`.gitconfig` est stowé"
    Contrairement à ce que l'on pourrait croire, `.gitconfig` **est bien déployé par Stow** (`~/.gitconfig → alm_dots/.gitconfig`). La configuration Git (nom, email, alias) est donc restaurée automatiquement à la réinstallation.

!!! info "`settings.local.json` non stowé"
    Ce fichier contient les permissions accordées à Claude Code session par session. Il est exclu de Stow et n'est pas versionné — Claude Code le recrée automatiquement.
