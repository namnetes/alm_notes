# Scripts et utilitaires

---

## Scripts exécutables — `.functions/bin/`

Ces scripts sont dans le `$PATH` et s'exécutent directement depuis n'importe quel répertoire.

### `update_system.sh` — Mise à jour système

```bash
update_system.sh
```

Exécute `sudo apt update && apt upgrade -y`, `snap refresh`, puis `apt autoremove`.

---

### `change_wallpaper.sh` — Fond d'écran aléatoire

```bash
change_wallpaper.sh
```

Sélectionne aléatoirement une image dans `~/.config/my_ubuntu/wallpapers/` et l'applique via `gsettings`. Installe automatiquement une tâche cron horaire au premier lancement.

---

### `update_hostname.sh` — Changement du nom d'hôte

```bash
sudo bash ~/.functions/bin/update_hostname.sh nouveau-nom
```

Détecte automatiquement systemd ou BusyBox. Met à jour `/etc/hostname` et `/etc/hosts`.

---

### `vid2mp3.sh` — Extraction audio

```bash
vid2mp3.sh video.mp4
vid2mp3.sh video.webm
```

Convertit `.mp4` ou `.webm` en `.mp3`. Détecte automatiquement le débit audio avec `ffprobe`.

---

### `init_zed.sh` — Réinitialisation de Zed

```bash
init_zed.sh
```

Supprime les extensions et la base de données Zed, puis restaure la configuration via `stow`. Demande de fermer Zed s'il est ouvert.

---

### `list_functions.sh` — Navigateur de fonctions

```bash
list_functions.sh
```

Affiche toutes les fonctions shell disponibles via un sélecteur FZF interactif. Permet de sélectionner et d'exécuter une fonction directement.

---

## Utilitaires Python — `.functions/tools/`

La documentation détaillée de chaque outil est disponible dans le dépôt sous `doc/`.

### `check_csv.py` — Validation de fichiers CSV

```bash
csvc fichier.csv
csvc -d ";" fichier.csv     # délimiteur personnalisé
csvc --strict fichier.csv   # mode strict
```

Vérifie que toutes les lignes ont le même nombre de colonnes. Délimiteur par défaut : `;`. Signale les incohérences avec le numéro de ligne.

Documentation complète : [doc/check_csv.md](https://github.com/namnetes/alm-dotfiles/blob/main/doc/check_csv.md)

---

### `rename_images.py` — Renommage en lot

```bash
renimg prefixe
```

Renomme toutes les images du répertoire courant en `prefixe_01.ext`, `prefixe_02.ext`, etc. Préserve l'extension d'origine.

Documentation complète : [doc/rename_images.md](https://github.com/namnetes/alm-dotfiles/blob/main/doc/rename_images.md)

---

### `encrypt_gpg.py` — Chiffrement GPG

```bash
gpgtool
```

Interface interactive pour chiffrer ou déchiffrer des fichiers avec un mot de passe. Produit des fichiers `.gpg`.

Documentation complète : [doc/encrypt_gpg.md](https://github.com/namnetes/alm-dotfiles/blob/main/doc/encrypt_gpg.md)

---

### `manage_kvm.py` — Gestion des VMs KVM

```bash
kadm
```

Interface curses (TUI) pour gérer les machines virtuelles KVM via libvirt.

| Fonction | Description |
|----------|-------------|
| Lister | Affiche les VMs avec état, adresse MAC et IP (via ARP) |
| Démarrer / Arrêter | Contrôle du cycle de vie |
| Cloner | Duplication d'une VM existante |
| Supprimer | Suppression propre |

Documentation complète : [doc/manage_kvm.md](https://github.com/namnetes/alm-dotfiles/blob/main/doc/manage_kvm.md)
