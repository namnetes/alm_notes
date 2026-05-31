# backup_googledrive

`backup_googledrive.sh` synchronise Google Drive localement via `rclone` et
crée des archives compressées déterministes avec déduplication par hash SHA256.

**Source :** `~/alm_tools/jobs/backup_googledrive.sh`

---

## Prérequis

| Outil | Installation | Rôle |
|-------|-------------|------|
| `rclone` | `sudo apt install rclone` + config | Synchronisation Google Drive |
| `pv` | `sudo apt install pv` | Barre de progression pendant la compression |
| `hashdeep` | `sudo apt install hashdeep` | Calcul du SHA256 de l'archive |

### Configurer rclone pour Google Drive

```bash
rclone config
# Choisir "n" (nouveau remote), nommer "googledrive", type "drive"
# Suivre l'authentification OAuth dans le navigateur
```

---

## Utilisation

```bash
~/alm_tools/jobs/backup_googledrive.sh
```

Par défaut, synchronise `$HOME/Documents` depuis Google Drive.
Pour changer le répertoire source :

```bash
SOURCE_DIR="Photos" ~/alm_tools/jobs/backup_googledrive.sh
```

---

## Processus détaillé

```
1. Vérification des outils (rclone, pv, hashdeep)
2. Synchronisation rclone → ~/backups/googledrive/
3. Création d'une archive tar.gz déterministe
4. Calcul du SHA256 via hashdeep
5. Déduplication : supprime la nouvelle archive si identique à la précédente
6. Affichage du résultat
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
| `~/backups/googledrive/rclone_sync.log` | Log de la dernière synchronisation rclone |

---

## Déduplication

Après chaque sauvegarde, le script compare le SHA256 de la nouvelle archive
avec celui de l'avant-dernière. Si les hashs sont identiques (aucune
modification détectée), la nouvelle archive est supprimée — évitant
d'accumuler des doublons.

---

## Planification (cron)

Pour automatiser la sauvegarde quotidienne :

```bash
crontab -e
# Ajouter :
0 2 * * * ~/alm_tools/jobs/backup_googledrive.sh >> ~/.nohups/backup_gdrive.log 2>&1
```
