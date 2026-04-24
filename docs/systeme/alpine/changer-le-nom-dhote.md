# Changer le nom d'hôte

## Changement temporaire

Ce changement n'est actif que jusqu'au prochain redémarrage.

```bash
sudo hostname nouveau-nom
```

Pour vérifier le nom actif :

```bash
hostname
```

## Changement permanent

Il faut modifier deux fichiers, puis redémarrer le service.

### 1. `/etc/hostname`

Ce fichier contient uniquement le nom court de la machine.

```bash
sudo nano /etc/hostname
```

Contenu attendu :

```
nouveau-nom
```

### 2. `/etc/hosts`

Ce fichier associe le nom d'hôte à des adresses IP locales.

```bash
sudo nano /etc/hosts
```

Contenu attendu :

```
127.0.0.1   nouveau-nom.domaine.local nouveau-nom localhost.localdomain localhost
::1         localhost localhost.localdomain
```

> Remplacez `nouveau-nom` et `domaine.local` par les valeurs adaptées à votre environnement.

### 3. Appliquer le changement

Redémarrer le service hostname pour prendre en compte les modifications sans reboot :

```bash
sudo rc-service hostname restart
```

Vérifier que le nouveau nom est bien pris en compte :

```bash
hostname
hostname -f
```

> `hostname` retourne le nom court, `hostname -f` retourne le nom complet (FQDN).
