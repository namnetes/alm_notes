# VM Alpine Linux avec Cloud-Init

Cloud-Init est un standard d'initialisation automatique de machines virtuelles. Au premier démarrage,
la VM lit un fichier de configuration (`user-data`) et applique automatiquement les paramètres définis :
nom d'hôte, utilisateurs, clés SSH, paquets, commandes. La VM est opérationnelle en moins d'une minute,
sans aucune interaction manuelle.

**Avantages par rapport à l'installation via `setup-alpine` :**

- Déploiement reproductible et scriptable
- Pas de wizard interactif à parcourir
- La configuration est un fichier texte, versionnable dans git

## Prérequis

| Composant | Requis |
|---|---|
| KVM / libvirt | Installé et actif sur l'hôte Ubuntu |
| Accès Internet | Pour télécharger l'image Alpine |
| Clé SSH | Paire de clés `~/.ssh/id_ed25519` (générée ci-dessous si absente) |

---

## 1. Installation des outils

```bash
sudo apt update
sudo apt install cloud-image-utils qemu-utils virtinst
```

| Paquet | Outil fourni | Rôle |
|---|---|---|
| `cloud-image-utils` | `cloud-localds` | Génère le seed ISO Cloud-Init |
| `qemu-utils` | `qemu-img` | Crée et manipule les disques virtuels |
| `virtinst` | `virt-install` | Crée les VM en ligne de commande |

---

## 2. Répertoire de travail

```bash
mkdir -p ~/VMs/alpine-test
cd ~/VMs/alpine-test
```

Tous les fichiers de cette procédure sont créés dans ce répertoire.

---

## 3. Clé SSH

Cloud-Init configure l'accès SSH par clé publique. Vérifiez qu'une paire de clés existe :

```bash
ls ~/.ssh/id_ed25519.pub
```

Si le fichier est absent, générez une paire de clés :

```bash
ssh-keygen -t ed25519 -C "alpine-test"
```

Appuyez sur `Entrée` à chaque question pour accepter les valeurs par défaut.

---

## 4. Téléchargement de l'image Alpine Cloud

Alpine Linux fournit des images QCOW2 pré-construites compatibles Cloud-Init, dites images `nocloud` :

```bash
wget https://dl-cdn.alpinelinux.org/alpine/v3.21/releases/cloud/nocloud_alpine-3.21.6-x86_64-bios-tiny-r0.qcow2 \
     -O alpine-base.qcow2
```

Vérifiez l'image téléchargée :

```bash
qemu-img info alpine-base.qcow2
```

!!! info "Image nocloud"
    Le préfixe `nocloud` signifie que Cloud-Init cherche sa configuration dans un ISO monté localement
    comme lecteur CD, sans dépendre d'un serveur de métadonnées distant (AWS, GCP, Azure, etc.).
    C'est le mode adapté à un usage local avec KVM.

---

## 5. Création du disque de la VM

Plutôt que de modifier l'image de base, créez un disque en mode **COW** (*Copy-On-Write*).
Ce disque utilise `alpine-base.qcow2` comme référence en lecture seule et n'écrit que les différences.
L'image de base reste intacte et peut être réutilisée pour d'autres VM.

```bash
qemu-img create \
    -f qcow2 \
    -b alpine-base.qcow2 \
    -F qcow2 \
    alpine-test.qcow2 \
    10G
```

| Argument | Signification |
|---|---|
| `-f qcow2` | Format du nouveau disque |
| `-b alpine-base.qcow2` | Image de base (*backing file*) |
| `-F qcow2` | Format de l'image de base |
| `10G` | Taille maximale allouée à la VM |

---

## 6. Fichiers Cloud-Init

Cloud-Init s'appuie sur deux fichiers :

- **`meta-data`** — identifiant d'instance et nom d'hôte
- **`user-data`** — configuration complète (utilisateur, paquets, commandes)

### meta-data

```bash
cat > meta-data << 'EOF'
instance-id: alpine-test
local-hostname: alpine-test
EOF
```

### user-data

La commande suivante lit automatiquement votre clé publique SSH et l'intègre dans la configuration.
Remplacez `galan` par le nom d'utilisateur souhaité dans la VM :

```bash
SSH_KEY=$(cat ~/.ssh/id_ed25519.pub)

cat > user-data << EOF
#cloud-config
hostname: alpine-test
fqdn: alpine-test.local
manage_etc_hosts: true

users:
  - name: galan
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/ash
    lock_passwd: false
    ssh_authorized_keys:
      - ${SSH_KEY}

packages:
  - bash
  - curl
  - nano
  - openssh
  - sudo

runcmd:
  - rc-update add sshd default
  - service sshd start

final_message: "La VM \$HOSTNAME est prête après \$UPTIME secondes."
EOF
```

!!! warning "Syntaxe YAML stricte"
    - La première ligne doit être exactement `#cloud-config` (le `#` est obligatoire, ce n'est pas un commentaire)
    - L'indentation utilise des **espaces uniquement**, jamais des tabulations
    - La clé SSH doit tenir sur **une seule ligne**

Vérifiez que la clé a bien été insérée :

```bash
grep "ssh-ed25519" user-data
```

---

## 7. Génération du seed ISO

Le seed ISO regroupe `meta-data` et `user-data` dans une image que la VM monte comme lecteur CD
au premier démarrage :

```bash
cloud-localds seed.iso user-data meta-data
```

Contrôlez la présence de tous les fichiers :

```bash
ls -lh ~/VMs/alpine-test/
```

Résultat attendu :

```
alpine-base.qcow2
alpine-test.qcow2
meta-data
seed.iso
user-data
```

---

## 8. Création de la VM

```bash
virt-install \
  --connect qemu:///system \
  --name alpine-test \
  --memory 512 \
  --vcpus 1 \
  --disk path=$HOME/VMs/alpine-test/alpine-test.qcow2,format=qcow2,bus=virtio \
  --disk path=$HOME/VMs/alpine-test/seed.iso,device=cdrom \
  --os-variant alpinelinux3.21 \
  --network network=default \
  --graphics none \
  --console pty,target_type=serial \
  --import \
  --noautoconsole
```

| Argument | Rôle |
|---|---|
| `--import` | Importe un disque existant, sans lancer d'installeur |
| `--noautoconsole` | Rend la main immédiatement sans attacher la console |
| `--os-variant alpinelinux3.21` | Applique les optimisations QEMU propres à Alpine 3.21 |
| `--network network=default` | Réseau NAT libvirt — la VM accède à Internet, l'hôte peut la joindre |

!!! warning "AppArmor sur Ubuntu"
    Sur Ubuntu, AppArmor peut bloquer l'accès de QEMU aux fichiers situés dans `~/VMs/`.
    Si `virt-install` échoue avec une erreur de permission, copiez les fichiers dans
    le répertoire standard libvirt et relancez :

    ```bash
    sudo cp ~/VMs/alpine-test/alpine-test.qcow2 /var/lib/libvirt/images/
    sudo cp ~/VMs/alpine-test/seed.iso /var/lib/libvirt/images/
    ```

    Puis adaptez les chemins `--disk` en remplaçant `$HOME/VMs/alpine-test/`
    par `/var/lib/libvirt/images/`.

!!! note "Variante OS non reconnue"
    Si `virt-install` signale que `alpinelinux3.21` est inconnu, listez les variantes disponibles :

    ```bash
    virt-install --os-variant list | grep alpine
    ```

    Utilisez la version la plus récente disponible, ou remplacez par `--os-variant generic`.

---

## 9. Connexion à la VM

Cloud-Init prend quelques dizaines de secondes pour s'exécuter. Attendez avant de vous connecter.

Récupérez l'adresse IP attribuée par le réseau NAT libvirt :

```bash
virsh net-dhcp-leases default
```

Connectez-vous en SSH :

```bash
ssh galan@<adresse-ip>
```

Pour suivre la progression de Cloud-Init via la console série :

```bash
virsh console alpine-test
```

Appuyez sur `Entrée` si aucune sortie n'apparaît immédiatement. Pour quitter la console : `Ctrl + ]`.

!!! tip "Vérifier que Cloud-Init a terminé"
    Une fois connecté à la VM :

    ```bash
    cloud-init status
    ```

    La réponse `status: done` confirme que la configuration s'est appliquée sans erreur.
    En cas d'erreur, les journaux détaillés sont dans `/var/log/cloud-init.log`.

---

## 10. Éjection du seed ISO

Une fois la VM configurée, le seed ISO n'est plus nécessaire. Éjectez-le pour éviter que
Cloud-Init ne tente de se réexécuter lors des redémarrages suivants.

Identifiez le nom du périphérique CD-ROM :

```bash
virsh domblklist alpine-test
```

Éjectez le média (remplacez `hda` par le nom de périphérique trouvé ci-dessus) :

```bash
virsh change-media alpine-test hda --eject
```

---

## Ajouter un répertoire partagé

Pour partager un répertoire entre l'hôte et cette VM via VirtioFS, consultez :
[Partage de répertoires via VirtioFS](creation-dun-partage-de-repertoires.md).

!!! info
    La procédure est identique que la VM ait été créée via virt-manager ou via Cloud-Init.
    Elle s'effectue post-installation dans virt-manager, la VM devant être à l'arrêt.

---

## Suppression de la VM

Pour supprimer complètement la VM :

```bash
# Arrêt forcé si la VM est en cours d'exécution
virsh destroy alpine-test 2>/dev/null

# Suppression de la définition libvirt
virsh undefine alpine-test

# Suppression des fichiers disque
rm -rf ~/VMs/alpine-test
```

!!! danger "Suppression irréversible"
    `rm -rf` supprime définitivement tous les fichiers, y compris le disque de la VM et ses données.
    Vérifiez deux fois le chemin avant de valider.
