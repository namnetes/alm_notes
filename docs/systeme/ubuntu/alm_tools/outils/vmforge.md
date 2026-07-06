# vmforge

`vmforge` crée et gère des machines virtuelles légères Alpine Linux sous KVM avec `cloud-init`.

**Source :** `~/alm_tools/cli/vmforge`

!!! tip "Après la création d'une VM"
    Une fois la VM démarrée, suivre le guide [Post-Installation Alpine](../../../../systeme/alpine/post-installation.md)
    pour configurer sudo, les paquets essentiels et le nom d'hôte.

---

## Prérequis

Installés automatiquement par `sudo make system` :
`qemu-kvm`, `libvirt-daemon-system`, `libvirt-clients`, `cloud-image-utils`, `acl`, `virtiofsd`.

L'utilisateur doit appartenir au groupe `libvirt` (effectif après déconnexion/reconnexion) :

```bash
sudo usermod -aG libvirt,kvm $USER
```

---

## Installation

```bash
cd ~/alm_tools/cli/vmforge

# Mode utilisateur (défaut) — shim dans ~/.local/bin, pas de sudo
bash install.sh

# Mode système — shim dans /usr/local/bin, requiert sudo
sudo bash install.sh system

# AppArmor seul — reconfigurer la règle libvirt-qemu
sudo bash install.sh apparmor
```

L'installateur effectue trois actions :

1. Crée un **shim** dans le répertoire cible (lien vers `bin/vmforge`)
2. Configure les **ACL** (`setfacl`) pour que `libvirt-qemu` accède aux images
3. Ajoute la **règle AppArmor** dans `/etc/apparmor.d/local/abstractions/libvirt-qemu`

## Désinstallation

```bash
cd ~/alm_tools/cli/vmforge
bash uninstall.sh              # utilisateur
sudo bash uninstall.sh system  # système
```

!!! info "Données non supprimées"
    La désinstallation ne supprime que le shim. Les VMs et l'image de base
    restent intactes. Pour tout supprimer :

    ```bash
    rm -rf ~/.local/share/vmforge
    rm -f  ~/alm_tools/cli/vmforge/lib/images/alpine-base.qcow2
    ```

---

## Utilisation rapide

```bash
# 1. Télécharger l'image Alpine de base (une seule fois)
vmforge base list

# 2. Créer une VM
vmforge create mon-serveur

# 3. Vérifier qu'elle tourne
vmforge list

# 4. Se connecter en SSH
vmforge ssh mon-serveur

# 5. Supprimer quand inutile
vmforge delete mon-serveur
```

---

## Commandes

| Commande | Description |
|----------|-------------|
| `vmforge create <nom> [options]` | Créer et démarrer une nouvelle VM (`--vcpus`, `--ram`, `--disk`, `--network`, `--ssh-key`, `--user`, `--share`) |
| `vmforge list` | Lister toutes les VMs |
| `vmforge ssh <nom> [-- args]` | Se connecter en SSH |
| `vmforge ip <nom>` | Afficher l'IP de la VM |
| `vmforge start <nom>` | Démarrer une VM arrêtée |
| `vmforge stop <nom>` | Arrêter proprement une VM |
| `vmforge delete <nom>` | Supprimer une VM (confirmation requise) |
| `vmforge apk <nom> [--packages f]` | Installer les paquets du fichier YAML (défaut : `lib/packages.yaml`) |
| `vmforge inventory` | Afficher l'inventaire Ansible au format INI |
| `vmforge base list` | Lister les 10 dernières versions Alpine et télécharger |
| `vmforge base download` | Télécharger la version définie dans `defaults.conf` |
| `vmforge base status` | Vérifier la présence de l'image de base |
| `vmforge help` | Aide complète |

---

## Caractéristiques

- Disques Copy-on-Write — empreinte disque minimale
- `cloud-init` pour la personnalisation au premier démarrage
- Injection automatique de la clé SSH `~/.ssh/id_ed25519.pub`
- Règles AppArmor pour l'isolation des processus libvirt

---

## Documentation interne

| Document | Sujet |
|----------|-------|
| [README.md](https://github.com/namnetes/alm_tools/blob/main/cli/vmforge/README.md) | Vue d'ensemble |
| [USAGE.md](https://github.com/namnetes/alm_tools/blob/main/cli/vmforge/USAGE.md) | Guide d'utilisation |
| `doc/01-concepts.md` | Architecture et concepts |
| `doc/02-installation.md` | Installation détaillée |
| `doc/03-configuration.md` | Options de configuration |
| `doc/04-commands.md` | Référence des commandes |
| `doc/05-cloud-init.md` | Personnalisation cloud-init |
| `doc/06-networking.md` | Configuration réseau |
| `doc/07-ansible.md` | Intégration Ansible |
| `doc/09-internals.md` | Fonctionnement interne |
| `doc/10-troubleshooting.md` | Résolution de problèmes |
| `doc/12-apparmor.md` | Règles AppArmor |
