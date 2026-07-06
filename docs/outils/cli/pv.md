# pv — voir passer les données dans un pipe

[pv](https://www.ivarch.com/programs/pv.shtml) (*pipe viewer*) s'insère dans
un pipeline et affiche **progression, débit, volume transféré et temps
restant estimé**. C'est la réponse au classique « ce `dd`/`tar`/`gzip`
travaille-t-il encore ? ». Version installée : **1.8.5** (paquet Ubuntu).

---

## Installation

Installé par le process de post-installation via la **liste de paquets APT**
(`config/packages_to_install.list` dans
[alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)).

```bash
pv --version         # pv 1.8.5
```

**Aucune configuration dans alm_dots** — pv est un maillon de pipeline pur :
pas de fichier rc, pas de variable d'environnement utile au quotidien, et
un alias figerait la position dans le pipe qui change à chaque usage.

---

## Principe

`pv` se comporte comme `cat` : il copie stdin vers stdout en affichant la
progression sur **stderr** (donc sans polluer les données) :

```console
$ pv gros-fichier.iso > /dev/null
2,10GiB 0:00:03 [ 692MiB/s] [==============>              ] 48% ETA 0:00:03
```

Quand pv connaît la taille (fichier en argument), il affiche un pourcentage
et une ETA ; sinon (flux), il montre volume cumulé et débit.

---

## Recettes

### Écrire une image disque avec progression (remplace le `dd` muet)

```bash
pv ubuntu-26.04.iso | sudo dd of=/dev/sdX bs=4M conv=fsync
```

Plus simple à retenir que `dd status=progress`, et l'ETA en plus.

### Compression / archivage

```bash
# tar + gzip avec progression sur la lecture
tar -cf - dossier/ | pv -s "$(du -sb dossier/ | awk '{print $1}')" \
  | gzip > dossier.tar.gz
```

`-s TAILLE` donne à pv la taille attendue → pourcentage + ETA exacts.
C'est le motif utilisé par le script de
[backup Google Drive](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md).

### Limiter le débit d'un transfert

```bash
# Copier en douceur, sans saturer le disque/réseau : 10 Mio/s max
pv -L 10m sauvegarde.tar.gz | ssh serveur 'cat > /backup/sauvegarde.tar.gz'
```

### Suivre un processus déjà lancé (`-d`)

Le `cp` géant tourne depuis 10 minutes sans que l'on sache où il en est :

```bash
pv -d "$(pgrep -f 'cp -r /source')"
```

pv s'attache aux descripteurs de fichiers du processus et montre la
progression de **chaque fichier ouvert** — sans rien interrompre.

### Compter sans afficher de barre

```bash
# Débit d'une génération de données, style compteur
./generateur | pv -btr > sortie.bin    # bytes + temps + débit
```

### Deux pv dans un même pipeline

```bash
# Progression avant ET après compression = ratio en direct
pv -cN brut gros.log | gzip | pv -cN compresse > gros.log.gz
     brut: 1,50GiB 0:00:12 [ 128MiB/s]
compresse:  187MiB 0:00:12 [15,6MiB/s]
```

`-c` (cursor) évite que les deux barres s'écrasent, `-N nom` les étiquette.

---

## Options à retenir

| Option | Effet |
|---|---|
| `-s TAILLE` | Taille attendue (pour % et ETA) : `-s 2g`, `-s "$(du -sb d \| awk '{print $1}')"` |
| `-L DÉBIT` | Limite le débit : `-L 10m` = 10 Mio/s |
| `-d PID` | S'attache à un processus en cours |
| `-c -N nom` | Multi-barres nommées dans un même pipeline |
| `-p -t -e -r -b` | Composants de l'affichage (progression, temps, ETA, débit, volume) |
| `-q` | Silencieux (utile avec `-L` : limiteur pur) |

---

## Références

- [Site pv](https://www.ivarch.com/programs/pv.shtml)
- `man pv`
- Utilisé par : [Backup Google Drive](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md)
