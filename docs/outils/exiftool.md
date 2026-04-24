# ExifTool

**ExifTool** est un utilitaire en ligne de commande gratuit et open source, développé par Phil Harvey. C'est la référence pour lire, écrire et supprimer les métadonnées dans une grande variété de formats de fichiers : images, vidéos, documents.

Site officiel : <https://exiftool.org/>

---

## Installation

=== "Ubuntu / Debian"
    ```bash
    sudo apt install exiftool perl-doc
    ```

    !!! info "À quoi sert `perl-doc` ?"
        ExifTool est écrit en Perl. Le paquet `perl-doc` fournit la documentation et les pages de manuel. Il est nécessaire pour consulter l'aide depuis le terminal (`man exiftool`).

=== "Alpine Linux"
    ```bash
    sudo apk add exiftool
    ```

=== "macOS (Homebrew)"
    ```bash
    brew install exiftool
    ```

Vérifiez l'installation :

```bash
exiftool -ver
```

---

## Formats supportés

ExifTool lit et écrit les métadonnées dans de nombreux formats :

| Catégorie | Formats |
|-----------|---------|
| **Images** | JPEG, TIFF, PNG, WebP, HEIC, RAW (CR2, NEF, ARW, DNG…) |
| **Vidéos** | MP4, MOV, AVI, MKV |
| **Documents** | PDF, DOCX, XLSX, PPTX |
| **Audio** | MP3, FLAC, WAV |

---

## Lire les métadonnées

### Toutes les métadonnées d'un fichier

```bash
exiftool photo.jpg
```

### Champs spécifiques

```bash
exiftool -Make -Model -DateTimeOriginal photo.jpg
```

### Format de sortie structuré

=== "JSON"
    ```bash
    exiftool -json photo.jpg
    ```

=== "CSV"
    ```bash
    exiftool -csv photo.jpg
    ```

=== "XML"
    ```bash
    exiftool -X photo.jpg
    ```

### Afficher les coordonnées GPS

```bash
exiftool -GPSLatitude -GPSLongitude -GPSAltitude photo.jpg
```

??? tip "Obtenir les coordonnées en degrés décimaux"
    Par défaut, les coordonnées s'affichent en degrés/minutes/secondes. Pour les obtenir en degrés décimaux (format Google Maps) :

    ```bash
    exiftool -GPSLatitude# -GPSLongitude# photo.jpg
    ```

    Le `#` force l'affichage de la valeur numérique brute.

---

## Modifier les métadonnées

!!! warning "Sauvegarde automatique"
    ExifTool crée un fichier de sauvegarde `_original` avant chaque modification. Par exemple, `photo.jpg_original`. Supprimez-le avec `-overwrite_original` si vous n'en avez pas besoin.

### Modifier la date de prise de vue

```bash
exiftool -DateTimeOriginal="2024:06:15 14:30:00" photo.jpg
```

Sans sauvegarde :

```bash
exiftool -overwrite_original -DateTimeOriginal="2024:06:15 14:30:00" photo.jpg
```

### Décaler une date (correction de fuseau horaire)

```bash
exiftool "-DateTimeOriginal+=2:0:0 0:0:0" photo.jpg
```

Ajoute 2 heures à la date existante. Utilisez `-=` pour soustraire.

### Ajouter auteur et copyright

```bash
exiftool -overwrite_original \
    -Artist="Alan Marchand" \
    -Copyright="© 2024 Alan Marchand" \
    photo.jpg
```

### Ajouter une description et des mots-clés

```bash
exiftool -overwrite_original \
    -ImageDescription="Vue depuis le col du Galibier" \
    -Keywords="montagne, alpes, paysage" \
    photo.jpg
```

### Modifier les coordonnées GPS

```bash
exiftool -overwrite_original \
    -GPSLatitude=45.0646 \
    -GPSLatitudeRef=N \
    -GPSLongitude=6.4057 \
    -GPSLongitudeRef=E \
    photo.jpg
```

---

## Supprimer les métadonnées

### Supprimer toutes les métadonnées

```bash
exiftool -all= photo.jpg
```

!!! tip "Usage typique"
    Indispensable avant de partager une photo en ligne. Les métadonnées peuvent contenir votre localisation GPS, le modèle de votre téléphone ou votre nom d'utilisateur.

### Supprimer uniquement les données GPS

```bash
exiftool -overwrite_original -GPS:all= photo.jpg
```

### Conserver certaines métadonnées, supprimer le reste

Supprimer tout sauf auteur et copyright :

```bash
exiftool -overwrite_original \
    -all= \
    -TagsFromFile @ \
    -Artist -Copyright \
    photo.jpg
```

---

## Traitement par lots

Toutes les commandes ExifTool fonctionnent sur un dossier entier en remplaçant le nom du fichier par un chemin de répertoire.

### Lire les métadonnées de tous les JPEG d'un dossier

```bash
exiftool -DateTimeOriginal -Make -Model /chemin/vers/dossier/*.jpg
```

### Supprimer les GPS de toutes les photos d'un dossier

```bash
exiftool -overwrite_original -GPS:all= /chemin/vers/dossier/
```

### Exporter les métadonnées de tout un dossier en CSV

```bash
exiftool -csv /chemin/vers/dossier/ > metadonnees.csv
```

### Traiter les sous-dossiers récursivement

Ajoutez le flag `-r` :

```bash
exiftool -r -overwrite_original -GPS:all= /chemin/vers/dossier/
```

---

## Renommer des fichiers

### Renommer par date de prise de vue

```bash
exiftool '-FileName<DateTimeOriginal' -d "%Y%m%d_%H%M%S.%%e" photo.jpg
```

Exemple de résultat : `photo.jpg` → `20240615_143000.jpg`

### Renommer tous les fichiers d'un dossier par date

```bash
exiftool -r '-FileName<DateTimeOriginal' -d "%Y%m%d_%H%M%S.%%e" /chemin/vers/dossier/
```

### Organiser dans des sous-dossiers par année/mois

```bash
exiftool '-Directory<DateTimeOriginal' -d "/chemin/destination/%Y/%m" /chemin/vers/dossier/
```

Déplace chaque photo dans un sous-dossier `2024/06/`, `2024/07/`, etc.

---

## Cas d'usage

### Anonymiser des photos avant de les partager

Supprime toutes les métadonnées (GPS, appareil, logiciel, auteur…) d'un lot de photos :

```bash
exiftool -overwrite_original -all= /chemin/vers/dossier/
```

### Corriger un décalage horaire après un voyage

Vous avez oublié de changer le fuseau horaire sur votre appareil photo. Toutes les photos ont 6 heures de retard :

```bash
exiftool -overwrite_original "-DateTimeOriginal+=0:0:0 6:0:0" /chemin/vers/dossier/
```

### Vérifier si une photo a été modifiée

Comparez la date EXIF (date de prise de vue) avec la date de modification du fichier :

```bash
exiftool -DateTimeOriginal -FileModifyDate photo.jpg
```

Un écart important peut indiquer une retouche ou un déplacement du fichier.

### Synchroniser la date du fichier avec la date EXIF

Utile après un transfert qui a écrasé les dates de fichier :

```bash
exiftool -overwrite_original "-FileModifyDate<DateTimeOriginal" /chemin/vers/dossier/
```

### Trouver toutes les photos prises avec un appareil précis

```bash
exiftool -r -if '$Make eq "Apple"' -FileName -DateTimeOriginal /chemin/vers/dossier/
```

Remplacez `Apple` par `Canon`, `Nikon`, `Sony`, etc.

### Extraire les miniatures embarquées (thumbnails)

Certains fichiers RAW contiennent une miniature JPEG intégrée :

```bash
exiftool -b -ThumbnailImage photo.cr2 > miniature.jpg
```

### Copier les métadonnées d'un fichier vers un autre

Utile après un traitement qui a effacé les métadonnées (export depuis Lightroom, etc.) :

```bash
exiftool -TagsFromFile original.jpg -all:all cible.jpg
```

### Lister toutes les focales utilisées dans un dossier

```bash
exiftool -r -FocalLength /chemin/vers/dossier/ | sort | uniq -c | sort -rn
```

---

## Référence rapide

| Besoin | Commande |
|--------|----------|
| Lire toutes les métadonnées | `exiftool fichier.jpg` |
| Lire un champ précis | `exiftool -NomDuChamp fichier.jpg` |
| Modifier un champ | `exiftool -overwrite_original -Champ="valeur" fichier.jpg` |
| Supprimer tout | `exiftool -overwrite_original -all= fichier.jpg` |
| Supprimer les GPS | `exiftool -overwrite_original -GPS:all= fichier.jpg` |
| Traitement récursif | Ajouter `-r` avant le chemin |
| Exporter en JSON | `exiftool -json fichier.jpg` |
| Renommer par date | `exiftool '-FileName<DateTimeOriginal' -d "%Y%m%d_%H%M%S.%%e" fichier.jpg` |
