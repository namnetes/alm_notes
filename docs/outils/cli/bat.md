# bat — `cat` avec coloration syntaxique

[bat](https://github.com/sharkdp/bat) affiche les fichiers avec coloration
syntaxique, numéros de ligne, marqueurs Git en marge et pagination
automatique. C'est aussi le *previewer* utilisé par [fzf](fzf.md) (++ctrl+t++,
`fs`). Version installée : **0.24.0** (paquet Ubuntu, juillet 2026).

---

## Installation — et l'affaire `batcat`

Installé par le process de post-installation via la **liste de paquets APT**
(`config/packages_to_install.list` dans
[alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)).

!!! warning "Sur Debian/Ubuntu, le binaire s'appelle `batcat`"
    Conflit de nom avec un autre paquet (`bacula-console-qt`). Or tous les
    outils (fzf, scripts, habitudes) attendent `bat`. Le bloc
    « Configuration de Bat » de `.bash_env` crée donc un **shim
    auto-réparant** à chaque démarrage de shell :

    ```text
    ~/.local/bin/bat → /usr/bin/batcat
    ```

    Comme pour `claude-switch`, rien à faire après une réinstallation —
    le lien se recrée seul dès que `batcat` est présent.

---

## Configuration (alm_dots)

### `~/.config/bat/config` — thème et syntaxes

Fichier versionné `alm_dots/.config/bat/config` (stowé) :

```text
# Thème 16 couleurs : bat suit la palette du terminal — donc le thème
# Tomorrow Night de kitty — au lieu d'imposer ses propres couleurs.
--theme="base16"

# Autoriser l'italique (kitty le rend correctement)
--italic-text=always

# Syntaxes pour les fichiers de config sans extension connue
--map-syntax=".fzfrc:Bourne Again Shell (bash)"
--map-syntax="*.conf:INI"
```

!!! tip "Pourquoi `base16` plutôt qu'un thème dédié ?"
    Les thèmes embarqués (`Monokai Extended` par défaut, `Dracula`, `Nord`…)
    imposent leurs couleurs RVB. `base16` n'utilise que les 16 couleurs
    ANSI du terminal : bat reste automatiquement assorti au thème kitty,
    aujourd'hui et après tout changement de palette. `bat --list-themes`
    pour explorer.

### `cat` remplacé (`.bash_aliases`, gardé par `command -v bat`)

```bash
alias cat='bat --paging=never --style=plain'
```

Sortie identique à `cat` (pas de bordure, pas de pagination) **plus** la
coloration. Le vrai `cat` reste accessible : `\cat` ou `command cat`.

### Pages man colorées (`.bash_env`)

```bash
export MANPAGER="sh -c 'col -bx | bat -l man -p'"
export MANROFFOPT="-c"
```

`man <commande>` passe désormais par bat : sections, options et exemples
colorés. Ajouté en juillet 2026 — c'est l'intégration bat au meilleur
rapport service/effort.

---

## Exemples d'usage

### Lecture quotidienne

```console
$ bat mkdocs.yml               # colore + numéros + pagination auto
$ bat -r 40:60 new-page.py     # uniquement les lignes 40 à 60
$ cat script.sh                # alias : sortie plain mais colorée
$ bat -A fichier.txt           # révèle tabs, espaces insécables, CRLF…
```

`-A` (*show-all*) est l'arme secrète contre les bugs invisibles :
indentation mixte, fins de ligne Windows, espaces insécables collés dans
un YAML.

### Forcer la syntaxe quand l'extension ne suffit pas

```console
$ bat -l yaml .pages                    # fichier awesome-pages sans extension
$ git show HEAD~2:mkdocs.yml | bat -l yaml
$ kubectl get pod mon-pod -o yaml | bat -l yaml
```

### Suivre un log avec coloration

```console
$ tail -f /var/log/syslog | bat --paging=never -l log
```

### Diff colorés

```console
$ bat --diff new-page.py            # ne montre que les zones modifiées (Git)
$ git diff | bat -l diff            # colorer n'importe quel diff
```

---

## Pièges connus

!!! note "Dans un pipe, bat redevient sage"
    Sortie redirigée = pas de couleurs ni décor (comportement `cat`).
    Pour forcer : `bat --color=always … | less -R`. C'est pour ça que les
    previews fzf utilisent explicitement `--color=always`.

!!! note "`--paging=never` vs `--style=plain`"
    `-p` (= `--style=plain`) enlève le décor mais **garde** la pagination ;
    `--paging=never` enlève la pagination mais garde le décor. L'alias
    `cat` combine les deux.

---

## Pour aller plus loin

Les scripts [bat-extras](https://github.com/eth-p/bat-extras) (`batgrep`,
`batdiff`, `batman`, `prettybat`) combinent bat avec ripgrep et git — non
installés ici pour l'instant, `MANPAGER` couvrant déjà le cas le plus utile.

---

## Références

- [Dépôt bat](https://github.com/sharkdp/bat)
- `bat --help`, `man bat`, `bat --list-themes`, `bat --list-languages`
- Shim + MANPAGER : `alm_dots/.bash_env` · alias : `alm_dots/.bash_aliases` ·
  config : `alm_dots/.config/bat/config`
