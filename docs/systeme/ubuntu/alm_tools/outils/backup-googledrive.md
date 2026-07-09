# backup_googledrive

`backup_googledrive.sh` synchronise Google Drive localement via `rclone` et
crée des archives compressées déterministes avec déduplication par hash SHA256.

**Source :** `~/alm_tools/jobs/backup_googledrive.sh`

---

## Prérequis

| Outil | Installation | Rôle |
|-------|-------------|------|
| `rclone` | `sudo make rclone` (postinstall) + config | Synchronisation Google Drive |
| `pv` | `sudo apt install pv` | Barre de progression pendant la compression |
| `hashdeep` | `sudo apt install hashdeep` | Calcul du SHA256 de l'archive |

!!! note "rclone : pas le paquet APT"
    Le module postinstall installe rclone via le **script officiel
    rclone.org**, car le paquet APT est très en retard sur l'amont
    (constaté : 1.60 en APT contre 1.74 en amont) — problématique pour un
    outil qui suit les APIs cloud. `pv` et `hashdeep` sont quant à eux déjà
    couverts par `sudo make pkg-install` (liste APT de postinstall).

### Configurer rclone pour Google Drive

```bash
rclone config
# Choisir "n" (nouveau remote), nommer "google_drive", type "drive"
# Suivre l'authentification OAuth dans le navigateur
```

!!! warning "Nom du remote"
    Le script attend un remote nommé exactement **`google_drive`** (avec
    underscore). Vérifier avec `rclone listremotes` — un nom différent
    provoque l'erreur `didn't find section in config file`.

### Sauvegarde et restauration de la config

`rclone` ne persiste jamais sa configuration à travers une réinstallation
du poste : le module postinstall `cli` réinstalle uniquement le binaire
`rclone`, jamais `~/.config/rclone/rclone.conf`. Sans sauvegarde
préalable, `rclone config` doit être intégralement refait après chaque
réinstallation — y compris l'authentification OAuth interactive dans le
navigateur, une contrainte de sécurité Google impossible à scripter pour
un compte personnel.

Le token OAuth obtenu est stocké dans `~/.config/rclone/rclone.conf`
(`refresh_token`, accès indéfini sans repasser par le navigateur) — c'est
ce fichier qu'il faut sauvegarder.

Config actuelle de référence : remote `google_drive`, type `drive`,
scope `drive.readonly` (lecture seule — suffisant pour un backup).

#### Sauvegarde

```bash
# 1. Chiffrer rclone.conf avec un mot de passe
gpgtool
# 1 (Chiffrer), chemin : ~/.config/rclone/rclone.conf

# 2. Encoder en base64 pour pouvoir le coller dans une note texte
base64 -w0 ~/.config/rclone/rclone.conf.gpg \
  > ~/.config/rclone/rclone.conf.gpg.b64

# 3. Copier dans le presse-papiers
wl-copy < ~/.config/rclone/rclone.conf.gpg.b64
# (Xorg/XWayland : xclip -selection clipboard < ...)

# 4. Nettoyer le fichier temporaire une fois collé dans Proton Pass
rm ~/.config/rclone/rclone.conf.gpg.b64
```

| Commutateur | Rôle |
|--------------|------|
| `base64 -w0` | Désactive le retour à la ligne automatique tous les 76 caractères — le blob doit tenir sur une seule ligne collable dans un champ de note. |
| `wl-copy` / `xclip -selection clipboard` | Copie dans le presse-papiers "standard" (`Ctrl+V`) — respectivement Wayland et Xorg/XWayland. |

Créer une nouvelle **note sécurisée** Proton Pass titrée `rclone.conf —
Google Drive backup`, et répartir le résultat dans deux emplacements
séparés :

| Emplacement | Contenu |
|-------------|---------|
| Corps de la note | Contenu de `rclone.conf.gpg.b64` |
| Champ caché `Mot de passe GPG` (`+ Ajouter un champ` → type `Caché`) | Le mot de passe saisi à l'étape 1 |

!!! danger "Jamais les deux dans le même champ"
    Le blob seul ou le mot de passe seul ne permettent pas de retrouver
    le secret — c'est cette séparation qui protège la config (le base64
    n'est qu'un encodage, pas un chiffrement : il ne protège rien à lui
    seul). Détail du principe dans le runbook générique [Sauvegarde et
    restauration d'un secret](../../../../securite/proton/sauvegarde-restauration.md).

#### Restauration

```bash
cd ~/alm_tools/postinstall && sudo make rclone   # réinstalle le binaire

# Récupérer le blob base64 depuis la note Proton Pass, puis :
echo "<blob collé depuis Proton Pass>" \
  | base64 -d > ~/.config/rclone/rclone.conf.gpg

gpgtool
# 2 (Déchiffrer), chemin : ~/.config/rclone/rclone.conf.gpg
# mot de passe : celui stocké dans le champ caché de la note

rclone listremotes    # doit afficher : google_drive:
```

---

## Utilisation

```bash
~/alm_tools/jobs/backup_googledrive.sh
```

Par défaut, `SOURCE_DIR` est vide et le script synchronise **la racine
complète du Drive**. Pour ne sauvegarder qu'un sous-dossier distant :

```bash
SOURCE_DIR="Documents" ~/alm_tools/jobs/backup_googledrive.sh
```

`SOURCE_DIR` doit toujours être un chemin **distant** (côté Drive), jamais
un chemin local.

---

## Anti-concurrence (verrou)

Le script empêche deux exécutions simultanées via `lock_guard` (fonction
partagée de `~/alm_tools/lib/common.sh`). Si une instance tourne déjà, un
second lancement s'arrête immédiatement :

```text
[INFO] 📋 Fichiers lock détectés :
[INFO]   - /tmp/backup_googledrive_pid34241.lock (✅ actif)
[FATAL] Arrêt du script pour éviter les conflits.
```

Le fichier de verrou est stocké dans `/tmp/backup_googledrive_pid<PID>.lock`
et supprimé automatiquement en fin d'exécution (même en cas d'erreur).

---

## Processus détaillé

Le script est découpé en fonctions (une bannière par fonction dans le
code), orchestrées depuis `main()` :

```mermaid
flowchart TD
    A([Lancement]) --> B[check_requirements\nVérifier rclone, pv, hashdeep]
    B --> C[prepare_directories\nCréer les répertoires si besoin]
    C --> D[show_configuration\nAfficher la config active]
    D --> E{lock_guard\nUne instance tourne déjà ?}
    E -->|Oui| F([Arrêt immédiat])
    E -->|Non| G["sync_google_drive\nrclone sync → ~/backups/googledrive/"]
    G --> H[create_archive\nArchive tar.gz déterministe]
    H --> I[compute_archive_checksum\nSHA256 via hashdeep]
    I --> J{deduplicate_archives\nHash identique à l'archive précédente ?}
    J -->|Oui| K[Supprimer la nouvelle archive]
    J -->|Non| L[Conserver l'archive]
    K --> M([Fin])
    L --> M

    classDef startStop fill:#e1f5fe,stroke:#01579b,color:#000
    classDef logic     fill:#e8eaf6,stroke:#1a237e,color:#000
    classDef error     fill:#ffebee,stroke:#c62828,color:#000
    class A,M startStop
    class B,C,D,G,H,I,K,L logic
    class F,E error
```

---

## Archives déterministes

Le script utilise une méthode de compression qui produit un hash SHA256
**identique si le contenu n'a pas changé**, permettant de détecter les vraies
modifications entre deux sauvegardes :

```bash
tar --sort=name \
    --mtime='UTC 2020-01-01' \
    --owner=0 --group=0 --numeric-owner \
    -c -C "$BACKUP_DIR" . \
  | gzip -9 -n \
  > archive.tar.gz
```

- `--sort=name` : ordre stable des fichiers
- `--mtime` fixe : élimine les variations de date de modification
- `--owner=0 --group=0` : élimine les variations d'utilisateur/groupe
- `gzip -n` : pas de timestamp dans l'en-tête gzip

---

## Emplacements

| Chemin | Contenu |
|--------|---------|
| `~/backups/googledrive/` | Fichiers synchronisés depuis Google Drive |
| `~/backups/archives/` | Archives `tar.gz` horodatées + fichiers SHA256 |
| `~/backups/archives/rclone_sync.log` | Log de la dernière synchronisation rclone (niveau `INFO`) |
| `/tmp/backup_googledrive_pid<PID>.lock` | Verrou anti-concurrence (existe pendant l'exécution) |

!!! warning "Pourquoi le log n'est PAS dans ~/backups/googledrive/"
    `rclone sync` rend la destination strictement identique à la source
    distante : tout fichier présent en local mais absent du Drive est
    supprimé. Si le log était écrit dans `~/backups/googledrive/`, rclone
    supprimerait son propre fichier de log à chaque synchronisation
    (constaté en pratique : le fichier disparaissait après un run complet).
    Il est donc stocké dans `~/backups/archives/`, jamais touché par la
    commande `sync`.

---

## Suivre une sauvegarde en cours

Le script tourne potentiellement longtemps sur un gros Drive (plusieurs
dizaines de Go). Pour vérifier son avancement depuis un autre terminal :

```bash
# Le script tourne-t-il, depuis combien de temps ?
ps aux | grep backup_googledrive | grep -v grep
ps -o pid,etimes,cmd -p <PID>

# Arbre des processus (rclone et ses sous-processus)
pstree -p <PID>

# Volume déjà transféré (l'indicateur le plus fiable)
du -sh ~/backups/googledrive

# Suivre les transferts en direct (nécessite --log-level INFO, déjà activé)
tail -f ~/backups/archives/rclone_sync.log
```

!!! note "Pourquoi pas juste le log ?"
    La barre de progression `--progress` de rclone (vitesse, %, ETA) ne
    s'affiche que dans le terminal où le script a été lancé — elle n'est
    pas récupérable depuis un autre terminal. Le log et la taille du
    dossier sont les seuls indicateurs consultables à distance.

---

## Déduplication

Après chaque sauvegarde, le script compare le SHA256 de la nouvelle archive
avec celui de l'avant-dernière. Si les hashs sont identiques (aucune
modification détectée), la nouvelle archive est supprimée — évitant
d'accumuler des doublons. C'est ce qui rend le script **idempotent** : le
relancer sans changement sur le Drive ne laisse aucun doublon derrière lui.

!!! warning "La compression a toujours lieu, même sans changement"
    Le script ne détecte pas les changements *avant* de compresser : il
    crée **systématiquement** une archive complète de tout
    `~/backups/googledrive/` (`tar` + `gzip`), calcule son SHA256, et
    seulement *ensuite* la supprime si elle est identique à la précédente.
    Seule la **conservation** de l'archive dépend du hash, pas sa
    **création**. Sur un gros volume (dizaines de Go), ce coût CPU/disque
    est donc payé à chaque exécution, qu'il y ait eu un changement ou non.

---

## Planification (cron)

Pour automatiser la sauvegarde quotidienne :

```bash
crontab -e
# Ajouter :
0 2 * * * ~/alm_tools/jobs/backup_googledrive.sh >> ~/.nohups/backup_gdrive.log 2>&1
```
