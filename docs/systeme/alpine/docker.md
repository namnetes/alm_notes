# Docker sur Alpine Linux

Ce guide explique comment installer, configurer et utiliser Docker sur une
machine virtuelle Alpine Linux. Il s'adresse aussi bien aux débutants qu'aux
utilisateurs déjà familiers avec Linux.

!!! info "Prérequis"
    - Une VM Alpine Linux installée et à jour (voir [VM avec Cloud-Init](vm-cloud-init.md))
    - Un accès Internet depuis la VM
    - Un utilisateur avec les droits `sudo`

---

## Qu'est-ce que Docker ?

Docker est une plateforme de **conteneurisation**. Un conteneur est un
environnement isolé qui embarque une application et toutes ses dépendances.
Contrairement à une machine virtuelle, un conteneur partage le noyau de
l'hôte : il est donc très léger et démarre en quelques secondes.

| Concept | Définition |
|---|---|
| **Image** | Modèle en lecture seule qui décrit un environnement (ex. une image Nginx avec sa configuration) |
| **Conteneur** | Instance en cours d'exécution d'une image |
| **Registry** | Entrepôt d'images (Docker Hub est le plus connu) |
| **Volume** | Répertoire persistant partagé entre l'hôte et un conteneur |

!!! tip "Pourquoi Docker sur Alpine Linux ?"
    Alpine Linux est une distribution particulièrement adaptée à Docker.
    Elle est légère (~5 Mo), sécurisée, et ses images Docker sont parmi
    les plus compactes disponibles. C'est la base la plus utilisée pour
    construire des images Docker minimalistes.

---

## Mise à jour du système

Avant toute installation, mettez le système à jour :

```bash
sudo apk update && sudo apk upgrade
```

---

## Installation de Docker

```bash
sudo apk add docker
```

Vérifiez que l'installation s'est bien déroulée :

```bash
docker --version
```

Exemple de sortie attendue :

```
Docker version 27.x.x, build xxxxxxx
```

---

## Démarrer Docker

Sur Alpine Linux, les services sont gérés par **OpenRC** (et non par systemd
comme sur Ubuntu ou Fedora). Les commandes sont donc différentes.

### Démarrer le service Docker

```bash
sudo rc-service docker start
```

### Vérifier que Docker est actif

```bash
sudo rc-service docker status
```

Résultat attendu :

```
 * status: started
```

### Activer Docker au démarrage du système

Sans cette étape, Docker ne démarre pas automatiquement après un redémarrage
de la VM :

```bash
sudo rc-update add docker
```

Vérifiez que Docker est bien dans le niveau de démarrage `default` :

```bash
rc-update show | grep docker
```

!!! info "OpenRC vs systemd"
    Sur Alpine Linux, les commandes de gestion des services sont :

    | Action | Alpine (OpenRC) | Ubuntu (systemd) |
    |---|---|---|
    | Démarrer | `rc-service docker start` | `systemctl start docker` |
    | Arrêter | `rc-service docker stop` | `systemctl stop docker` |
    | Statut | `rc-service docker status` | `systemctl status docker` |
    | Activer au boot | `rc-update add docker` | `systemctl enable docker` |

---

## Utiliser Docker sans `sudo`

Par défaut, seul `root` peut exécuter les commandes Docker. Pour permettre
à un utilisateur normal de le faire, ajoutez-le au groupe `docker` :

```bash
sudo addgroup $USER docker
```

!!! warning "Reconnexion obligatoire"
    Le changement de groupe ne prend effet qu'à la prochaine connexion.
    Déconnectez-vous puis reconnectez-vous, ou ouvrez une nouvelle session :

    ```bash
    newgrp docker
    ```

Vérifiez que votre utilisateur est bien dans le groupe :

```bash
groups
```

Le mot `docker` doit apparaître dans la liste.

!!! danger "Implications de sécurité"
    Appartenir au groupe `docker` donne des droits équivalents à `root` sur
    l'hôte. Ne l'accordez qu'aux utilisateurs de confiance.

---

## Vérification : premier conteneur

Testez que Docker fonctionne correctement :

```bash
docker run hello-world
```

Docker télécharge l'image `hello-world` depuis Docker Hub et l'exécute.
Vous devez voir un message commençant par :

```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

Si cette commande réussit, Docker est opérationnel.

---

## Commandes Docker essentielles

### Gérer les images

```bash
# Télécharger une image sans la lancer
docker pull nginx

# Lister les images téléchargées
docker images

# Supprimer une image
docker rmi nginx
```

### Lancer des conteneurs

```bash
# Lancer un conteneur interactif (Alpine dans Alpine !)
docker run -it alpine sh

# Lancer un conteneur en arrière-plan (mode détaché)
docker run -d --name mon-nginx -p 8080:80 nginx

# Lancer avec un volume (répertoire partagé hôte ↔ conteneur)
docker run -d \
  --name mon-nginx \
  -p 8080:80 \
  -v /home/utilisateur/html:/usr/share/nginx/html \
  nginx
```

| Option | Signification |
|---|---|
| `-it` | Mode interactif avec terminal |
| `-d` | Arrière-plan (detached) |
| `--name` | Nom du conteneur |
| `-p 8080:80` | Port hôte `8080` → port conteneur `80` |
| `-v src:dst` | Volume : répertoire hôte `src` monté sur `dst` |

### Gérer les conteneurs en cours d'exécution

```bash
# Lister les conteneurs actifs
docker ps

# Lister tous les conteneurs (actifs et arrêtés)
docker ps -a

# Afficher les journaux d'un conteneur
docker logs mon-nginx

# Afficher les journaux en temps réel
docker logs -f mon-nginx

# Ouvrir un shell dans un conteneur en cours d'exécution
docker exec -it mon-nginx sh

# Arrêter un conteneur
docker stop mon-nginx

# Redémarrer un conteneur
docker restart mon-nginx

# Supprimer un conteneur arrêté
docker rm mon-nginx

# Arrêter et supprimer en une commande
docker rm -f mon-nginx
```

### Nettoyage

```bash
# Supprimer tous les conteneurs arrêtés
docker container prune

# Supprimer les images non utilisées
docker image prune

# Nettoyage global (conteneurs, images, réseaux non utilisés)
docker system prune

# Voir l'espace disque utilisé par Docker
docker system df
```

!!! tip "Nettoyage régulier"
    Les images et conteneurs s'accumulent rapidement. Lancez `docker system prune`
    régulièrement pour libérer de l'espace disque.

---

## Docker Compose

Docker Compose permet de définir et lancer plusieurs conteneurs ensemble
via un fichier `compose.yml` (ou `docker-compose.yml`).

### Installer Docker Compose

Deux versions coexistent sur Alpine :

| Version | Commande shell | Installation |
|---|---|---|
| **v1** (legacy, Python) | `docker-compose` | `sudo apk add docker-compose` |
| **v2** (recommandée, plugin Go) | `docker compose` | `sudo apk add docker-cli-compose` |

```bash
# Installer Compose v2 (recommandé)
sudo apk add docker-cli-compose

# Vérifier
docker compose version
```

!!! warning "docker-compose vs docker compose"
    - `docker-compose` (avec tiret) = version 1, maintenue mais obsolète
    - `docker compose` (sans tiret) = version 2, intégrée au CLI Docker

    Utilisez toujours **`docker compose`** (v2) pour les nouveaux projets.

### Exemple de fichier `compose.yml`

Voici un exemple concret : un serveur Nginx qui sert des fichiers statiques.

Créez un répertoire de test :

```bash
mkdir -p ~/test-compose/html
cd ~/test-compose
```

Créez une page HTML de test :

```bash
cat > html/index.html << 'EOF'
<!DOCTYPE html>
<html>
<body>
  <h1>Docker Compose fonctionne !</h1>
</body>
</html>
EOF
```

Créez le fichier `compose.yml` :

```yaml
services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro
    restart: unless-stopped
```

| Clé | Signification |
|---|---|
| `image` | Image Docker à utiliser |
| `ports` | Correspondance port hôte : port conteneur |
| `volumes` | Montage de répertoire (`ro` = lecture seule) |
| `restart` | Politique de redémarrage automatique |

### Commandes Docker Compose essentielles

```bash
# Démarrer les services (en arrière-plan)
docker compose up -d

# Voir l'état des services
docker compose ps

# Afficher les journaux
docker compose logs

# Afficher les journaux en temps réel
docker compose logs -f

# Arrêter les services (sans supprimer)
docker compose stop

# Arrêter et supprimer les conteneurs
docker compose down

# Arrêter, supprimer conteneurs ET volumes
docker compose down -v

# Redémarrer après modification du compose.yml
docker compose up -d --force-recreate
```

### Tester l'exemple

```bash
# Depuis ~/test-compose
docker compose up -d

# Vérifier que le service tourne
docker compose ps

# Tester depuis la VM
curl http://localhost:8080
```

Vous devez voir le contenu de `index.html`. Arrêtez ensuite le service :

```bash
docker compose down
```

---

## Dépannage

### Docker refuse de démarrer

```bash
# Vérifier les journaux du service
sudo rc-service docker status
dmesg | tail -20
```

Cause fréquente : le module noyau `overlay` n'est pas chargé.

```bash
# Charger le module
sudo modprobe overlay

# Le rendre persistant au redémarrage
echo "overlay" | sudo tee -a /etc/modules
```

### `Permission denied` lors d'une commande docker

Votre utilisateur n'est pas dans le groupe `docker`, ou la session n'a pas
été rechargée après l'ajout.

```bash
groups            # vérifier les groupes actuels
sudo addgroup $USER docker
newgrp docker     # recharger sans se déconnecter
```

### Le port est déjà utilisé

```bash
# Voir quel processus utilise le port 8080
sudo ss -tulnp | grep 8080

# Choisir un autre port dans compose.yml
# "8081:80" au lieu de "8080:80"
```

### Espace disque insuffisant

```bash
# Voir la place disponible
df -h

# Nettoyer Docker
docker system prune -f
docker volume prune -f
```

---

## Pour aller plus loin

- **Lazydocker** — interface graphique en terminal pour gérer Docker :
  voir la page [Lazydocker](lazydocker.md)
- **Partage de répertoires** — pour partager des dossiers entre l'hôte et
  la VM : voir [Partage de répertoires via VirtioFS](creation-dun-partage-de-repertoires.md)
- **Documentation officielle Docker** : [docs.docker.com](https://docs.docker.com)
