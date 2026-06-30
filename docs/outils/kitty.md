# Kitty

**Kitty** est un émulateur de terminal GPU-accelerated, extensible via Python
et piloté intégralement depuis le clavier. C'est le terminal par défaut de
l'environnement `alm_dots`.

**Configuration :** `~/alm_dots/.config/kitty/kitty.conf` (stowé → `~/.config/kitty/kitty.conf`)

!!! tip "Intégration Claude AI"
    Les raccourcis `kitty_mod+a/x/s` permettent d'analyser le terminal avec Claude directement
    depuis Kitty. Voir [Claude — Assistant terminal](claude-code/terminal.md).

---

## Raccourcis clavier

`kitty_mod` = `Ctrl+Shift` (valeur par défaut non modifiée).

### Navigation

| Raccourci | Action |
|-----------|--------|
| `Ctrl+1` … `Ctrl+4` | Aller à l'onglet 1 … 4 |
| `kitty_mod+(` | Fenêtre précédente (panneau) |
| `kitty_mod+)` | Fenêtre suivante (panneau) |
| `kitty_mod+z` | Basculer le layout Stack (plein écran d'un panneau) |

### Lancement rapide

| Raccourci | Action |
|-----------|--------|
| `kitty_mod+F11` | Nouvel onglet → `btop` |
| `kitty_mod+F12` | Nouvel onglet → `yazi` |
| `kitty_mod+F1` | Nouvel onglet → launcher SSH interactif (VMs KVM) |

### Clipboard et URL

| Raccourci | Action |
|-----------|--------|
| `kitty_mod+c` | Copier dans le presse-papiers |
| `kitty_mod+v` | Coller depuis le presse-papiers |
| `kitty_mod+u` | Ouvrir l'URL sous le curseur dans le navigateur |
| `kitty_mod+r` | Renommer l'onglet courant |

### Hints kitten

Le **hints kitten** est l'une des fonctions les plus puissantes de Kitty.
Il détecte et met en surbrillance des éléments dans l'output du terminal
(URLs, chemins, hashes) et permet de les ouvrir ou de les insérer dans le
prompt en un raccourci.

| Raccourci | Action |
|-----------|--------|
| `kitty_mod+e` | Ouvrir une URL visible avec le navigateur par défaut |
| `kitty_mod+p` | Sélectionner un chemin de fichier → inséré dans le prompt |
| `kitty_mod+h` | Sélectionner un hash git → inséré dans le prompt |

**Exemple d'usage de `kitty_mod+p` :**

```
$ ls -la
drwxr-xr-x  ~/alm_notes/docs/outils/kitty.md

# kitty_mod+p met en surbrillance tous les chemins détectés
# Appuyer sur la lettre indiquée → insère le chemin dans le prompt courant
$ vim ~/alm_notes/docs/outils/kitty.md   ← inséré automatiquement
```

**Exemple d'usage de `kitty_mod+h` :**

```
$ git log --oneline
a1b2c3d  docs: update kitty config
e4f5g6h  feat: add gnome-settings module

# kitty_mod+h surligne les hashes
# Sélectionner a1b2c3d → git show a1b2c3d inséré dans le prompt
```

---

## Fonctionnalités notables

### Sélection automatique (`copy_on_select clipboard`)

Tout texte sélectionné à la souris est immédiatement copié dans le
presse-papiers système. Pas besoin de `Ctrl+C` après une sélection.

### Sélection de mots intelligente

Double-clic sur un token sélectionne l'ensemble du mot en incluant les
caractères `@-./_~?&=%+#`. Cela permet de sélectionner :

- des URLs complètes : `https://github.com/user/repo`
- des chemins : `~/alm_dots/.config/kitty/kitty.conf`
- des variables shell : `$HOME`, `${MY_VAR}`
- des tokens de code : `my_function`, `@decorator`

### Confirmation avant collage (`paste_actions`)

Si le texte à coller est volumineux, Kitty demande confirmation avant de
l'injecter dans le terminal. Protège contre les collages accidentels de
scripts ou de commandes dangereuses.

Les URLs sont automatiquement quotées si elles sont collées à un prompt
shell, évitant les problèmes d'interprétation des caractères spéciaux.

### Notification de fin de commande (`notify_on_cmd_finish`)

Quand une commande tourne dans un onglet non actif depuis plus de 10 secondes,
une notification desktop est envoyée à la fin. Utile pour les compilations,
les `make all`, les téléchargements.

```bash
# Lance une compilation longue dans l'onglet courant
make all
# Passer sur un autre onglet — une notification arrivera à la fin
```

### Contrôle à distance sécurisé

`allow_remote_control socket-only` + `listen_on unix:/tmp/kitty-{kitty_pid}`

Kitty expose un socket Unix par instance. Les commandes `kitty @` (comme
le launcher SSH) passent par ce socket. Aucun processus *dans* le terminal
ne peut piloter Kitty sans y avoir accès explicitement.

```bash
# Lister les fenêtres ouvertes (depuis le même socket)
kitty @ ls

# Envoyer du texte à une fenêtre spécifique
kitty @ send-text --match title:btop "q"
```

!!! warning "`--match title:QUERY` n'est pas un match littéral"
    `QUERY` passe par le mini-langage d'expressions booléennes de Kitty :
    un espace y sépare deux termes combinables (`and`/`or`), et des
    parenthèses non échappées sont lues comme un groupe regex. Un titre
    d'onglet contenant un espace ou des parenthèses littérales (ex.
    `uss-mirror (claude)`) casse donc le matching. Préférer un motif sans
    espace ni parenthèse, ex. `title:uss-mirror.*claude`. Voir l'exemple
    concret dans [Environnement shell — workspace
    openz_uss-mirror](../systeme/ubuntu/alm_dots/environnement-shell.md#workspace-openz_uss-mirror-onglets-kitty-pour-docs-et-claude).

### Scrollback enrichi

`scrollback_pager less --chop-long-lines --RAW-CONTROL-CHARS +INPUT_LINE_NUMBER`

- `--chop-long-lines` : les lignes longues sont tronquées (pas de retour à la ligne)
- `--RAW-CONTROL-CHARS` : les couleurs ANSI sont preservées dans le scrollback
- `+INPUT_LINE_NUMBER` : positionne `less` à la dernière ligne visible

### Layouts

`enabled_layouts Tall, *` — le layout **Tall** divise la fenêtre verticalement
(une colonne principale large à gauche, les autres à droite). `*` active tous
les autres layouts.

`kitty_mod+z` bascule le layout **Stack** : la fenêtre active passe en plein
écran, les autres sont cachées. Deuxième appui : retour au layout précédent.

---

## Thème Catppuccin Macchiato

Le thème est chargé depuis un fichier externe :

```
include current-theme.conf
```

Pour changer de thème :

```bash
# Lister les thèmes disponibles
kitty +kitten themes

# Appliquer un thème et l'enregistrer dans current-theme.conf
kitty +kitten themes --reload-in=all Catppuccin-Macchiato
```

La couleur de bordure active (`#c6a0f6`) est alignée manuellement sur la
lavande du thème Catppuccin Macchiato.

---

## Nerd Fonts et icônes

```
symbol_map U+23FB-U+23FE,U+2665,...  FiraCode Nerd Font Mono
```

Les plages Unicode des icônes Nerd Fonts sont redirigées vers la variante
**Mono** de FiraCode. Cette variante a une largeur fixe d'1 cellule pour
les icônes — la variante normale peut produire des icônes trop larges qui
décalent l'alignement dans Yazi, Starship ou btop.

---

## Launcher SSH interactif (`kitty_mod+F1`)

Script `~/.config/kitty/kittens/ssh_alpinelinux.sh` :

1. Demande le nom d'utilisateur SSH (défaut : compte courant)
2. Liste les VMs KVM en cours d'exécution avec leur IP via `virsh`
3. Ouvre un nouvel onglet Kitty et se connecte en SSH à la VM choisie

Prérequis : `libvirt` installé et les VMs démarrées (voir [vmforge](../systeme/ubuntu/alm_tools/outils/vmforge.md)).

---

## Référence des options principales

| Option | Valeur | Effet |
|--------|--------|-------|
| `allow_remote_control` | `socket-only` | Contrôle via socket uniquement |
| `listen_on` | `unix:/tmp/kitty-{kitty_pid}` | Socket par instance |
| `cursor_shape` | `beam` | Curseur en barre fine |
| `cursor_blink_interval` | `0` | Pas de clignotement |
| `copy_on_select` | `clipboard` | Copie auto à la sélection |
| `mouse_hide_wait` | `3.0` | Cache la souris après 3s |
| `select_by_word_characters` | `@-./_~?&=%+#` | Sélection de tokens complets |
| `strip_trailing_spaces` | `smart` | Supprime espaces trailing à la copie |
| `paste_actions` | `quote-urls-at-prompt,confirm-if-large` | Sécurité au collage |
| `notify_on_cmd_finish` | `unfocused 10` | Notif après 10s en arrière-plan |
| `confirm_os_window_close` | `-1` | Confirme toujours avant fermeture |
| `background_opacity` | `0.9` | Légère transparence |
| `scrollback_lines` | `10000` | Historique étendu |
| `remember_window_size` | `yes` | Retient la dernière taille |
| `tab_bar_min_tabs` | `2` | Barre visible seulement si 2+ onglets |
| `disable_ligatures` | `never` | Ligatures toujours actives |
