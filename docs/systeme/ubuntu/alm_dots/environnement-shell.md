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

## Chaîne de chargement

Trois fichiers, sourcés dans un ordre fixe, construisent l'environnement
shell complet. L'ordre est déterminé par **`~/.bashrc`**, pas par
`alm_dots` lui-même :

```bash
# Extrait réel de ~/.bashrc, dans l'ordre où les blocs apparaissent
if [ -f ~/.bash_aliases ]; then
    source ~/.bash_aliases
fi

if [ -f ~/.bash_env ]; then
    source ~/.bash_env
fi

# Il est important de déclencher .bash_functions après
# avoir configuré les alias !
if [ -f ~/.bash_functions ]; then
    source ~/.bash_functions
fi
```

!!! danger "`~/.bashrc` n'est pas versionné dans `alm_dots`"
    Ces trois blocs `source` vivent dans le `~/.bashrc` **standard
    d'Ubuntu** (`/etc/skel/.bashrc`), édité à la main sur chaque machine —
    aucun `.bashrc` n'existe dans le dépôt, et `.stow-local-ignore` ne
    l'exclut pas non plus puisqu'il n'y a simplement rien à exclure.

    **Conséquence concrète** : sur une réinstallation fraîche, `stow .`
    déploie bien `.bash_aliases`, `.bash_env`, `.bash_functions` et
    `.functions/` dans `$HOME` — mais **rien ne les source
    automatiquement**. Le `.bashrc` par défaut d'Ubuntu sait sourcer
    `.bash_aliases` (c'est standard), mais ignore totalement `.bash_env`
    et `.bash_functions`. Sans réédition manuelle de `~/.bashrc` pour
    ajouter les deux blocs `source` correspondants, ces deux fichiers
    existent sur disque mais restent silencieusement inertes — aucune
    erreur, juste des alias/fonctions/outils absents. Ce n'est documenté
    nulle part ailleurs dans le tutoriel de déploiement : à faire à la main
    après le premier `stow .` sur une machine neuve.

Le commentaire du `.bashrc` lui-même justifie l'ordre
`.bash_aliases` → `.bash_functions` par « il faut configurer les alias
avant les fonctions ». En pratique, cette raison précise ne tient pas :
les alias Bash sont substitués **au moment de la frappe** de la commande,
pas au moment de leur déclaration — un alias comme `myip='show_ip'`
(défini dans `.bash_aliases`, où `show_ip` n'existe pas encore) fonctionne
très bien même défini avant la fonction, du moment que la fonction existe
quand l'utilisateur tape effectivement `myip`. L'ordre ne coûte rien à
garder, mais ce n'est pas *cette* dépendance-là qui l'impose — voir plus
bas la vraie raison qui rend `.bash_env` → `.bash_functions` réellement
obligatoire.

---

## `.bash_env` — initialisation des outils CLI

Sourcé en deuxième (après `.bash_aliases`, avant `.bash_functions`), ce
fichier configure chaque outil CLI dans l'ordre suivant :

| Ordre | Outil | Rôle |
|-------|-------|------|
| 1 | **Starship** | Invite de commandes visuelle avec icônes Nerd Font |
| 2 | **Éditeur par défaut** | Zed (avec fallback Nano) |
| 3 | **Jupyter** | Environnement sandbox `~/workspaces/sandbox` |
| 4 | **bat / batcat** | Remplacement de `cat` avec coloration syntaxique — shim auto-réparant, `MANPAGER`, thème `base16` — voir [la page dédiée](../../../outils/cli/bat.md) |
| 5 | **claude-switch** | Recrée le lien `~/.local/bin/claude-switch → .functions/bin/claude-switch` à chaque démarrage (bascule abonnement / clé API pour Claude Code) |
| 6 | **FZF** | Recherche floue — `.fzfrc` + ++ctrl+r++/++ctrl+t++/++alt+c++, alias `fz`, `fs` et fonction `fcd` — voir [la page dédiée](../../../outils/cli/fzf.md) |
| 7 | **ripgrep** | Recherche rapide — config `RIPGREP_CONFIG_PATH` + alias `rgf`, `rgdot`, `rgc`, `rgt`, `rgx`, `rgu`, `rgl` — voir [la page dédiée](../../../outils/cli/ripgrep.md) |
| 8 | **zoxide** | Remplacement intelligent de `cd` via `zoxide init --cmd cd` (mémorise les répertoires fréquents) — voir [la page dédiée](../../../outils/cli/zoxide.md) |
| 9 | **fnm** | Gestionnaire de versions Node.js avec auto-switch par répertoire — init **après zoxide** (enchaînement des hooks `cd`) — voir [la page dédiée](../../../outils/cli/fnm.md) |
| 10 | **Alerte MAJ upstream** | Affiche le cache de `check_updates.sh` (alm_tools) : fzf, xan, starship, fnm, uv, rclone, kitty, pass-cli + Node LTS — aucun appel réseau à l'ouverture du shell |
| 11 | **eza** | Remplacement de `ls` avec informations Git intégrées — voir [la page dédiée](../../../outils/cli/eza.md) |
| 12 | **uv** | Gestionnaire de paquets Python |
| 13 | **SDKMAN** | Gestionnaire de versions Java/Groovy |
| 14 | **Alias Git** | Chargés dynamiquement depuis `.gitconfig` |
| 15 | **PATH** | Déduplication — `~/.local/bin` en priorité |
| 16 | **Fond d'écran** | Lance `change_wallpaper.sh` en arrière-plan au démarrage |
| 17 | **CSS Pandoc** | Vérification silencieuse des feuilles de style `~/.local/share/pandoc` (utilisées par `md2html`) |

### Pourquoi cet ordre compte — dépendances implicites vérifiées

| Dépendance | Où | Ce qui casserait dans l'ordre inverse |
|---|---|---|
| **bat/batcat (4) avant FZF (6)** | `.bash_env` | Les aperçus FZF (`FZF_CTRL_T_OPTS`, l'alias `fs`) invoquent la commande `bat` par son nom. Sur une machine où seul `batcat` existe, le shim `~/.local/bin/bat` est créé au bloc 4 — s'il n'existait pas encore, les aperçus échoueraient avec « commande introuvable ». |
| **zoxide (8) avant fnm (9)** | `.bash_env`, déjà commenté dans le fichier | `fnm env --use-on-cd` pose un `alias cd=__fnmcd` dont le `\cd` interne doit retomber sur la **fonction** `cd` de zoxide. Si fnm passait en premier, `zoxide init --cmd cd` écraserait silencieusement l'alias fnm — plus de bascule de version Node au `cd`. |
| **`.bash_env` (bloc 15, `clean_path`) après TOUT ajout au PATH** | Entre fichiers, dans `.bash_env` | `clean_path()` (définie dans `.functions/lib/clean_path.sh`) capture le `$PATH` **au moment où elle est appelée** et le réordonne une fois pour toutes. Elle doit donc s'exécuter après les trois blocs qui modifient le PATH plus haut : le shim bat/batcat (4), fnm (9) et l'export de `~/.local/bin/env` par uv (12) — c'est le cas aujourd'hui (bloc 15), mais **rien ne l'impose structurellement** : un nouveau bloc ajouté après `clean_path` et modifiant le PATH échapperait silencieusement au nettoyage, sans erreur ni avertissement. |
| **`.bash_env` avant `.bash_functions`** | Entre fichiers, **non documenté dans le code** | `ipy()` et `jl()` ne sont **définies** (pas seulement appelées) que si `$SANDBOX_HOME` est déjà exporté — variable réglée par le bloc Jupyter de `.bash_env` (ordre 3). C'est une dépendance réelle et actuellement correcte (`.bashrc` source `.bash_env` avant `.bash_functions`), mais aucun commentaire ne l'explique dans le code — contrairement au couple zoxide/fnm ci-dessus. Inverser l'ordre dans `.bashrc` ferait disparaître silencieusement `ipy` et `jl` (aucune erreur : le `if` autour de leur définition serait simplement faux). |

---

## Alias shell — `.bash_aliases`

Une soixantaine d'alias statiques (répartis entre `.bash_aliases` pour les
alias généraux et `.bash_env` pour ceux liés à un outil), auxquels s'ajoutent
une trentaine d'alias Git générés dynamiquement. Exemples représentatifs :

```bash
alias eza='eza --color=auto --icons=auto --group-directories-first'
alias ll='eza -l --git --time-style=long-iso'   # hérite de l'alias eza
alias lt='eza --tree --level=2'
alias cat='bat --paging=never --style=plain'
alias tl='shims'        # inventaire des outils personnels
```

`cd` n'est pas un alias : zoxide le remplace directement via
`eval "$(zoxide init --cmd cd bash)"` dans `.bash_env`.

Les alias eza complets (avec exemples d'usage) sont documentés dans
[Outils > CLI modernes > eza](../../../outils/cli/eza.md).

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
| `ldpath` | `ldpath` | Idem pour `$LD_LIBRARY_PATH` |
| `rule` | `rule` | Règle numérique alignée à la largeur du terminal (utile pour vérifier la longueur de ligne) |
| `rh` | `rh fichier` | `rule` + `head` : affiche le début d'un fichier sous une règle numérique |
| `rhc` | `rhc fichier` | Comme `rh`, avec la longueur de chaque ligne en préfixe |
| `th` | `th fichier` | `rule` + `tail` : affiche la fin d'un fichier sous une règle numérique |
| `ge` | `ge fichier` | Ouvre gnome-text-editor en arrière-plan |
| `dlvi` | `dlvi nginx redis` | Interroge Docker Hub pour la dernière version d'une ou plusieurs images |
| `gsp` | `gsp` | Statut Git de `alm_dots`, `alm_tools`, `alm_notes`, `alm_dashboard` en un coup d'œil |
| `grh` | `grh` | Écrase l'historique Git du dépôt courant en un seul commit ([reset_historique_git](../alm_tools/outils/reset-historique-git.md)) |
| `renimg` | `renimg prefixe` | Renomme toutes les images du dossier courant en `prefixe_01.ext`, `prefixe_02.ext`… |
| `csvc` | `csvc -f fichier.csv` | Vérifie la cohérence du nombre de colonnes d'un fichier CSV |
| `finfo` | `finfo ~/.bash_functions` | Ouvre un sélecteur FZF sur les fonctions d'un script Bash |
| `show_ip` | `show_ip` ou `myip` | Affiche toutes les interfaces réseau avec leurs adresses IPv4/IPv6 |
| `kadm` | `kadm` | Interface TUI pour gérer les machines virtuelles KVM |
| `gpgtool` | `gpgtool` | Interface interactive pour chiffrer/déchiffrer des fichiers GPG |
| `usbboot` | `usbboot /dev/sdb` | Teste si une clé USB est bootable en la démarrant dans QEMU |
| `mkdocs-pdf` | `mkdocs-pdf chemin/page` | Exporte une page MkDocs en PDF via Brave (serveur MkDocs doit être actif) |
| `md2html` | `md2html fichier.md [theme]` | Convertit un Markdown en HTML autonome via Pandoc (thème CSS `water` par défaut) |
| `pandoc-css` | `pandoc-css` | Télécharge / synchronise les feuilles CSS Pandoc dans `~/.local/share/pandoc` |
| `init_zed` | `init_zed` | Purge les extensions et la base de données Zed, restaure la config via `stow` |
| `shims` / `tl` | `tl` | Inventaire de tous les outils personnels installés avec statut ✓ / ✗ |
| `shim_add` | `shim_add alias cmd script proj desc` | Enregistre un nouvel outil dans le registre des shims |
| `openz` | `openz` | Ouvre (ou rejoint) les onglets docs + Claude du workspace `openz_uss-mirror` dans la fenêtre Kitty courante |
| `openz-stop` | `openz-stop` | Ferme les onglets docs + Claude du workspace `openz_uss-mirror` (instance courante **et** fenêtre dédiée ouverte par `openz-new`) |
| `openz-new` | `openz-new` | Ouvre une nouvelle fenêtre Kitty dédiée, via le fichier de session `~/.config/kitty/openz_uss-mirror.session` |

Les fonctions `ai`, `explain` et `fix` (assistant Claude dans le terminal)
sont documentées dans [Claude Code > Assistant
terminal](../../../outils/claude-code/terminal.md).

### Workspace `openz_uss-mirror` — onglets Kitty pour docs et Claude

`openz` automatise l'ouverture de l'environnement de travail du projet
`~/workspaces/openz_uss-mirror` : un onglet `make docs` (serveur MkDocs) et
un onglet `claude` (session Claude Code), tous deux pilotés via le contrôle
à distance Kitty (`kitty @ ...`, voir [Kitty — contrôle à
distance](../../../outils/kitty/index.md#controle-a-distance-securise)).

```bash
openz        # ouvre les 2 onglets, ou rejoint ceux déjà ouverts
openz-stop   # ferme les 2 onglets
openz-new    # ouvre une nouvelle fenêtre Kitty dédiée (session pré-définie)
```

La détection « déjà ouvert » de `openz` interroge `kitty @ ls` :

```bash
kitty @ ls --match-tab "title:uss-mirror" >/dev/null 2>&1
```

`openz` et `openz-stop` doivent ensuite **cibler** un onglet précis pour
le focaliser ou le fermer (`kitty @ focus-tab` / `close-tab --match
title:...`).

!!! warning "Ne jamais `grep` la sortie complète de `kitty @ ls`"
    La première version de la détection faisait `kitty @ ls | grep -q
    "uss-mirror"`. Le JSON renvoyé par `kitty @ ls` contient bien plus que
    les titres d'onglets — notamment le `cwd` de chaque fenêtre. Résultat :
    **n'importe quel onglet ordinaire** (même titré simplement « bash »)
    dont le répertoire courant est `~/workspaces/openz_uss-mirror` (par
    exemple après un `cd` manuel dans le projet) faisait croire à `openz`
    que les onglets dédiés étaient déjà ouverts, alors qu'ils n'existaient
    pas — `openz` ne créait alors rien, silencieusement.

    **Solution retenue** : utiliser `kitty @ ls --match-tab
    "title:uss-mirror"` (voir la doc de l'option `--match-tab` exposée par
    `kitty @ ls`), qui ne filtre que sur le **titre** des onglets, jamais
    sur leur `cwd` ou le reste du JSON.

!!! warning "`kitty @ --match title:...` n'est pas un simple match littéral"
    Le `--match title:QUERY` de Kitty utilise son propre mini-langage
    d'expressions booléennes : un **espace** dans `QUERY` est interprété
    comme séparateur entre deux termes combinables (`and`/`or`), et des
    parenthèses non échappées sont interprétées comme un **groupe regex**.
    Un titre d'onglet comme `uss-mirror (claude)` (espace + parenthèses
    littérales) casse donc le matching — Kitty renvoie une erreur du genre
    `Error: No location specified before claude`, souvent masquée si le
    `stderr` est redirigé vers `/dev/null`.

    **Solution retenue ici** : utiliser un motif regex sans espace ni
    parenthèse littérale, par exemple `title:uss-mirror.*claude` plutôt que
    `title:uss-mirror (claude)`. Le titre affiché à l'écran (`--tab-title`)
    peut rester inchangé — seul le motif de `--match` doit être adapté.

`openz-new` lance un **second processus Kitty indépendant**
(`kitty --session ...`) plutôt qu'un onglet de l'instance courante. Sans
précaution, ce process hérite du terminal de contrôle du shell appelant :
ses logs internes (avertissements de config, erreurs de parsing du
protocole clavier…) s'impriment dans le shell d'origine, qui peut aussi
perdre la main sur son tty. D'où le détachement complet :

```bash
setsid kitty --session "$HOME/.config/kitty/openz_uss-mirror.session" \
    </dev/null >/dev/null 2>&1 &
disown
```

- `setsid` détache le nouveau process de la session de contrôle du
  terminal courant.
- `</dev/null >/dev/null 2>&1` coupe les flux hérités (plus de logs
  parasites).
- `disown` retire le job de la table des jobs du shell.

#### `openz-stop` face à la fenêtre dédiée `openz-new`

Une fenêtre ouverte par `openz-new` est un **process Kitty séparé**, avec
son propre socket de contrôle à distance (`/tmp/kitty-<pid>`, voir
[Kitty — contrôle à distance](../../../outils/kitty/index.md#controle-a-distance-securise)).
La commande `kitty @ close-tab` lancée depuis l'instance courante ne peut
donc pas atteindre ses onglets — `openz-stop` cherchait initialement à les
fermer via le socket par défaut et échouait silencieusement.

`openz-stop` repère maintenant ce process dédié via `pgrep`, puis ferme
tous ses onglets en ciblant explicitement son socket — ce qui éteint
proprement toute la fenêtre (Kitty quitte de lui-même une fois le dernier
onglet fermé, sans demande de confirmation bloquante) :

```bash
local pid
for pid in $(pgrep -f "^kitty --session.*openz_uss-mirror"); do
    kitty @ --to "unix:/tmp/kitty-$pid" close-tab --match all 2>/dev/null
done
```

!!! tip "Pourquoi `^` en début de motif `pgrep -f`"
    `pgrep -f` matche sur la ligne de commande complète du process. Sans
    ancrage `^kitty`, le motif peut matcher n'importe quel process dont
    la ligne de commande *contient* le texte recherché en argument — par
    exemple un shell wrapper qui reçoit ce motif comme chaîne littérale
    (cas vécu en debug avec l'outil Bash de Claude Code, dont chaque appel
    encapsule la commande dans un `bash -c "..."`). Ancrer sur `^kitty`
    garantit que seul un process dont la commande **commence** par
    `kitty --session` est sélectionné.

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

!!! info "État actuel (2026-07-05)"
    Le registre `~/.local/share/alm_tools/shims.tsv` n'existe pas encore —
    `tl` affiche "Aucun registre trouvé" et liste tous les scripts
    texte/script de `~/.local/bin` comme orphelins :

    | Script | Éligibilité à l'enregistrement |
    |--------|-------------------------------|
    | `wnp` | Artefact ancien (shim historique de `new-page.py`) — **à ne pas enregistrer**, voir le `CLAUDE.md` du dépôt `alm_notes` |
    | `vmforge` | Outil actif et documenté ([vmforge](../alm_tools/outils/vmforge.md)) — candidat légitime à `shim_add` |
    | `env` | Script résiduel de l'installeur uv — pas un outil personnel, à ne pas enregistrer |

    Hors du périmètre de la détection : les binaires compilés ELF (`uv`,
    `uvx`, `shai`, `mdbook`…) et les **liens symboliques** (`claude-switch`,
    `editor`, `zed-docs-update` — ce dernier est d'ailleurs un lien cassé
    vers l'ancien dépôt `alm_docs`).

---

## Convention `.functions/` : bin vs lib vs tools

Trois sous-répertoires, trois rôles disjoints — jamais mélangés dans le
dépôt :

| Répertoire | Contenu | Exécuté comment | Trait distinctif |
|---|---|---|---|
| **`bin/`** | Scripts Bash **autonomes** (`update_system.sh`, `vid2mp3.sh`, `claude-switch`...) | En sous-processus, directement ou via un alias/fonction qui les appelle par chemin absolu | Chaque script a son propre `#!/usr/bin/env bash` **et** `set -euo pipefail` — sûr, car une erreur n'affecte que ce sous-processus, jamais le shell interactif appelant |
| **`lib/`** | Bibliothèques à **sourcer** (`clean_path.sh`, `git_aliases.sh`) | Via `source ".../lib/xxx.sh"` puis appel explicite de la fonction qu'il définit | **Aucun** `set -euo pipefail` — un mode strict sourcé dans le shell interactif changerait son comportement global (une variable non définie ailleurs dans la session ferait planter le terminal). Ces fichiers ne font que déclarer des fonctions, sans effet de bord à la simple lecture |
| **`tools/`** | Scripts **Python** (`check_csv.py`, `manage_kvm.py`...) | Jamais appelés directement — toujours enveloppés par une fonction dans `.bash_functions` qui préfixe `uv run python3` (ou `uv run --with <dep> python3` pour une dépendance ponctuelle, ex. `gpgtool` → `--with python-gnupg`) | Le script Python n'a pas à gérer son propre venv ni ses dépendances : `uv run` s'en charge à la volée |

Cette séparation répond à une question simple avant d'ajouter quoi que ce
soit : *"ce nouveau code doit-il modifier l'état du shell qui l'appelle
(PATH, alias, fonctions), ou peut-il vivre dans son propre process ?"* Si
oui → `lib/` (sourcé). Si non et que c'est du Bash → `bin/`. Si c'est du
Python → `tools/`, avec un petit wrapper dans `.bash_functions`.

---

## Comment ajouter sans casser l'existant

### Exemple 1 — ajouter un alias `dc` pour `docker compose`

Un alias ne dépend jamais de l'ordre de chargement : c'est une simple
substitution de texte, résolue à la frappe de la commande, pas à sa
déclaration. Deux emplacements possibles selon la nature de l'alias :

- **Générique, aucune condition** → `.bash_aliases` :

    ```bash
    alias dc='docker compose'
    ```

- **Lié à un outil déjà testé dans `.bash_env`** (ex. un alias qui ne doit
  exister que si `docker` est installé) → à côté du bloc de l'outil
  correspondant dans `.bash_env`, à l'intérieur du même `if command -v ...`
  s'il y en a un déjà, ou dans un nouveau bloc gardé :

    ```bash
    if command -v docker >/dev/null 2>&1; then
      alias dc='docker compose'
    fi
    ```

Dans les deux cas : `source ~/.bashrc` (ou nouveau terminal) suffit à
activer l'alias. Aucun risque de casser l'existant tant que le nom choisi
n'entre pas en conflit avec un alias déjà défini plus loin dans la chaîne
de chargement (un alias redéfini plus tard **écrase** silencieusement le
précédent — pas d'erreur, juste le dernier qui gagne).

### Exemple 2 — ajouter une fonction `yt()` qui dépend de `yt-dlp`

Toutes les fonctions conditionnelles du dépôt suivent le même patron —
garder cette convention pour la cohérence et pour que `shims`/`tl` la
détecte correctement :

```bash
# Dans .bash_functions, section appropriée (ou nouvelle section ##)
if command -v yt-dlp >/dev/null 2>&1; then
  # Télécharge une vidéo en 1080p max — usage : yt <url>
  yt() {
    yt-dlp -f 'bv*[height<=1080]+ba/b[height<=1080]' "$1"
  }
fi
```

Points d'attention avant d'ajouter :

- **Si la fonction a besoin d'une variable exportée par `.bash_env`**
  (comme `ipy`/`jl` avec `$SANDBOX_HOME`), c'est sûr de le faire dans
  `.bash_functions` : ce fichier est **toujours** sourcé après `.bash_env`
  dans `~/.bashrc` (voir [Chaîne de chargement](#chaine-de-chargement)).
  L'inverse — une fonction de `.bash_env` qui dépendrait d'une variable
  définie seulement dans `.bash_functions` — ne fonctionnerait **pas** :
  ce serait le seul cas où l'ordre casse réellement quelque chose.
- **Ne pas dupliquer une garde déjà faite plus haut.** Si l'outil est déjà
  testé ailleurs dans le même fichier (ex. un bloc `if command -v
  yt-dlp` existant), ajouter la fonction à l'intérieur de ce bloc plutôt
  que d'en ouvrir un second.
- **Si la fonction appelle un script externe** (Python via `tools/`, ou
  un exécutable de `bin/`), toujours passer par le chemin absolu
  `$HOME/.functions/...` — jamais un chemin relatif, la fonction doit
  marcher depuis n'importe quel répertoire courant.

---

## Configuration FZF — `.fzfrc`

| Paramètre | Valeur |
|-----------|--------|
| Hauteur | 45 % |
| Disposition | Inversée (en haut de l'écran) |
| Sélection multiple | Activée |
| Navigation cyclique | Activée |
| Prévisualisation | `bat` à droite, largeur 60 % |
| Raccourci bas | `Ctrl+J` |
| Raccourci haut | `Ctrl+K` |

### Raccourcis clavier FZF

`.bash_env` active l'intégration shell via `eval "$(fzf --bash)"` (fzf
upstream ≥ 0.48 ; repli sur les fichiers `key-bindings.bash` /
`completion.bash` si absent), ce qui ajoute trois raccourcis globaux dans le
shell — utilisables dans n'importe quelle commande, pas seulement avec les
alias `f*` ci-dessous :

| Raccourci | Effet |
|-----------|-------|
| `Ctrl+T` | Ouvre FZF et insère le(s) chemin(s) sélectionné(s) à la position du curseur |
| `Ctrl+R` | Recherche floue dans l'historique des commandes |
| `Alt+C` | Ouvre FZF sur les sous-répertoires et `cd` dans celui sélectionné |

### Alias FZF — `.bash_env` (bloc FZF)

| Alias | Commande | Description |
|-------|----------|-------------|
| `ff` | `fzf` | Lance FZF brut sur le répertoire courant |
| `fz` | `fzf --bind "enter:become(zed {+})"` | Sélectionne un fichier via FZF et l'ouvre dans Zed |
| `fn` | `fzf --bind "enter:become(nano {+})"` | Idem, ouverture dans Nano |
| `fh` | `history \| fzf --tac --no-sort` | Recherche floue dans l'historique (alternative à `Ctrl+R`) |
| `fs` | `rg --files \| fzf --preview 'bat ...'` | Recherche un fichier avec aperçu `bat` coloré |

`fcd` (recherche un sous-répertoire et s'y déplace) est une **fonction**
définie dans le même bloc, pas un alias.

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

Supprime les entrées dupliquées dans `$PATH` et place `~/.local/bin` et
`/snap/bin` en tête. Appelée en avant-dernier bloc de `.bash_env` (ordre
15) — voir [Pourquoi cet ordre
compte](#pourquoi-cet-ordre-compte-dependances-implicites-verifiees) pour
la liste exacte des blocs qui modifient le PATH avant elle, et pourquoi sa
position n'est pas structurellement garantie.
