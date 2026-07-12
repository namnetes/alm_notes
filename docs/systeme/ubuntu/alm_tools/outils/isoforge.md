# isoforge

`isoforge` crée et gère des machines virtuelles **Ubuntu Desktop** sous KVM via
**autoinstall** (Subiquity) — le pendant de [vmforge](vmforge.md) pour un
desktop complet plutôt qu'un serveur Alpine minimal.

**Source :** `~/alm_tools/cli/isoforge`

!!! info "isoforge vs vmforge"
    Même famille d'outils, même style de commandes, mais deux cas d'usage
    différents : vmforge crée des VMs Alpine légères en quelques secondes
    (image cloud pré-installée, disque Copy-on-Write) — utile pour tester un
    script rapidement. isoforge installe une vraie Ubuntu Desktop depuis zéro
    (~10 minutes, autoinstall complet, disque autonome sans backing store) —
    utile pour tester un process de postinstallation ou une régression GNOME
    dans des conditions représentatives d'un vrai poste.

---

## Prérequis

Identiques à vmforge — installés automatiquement par `sudo make system` :
`qemu-kvm`, `libvirt-daemon-system`, `libvirt-clients`, `cloud-image-utils`, `acl`.

```bash
sudo usermod -aG libvirt,kvm $USER
```

---

## Installation

```bash
cd ~/alm_tools/cli/isoforge

# Mode utilisateur (défaut) — shim dans ~/.local/bin, pas de sudo
bash install.sh

# Mode système — shim dans /usr/local/bin, requiert sudo
sudo bash install.sh system
```

Contrairement à vmforge, **pas de mode `apparmor`** : isoforge n'a pas eu
besoin de règle AppArmor locale après test réel — voir
[AppArmor : un DENIED bénin, non corrigé](#apparmor-un-denied-benin-non-corrige)
plus bas.

## Désinstallation

```bash
cd ~/alm_tools/cli/isoforge
bash uninstall.sh              # utilisateur
sudo bash uninstall.sh system  # système
```

!!! info "Données non supprimées"
    ```bash
    rm -rf ~/.local/share/isoforge
    rm -f  ~/alm_tools/cli/isoforge/lib/images/ubuntu-*.iso
    ```

---

## Utilisation rapide

```bash
# 1. Télécharger l'ISO Ubuntu Desktop de base (une seule fois, ~6 Go)
isoforge base list

# 2. Créer une VM (autoinstall complet, ~10 min sans intervention)
isoforge create ma-vm

# 3. Snapshot juste après l'installation — évite de repasser par
#    l'autoinstall à chaque cycle de test
isoforge snapshot create ma-vm pristine

# 4. Se connecter en SSH
isoforge ssh ma-vm

# 5. Revenir à l'état pristine après un test destructeur
isoforge snapshot revert ma-vm pristine

# 6. Supprimer quand inutile
isoforge delete ma-vm
```

---

## Commandes

| Commande | Description |
|----------|-------------|
| `isoforge create <nom> [options]` | Créer et installer une VM Ubuntu Desktop (`--vcpus`, `--ram`, `--disk`, `--network`, `--ssh-key`, `--user`, `--autologin`) |
| `isoforge list` | Lister toutes les VM |
| `isoforge ssh <nom> [-- args]` | Se connecter en SSH |
| `isoforge ip <nom>` | Afficher l'IP de la VM |
| `isoforge start <nom>` | Démarrer une VM arrêtée |
| `isoforge stop <nom>` | Arrêter proprement une VM |
| `isoforge delete <nom>` | Supprimer une VM (confirmation requise) |
| `isoforge inventory` | Afficher l'inventaire Ansible au format INI |
| `isoforge snapshot create <vm> [nom]` | Créer un snapshot (nom auto : `snap-AAAAMMJJ-HHMMSS`) |
| `isoforge snapshot list <vm>` | Lister les snapshots d'une VM |
| `isoforge snapshot revert <vm> <nom>` | Revenir à l'état d'un snapshot |
| `isoforge snapshot delete <vm> <nom>` | Supprimer un snapshot |
| `isoforge base list` | Lister les ISO Ubuntu Desktop disponibles et en télécharger une |
| `isoforge base download` | Télécharger l'ISO définie dans `configs/defaults.conf` |
| `isoforge base status` | Vérifier la présence de l'ISO de base |
| `isoforge help` | Aide complète |

`--autologin` active l'auto-login GDM (désactivé par défaut — un outil qui
teste un process de postinstallation gagne à exiger une authentification
explicite plutôt qu'à la masquer, sauf besoin ponctuel d'une session desktop
automatique, ex. pour tester GSConnect après reboot).

---

## Caractéristiques

- Autoinstall Subiquity complet, sans interaction (`interactive-sections: []`)
- Disque qcow2 **autonome**, pas de backing store COW (contrairement à
  vmforge/Alpine) — chaque VM subit son propre autoinstall complet, d'où
  l'intérêt du snapshot juste après installation pour éviter de le
  répéter à chaque cycle de test
- Snapshots libvirt (`create`/`list`/`revert`/`delete`) pour un cycle
  create → test → revert rapide
- Clé SSH d'automatisation dédiée (`~/.ssh/vm-automation_ed25519`, sans
  passphrase ni hardware token) — une clé personnelle sécurisée par une
  security key FIDO2 casserait l'attente SSH en arrière-plan, qui tourne
  sans personne pour confirmer le tap physique

---

## Bugs de templating rencontrés en le construisant

**Leçon générale, réutilisable au-delà d'isoforge** : toute substitution
multi-couches bash → YAML → `sed`-dans-la-VM est fragile dès qu'un
caractère spécial à une couche est aussi significatif à la couche
suivante. Éviter les métacaractères (`\`, `[`, `]`, newline littérale…)
dans le texte injecté par substitution, ou à défaut tester en conditions
réelles plutôt que de faire confiance à la logique du motif — les trois
cas ci-dessous ont chacun d'abord semblé corrects sur le papier.

### Newline littérale vs `\n` dans le `sed` de génération

`cmd_create` construit le YAML `user-data` autoinstall via un `sed -e
"s|__AUTOLOGIN_LATE_COMMANDS__|${autologin_late_cmd}|g"`. Une vraie
newline **embarquée** dans `${autologin_late_cmd}` casse la commande `sed`
elle-même (`commande s inachevée`) — `sed` interprète chaque newline du
texte de remplacement comme une fin d'instruction, pas comme un simple
caractère à insérer.

**Correctif** : `\n` **littéral** (deux caractères, backslash + n) dans la
variable bash, que `sed` interprète correctement comme séparateur de ligne
dans le texte de remplacement — même pattern déjà utilisé par vmforge pour
`__SHARE_RUNCMDS__`.

### Antislashs perdus à travers le `sed` de génération

Première tentative pour activer l'auto-login GDM : insérer une ligne après
`[daemon]` dans `/etc/gdm3/custom.conf`, via un motif `sed` échappé
(`\[daemon\]`, `\s*`) exécuté **dans la VM** au moment du `curtin
in-target`. Deux échecs constatés en testant réellement :

1. `\[daemon\]` traverse le `sed` de génération (celui qui construit le
   YAML, côté hôte) et **perd ses antislashs** — le texte de remplacement
   devient `[daemon]` tel quel, qui pour `sed` est une **classe de
   caractères** (« d », « a », « e », « m », « o », « n »), pas une
   séquence littérale. Zéro substitution côté VM.
2. `\s*` subit le même sort → `s*`, motif tout aussi cassé.

**Correctif** : abandonner l'insertion après `[daemon]` au profit d'une
correspondance **littérale exacte**, sans aucun antislash, sur les lignes
toggle déjà présentes dans le `custom.conf` par défaut d'Ubuntu Desktop
(testé sur 24.04.4) : `#  AutomaticLoginEnable = true` /
`#  AutomaticLogin = user1` → décommentées telles quelles.

### `--diskspec` aurait visé le mauvais disque

`cmd_snapshot create` n'utilise **aucun** `--diskspec` explicite —
volontairement. Testé en réel : `virsh snapshot-create-as` exclut déjà
tout seul le cdrom du seed (`device=cdrom` → `snapshot='no'` automatique)
et ne snapshotte que le disque qcow2 réel. Un `--diskspec sda=...`
explicite aurait d'ailleurs ciblé le **mauvais** disque : avec l'ordre
`--disk path=...,bus=virtio` puis `--disk device=cdrom` utilisé par
`cmd_create`, le disque principal est nommé `vda` et c'est le **cdrom**
qui hérite de `sda` — l'inverse de ce qu'on voudrait cibler.

### AppArmor : un DENIED bénin, non corrigé

`install.sh` n'ajoute **aucune** règle AppArmor, contrairement à vmforge.
Un cycle complet (`create` → `snapshot create/revert` → suppression) a été
testé sans aucune règle : le profil `virt-aa-helper` se voit bien refuser
la lecture du disque de la VM à chaque (re)démarrage de domaine (règle
`deny @{HOME}/.*/** mrwkl,` codée en dur dans le profil système, qui
bloque tout sous-dossier caché de `$HOME`), mais sans impact fonctionnel
observé — `virt-aa-helper` dégrade proprement plutôt que de bloquer.
Corriger nécessiterait d'éditer un fichier profil système livré par le
paquet libvirt (pas un point d'extension `local/` prévu pour ça) — pour un
bénéfice nul actuellement. Détail complet, y compris la commande de
vérification à rejouer si le comportement change un jour :
[`cli/isoforge/README.md`](https://github.com/namnetes/alm_tools/blob/main/cli/isoforge/README.md#apparmor--pas-de-r%C3%A8gle-locale-denied-connu-et-sans-impact).

---

## Documentation interne

| Document | Sujet |
|----------|-------|
| [README.md](https://github.com/namnetes/alm_tools/blob/main/cli/isoforge/README.md) | Vue d'ensemble, spike de faisabilité, AppArmor |
| [BACKLOG.md](https://github.com/namnetes/alm_tools/blob/main/postinstall/BACKLOG.md) | Bugs postinstall trouvés en testant avec isoforge |
