# Tirer le meilleur parti de Kitty

Kitty n'est pas qu'un émulateur rapide : c'est un terminal **pilotable au
clavier de bout en bout**, avec une intégration shell qui comprend où sont
les prompts, les sorties de commandes et les objets affichés (URLs,
chemins, hashes). Cette page montre, exemple par exemple, comment
exploiter tout ça au quotidien. La configuration correspondante est
décrite dans la [référence](index.md).

`kitty_mod` = ++ctrl+shift++ (défaut).

---

## Naviguer dans l'historique comme dans un fichier

### Le scrollback dans `less` — ++ctrl+shift+h++

Ouvre **tout l'historique du terminal** dans `less`, couleurs comprises.
On y retrouve les réflexes habituels :

| Touche | Effet |
|--------|-------|
| ++slash++ `motif` | Rechercher vers le haut de l'écran |
| ++n++ / ++shift+n++ | Occurrence suivante / précédente |
| ++g++ / ++shift+g++ | Début / fin de l'historique |
| ++q++ | Quitter et revenir au terminal |

Grâce à `scrollback_pager_history_size 10`, le pager remonte sur
**~10 Mo d'historique** — bien au-delà des 10 000 lignes affichables à
l'écran. Retrouver une erreur d'un `make` lancé il y a deux heures ne
demande plus de re-exécuter quoi que ce soit.

### Sauter de prompt en prompt — ++ctrl+shift+k++ / ++ctrl+shift+j++

L'intégration shell marque chaque prompt. Plutôt que de scroller à la
molette, ces raccourcis (style vim : `k` monte, `j` descend) sautent
**directement à la commande précédente / suivante** dans le scrollback —
la sortie d'une longue commande se traverse d'un seul coup.

### Revoir la dernière sortie — ++ctrl+shift+g++

Affiche dans le pager **uniquement la sortie de la dernière commande**.
Idéal après un `pytest` ou un `make` verbeux : pas besoin de chercher où
commençait la sortie.

```bash
uv run pytest          # 300 lignes défilent…
# ctrl+shift+g → seule la sortie de pytest, dans less, recherche incluse
```

---

## Hints — attraper ce qui est à l'écran sans la souris

Le principe est toujours le même : le raccourci **surligne les éléments
détectés** à l'écran, chaque élément reçoit une lettre, taper la lettre
déclenche l'action.

### URLs — ++ctrl+shift+e++

Surligne toutes les URLs visibles et ouvre celle choisie dans le
navigateur. Fonctionne sur la sortie de `git push` (lien « Create a pull
request »), les messages d'erreur avec lien vers une doc, etc.

### Chemins → prompt — ++ctrl+shift+p++

```console
$ uv run ruff check .
docs/macros.py:12:5: F841 Local variable `unused` is assigned but never used

# ctrl+shift+p surligne docs/macros.py → la lettre l'insère dans le prompt
$ zed docs/macros.py
```

### Hashes git → prompt — ++ctrl+shift+y++

```console
$ glg
b006261 docs(gdm): adopt centered-lowered login box
19efd75 docs(gdm): add ImageMagick image-prep page

# Taper « git show », ctrl+shift+y, choisir le hash → il complète la ligne
$ git show b006261
```

### `fichier:ligne` → Zed — ++ctrl+shift+o++

Le plus productif des quatre : toute référence `fichier:ligne` (sortie de
`ruff`, traceback Python, `grep -n`, `git grep -n`…) s'ouvre
**directement dans Zed à la bonne ligne** :

```console
$ uv run ruff check .
new-page.py:57:9: E722 Do not use bare `except`

# ctrl+shift+o, choisir la référence → Zed s'ouvre sur new-page.py ligne 57
```

!!! tip "Ça marche aussi sur les tracebacks"
    ```
    File "/home/galan/alm_notes/new-page.py", line 212, in main
    ```
    est détecté comme les autres formats — un traceback Python se
    remonte fichier par fichier sans jamais copier-coller un chemin.

---

## Splits — découper l'écran façon IDE

Le layout **Splits** autorise un découpage libre : chaque fenêtre peut
être coupée horizontalement ou verticalement, comme dans un IDE.

- ++ctrl+shift+l++ — cycler les layouts (Tall → Splits → …) ;
- ++ctrl+shift+d++ — nouvelle fenêtre en **split du panneau courant**,
  ouverte dans le répertoire courant (en layout Tall, la position est
  ignorée : la fenêtre s'ajoute normalement) ;
- ++ctrl+shift+r++ — mode redimensionnement (flèches pour ajuster,
  ++enter++ pour valider) ;
- `kitty_mod+(` / `kitty_mod+)` — circuler entre les panneaux ;
- ++ctrl+shift+z++ — zoom Stack : le panneau actif passe plein écran,
  deuxième appui pour revenir.

Session type « édition + serveur + logs » dans un seul onglet :

```
┌───────────────────────────┬──────────────────┐
│                           │ make docs-start  │
│  éditeur / commandes      ├──────────────────┤
│                           │ mkl (logs -f)    │
└───────────────────────────┴──────────────────┘
```

---

## Travailler dans le répertoire courant

Par défaut, ++ctrl+shift+enter++ (nouvelle fenêtre) et ++ctrl+shift+t++
(nouvel onglet) démarrent dans `$HOME`. Les deux sont remappés avec
`launch --cwd=current` : le nouveau shell démarre **là où on
travaille**. Au milieu d'un projet, un deuxième shell sur le même
répertoire coûte un seul raccourci.

---

## Markers — surligner les erreurs dans un flux

++ctrl+shift+m++ active/désactive le surlignage de `error` (couleur 1)
et `warn` (couleur 2), insensible à la casse, sur tout ce qui s'affiche.
C'est fait pour le suivi de logs en continu :

```bash
mkl                      # journalctl --user -u mkdocs.service -b -f
# ctrl+shift+m → chaque ERROR/WARN qui défile est surligné
```

Les couleurs des trois groupes de marks sont définies par le thème
(`mark1_background`…, ici les tons Catppuccin). Un deuxième appui
désactive le marker.

---

## Broadcast — un clavier, toutes les fenêtres

++ctrl+shift+f9++ ouvre une fenêtre spéciale : **tout ce qui y est tapé
est répété dans toutes les fenêtres** de l'instance Kitty. Cas d'usage
typique avec plusieurs VMs :

1. Ouvrir un onglet, le splitter en 3 (++ctrl+shift+d++), une connexion
   SSH par panneau (launcher ++ctrl+shift+f1++) ;
2. ++ctrl+shift+f9++ → taper `sudo apk upgrade` : la commande part sur
   les trois VMs à la fois ;
3. Fermer la fenêtre broadcast pour reprendre la main panneau par
   panneau.

---

## kitten ssh — SSH sans friction

`kitten ssh` remplace `ssh` et corrige les deux plaies du SSH depuis un
terminal moderne :

- il **copie le terminfo `xterm-kitty`** sur l'hôte distant — sans ça,
  Alpine (et d'autres distributions minimales) ne connaît pas le
  terminal : touches fléchées cassées, `clear` erratique, `TERM unknown` ;
- il embarque l'**intégration shell** (sauts de prompt, dernière sortie…)
  qui fonctionne alors aussi à distance.

```bash
kitten ssh galan@192.168.122.34    # à la place de ssh
```

Le [launcher SSH](index.md#launcher-ssh-interactif-kitty_modf1)
(++ctrl+shift+f1++) l'utilise désormais automatiquement pour les VMs
Alpine.

---

## kitten diff — diffs côte à côte

Déjà branché dans `~/.gitconfig` (`[difftool "kitty"]`) avec les alias
maison :

```bash
gdt                    # git difftool : diff côte à côte, coloré, dans Kitty
gdts                   # git difftool --staged
kitten diff a.py b.py  # comparer deux fichiers hors git
```

Navigation dans le diff : ++j++ / ++k++ pour défiler, ++n++ / ++p++
pour changer de fichier, ++q++ pour quitter.

---

## Petits gestes qui changent tout

| Raccourci | Effet |
|-----------|-------|
| ++ctrl+shift+alt+t++ | Renommer l'onglet courant |
| ++ctrl+shift+u++ | Insérer un caractère Unicode (recherche par nom : `arrow`, `check`…) |
| ++ctrl+shift+f5++ | **Recharger `kitty.conf`** sans fermer le terminal |
| ++ctrl+shift+f11++ | Onglet `btop` |
| ++ctrl+shift+f12++ | Redémarrer `mkdocs.service` (overlay de confirmation) |
| Double-clic | Sélectionne un token complet (URL, chemin, `$VAR`) |
| Sélection souris | Copie automatique (`copy_on_select clipboard`) |

---

## Ce que la 0.47 apporte (vs le 0.32 d'apt)

Le passage aux [binaires upstream](index.md#installation) saute ~15
versions d'un coup. L'essentiel, trié par impact ici :

### Actif sans rien faire

| Nouveauté | Version | Effet |
|-----------|---------|-------|
| **Palette de commandes** ++ctrl+shift+f3++ | 0.46 | Toutes les actions Kitty (mappées ou non) cherchables au clavier — le « Ctrl+Shift+P » du terminal, parfait pour retrouver un raccourci oublié |
| **Rechargement auto de la config** | 0.47 | `kitty.conf` sauvegardé = appliqué immédiatement à toutes les fenêtres (++ctrl+shift+f5++ devient un secours) |
| **Splits à la souris** | 0.46 | Les bordures entre panneaux se déplacent à la souris — complète ++ctrl+shift+r++ |
| **Onglets à la souris** | 0.46 | Glisser pour réordonner, détacher vers une autre fenêtre OS |
| **Scrollbar + défilement cinétique** | 0.43 / 0.46 | Barre de défilement discrète dans le scrollback, inertie au touchpad |
| **Parsing SIMD** | 0.33 | ×2 sur le traitement des flux — visible sur un `cat` de gros fichier ou des logs rapides |
| **Fractional scaling Wayland** | 0.34 | Rendu au pixel près sans redimensionnement compositeur |

### À activer si l'envie vient

- **`cursor_trail`** (0.37) — traînée animée du curseur sur les grands
  sauts. La valeur est un délai en millisecondes de stabilité avant
  que l'animation ne se déclenche :

    ```
    cursor_trail 3
    ```

- **Terminal flottant style Quake** (0.42) — une fenêtre terminal qui
  apparaît/disparaît par-dessus le bureau :

    ```bash
    kitten quick-access-terminal
    ```

    À lier à un raccourci clavier **GNOME** (Paramètres → Clavier) pour
    l'avoir depuis n'importe quelle application.

- **Sélecteur de polices interactif** (0.36) — aperçu en direct des
  polices, variantes et *features* OpenType (stylistic sets FiraCode) :

    ```bash
    kitten choose-fonts
    ```

- **Notifications depuis un script** (0.36) — y compris à travers SSH :

    ```bash
    make docs-build && kitten notify "MkDocs" "Build terminé"
    ```

### À prendre en compte

!!! warning "Différences de comportement"
    - **La config se recharge toute seule** (0.47) : une édition de
      `kitty.conf` s'applique aussitôt à toutes les fenêtres 0.47 —
      plus de « je testerai au prochain lancement ».
    - **Fenêtres mixtes pendant la transition** : les fenêtres ouvertes
      avant la bascule tournent encore sur l'ancien binaire ; les
      nouvelles sont en 0.47. Rouvrir ses terminaux après la migration
      évite les surprises (`kitty @` entre versions notamment).
    - **Mises à jour désormais manuelles** : relancer l'installeur
      (section [Installation](index.md#installation)) — apt ne pousse
      plus rien.
    - `background_opacity` ne s'applique plus aux images de fond
      (0.43, breaking) — sans effet ici (`background_image none`).
    - Le flou d'arrière-plan (0.46) ne fonctionne que sous KDE — pas
      d'effet sur GNOME.

!!! info "Et l'API `kitty @` ?"
    Tout ce que font ces raccourcis est scriptable via le
    [contrôle à distance](index.md#controle-a-distance-securise) —
    c'est le mécanisme derrière le launcher SSH, la session `openz` et
    l'[assistant Claude](../claude-code/terminal.md).

!!! note "À venir"
    Les outils shell qui complètent Kitty (`eza`, `ripgrep`, `fzf`,
    `zoxide`…) auront leurs propres pages — cette page reste centrée
    sur ce que le terminal lui-même sait faire.
