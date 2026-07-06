# fzf — la recherche floue interactive

[fzf](https://github.com/junegunn/fzf) (*fuzzy finder*) transforme n'importe
quelle liste (fichiers, historique, processus…) en menu interactif filtrable
en tapant quelques lettres. C'est la colle universelle du shell : tout ce qui
produit des lignes peut être « pipé » dans fzf. Version installée : **0.73.1**
(binaire upstream, juillet 2026).

---

## Installation

Deux canaux existent :

- **Module postinstall** `modules/cli/install_fzf.sh` (`sudo make fzf`,
  installé actuellement) — télécharge la **dernière release GitHub** dans
  `/usr/local/bin/fzf`, prioritaire dans le `PATH`. Il ne s'exécute que si
  aucun `fzf` n'est présent — c'est pourquoi `fzf` a été retiré de
  `packages_to_install.list` : sinon le paquet APT s'installerait en premier
  et court-circuiterait ce module à chaque `make all`.
- **Paquet APT Ubuntu** — ancien canal, fournissait la 0.44.1 ainsi que des
  fichiers d'intégration shell dans `/usr/share/doc/fzf/examples/`. Plus
  utilisé depuis la migration de juillet 2026.

!!! note "Migration effectuée (juillet 2026)"
    Passage de la 0.44 (paquet APT) à la 0.73.1 (upstream) : intégration
    `--bash` native, `--tmux`, meilleurs aperçus. Le `.bash_env` gérait déjà
    les deux cas de figure, donc aucun changement côté raccourcis clavier.
    Procédure suivie :

    ```bash
    sudo apt remove fzf
    sudo make -C ~/alm_tools/postinstall fzf
    ```

---

## Configuration (alm_dots)

### `~/.fzfrc` — les options par défaut

Fichier versionné `alm_dots/.fzfrc` (stowé), chargé **nativement** via
`export FZF_DEFAULT_OPTS_FILE="$HOME/.fzfrc"` (fzf ≥ 0.54). Les commentaires
dans ce fichier sont supportés directement par fzf depuis la 0.55 — plus
besoin d'un chargeur maison pour les retirer.

```text
--height=45%          # 45 % de la hauteur du terminal
--layout=reverse      # prompt et résultats en haut
--border --info=inline
--prompt="❯ "
--multi               # sélection multiple (Tab / Maj+Tab)
--cycle
--bind=ctrl-j:down,ctrl-k:up
--color=…             # palette Tomorrow Night, assortie à kitty
```

!!! note "Historique : le chargeur `sed` (retiré en juillet 2026)"
    Avant fzf 0.55, `FZF_DEFAULT_OPTS` ne supportait aucun commentaire. Un
    ancien chargeur naïf (`cat ~/.fzfrc`) exportait le fichier **brut** :
    les apostrophes des commentaires s'appariaient comme des guillemets et
    « avalaient » le texte, cassant *tous* les appels fzf
    (`unknown option: #`). Un chargeur `sed` a corrigé ça temporairement ;
    il a été retiré au profit du support natif `FZF_DEFAULT_OPTS_FILE` une
    fois la migration vers la version upstream faite.

### Variables d'environnement (`.bash_env`, gardées par `command -v`)

| Variable | Valeur | Effet |
|---|---|---|
| `FZF_DEFAULT_COMMAND` | `rg --files --hidden --glob "!.git/*"` | Liste des fichiers : respecte `.gitignore`, inclut les dotfiles |
| `FZF_CTRL_T_COMMAND` | idem | Même source pour ++ctrl+t++ |
| `FZF_ALT_C_COMMAND` | `find … -type d` (sans `.git`) | Source des dossiers pour ++alt+c++ |
| `FZF_CTRL_T_OPTS` | aperçu `bat` | Contenu du fichier à droite |
| `FZF_ALT_C_OPTS` | aperçu `eza --tree` | Arbre du dossier survolé |

L'aperçu `bat` n'est **plus** dans les options par défaut : il ne s'applique
qu'à ++ctrl+t++ et `fs` — dans ++ctrl+r++, un aperçu qui tente d'ouvrir une
ligne d'historique comme un fichier n'a pas de sens. Depuis fzf 0.68,
`FZF_CTRL_T_OPTS` utilise `wrap-word` (retour à la ligne au mot plutôt
qu'au caractère) pour un aperçu plus lisible.

### Raccourcis clavier natifs

Chargés en fin de bloc via l'intégration native `eval "$(fzf --bash)"`
(fzf ≥ 0.48, embarquée dans le binaire — plus de dépendance à des fichiers
d'exemples externes) :

| Raccourci | Action |
|---|---|
| ++ctrl+r++ | Historique des commandes en fuzzy — **le** raccourci à connaître |
| ++ctrl+t++ | Insère le(s) fichier(s) choisi(s) dans la ligne de commande |
| ++alt+c++ | `cd` vers le dossier choisi |
| `commande **`++tab++ | Complétion fuzzy : `vim **`++tab++, `code **`++tab++, `ssh **`++tab++, `kill -9 **`++tab++, `zed **`++tab++, `nano **`++tab++, `shellcheck **`++tab++, `tree **`++tab++, `ncdu **`++tab++ |

!!! warning "Certaines commandes ne sont pas couvertes par défaut"
    fzf n'enregistre la complétion `**`+Tab que pour une liste fixe de
    commandes (`vim`, `nvim`, `code`, `emacs`, `git`, `ssh`, `kill`…) — il
    n'existe pas de handler générique pour les commandes absentes de cette
    liste. Sans intervention, `**`+Tab ne fait **rien** après ces
    commandes. Enregistrements manuels ajoutés dans `.bash_env` juste après
    `eval "$(fzf --bash)"` :

    ```bash
    command -v zed        >/dev/null 2>&1 && _fzf_setup_completion path zed
    command -v nano       >/dev/null 2>&1 && _fzf_setup_completion path nano
    command -v shellcheck >/dev/null 2>&1 && _fzf_setup_completion path shellcheck
    command -v tree       >/dev/null 2>&1 && _fzf_setup_completion dir tree
    command -v ncdu       >/dev/null 2>&1 && _fzf_setup_completion dir ncdu
    ```

    `path` propose fichiers et dossiers ; `dir` ne propose que des dossiers
    (adapté à `tree`/`ncdu`, qui n'acceptent pas de fichier seul). Pour
    ajouter une autre commande non couverte, même principe.

    `glow` (visualiseur Markdown terminal) avait été envisagé puis
    désinstallé (juillet 2026) : son rendu ne reflétait pas les extensions
    Material (admonitions…) du site MkDocs réel — mieux vaut vérifier via
    `make docs` qu'un aperçu terminal trompeur, et aucun script du dépôt
    n'en dépendait.

### Alias et fonctions

| Nom | Définition | Usage |
|---|---|---|
| `fz` | `fzf --bind "enter:become(zed {+})"` | Ouvrir la sélection (multi) dans Zed |
| `fn` | idem avec `nano` | Ouvrir dans nano |
| `ff` | `fzf` | fzf brut, pour les pipes |
| `fh` | `history \| fzf --tac --no-sort` | Fouiller l'historique (affichage seul) |
| `fcd` | fonction | `cd` interactif (équivalent ++alt+c++) |
| `fs` | `rg --files \| fzf --preview 'bat …'` | Explorer les fichiers avec aperçu |

!!! note "`enter:become(...)` plutôt que `zed $(fzf)`"
    L'ancienne forme `zed $(fzf)` cassait sur les noms avec espaces et
    lançait `zed` même après une annulation (++esc++). `become()` remplace
    le processus fzf par la commande, avec la sélection correctement
    échappée — annulation = il ne se passe rien.

    `become()` n'existe que depuis fzf 0.48 : sur le paquet apt 0.44
    installé jusqu'en juillet 2026, ces alias étaient en réalité inopérants
    (action inconnue). Ils ne sont fonctionnels que depuis la migration
    vers la version upstream.

---

## Exemples d'usage

### Le réflexe quotidien : ++ctrl+r++

```console
$ <Ctrl+R> stow
❯ stow
> cd ~/alm_dots && stow --restow .
  stow --simulate .
```

Taper quelques lettres (même non consécutives : `mkdcs` trouve
`make docs-start`), ++enter++ pour rappeler la commande.

### Complétion fuzzy `**` — universelle

```console
$ zed **<Tab>          # choisir un fichier à ouvrir
$ cd ~/alm**<Tab>      # naviguer
$ kill -9 **<Tab>      # choisir un processus (avec ligne complète)
$ ssh **<Tab>          # hôtes depuis ~/.ssh/config
```

### `fs` — retrouver un fichier en le feuilletant

```console
$ fs
❯ conf
> docs/outils/claude-code/configuration.md   ┌──────────────────────┐
  docs/outils/kitty/index.md                 │ # Configuration      │
  mkdocs.yml                                 │ Claude Code charge…  │
```

++tab++ pour sélectionner plusieurs fichiers, ++enter++ imprime les chemins.

### fzf comme brique de script

```bash
# Basculer de branche git en fuzzy
git branch | fzf --height 20% | xargs git checkout

# Tuer un processus choisi interactivement
ps aux | fzf --header-lines=1 | awk '{print $2}' | xargs kill

# Choisir un fichier du dépôt et copier son chemin
rg --files | fzf | tee /dev/tty | wl-copy
```

---

## Pièges connus

!!! warning "`FZF_DEFAULT_OPTS` s'applique à *tous* les fzf"
    Y compris ceux lancés par des scripts tiers. `--multi` et `--cycle`
    sont inoffensifs, mais éviter d'y mettre des `--bind` exotiques sur
    ++enter++ ou des `--preview` par défaut.

!!! info "Fonctionnalités upstream disponibles mais non utilisées"
    La 0.73.1 apporte `--tmux`/`--popup` (fenêtre flottante tmux/Zellij),
    `--ghost=TEXT` (texte de suggestion sur saisie vide) et des presets
    `--style`. Volontairement pas adoptées ici : pas d'usage tmux sur ce
    poste, et les deux autres sont cosmétiques — à reconsidérer si le
    besoin apparaît.

---

## Références

- [Dépôt fzf](https://github.com/junegunn/fzf) — README très complet
- [Exemples communautaires](https://github.com/junegunn/fzf/wiki/examples)
- `man fzf`
- Config : `alm_dots/.fzfrc` · variables et alias : `alm_dots/.bash_env`
