# eza — le remplaçant moderne de `ls`

[eza](https://github.com/eza-community/eza) est un remplaçant de `ls` écrit
en Rust : couleurs par type de fichier, icônes Nerd Font, statut Git par
fichier, vue arborescente intégrée. Version installée : **v0.23.4** (juillet
2026), via le dépôt APT officiel du projet.

---

## Installation

Installé par le process de post-installation
([alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)) :

```bash
cd ~/alm_tools/postinstall
sudo make eza          # module seul
sudo make cli          # ou avec tous les outils CLI (uv, starship, fzf…)
```

Le module `modules/cli/install_eza.sh` enregistre le dépôt APT
`deb.gierens.de` (signé) puis installe le paquet — les mises à jour suivent
ensuite les `apt upgrade` classiques. Le paquet fournit aussi :

- les **complétions bash** (`/usr/share/bash-completion/completions/eza`) —
  chargées automatiquement ;
- les **pages man** : `man eza`, `man eza_colors`.

```bash
eza --version          # vérifier l'installation
```

---

## Configuration (alm_dots)

Les alias vivent dans `alm_dots/.bash_env` (stowé vers `~/.bash_env`) et ne
sont définis **que si eza est présent** :

```bash
if command -v eza &>/dev/null; then

  # Base commune héritée par tous les alias ci-dessous (bash étend
  # récursivement le premier mot d'un alias) : couleurs, icônes Nerd Font
  # (auto : désactivées hors TTY, les pipes restent propres), dossiers
  # regroupés en premier.
  alias eza='eza --color=auto --icons=auto --group-directories-first'
  alias ls='eza'
  ...
fi
```

!!! tip "Le motif « alias de base + héritage »"
    Bash ré-étend le premier mot d'un alias : `ll` → `eza -l --git …` →
    l'alias `eza` → `eza --color=auto --icons=auto --group-directories-first
    -l --git …`. Les options communes ne sont donc écrites **qu'une fois**,
    dans l'alias `eza`.

!!! info "Icônes : `--icons=auto`, pas `always`"
    `auto` n'affiche les icônes que si la sortie est un terminal — un
    `ls | grep …` ou une redirection vers un fichier reste propre. Les
    icônes nécessitent une **Nerd Font** ; kitty utilise FiraCode Nerd Font,
    voir [Kitty](../kitty/index.md).

---

## Les alias en place

| Alias | Commande effective (hors base commune) | Usage |
|---|---|---|
| `ls` | `eza` | Listing standard coloré, dossiers d'abord |
| `ll` | `eza -l --git --time-style=long-iso` | Détail + statut Git + dates ISO |
| `la`, `l` | `eza -la --git --time-style=long-iso` | Idem avec fichiers cachés |
| `lt` | `eza --tree --level=2` | Arborescence, 2 niveaux |
| `lt3` | `eza --tree --level=3` | Arborescence, 3 niveaux |
| `ltg` | `eza --tree --git-ignore` | Arborescence qui respecte `.gitignore` |
| `lS` | `eza -l --sort=size` | Tri par taille croissante (les gros en bas) |
| `lD` | `eza -l --sort=date` | Tri par date (les récents en bas) |
| `lx` | `eza -l --sort=extension` | Tri par extension |
| `l1` | `eza -1` | Un nom par ligne (pratique pour les pipes) |
| `lh` | `eza -lad -I ".|.." .*` | Uniquement les entrées cachées |
| `ldir` | `eza -la --only-dirs` | Uniquement les répertoires |

---

## Exemples d'usage

### `ll` — le quotidien : détail, Git, dates lisibles

```console
$ ll
drwxrwxr-x    - galan 2026-07-04 20:31 docs
drwxrwxr-x    - galan 2026-07-04 18:02 drafts
.rw-rw-r-- 4,3k galan 2026-07-04 20:31 CLAUDE.md    -M
.rw-rw-r-- 1,2k galan 2026-06-12 09:14 Makefile
```

La colonne Git (`-M` = modifié, `-N` = nouveau, `-I` = ignoré) donne l'état
du dépôt fichier par fichier, sans lancer `git status`.

### `ltg` — arborescence d'un projet sans le bruit

```console
$ ltg
.
├── docs
│   ├── index.md
│   └── outils
├── mkdocs.yml
└── new-page.py
```

Contrairement à `lt`, les répertoires ignorés (`site/`, `__pycache__/`,
`.venv/`…) n'apparaissent pas : c'est l'équivalent de `tree` qui lirait
`.gitignore`.

### `lS` — retrouver ce qui prend de la place

```console
$ lS
.rw-rw-r--  1,2k galan  4 Jul 20:31 Makefile
.rw-rw-r--  4,3k galan  4 Jul 20:31 CLAUDE.md
.rw-rw-r-- 245,8k galan  4 Jul 20:31 uv.lock
```

Tri **croissant** : les plus gros fichiers sont en bas, donc immédiatement
visibles au-dessus du prompt.

### `lh` — inspecter les dotfiles d'un répertoire

```console
$ lh
drwxrwxr-x - galan  4 Jul 20:40 .claude
.rw-rw-r-- 7 galan  4 Jul 20:40 .gitignore
.rw-rw-r-- 3 galan  4 Jul 20:40 .python-version
```

Le glob `.*` sélectionne les entrées cachées ; `-I ".|.."` (ignore-glob)
masque les pseudo-entrées `.` et `..` ; `-d` liste les dossiers eux-mêmes au
lieu de leur contenu.

### Options ponctuelles utiles (sans alias)

```bash
eza -l --total-size dossiers/     # taille récursive réelle des dossiers (lent)
eza -l -I "*.pyc|__pycache__"     # exclure par glob
eza -l --sort=date --reverse      # les plus récents EN HAUT
eza -lh --header                  # ligne d'en-têtes de colonnes
eza --hyperlink                   # noms cliquables (kitty : Ctrl+Maj+clic)
```

---

## Pièges connus

!!! warning "Depuis v0.23 : `eza` sans argument lit stdin s'il est redirigé"
    Quand stdin n'est **pas** un TTY (script, cron, pipe vide), `eza` sans
    argument lit la liste des chemins **depuis stdin** au lieu de lister le
    répertoire courant — avec un stdin vide, il n'affiche rien du tout.
    Dans un script, toujours donner le chemin explicitement : `eza .`
    En interactif, aucun impact.

!!! note "Les tris sont croissants par défaut"
    `--sort=size` et `--sort=date` placent les plus gros / plus récents **en
    bas** (donc visibles au-dessus du prompt). Ajouter `--reverse` pour
    l'ordre inverse.

---

## Pour aller plus loin — thème de couleurs

eza lit un fichier optionnel `~/.config/eza/theme.yml` pour personnaliser
toutes les couleurs (par extension, par type, par colonne). Des thèmes prêts
à l'emploi (Catppuccin, Dracula, Gruvbox…) sont maintenus dans
[eza-community/eza-themes](https://github.com/eza-community/eza-themes).
Non déployé ici pour l'instant : les couleurs par défaut sont cohérentes
avec le thème kitty.

```bash
mkdir -p ~/.config/eza
ln -s <thème>.yml ~/.config/eza/theme.yml   # à stower via alm_dots le cas échéant
```

---

## Références

- [Dépôt eza](https://github.com/eza-community/eza)
- [Installation Debian/Ubuntu (dépôt gierens.de)](https://github.com/eza-community/eza/blob/main/INSTALL.md#debian-and-ubuntu)
- `man eza`, `man eza_colors`
- Alias : `alm_dots/.bash_env`, section « Intégration de eza »
