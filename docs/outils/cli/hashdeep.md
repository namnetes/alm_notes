# hashdeep — empreintes et audit d'intégrité récursifs

[hashdeep](https://github.com/jessek/hashdeep) calcule des sommes de
contrôle (MD5, SHA-1, SHA-256…) **récursivement** sur des arborescences
entières, et surtout sait ensuite **auditer** : comparer l'état actuel d'un
répertoire à un manifeste de référence et dire précisément ce qui a changé,
disparu ou été ajouté. Version installée : **4.4** (paquet Ubuntu).

Le paquet fournit aussi `md5deep`, `sha1deep`, `sha256deep` — mêmes options,
algorithme fixé par le nom.

---

## Installation

Installé par le process de post-installation via la **liste de paquets APT**
(`config/packages_to_install.list` dans
[alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)).
Le paquet `md5deep` historique est une coquille vide qui pointe vers
`hashdeep` — seule l'entrée `hashdeep` figure dans la liste.

```bash
hashdeep -V          # 4.4
```

**Aucune configuration dans alm_dots** — choix délibéré : outil ponctuel,
sans variable d'environnement ni fichier rc ; les recettes ci-dessous
remplacent avantageusement des alias qu'on n'utiliserait pas assez pour les
retenir.

---

## Les deux gestes essentiels

### 1. Créer un manifeste de référence

```bash
hashdeep -c sha256 -r ~/Documents > ~/manifeste-documents.txt
```

- `-c sha256` : algorithme (défaut : MD5 **et** SHA-256 — précisez pour
  alléger)
- `-r` : récursif
- Le manifeste liste taille + empreinte + chemin absolu de chaque fichier.

### 2. Auditer plus tard contre ce manifeste

```bash
hashdeep -c sha256 -r -a -k ~/manifeste-documents.txt ~/Documents
hashdeep: Audit passed
```

- `-k fichier` : charge le manifeste « connu »
- `-a` : mode audit — verdict global réussite/échec
- Ajouter `-v` (ou `-vv`) pour le détail : fichiers modifiés, déplacés,
  absents du manifeste, connus mais disparus.

```console
$ hashdeep -c sha256 -r -a -vv -k manifeste.txt ~/Documents
/home/galan/Documents/rapport.odt: No match     ← modifié ou nouveau
/home/galan/Documents/ancien.txt: Known file not used  ← disparu
hashdeep: Audit failed
   Files matched: 412
   Files moved: 3
   New files found: 1
   Known files not found: 1
```

---

## Recettes

### Vérifier une copie (sauvegarde USB, transfert réseau)

```bash
hashdeep -c sha256 -r /source > /tmp/src.txt
hashdeep -c sha256 -r -a -k /tmp/src.txt /media/usb/copie \
  && echo "Copie conforme"
```

!!! warning "Chemins absolus dans le manifeste"
    L'audit compare aussi les chemins. Pour comparer deux arborescences à
    des emplacements différents, générer les manifestes **en chemins
    relatifs** en se plaçant dans chaque racine :

    ```bash
    (cd /source && hashdeep -c sha256 -r -l .) > /tmp/src.txt
    (cd /media/usb/copie && hashdeep -c sha256 -r -a -l -k /tmp/src.txt .)
    ```

    `-l` = chemins relatifs.

### Détecter la corruption silencieuse (*bitrot*) d'archives froides

```bash
# À l'archivage
hashdeep -c sha256 -r -l ~/archives > ~/archives/.manifeste

# Contrôle périodique
cd ~/archives && hashdeep -c sha256 -r -l -a -k .manifeste . \
  || echo "ALERTE : intégrité compromise"
```

### Retrouver des fichiers connus (mode *matching*)

```bash
# Quels fichiers de ce dossier sont déjà dans mon manifeste ? (doublons)
hashdeep -c sha256 -r -m -k manifeste.txt ~/Téléchargements

# Lesquels sont inconnus ? (-x = négatif)
hashdeep -c sha256 -r -x -k manifeste.txt ~/Téléchargements
```

### Empreinte d'un seul fichier, façon `sha256sum`

```bash
sha256deep archive.tar.gz          # fourni par le paquet hashdeep
```

C'est ce que fait le script de
[backup Google Drive](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md) :
SHA-256 de chaque archive `tar.gz`, comparé au précédent pour **dédupliquer**
les sauvegardes identiques.

---

## hashdeep ou `sha256sum` ?

| Besoin | Outil |
|---|---|
| Empreinte d'un ou deux fichiers | `sha256sum` (coreutils, partout) |
| Vérifier un ISO téléchargé (`SHA256SUMS`) | `sha256sum -c` |
| Manifeste **récursif** d'une arborescence | **hashdeep** |
| Audit complet : modifiés + nouveaux + disparus + déplacés | **hashdeep** (`sha256sum -c` ne voit ni les nouveaux ni les déplacés) |
| Chercher des doublons contre une base connue | **hashdeep** `-m` / `-x` |

---

## Références

- [Dépôt hashdeep](https://github.com/jessek/hashdeep)
- `man hashdeep`
- Utilisé par : [Backup Google Drive](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md)
