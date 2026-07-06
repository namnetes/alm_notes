# eCryptfs

eCryptfs est un système de chiffrement de fichiers intégré directement au noyau Linux depuis la version 2.6.19 (2006). Il fonctionne comme un système de fichiers empilé : les fichiers sont chiffrés à la volée lors de l'écriture et déchiffrés à la lecture, de façon transparente pour les applications.

**Cas d'usage principal :** protéger un répertoire `~/Private` dans votre répertoire personnel. Les données chiffrées sont stockées dans `~/.Private` (chiffré, sur le disque) et apparaissent déchiffrées dans `~/Private` uniquement lorsque vous êtes connecté.

---

## Installation

```bash
sudo apt install ecryptfs-utils
```

---

## Créer le répertoire chiffré

```bash
ecryptfs-setup-private
```

La commande pose deux questions :

| Question | Réponse attendue |
|----------|-----------------|
| **Enter your login passphrase** | Votre mot de passe de connexion Linux (celui que vous tapez à l'ouverture de session) |
| **Enter your Mount Passphrase** | Une phrase de passe forte et unique. Appuyez sur Entrée pour en générer une automatiquement, ou saisissez la vôtre. |

??? example "Exemple de sortie"
    ```
    Enter your login passphrase [galan]:
    Enter your mount passphrase [leave blank to generate one]:
    Enter your mount passphrase (again):

    ************************************************************************
    YOU SHOULD RECORD YOUR MOUNT PASSPHRASE AND STORE IT IN A SAFE LOCATION.
      ecryptfs-unwrap-passphrase ~/.ecryptfs/wrapped-passphrase
    THIS WILL BE REQUIRED IF YOU NEED TO RECOVER YOUR DATA AT A LATER TIME.
    ************************************************************************

    Done configuring.
    Testing mount/write/umount/read...
    Testing succeeded.

    Logout, and log back in to begin using your encrypted directory.
    ```

Une fois la commande terminée, **déconnectez-vous puis reconnectez-vous** pour que les changements prennent effet.

### Ce qui est créé

| Chemin | Rôle |
|--------|------|
| `~/.Private/` | Répertoire chiffré sur le disque — contient les données sous forme chiffrée |
| `~/Private/` | Point de montage — vos fichiers déchiffrés apparaissent ici quand vous êtes connecté |
| `~/.ecryptfs/wrapped-passphrase` | Phrase de passe de montage chiffrée avec votre mot de passe Linux |

---

## Utilisation quotidienne

### Monter (déverrouiller) le répertoire

À la connexion, le montage est automatique. Pour le faire manuellement :

```bash
ecryptfs-mount-private
```

### Démonter (verrouiller) le répertoire

```bash
ecryptfs-umount-private
```

!!! tip
    Après démontage, `~/Private` affiche deux fichiers de démarrage laissés par eCryptfs (`README.txt` et `Access-Your-Private-Data.desktop`). C'est normal — vos données chiffrées restent intactes dans `~/.Private`.

---

## La phrase de passe de montage

C'est la clé maîtresse du chiffrement. Elle est générée à la création du répertoire et stockée chiffrée dans `~/.ecryptfs/wrapped-passphrase`, protégée par votre mot de passe Linux.

!!! danger "Ne jamais perdre cette phrase de passe"
    Si elle est perdue, les données dans `~/.Private` sont **définitivement irrécupérables**, même avec le mot de passe Linux.

### Afficher la phrase de passe

```bash
ecryptfs-unwrap-passphrase
```

Le système demande votre mot de passe Linux, puis affiche la phrase de passe de montage en clair.

!!! warning "Stockage sécurisé"
    Notez cette phrase dans un gestionnaire de mots de passe (Proton Pass, KeePassXC…) ou sur papier dans un endroit physiquement sécurisé. **Ne la stockez jamais en clair sur le même disque que les données chiffrées.**

---

## Sauvegarde

Pour garantir la récupération des données, trois éléments sont indispensables :

| Élément | Emplacement | Priorité |
|---------|-------------|----------|
| Phrase de passe de montage | À noter séparément (gestionnaire de mots de passe) | **Critique** |
| Données chiffrées | `~/.Private/` | Haute |
| Configuration eCryptfs | `~/.ecryptfs/` | Haute |

### Procédure

**Étape 1 — Récupérer et noter la phrase de passe de montage :**

```bash
ecryptfs-unwrap-passphrase
```

Conservez-la dans votre gestionnaire de mots de passe.

**Étape 2 — Démonter le répertoire (sauvegarde à froid) :**

```bash
ecryptfs-umount-private
```

!!! info "Pourquoi démonter avant de sauvegarder ?"
    Une sauvegarde à froid garantit la cohérence des données. Si des fichiers sont en cours d'écriture pendant la copie, l'archive pourrait être corrompue.

**Étape 3 — Sauvegarder les répertoires :**

=== "tar (archive compressée)"
    ```bash
    cd ~
    tar -cvzf ~/sauvegardes/ecryptfs_$(date +%Y%m%d_%H%M%S).tar.gz \
        .ecryptfs \
        .Private
    ```

    Copiez ensuite l'archive sur un support externe (disque, clé USB, stockage distant).

=== "rsync (synchronisation)"
    ```bash
    rsync -av ~/.ecryptfs/  ~/sauvegardes/ecryptfs/config/
    rsync -av ~/.Private/   ~/sauvegardes/ecryptfs/data/
    ```

---

## Restauration sur un nouveau système

### Prérequis

1. `ecryptfs-utils` installé : `sudo apt install ecryptfs-utils`
2. La **phrase de passe de montage** disponible
3. Les sauvegardes de `~/.ecryptfs/` et `~/.Private/`

### Procédure

**Étape 1 — Créer les répertoires :**

```bash
mkdir -p ~/.ecryptfs ~/.Private
sudo chown -R $USER:$USER ~/.ecryptfs ~/.Private
```

**Étape 2 — Restaurer les fichiers de sauvegarde :**

=== "Depuis une archive tar"
    ```bash
    tar -xvzf ~/sauvegardes/ecryptfs_20250101_120000.tar.gz -C ~
    ```

    L'option `-C ~` extrait les dossiers directement à la racine du répertoire personnel.

=== "Depuis des dossiers rsync"
    ```bash
    cp -r ~/sauvegardes/ecryptfs/config/  ~/.ecryptfs/
    cp -r ~/sauvegardes/ecryptfs/data/    ~/.Private/
    ```

**Étape 3 — Ré-envelopper la phrase de passe avec le nouveau mot de passe Linux :**

Le fichier `wrapped-passphrase` restauré est chiffré avec l'**ancien** mot de passe. Il faut le re-chiffrer avec le mot de passe du nouveau compte.

```bash
ecryptfs-wrap-passphrase ~/.ecryptfs/wrapped-passphrase
```

La commande demande interactivement :

1. La **phrase de passe de montage** (celle que vous avez notée)
2. Le **mot de passe Linux actuel** (deux fois)

**Étape 4 — Tester le montage :**

```bash
ecryptfs-mount-private
ls ~/Private
```

Si vos fichiers s'affichent, la restauration est réussie.

---

## Récupération d'urgence (SystemRescueCD)

En cas de système inaccessible, les données peuvent être récupérées depuis un environnement live (SystemRescueCD, Ubuntu Live USB…) à condition de disposer de la phrase de passe de montage.

### Monter la partition Linux

```bash
sudo fdisk -l                          # Identifier la partition (ex. /dev/sda3)
sudo mkdir /mnt/linux_root
sudo mount /dev/sdaX /mnt/linux_root  # Remplacer sdaX par la partition trouvée
```

### Récupérer la phrase de passe (si oubliée)

Si vous connaissez encore votre mot de passe Linux mais avez oublié la phrase de passe de montage :

```bash
ecryptfs-unwrap-passphrase \
    /mnt/linux_root/home/<utilisateur>/.ecryptfs/wrapped-passphrase
```

Entrez votre mot de passe Linux quand demandé. La phrase de passe s'affiche.

### Monter le répertoire chiffré

```bash
sudo mkdir /mnt/dechiffre
sudo mount -t ecryptfs \
    /mnt/linux_root/home/<utilisateur>/.Private \
    /mnt/dechiffre
```

Répondez aux questions :

| Question | Réponse |
|----------|---------|
| Passphrase | Votre phrase de passe de montage |
| Cipher | `aes` (Entrée pour accepter) |
| Key bytes | `16` (Entrée pour accepter) |
| Enable plaintext passthrough | `n` |
| Enable filename encryption | `y` |

Vos fichiers sont maintenant accessibles dans `/mnt/dechiffre`. Copiez-les sur un support externe.

### Démonter proprement

```bash
sudo umount /mnt/dechiffre
sudo umount /mnt/linux_root
```

---

## Suppression du répertoire chiffré

!!! danger "Opération irréversible"
    Sauvegardez toutes les données importantes **avant** de commencer.

**Étape 1 — Démonter :**

```bash
ecryptfs-umount-private
```

**Étape 2 — Supprimer les répertoires :**

```bash
chmod 700 ~/Private && rm -rf ~/Private
rm -rf ~/.Private
```

**Étape 3 — Supprimer la configuration :**

```bash
rm -rf ~/.ecryptfs
```

**Étape 4 — Désinstaller le paquet (optionnel) :**

```bash
sudo apt remove ecryptfs-utils && sudo apt autoremove
```

---

## Désactiver le montage automatique

Par défaut, `~/Private` est monté automatiquement à chaque connexion via PAM. Pour désactiver ce comportement :

```bash
mv ~/.ecryptfs/auto-mount ~/.ecryptfs/auto-mount_disabled
```

Après reconnexion, le montage ne sera plus automatique. Utilisez `ecryptfs-mount-private` pour monter manuellement.

Pour réactiver :

```bash
mv ~/.ecryptfs/auto-mount_disabled ~/.ecryptfs/auto-mount
```

---

## Référence rapide

| Besoin | Commande |
|--------|----------|
| Créer le répertoire chiffré | `ecryptfs-setup-private` |
| Monter manuellement | `ecryptfs-mount-private` |
| Démonter | `ecryptfs-umount-private` |
| Afficher la phrase de passe | `ecryptfs-unwrap-passphrase` |
| Re-chiffrer avec nouveau mot de passe | `ecryptfs-wrap-passphrase ~/.ecryptfs/wrapped-passphrase` |
