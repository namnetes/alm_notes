# yt-dlp

[yt-dlp](https://github.com/yt-dlp/yt-dlp) est un outil en ligne de commande open source pour télécharger vidéos, audios et métadonnées depuis plusieurs centaines de plateformes : YouTube, Vimeo, SoundCloud, Twitch, Twitter/X, Dailymotion, etc.

C'est un fork amélioré de youtube-dl, avec une meilleure prise en charge des sites modernes et une communauté très active.

---

## Installation

=== "Docker (recommandé)"
    ```bash
    docker pull jauderho/yt-dlp:latest
    ```

    Aucune dépendance à installer sur la machine hôte. C'est l'approche décrite dans ce guide.

=== "pip (Python)"
    ```bash
    pip install yt-dlp
    ```

=== "Ubuntu / Debian"
    ```bash
    sudo apt install yt-dlp
    ```

    !!! warning "Version potentiellement ancienne"
        Le paquet des dépôts Ubuntu peut être en retard sur la version officielle. Préférez `pip` ou Docker pour avoir la dernière version.

=== "Alpine Linux"
    ```bash
    sudo apk add yt-dlp
    ```

---

## Utilisation de base

Les exemples ci-dessous utilisent l'installation Docker. Remplacez `docker run --rm jauderho/yt-dlp:latest` par `yt-dlp` si vous l'avez installé directement.

### Télécharger une vidéo en meilleure qualité

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -f bestvideo+bestaudio \
    "https://youtu.be/XXXX"
```

### Télécharger uniquement l'audio

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -x --audio-format mp3 --audio-quality 0 \
    "https://youtu.be/XXXX"
```

`-x` extrait uniquement la piste audio. `--audio-quality 0` correspond à la meilleure qualité disponible.

### Choisir la qualité vidéo

Listez les formats disponibles pour une vidéo :

```bash
docker run --rm jauderho/yt-dlp:latest -F "https://youtu.be/XXXX"
```

Puis téléchargez le format souhaité par son identifiant :

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -f 137+140 \
    "https://youtu.be/XXXX"
```

??? tip "Sélecteurs de qualité courants"
    | Sélecteur | Signification |
    |-----------|---------------|
    | `bestvideo+bestaudio` | Meilleure vidéo + meilleur audio (fusionnés) |
    | `best` | Meilleur flux unique (pas toujours la meilleure qualité) |
    | `bestvideo[height<=1080]+bestaudio` | Limite la résolution à 1080p |
    | `bestvideo[height<=720]+bestaudio` | Limite à 720p |
    | `worstvideo+worstaudio` | Plus petite taille (utile pour tester) |

### Télécharger avec les sous-titres

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -f bestvideo+bestaudio \
    --write-subs --sub-langs fr,en \
    "https://youtu.be/XXXX"
```

??? tip "Sous-titres automatiques"
    Pour inclure les sous-titres générés automatiquement (IA) :

    ```bash
    --write-auto-subs --sub-langs fr
    ```

---

## Script de téléchargement

Ce script accepte **une ou plusieurs URL en argument** ou **un fichier texte contenant les URL** (une par ligne). Il est conçu pour fonctionner sur Alpine Linux avec un [répertoire partagé](../systeme/alpine/creation-dun-partage-de-repertoires.md) entre la VM et l'hôte Ubuntu.

### Script `ytdl.sh`

```bash
#!/usr/bin/env sh

DOWNLOAD_PATH="/mnt/shared"

usage() {
  printf 'Usage : %s [-f fichier.txt] [URL...]\n\n' "$0"
  printf 'Options :\n'
  printf '  -f fichier   Fichier texte contenant les URL (une par ligne)\n'
  printf '               Lignes vides et lignes commençant par # ignorées.\n'
  printf '  URL...       Une ou plusieurs URL passées directement\n\n'
  printf 'Exemples :\n'
  printf '  %s https://youtu.be/xxxx\n' "$0"
  printf '  %s https://youtu.be/xxxx https://youtu.be/yyyy\n' "$0"
  printf '  %s -f ~/videos/urls.txt\n' "$0"
  exit 1
}

collect_from_file() {
  while IFS= read -r line; do
    case "$line" in
      ''|'#'*) continue ;;
    esac
    printf '%s\n' "$line"
  done < "$1"
}

download() {
  docker run --rm \
    -v "$DOWNLOAD_PATH":/workdir:rw \
    jauderho/yt-dlp:latest \
    -P home:/workdir \
    -f "bestvideo+bestaudio" \
    "$1"
}

if [ "$#" -eq 0 ]; then
  usage
fi

TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

while [ "$#" -gt 0 ]; do
  case "$1" in
    -f)
      shift
      if [ ! -f "$1" ]; then
        printf 'Erreur : fichier "%s" introuvable.\n' "$1" >&2
        exit 1
      fi
      collect_from_file "$1" >> "$TMPFILE"
      ;;
    -h|--help) usage ;;
    -*) printf 'Option inconnue : %s\n' "$1" >&2; usage ;;
    *) printf '%s\n' "$1" >> "$TMPFILE" ;;
  esac
  shift
done

if [ ! -s "$TMPFILE" ]; then
  printf 'Erreur : aucune URL fournie.\n' >&2
  usage
fi

TOTAL=$(wc -l < "$TMPFILE")
CURRENT=0

while IFS= read -r url; do
  CURRENT=$((CURRENT + 1))
  printf '\n[%d/%d] %s\n' "$CURRENT" "$TOTAL" "$url"
  download "$url"
done < "$TMPFILE"

printf '\nTerminé : %d vidéo(s) téléchargée(s).\n' "$TOTAL"
```

### Format du fichier d'URLs

Créez un fichier texte (ex. `urls.txt`) avec une URL par ligne. Les lignes vides et les commentaires (`#`) sont ignorés.

```text
# Conférences
https://youtu.be/XXXX
https://youtu.be/YYYY

# Tutoriels
https://vimeo.com/ZZZZ

# Musique
https://soundcloud.com/artiste/titre
```

### Utilisation du script

```bash
# Une seule URL
./ytdl.sh https://youtu.be/XXXX

# Plusieurs URLs directement
./ytdl.sh https://youtu.be/XXXX https://youtu.be/YYYY

# Depuis un fichier
./ytdl.sh -f urls.txt
```

---

## Cas d'usage

### Télécharger une playlist complète

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -f bestvideo+bestaudio \
    --yes-playlist \
    "https://youtube.com/playlist?list=XXXX"
```

??? tip "Limiter le nombre de vidéos d'une playlist"
    ```bash
    --playlist-end 10   # Télécharge seulement les 10 premières vidéos
    --playlist-start 5  # Commence à la 5e vidéo
    ```

### Simuler un téléchargement (dry run)

Vérifiez ce qui serait téléchargé sans rien écrire sur le disque :

```bash
docker run --rm jauderho/yt-dlp:latest \
    --simulate --print filename \
    "https://youtu.be/XXXX"
```

### Nommer les fichiers automatiquement

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -o "%(upload_date)s - %(title)s.%(ext)s" \
    "https://youtu.be/XXXX"
```

Résultat : `20240615 - Titre de la vidéo.mp4`

??? tip "Variables de nommage utiles"
    | Variable | Contenu |
    |----------|---------|
    | `%(title)s` | Titre de la vidéo |
    | `%(uploader)s` | Nom de la chaîne |
    | `%(upload_date)s` | Date de mise en ligne (AAAAMMJJ) |
    | `%(id)s` | Identifiant unique de la vidéo |
    | `%(ext)s` | Extension du fichier |

### Reprendre un téléchargement interrompu

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -f bestvideo+bestaudio \
    --continue \
    "https://youtu.be/XXXX"
```

### Limiter la vitesse de téléchargement

Pour ne pas saturer la connexion :

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    --limit-rate 2M \
    "https://youtu.be/XXXX"
```

`2M` = 2 Mo/s. Accepte les suffixes `K`, `M`, `G`.

### Télécharger uniquement les métadonnées

Pour archiver les informations sans télécharger la vidéo :

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    --write-info-json --write-thumbnail --skip-download \
    "https://youtu.be/XXXX"
```

Produit un fichier `.info.json` avec toutes les métadonnées et la miniature de la vidéo.

### Extraire l'audio d'une playlist en MP3

```bash
docker run --rm -v "$PWD":/workdir:rw jauderho/yt-dlp:latest \
    -P home:/workdir \
    -x --audio-format mp3 --audio-quality 0 \
    --yes-playlist \
    -o "%(playlist_index)02d - %(title)s.%(ext)s" \
    "https://youtube.com/playlist?list=XXXX"
```

Numérote automatiquement les fichiers (`01 - Titre.mp3`, `02 - Titre.mp3`…).

---

## Référence rapide

| Besoin | Option |
|--------|--------|
| Meilleure qualité vidéo | `-f bestvideo+bestaudio` |
| Audio seul en MP3 | `-x --audio-format mp3 --audio-quality 0` |
| Lister les formats disponibles | `-F` |
| Limiter à 1080p | `-f bestvideo[height<=1080]+bestaudio` |
| Télécharger une playlist | `--yes-playlist` |
| Sous-titres | `--write-subs --sub-langs fr` |
| Nommer les fichiers | `-o "%(title)s.%(ext)s"` |
| Simuler sans télécharger | `--simulate` |
| Reprendre un téléchargement | `--continue` |
| Limiter la vitesse | `--limit-rate 2M` |
| Métadonnées seules | `--write-info-json --skip-download` |
| Depuis un fichier d'URLs | `-f urls.txt` (script `ytdl.sh`) |
