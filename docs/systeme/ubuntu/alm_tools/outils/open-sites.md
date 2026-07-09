# open-sites

`open-sites` lance et gère une liste personnelle de pages de connexion à des sites.
Le fichier de données ne contient que deux colonnes (`nom`, `url`) — pas de mot de passe.

**Source :** `~/alm_tools/cli/open-sites`

---

## Prérequis

[`fzf`](https://github.com/junegunn/fzf) installé et dans le `PATH` — utilisé pour
choisir un site sans en taper le nom exact (`connect`, `remove`, `edit`). Le
picker affiche un panneau de prévisualisation avec l'URL du site survolé,
pour vérifier la cible avant de valider.

---

## Installation

**Usage normal** — installer depuis le dépôt :

```bash
cd ~/alm_tools
uv tool install ./cli/open-sites
```

**Mode développement** — les modifications du code source sont actives immédiatement :

```bash
cd ~/alm_tools/cli/open-sites
uv tool install --editable .
```

!!! warning "Après toute modification du code : réinstaller la commande globale"
    `uv tool install` fait une **copie figée** du code au moment de l'installation.
    La commande globale `open-sites` (celle utilisable depuis n'importe quel
    répertoire) ne reflète donc **pas** automatiquement les changements du
    code source — contrairement à `uv run open-sites` depuis le dossier du
    projet, toujours à jour. Après une modification :

    ```bash
    uv tool install --no-cache ~/alm_tools/cli/open-sites
    ```

    `--no-cache` seul suffit : il force la reconstruction du paquet et
    réinstalle par-dessus la version existante, pas besoin d'un
    `uv tool uninstall` séparé ni du flag `--force` en plus.

## Désinstallation

```bash
uv tool uninstall open-sites
```

Supprime le shim `~/.local/bin/open-sites` et l'environnement isolé
`~/.local/share/uv/tools/open-sites/`.

---

## Utilisation

```bash
# Lister tous les sites suivis
open-sites list

# Ouvrir un site directement par son nom
open-sites connect GitHub

# Ouvrir un site en le choisissant via fzf (nom omis)
open-sites connect

# Ouvrir tous les sites, un par un, en attendant Entrée entre chaque
open-sites loop

# Ajouter un site (rejete si le nom existe deja)
open-sites add Netflix https://www.netflix.com/login

# Retirer un site (fzf si le nom est omis, puis confirmation demandee)
open-sites remove

# Modifier le nom/URL d'un site (fzf si le nom est omis)
open-sites edit GitHub

# Pointer vers un autre fichier que celui par défaut
open-sites list --file /chemin/vers/autre.csv
```

---

## Options principales

| Option | Description |
|--------|-------------|
| `--file PATH` / `-f PATH` | Chemin du fichier CSV des sites (défaut : `data/open-sites.csv`) |
| `--version` / `-V` | Afficher la version et quitter |

---

## Robustesse et sécurité

- **`remove` demande toujours confirmation** (`y/N`, avec nom et URL affichés) avant de supprimer — y compris quand le site a été choisi via `fzf`.
- **`add` rejette un nom déjà existant** (insensible à la casse) ; **`edit` fait de même** si le nouveau nom entre en collision avec un autre site suivi — aucune des deux commandes ne peut créer un doublon silencieux.
- **`add` garde le fichier trié** alphabétiquement par nom après chaque insertion.
- **Fichier CSV absent** (ex. juste après une installation fraîche) : toutes les commandes le traitent comme une liste vide plutôt que de planter ; `add` crée le fichier (et son dossier parent `data/` si besoin) à la première écriture.
- **Doublons déjà présents** dans le fichier (édition manuelle) : un avertissement est affiché au chargement, la première occurrence trouvée est utilisée.
- **`connect`/`loop` rendent la main immédiatement** après avoir lancé le navigateur (`xdg-open` en sous-processus détaché, jamais d'attente sur le processus du navigateur).

---

## Fichier de données

`data/open-sites.csv` (2 colonnes : `nom;url`, texte brut) — **jamais commité**
(`.gitignore` du projet), car il révèle l'inventaire personnel de comptes
(banques, mutuelle, employeur...). Une réinstallation du poste réinstalle
l'outil mais **pas** ce fichier — à restaurer depuis sa propre sauvegarde.

### Sauvegarde et restauration du fichier

Chemin réel par défaut : `~/alm_tools/cli/open-sites/data/open-sites.csv`
— chemin absolu **fixe dans le code** (pas dérivé de l'emplacement du
script), pour continuer à fonctionner à l'identique que l'outil soit
lancé depuis les sources (`uv run open-sites`) ou installé globalement
(`uv tool install`), qui ne livre que le paquet, jamais le dossier
`data/` du dépôt.

#### Sauvegarde

```bash
# 1. Chiffrer le fichier avec un mot de passe
gpgtool
# 1 (Chiffrer), chemin : ~/alm_tools/cli/open-sites/data/open-sites.csv

# 2. Encoder en base64 pour pouvoir le coller dans une note texte
base64 -w0 ~/alm_tools/cli/open-sites/data/open-sites.csv.gpg \
  > ~/alm_tools/cli/open-sites/data/open-sites.csv.gpg.b64

# 3. Copier dans le presse-papiers
wl-copy < ~/alm_tools/cli/open-sites/data/open-sites.csv.gpg.b64
# (Xorg/XWayland : xclip -selection clipboard < ...)

# 4. Nettoyer le fichier temporaire une fois collé dans Proton Pass
rm ~/alm_tools/cli/open-sites/data/open-sites.csv.gpg.b64
```

| Commutateur | Rôle |
|--------------|------|
| `base64 -w0` | Désactive le retour à la ligne automatique tous les 76 caractères — le blob doit tenir sur une seule ligne collable dans un champ de note. |
| `wl-copy` / `xclip -selection clipboard` | Copie dans le presse-papiers "standard" (`Ctrl+V`) — respectivement Wayland et Xorg/XWayland. |

Créer une nouvelle **note sécurisée** Proton Pass titrée `open-sites.csv
— Comptes suivis`, et répartir le résultat dans deux emplacements
séparés :

| Emplacement | Contenu |
|-------------|---------|
| Corps de la note | Contenu de `open-sites.csv.gpg.b64` |
| Champ caché `Mot de passe GPG` (`+ Ajouter un champ` → type `Caché`) | Le mot de passe saisi à l'étape 1 |

!!! danger "Jamais les deux dans le même champ"
    Le blob seul ou le mot de passe seul ne permettent pas de retrouver
    le secret — c'est cette séparation qui protège le fichier (le base64
    n'est qu'un encodage, pas un chiffrement : il ne protège rien à lui
    seul). Détail du principe dans le runbook générique [Sauvegarde et
    restauration d'un secret](../../../../securite/proton/sauvegarde-restauration.md).

#### Restauration

```bash
cd ~/alm_tools && uv tool install ./cli/open-sites   # réinstalle l'outil

# Récupérer le blob base64 depuis la note Proton Pass, puis :
echo "<blob collé depuis Proton Pass>" \
  | base64 -d > ~/alm_tools/cli/open-sites/data/open-sites.csv.gpg

gpgtool
# 2 (Déchiffrer), chemin : ~/alm_tools/cli/open-sites/data/open-sites.csv.gpg
# mot de passe : celui stocké dans le champ caché de la note

open-sites list    # doit afficher la liste des sites restaurée
```

!!! tip "Note Proton Pass existante mal nommée"
    Si votre note s'appelle encore `Pass Tool (csv.file)`, renommez-la en
    `open-sites.csv — Comptes suivis` : le fichier sauvegardé appartient
    à `open-sites`, pas à `pass-tool` (qui n'a pas de fichier de données).

---

## Raccourci clavier (kitty)

Comme `connect`/`remove`/`edit`/`loop` sont interactifs (`fzf`, Entrée pour
continuer), ils ont besoin d'un vrai terminal. Dans `kitty.conf` :

```
map ctrl+alt+o launch --type=overlay open-sites connect
```

Ouvre une petite fenêtre overlay avec le picker `fzf` à chaque appui sur le raccourci.

---

## Complétion bash

Installée automatiquement par le module postinstall
[`install_open_sites.sh`](../postinstall/post-installation.md) : script généré
dans `~/.bash_completions/open-sites.sh`, sourcé depuis `.bashrc`. Complète à
la fois les sous-commandes (`list`, `connect`, `loop`, `add`, `remove`,
`edit`) et les options de chacune (interrogation dynamique du programme à
chaque appui sur Tab — reste à jour sans régénération si le code évolue).

---

Documentation complète : [cli/open-sites/README.md](https://github.com/namnetes/alm_tools/blob/main/cli/open-sites/README.md)
