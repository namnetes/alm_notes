# ripgrep — le remplaçant moderne de `grep`

[ripgrep](https://github.com/BurntSushi/ripgrep) (`rg`) est un outil de
recherche récursive écrit en Rust, généralement **le plus rapide** de sa
catégorie. Il respecte `.gitignore` par défaut, ignore les fichiers binaires
et les dossiers cachés, et colore les résultats. Version installée :
**14.1.0** (paquet Ubuntu, juillet 2026).

---

## Installation

Installé par le process de post-installation via la **liste de paquets APT**
(`config/packages_to_install.list` dans
[alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)) —
pas de module dédié : le paquet Ubuntu est récent et suffit.

```bash
rg --version           # ripgrep 14.1.0
```

---

## Configuration (alm_dots)

### Le fichier de config — la bonne pratique ripgrep

ripgrep ne lit **aucun** fichier de config par défaut : il faut pointer la
variable `RIPGREP_CONFIG_PATH` vers un fichier d'options. C'est le mécanisme
standard pour définir ses défauts *une seule fois* au lieu de les répéter
dans chaque alias.

Fichier versionné `alm_dots/.config/ripgrep/config`, stowé vers
`~/.config/ripgrep/config` :

```text
# Insensible à la casse si le motif est tout en minuscules, sensible sinon
--smart-case

# Ne jamais fouiller .git, même quand --hidden est actif
--glob=!.git/*

# Tronquer les lignes interminables (minifiés, lockfiles) avec un aperçu
--max-columns=150
--max-columns-preview

# Chemins cliquables dans le terminal (kitty : Ctrl+Maj+clic)
--hyperlink-format=default
```

La variable est exportée dans `.bash_env`, **uniquement si rg est installé
et si le fichier existe** :

```bash
if command -v rg &>/dev/null; then
  [ -f "$HOME/.config/ripgrep/config" ] \
    && export RIPGREP_CONFIG_PATH="$HOME/.config/ripgrep/config"
  ...
fi
```

!!! warning "La config s'applique à *tous* les appels `rg`"
    Y compris dans les scripts. Un script qui a besoin d'un comportement
    déterministe doit appeler **`rg --no-config`** (ou vider
    `RIPGREP_CONFIG_PATH`).

### Les alias en place

Définis dans `alm_dots/.bash_env` (gardés par `command -v rg`) :

| Alias | Commande | Usage |
|---|---|---|
| `rgf` | `rg --hidden --follow` | Recherche étendue : dotfiles inclus, symlinks suivis |
| `rgdot` | `rg --hidden --glob ".*"` | Uniquement dans les fichiers cachés |
| `rgc` | `rg -C 3` | 3 lignes de contexte autour de chaque résultat |
| `rgt` | `rg --type` | Limité à un type de fichier : `rgt py TODO` |
| `rgx` | `rg --glob "!**/{tests,build,dist}/**"` | Exclut tests et artefacts de build |
| `rgu` | `rg -uu` | **Tout** : fichiers cachés *et* ignorés par `.gitignore` |
| `rgl` | `rg -l` | Liste seulement les fichiers contenant le motif |

!!! note "Alias supprimés en juillet 2026 : `rgv` et `rggit`"
    - `rgv` (`rg --smart-case`) : redondant depuis que `--smart-case` est
      dans le fichier de config — `rg` seul fait pareil.
    - `rggit` (`rg --files | xargs rg`) : produisait **exactement** le même
      résultat que `rg` seul (qui respecte déjà `.gitignore`), en plus lent —
      et sans argument, le premier nom de fichier devenait le motif.

---

## Exemples d'usage

### La recherche de tous les jours

```console
$ rg tache            # smart-case : trouve tache, Tache, TACHE
$ rg Tache            # une majuscule dans le motif → sensible à la casse
$ rg -w let           # mot entier : "let" mais pas "delete"
$ rg 'fn \w+_test'    # regex Rust (rapide), quoter les motifs complexes
```

### `rgt` — cibler un langage

```console
$ rgt py 'def main'          # uniquement les .py
$ rgt md 'TODO'              # uniquement le Markdown
$ rg --type-list | rg yaml   # voir les extensions couvertes par un type
```

### `rgu` — quand rg « ne trouve pas » un fichier qui existe

`rg` ignore par défaut ce que `.gitignore` exclut (`site/`, `.venv/`,
`node_modules/`…) ainsi que les fichiers cachés. Pour chercher *vraiment
partout* :

```console
$ rg ma_fonction           # rien…
$ rgu ma_fonction          # ah : elle était dans site/ (généré)
site/js/app.js:12:function ma_fonction() {
```

### `rgl` + pipe — enchaîner sur les fichiers trouvés

```console
$ rgl 'yaml.safe_load'                 # quels fichiers ?
new-page.py
$ rgl -0 TODO | xargs -0 zed           # ouvrir tous les fichiers concernés
```

### Contexte, remplacement, statistiques

```console
$ rgc 'PORT ='                  # 3 lignes avant/après
$ rg 'http:' --replace 'https:' # aperçu du remplacement (ne modifie RIEN)
$ rg TODO --stats               # nombre de matches, fichiers, durée
```

!!! tip "`--replace` ne modifie jamais les fichiers"
    C'est un aperçu dans le terminal. Pour modifier réellement, combiner
    avec `sd` ou `sed`, ou utiliser l'aperçu pour valider avant.

### Chemins cliquables (kitty)

Grâce à `--hyperlink-format=default` dans la config, chaque chemin affiché
par `rg` est un lien hypertexte : ++ctrl+shift++ + clic ouvre le fichier —
voir [Kitty](../kitty/index.md).

---

## Pièges connus

!!! warning "« rg ne trouve rien » — trois causes classiques"
    1. Le fichier est **ignoré** (`.gitignore`, `.ignore`) → `rgu`
    2. Le fichier est **caché** (dotfile) → `rgf` ou `rgdot`
    3. Le fichier est détecté **binaire** (octet NUL) → `rg -a`

!!! note "grep n'est pas aliasé vers rg"
    `rg` remplace `grep` à l'usage interactif, mais les options diffèrent
    (`grep -r` ≠ `rg`, regex POSIX ≠ regex Rust). Aliaser `grep=rg`
    casserait les scripts — on garde les deux commandes distinctes.

---

## Références

- [Dépôt ripgrep](https://github.com/BurntSushi/ripgrep)
- [Guide officiel](https://github.com/BurntSushi/ripgrep/blob/master/GUIDE.md)
  (dont la section configuration)
- `man rg`
- Config : `alm_dots/.config/ripgrep/config` · alias : `alm_dots/.bash_env`
