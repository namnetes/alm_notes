# Post-Installation Alpine Linux

Ce guide couvre les étapes essentielles à réaliser juste après l'installation
d'Alpine Linux. À la fin de cette page, votre système sera à jour, `sudo`
configuré, et les outils courants installés.

!!! info "Prérequis"
    - Alpine Linux installé (voir [VM avec Cloud-Init](vm-cloud-init.md))
    - Connexion en tant que **root** pour les premières étapes
    - Accès Internet depuis la VM

---

## 1. Activer le dépôt community

Alpine Linux propose deux dépôts de paquets :

| Dépôt | Contenu |
|---|---|
| **main** | Paquets essentiels, maintenus par l'équipe Alpine |
| **community** | Paquets supplémentaires, maintenus par la communauté |

Le dépôt `community` est **désactivé par défaut**. La quasi-totalité des outils
utiles s'y trouvent — il faut donc l'activer en priorité.

### Modifier le fichier de configuration

Le fichier `/etc/apk/repositories` liste les sources de paquets. Son contenu
ressemble à ceci :

```
http://dl-cdn.alpinelinux.org/alpine/v3.21/main
#http://dl-cdn.alpinelinux.org/alpine/v3.21/community
```

Le `#` en début de ligne signifie que la ligne est **commentée** (ignorée).
Il suffit de le supprimer pour activer le dépôt.

=== "Avec nano"

    ```bash
    nano /etc/apk/repositories
    ```

    Supprimez le `#` devant la ligne `community`.
    Enregistrez avec `Ctrl+O` puis quittez avec `Ctrl+X`.

=== "Avec sed"

    ```bash
    sed -i 's|^#\(.*community\)|\1|' /etc/apk/repositories
    ```

    Cette commande supprime automatiquement le `#` devant la ligne `community`,
    quelle que soit l'URL du miroir configuré.

Vérifiez le résultat :

```bash
cat /etc/apk/repositories
```

Les deux lignes doivent être actives (sans `#` devant `community`).

---

## 2. Mettre à jour le système

Après avoir activé les dépôts, mettez à jour l'index et les paquets installés :

```bash
apk update && apk upgrade
```

!!! tip "Bonne pratique"
    Lancez toujours ces deux commandes ensemble avant d'installer quoi que ce
    soit. `apk update` rafraîchit la liste des paquets disponibles, `apk upgrade`
    applique les mises à jour disponibles.

---

## 3. Installer et configurer sudo

### Pourquoi sudo ?

Par défaut, seul `root` peut effectuer des opérations d'administration
(installer des paquets, modifier des fichiers système…). Travailler en
permanence en tant que `root` est risqué : une faute de frappe peut avoir
des conséquences graves et irréversibles.

`sudo` (*superuser do*) permet à un utilisateur ordinaire d'exécuter
ponctuellement des commandes avec les droits administrateur, après saisie
de son mot de passe.

### Installation

```bash
apk add sudo
```

### Ajouter l'utilisateur au groupe wheel

Sur Alpine Linux, le groupe `wheel` regroupe les utilisateurs autorisés à
utiliser `sudo`. Remplacez `votre-utilisateur` par votre nom d'utilisateur :

```bash
addgroup votre-utilisateur wheel
```

!!! example "Exemple"
    Si votre compte s'appelle `alice` :
    ```bash
    addgroup alice wheel
    ```

### Activer les droits sudo pour le groupe wheel

Ouvrez la configuration de sudo avec la commande dédiée `visudo` :

!!! warning "Toujours utiliser `visudo`"
    Ne modifiez jamais `/etc/sudoers` directement avec un éditeur texte.
    `visudo` vérifie la syntaxe avant d'enregistrer — une erreur rendrait
    `sudo` inutilisable.

=== "Avec nano (recommandé)"

    Installez nano si ce n'est pas déjà fait :

    ```bash
    apk add nano
    ```

    Puis ouvrez `visudo` en forçant nano comme éditeur :

    ```bash
    EDITOR=nano visudo
    ```

=== "Avec vi (par défaut)"

    ```bash
    visudo
    ```

    `vi` est l'éditeur par défaut sur Alpine. Quelques commandes essentielles :

    | Action | Commande |
    |---|---|
    | Passer en mode insertion | `i` |
    | Revenir en mode commande | `Échap` |
    | Enregistrer et quitter | `:wq` + `Entrée` |
    | Quitter sans enregistrer | `:q!` + `Entrée` |

Recherchez la ligne suivante (elle est commentée) :

```
# %wheel ALL=(ALL:ALL) ALL
```

Supprimez le `#` pour l'activer :

```
%wheel ALL=(ALL:ALL) ALL
```

Enregistrez et quittez.

### Vérifier la configuration

Déconnectez-vous du compte root et reconnectez-vous avec votre compte
utilisateur :

```bash
exit
```

!!! info "Pourquoi se reconnecter ?"
    Les changements de groupe (ici l'ajout au groupe `wheel`) ne prennent
    effet qu'à la prochaine connexion. Tant que la session est ouverte,
    l'ancien groupe s'applique.

Vérifiez que `sudo` fonctionne :

```bash
sudo whoami
```

La réponse attendue est `root`. Si c'est le cas, `sudo` est opérationnel.

??? note "Personnaliser la durée du cache du mot de passe"
    Par défaut, sudo mémorise votre mot de passe pendant 5 minutes. Pour
    modifier ce délai, ajoutez dans `/etc/sudoers` via `visudo` :

    ```bash
    # Durée globale en minutes (ici 10 minutes)
    Defaults timestamp_timeout=10

    # Durée spécifique à un utilisateur (ici 60 minutes)
    Defaults:votre-utilisateur timestamp_timeout=60
    ```

??? note "Autoriser certaines commandes sans mot de passe"
    Pour des scripts automatisés (clonage de VM, redémarrage planifié…),
    il est possible d'autoriser des commandes précises sans saisie de
    mot de passe. À ajouter via `visudo` :

    ```
    # Autoriser votre-utilisateur à changer le nom d'hôte et éteindre sans mot de passe
    votre-utilisateur ALL=(ALL) NOPASSWD: /bin/hostname *, /sbin/poweroff
    ```

    !!! danger "À utiliser avec discernement"
        N'autorisez que les commandes strictement nécessaires. `NOPASSWD`
        contourne la protection offerte par sudo.

---

## 4. Paquets utiles

Ces paquets couvrent les besoins courants d'administration, de réseau et de
développement. Ils sont tous disponibles dans le dépôt `community`.

=== "Installation en une commande"

    Pour tout installer d'un coup :

    ```bash
    sudo apk add \
      bat bind-tools bzip2 coreutils curl eza fzf \
      git gnupg htop iftop iproute2 iputils jq \
      lsof nano ncdu net-tools nload nmap nmap-ncat \
      ripgrep stow strace tree unzip vim wget xz zip
    ```

=== "Par catégorie"

    Installez uniquement les catégories dont vous avez besoin.

    ---

    **Navigation et fichiers**

    ```bash
    sudo apk add bat eza tree ncdu fzf ripgrep
    ```

    | Paquet | Description |
    |---|---|
    | `bat` | Clone moderne de `cat` avec coloration syntaxique |
    | `eza` | Remplacement de `ls` avec couleurs et icônes |
    | `tree` | Affichage arborescent des répertoires |
    | `ncdu` | Analyse interactive de l'espace disque |
    | `fzf` | Recherche interactive dans l'historique, les fichiers… |
    | `ripgrep` | Recherche ultra-rapide dans les fichiers (remplace `grep`) |

    ---

    **Réseau**

    ```bash
    sudo apk add curl wget bind-tools iputils iproute2 net-tools iftop nload nmap nmap-ncat
    ```

    | Paquet | Description |
    |---|---|
    | `curl` | Transferts HTTP/FTP depuis le terminal |
    | `wget` | Téléchargement de fichiers via HTTP/FTP |
    | `bind-tools` | Outils DNS : `dig`, `nslookup`, `host` |
    | `iputils` | `ping`, `traceroute` |
    | `iproute2` | Commandes modernes : `ip`, `ss` |
    | `net-tools` | Outils classiques : `ifconfig`, `netstat` |
    | `iftop` | Surveillance de la bande passante en temps réel |
    | `nload` | Visualisation du trafic réseau |
    | `nmap` | Scanner de ports et d'hôtes réseau |
    | `nmap-ncat` | Netcat version nmap (communication réseau) |

    ---

    **Texte et données**

    ```bash
    sudo apk add nano vim jq
    ```

    | Paquet | Description |
    |---|---|
    | `nano` | Éditeur de texte simple (idéal pour débuter) |
    | `vim` | Éditeur de texte avancé |
    | `jq` | Manipulation de JSON en ligne de commande |

    ---

    **Compression**

    ```bash
    sudo apk add unzip zip xz bzip2
    ```

    | Paquet | Description |
    |---|---|
    | `unzip` / `zip` | Compression/décompression `.zip` |
    | `xz` | Compression `.xz` (archives `.tar.xz`) |
    | `bzip2` | Compression `.bz2` (archives `.tar.bz2`) |

    ---

    **Développement et administration**

    ```bash
    sudo apk add git gnupg stow htop lsof strace coreutils
    ```

    | Paquet | Description |
    |---|---|
    | `git` | Gestion de versions |
    | `gnupg` | Chiffrement, signature et gestion de clés GPG |
    | `stow` | Gestion de liens symboliques (dotfiles) |
    | `htop` | Visualisation interactive des processus |
    | `lsof` | Liste des fichiers ouverts par les processus |
    | `strace` | Traçage des appels système (débogage) |
    | `coreutils` | Outils GNU de base (`ls`, `cp`, `mv`…) |

---

## 5. Pour aller plus loin

| Sujet | Page dédiée |
|---|---|
| Changer le nom d'hôte de la VM | [Changer le nom d'hôte](changer-le-nom-dhote.md) |
| Partager un répertoire entre l'hôte et la VM | [Création d'un partage de répertoire(s)](creation-dun-partage-de-repertoires.md) |
| Installer Docker | [Docker sur Alpine](docker.md) |

---

## 6. Compatibilité des terminaux (optionnel)

Si vous vous connectez à la VM depuis un terminal moderne (Kitty, foot,
Ghostty, WezTerm…) et que vous obtenez une erreur du type
`Error opening terminal: xterm-kitty`, consultez la page dédiée :

[Compatibilité des terminaux via SSH](compatibilite-terminal.md)
