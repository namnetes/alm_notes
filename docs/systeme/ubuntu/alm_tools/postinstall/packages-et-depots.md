# Packages et dépôts

Cette page recense l'inventaire complet de ce que `postinstall` installe ou
retire : dépôts PPA, paquets APT (regroupés par usage), applications Snap et
outils installés hors APT par des modules dédiés. Chaque liste correspond à un
fichier de configuration ou à un module, indiqué dans le titre de section.

---

## Dépôts PPA — `postinstall/config/ppas.list`

| PPA | Outil installé | Statut |
|-----|---------------|--------|
| `ppa:ansible/ansible` | Ansible | Commenté — attendre confirmation support Ubuntu 26.04 |

!!! warning "Compatibilité 26.04"
    Le PPA Ansible est désactivé jusqu'à confirmation que le nom de code *resolute* est supporté.
    Vérification : `curl -s https://launchpad.net/~ansible/+archive/ubuntu/ansible | grep -i "resolute"`

---

## Paquets APT — `postinstall/config/packages_to_install.list`

### Outils système

| Paquet | Description |
|--------|-------------|
| `build-essential` | Suite de compilation C/C++ — gcc, g++, make, libc6-dev |
| `sudo` | Élévation de privilèges par commande |
| `lsb-release` | Identification de la distribution (nom de code, version) |
| `software-properties-common` | Gestion des dépôts APT et des PPAs |
| `gnome-tweaks` | Ajustements visuels GNOME non exposés dans les paramètres |
| `gnome-shell-extension-manager` | Interface graphique pour installer et gérer les extensions GNOME Shell |
| `gnome-shell-extensions` | Pack d'extensions officielles GNOME Shell |

### Utilitaires shell

| Paquet | Description |
|--------|-------------|
| `avahi-daemon` | Démon mDNS/DNS-SD pour la découverte de services en réseau local (Zeroconf) |
| `avahi-utils` | Outils CLI pour interroger les services Avahi sur le réseau |
| `bat` | Remplacement de `cat` avec coloration syntaxique, numéros de ligne et intégration Git |
| `btop` | Moniteur de ressources interactif et personnalisable (CPU, RAM, disque, réseau) |
| `colordiff` | Enveloppe autour de `diff` qui colorise les sorties pour une lecture plus rapide |
| `curl` | Transfert de données via HTTP, HTTPS, FTP — incontournable pour les scripts |
| `dos2unix` | Convertit les fins de ligne Windows (`\r\n`) en Unix (`\n`) |
| `fd-find` | Remplacement de `find` — syntaxe intuitive, bien plus rapide, respect `.gitignore` |
| `fdupes` | Détecte et supprime les fichiers dupliqués par comparaison de contenu (hash) |
| `fzf` | Sélecteur flou interactif universel — s'intègre à bash, vim, git |
| `jq` | Processeur JSON en ligne de commande — filtre, transforme, formate |
| `man-db` | Base de données des pages de manuel et commande `man` |
| `meld` | Outil graphique de comparaison et fusion de fichiers et répertoires, intégré à Git |
| `netcat-openbsd` | Couteau suisse TCP/UDP — test de ports, tunnels, transferts de fichiers |
| `pdfgrep` | Recherche d'expressions régulières dans les fichiers PDF |
| `pv` | Barre de progression pour flux de données via pipes — utilisé par `tar`/`gzip` dans les scripts de sauvegarde |
| `rename` | Renommage de fichiers en masse par expressions régulières Perl |
| `ripgrep` | Remplacement de `grep` ultra-rapide avec respect `.gitignore` et coloration |
| `delta` | Visualiseur de diffs Git avec coloration syntaxique et numéros de ligne |
| `shellcheck` | Analyseur statique pour scripts Bash — détecte bugs et mauvaises pratiques |
| `aspell` | Vérificateur orthographique interactif en ligne de commande |
| `aspell-fr` | Dictionnaire français pour aspell |
| `hunspell` | Moteur de vérification orthographique utilisé par LibreOffice et Firefox |
| `hunspell-fr` | Dictionnaire français pour hunspell |
| `hunspell-en-us` | Dictionnaire anglais américain pour hunspell |
| `hyphen-fr` | Règles de coupure syllabique française pour LibreOffice |
| `hyphen-en-us` | Règles de coupure syllabique anglaise pour LibreOffice |
| `mythes-en-us` | Thésaurus anglais pour le module Synonymes de LibreOffice |
| `enchant-2` | Bibliothèque d'abstraction orthographique (aspell/hunspell) utilisée par certains éditeurs |
| `strace` | Trace en temps réel les appels système d'un processus — indispensable pour le débogage |
| `tree` | Affiche l'arborescence d'un répertoire sous forme visuelle dans le terminal |
| `wget` | Téléchargement récursif de fichiers web (HTTP, HTTPS, FTP), supporte les reprises |
| `xclip` | Presse-papiers X11 scriptable — compatible XWayland sur Ubuntu 26.04 |
| `wl-clipboard` | Presse-papiers natif Wayland (`wl-copy` / `wl-paste`) |
| `zoxide` | Remplacement intelligent de `cd` — apprend les répertoires fréquents, jump rapide |

### Environnement dynamique

| Paquet | Description |
|--------|-------------|
| `direnv` | Charge et décharge automatiquement les variables d'environnement selon le répertoire courant |

### Développement général

| Paquet | Description |
|--------|-------------|
| `exuberant-ctags` | Génère des fichiers de tags pour la navigation dans le code source (C, Python, etc.) |
| `git` | Système de gestion de versions distribué |
| `tig` | Interface texte (TUI) pour parcourir l'historique Git |
| `gawk` | Implémentation GNU de awk — traitement avancé de fichiers texte structurés |
| `gdb` | Débogueur GNU pour C et C++ — points d'arrêt, inspection mémoire, backtraces |
| `indent` | Reformate automatiquement le code C selon les conventions GNU ou K&R |
| `libusb-dev` | En-têtes de développement pour la communication USB directe (libusb-1.0) |
| `stow` | Gestion de symlinks pour les dotfiles — crée une arborescence miroir dans `$HOME` |

### Développement Python

| Paquet | Description |
|--------|-------------|
| `pipx` | Installe des outils Python dans des environnements isolés automatiquement gérés |
| `python3-full` | Python 3 complet avec bibliothèques standard, IDLE et support venv |
| `python3-pip` | Gestionnaire de paquets PyPI pour Python |
| `python3-pylsp` | Serveur LSP Python — autocomplétion, linting et navigation dans les IDE |
| `python3-pytest` | Framework de tests unitaires Python moderne — fixtures, parametrize, plugins |
| `python3-venv` | Création d'environnements virtuels Python isolés |
| `sqlite3` | Interface CLI pour les bases de données SQLite |
| `sqlite3-doc` | Documentation officielle SQLite avec exemples |

### Documentation et visualisation

| Paquet | Description |
|--------|-------------|
| `elfutils` | Outils d'analyse et de manipulation de binaires ELF (Linux natif) |
| `graphviz` | Génération de graphes à partir de descriptions DOT — diagrammes d'architecture |
| `imagemagick` | Suite de manipulation d'images en ligne de commande (redimensionnement, conversion, watermark) |
| `poppler-utils` | Extraction de texte et d'images depuis des fichiers PDF (`pdftotext`, `pdfimages`) |
| `pandoc` | Conversion universelle de documents : Markdown → PDF, HTML, DOCX, EPUB |
| `texlive-xetex` | Moteur XeLaTeX pour la génération de PDF Unicode avec Pandoc |
| `texlive-fonts-recommended` | Polices LaTeX recommandées compatibles Unicode et XeLaTeX |
| `texlive-latex-extra` | Extensions LaTeX pour tableaux avancés, images, styles personnalisés |
| `wkhtmltopdf` | Conversion HTML → PDF via WebKit — rendu fidèle au navigateur |

### Gestion des photos et images

| Paquet | Description |
|--------|-------------|
| `dupeguru` | Détecteur graphique de fichiers et images en double — comparaison par hash et contenu visuel |
| `exiv2` | Lecture et édition des métadonnées EXIF, IPTC et XMP des photos en ligne de commande |
| `gthumb` | Visionneuse d'images avec organisation par albums, retouches légères et export |

### Interface et GNOME

| Paquet | Description |
|--------|-------------|
| `dconf-editor` | Éditeur graphique du registre GNOME — accès aux clés dconf non exposées dans les paramètres |
| `gir1.2-gtk-4.0` | Données d'introspection GObject pour GTK 4 — nécessaire pour certains scripts PyGObject |
| `gnome-calendar` | Calendrier GNOME avec synchronisation GNOME Online Accounts |
| `gnome-contacts` | Carnet d'adresses GNOME intégré à GNOME Online Accounts |
| `gnome-user-share` | Partage de fichiers personnel via WebDAV ou Bluetooth |
| `fonts-noto` | Famille de polices Unicode complète — couverture mondiale sans "tofu" (□) |
| `gparted` | Éditeur de partitions graphique — redimensionnement, création, formatage |
| `nautilus-admin` | Ajoute "Ouvrir en tant qu'administrateur" dans le menu contextuel Nautilus |
| `nautilus-image-converter` | Conversion et redimensionnement d'images depuis Nautilus |
| `nautilus-share` | Partage de dossiers Samba directement depuis Nautilus |
| `nautilus-wipe` | Suppression sécurisée de fichiers (écrasement) depuis Nautilus |

### Sécurité et chiffrement

| Paquet | Description |
|--------|-------------|
| `ecryptfs-utils` | Chiffrement de répertoires à la volée via eCryptfs (couche VFS Linux) |
| `libpam-pwquality` | Module PAM qui impose des règles de complexité sur les mots de passe |
| `libsecret-tools` | Accès en ligne de commande au trousseau GNOME Keyring (`secret-tool`) |

### Intégrité et vérification de fichiers

| Paquet | Description |
|--------|-------------|
| `hashdeep` | Calcul récursif et vérification de checksums multiples (MD5, SHA1, SHA256, Tiger) — utilisé pour la déduplication d'archives dans les scripts de sauvegarde |
| `rhash` | Génération rapide de checksums multiples depuis la ligne de commande |

### Réseau et partage

| Paquet | Description |
|--------|-------------|
| `bridge-utils` | Création et gestion de ponts réseau Linux — utilisé pour les interfaces VM et containers |
| `cifs-utils` | Montage de partages Windows/Samba via le protocole CIFS/SMB |
| `samba` | Serveur de fichiers et d'imprimantes SMB/CIFS pour partager avec Windows |

### Virtualisation KVM

| Paquet | Description |
|--------|-------------|
| `acl` | Listes de contrôle d'accès étendues — requis par vmforge pour les permissions libvirt-qemu |
| `cloud-image-utils` | Contient `cloud-localds` pour créer les seeds ISO cloud-init (requis par vmforge) |
| `libvirt-clients` | Outils CLI pour piloter libvirt : `virsh`, `virt-xml` |
| `libvirt-clients-qemu` | Clients spécifiques QEMU pour la gestion via libvirt |
| `libvirt-daemon` | Service principal libvirt — gestion du cycle de vie des VMs |
| `libvirt-daemon-driver-lxc` | Support des containers LXC dans libvirt |
| `libvirt-daemon-driver-vbox` | Support VirtualBox dans libvirt |
| `libvirt-daemon-system` | Intégration systemd de libvirt avec démarrage automatique (requis par vmforge) |
| `qemu-kvm` | Moteur de virtualisation QEMU avec accélération KVM matérielle (requis par vmforge) |
| `qemu-system-x86` | Émulateur complet x86 — VMs 32 et 64 bits |
| `virt-manager` | Interface graphique de gestion de machines virtuelles KVM |
| `virtiofsd` | Démon virtio-fs pour les partages de répertoires entre hôte et VM |

### GPU et performances

| Paquet | Description |
|--------|-------------|
| `mesa-utils` | `glxinfo` et `glxgears` — diagnostic des drivers OpenGL et GPU |
| `vulkan-tools` | `vulkaninfo` — vérification des drivers Vulkan (RADV pour AMD, NVIDIA) |
| `numactl` | Contrôle de l'affinité CPU/NUMA et de la topologie mémoire |

### Multimédia et édition

| Paquet | Description |
|--------|-------------|
| `shotcut` | Montage vidéo non linéaire open source — timeline, filtres, export multi-format |
| `vlc` | Lecteur multimédia universel — tous formats, streaming, lecture de disques |
| `ffmpeg` | Suite de traitement audio/vidéo en ligne de commande — conversion, extraction, streaming |

### Indexation et recherche

| Paquet | Description |
|--------|-------------|
| `ncdu` | Analyseur de disque interactif dans le terminal — navigation, suppression |
| `plocate` | Version rapide de `locate` — recherche de fichiers par nom dans une base indexée |

### Autres outils

| Paquet | Description |
|--------|-------------|
| `dbus-x11` | Support D-Bus pour les applications X11 |
| `kitty-terminfo` | Terminfo `xterm-kitty` seul — kitty lui-même est installé par `make kitty` (installeur upstream, voir groupe apps) |
| `sharutils` | Encodage/décodage d'archives shell (`shar`, `uudecode`) |

---

## Paquets et applications supprimés

### APT — `postinstall/config/packages_to_remove.list`

| Paquet | Raison |
|--------|--------|
| `screen` | Remplacé par tmux ou kitty — héritage historique non utile |

### Firefox — module `remove-firefox`

| Application | Raison |
|-------------|--------|
| `firefox` | Snap trop lourd et lent à démarrer — remplacé par Brave (DEB) |

!!! warning "Suppression définitive, pas seulement le Snap"
    Sur Ubuntu (et TUXEDO OS), `firefox` est aussi un **paquet APT
    transitoire** dont l'unique rôle est de (ré)installer le Snap à chaque
    configuration/mise à jour du paquet. Il est marqué *automatique* car
    c'est un `Recommends` de `ubuntu-desktop`/`ubuntu-desktop-minimal` —
    purger uniquement le Snap ne suffit donc pas : le paquet deb revient au
    prochain `apt dist-upgrade` (`sudo make system`) et réinstalle le Snap
    avec lui.

    Le module `remove-firefox` traite les deux couches :

    1. **Purge du paquet APT** `firefox` (et `firefox-esr` si présent).
    2. **Épinglage anti-réinstallation** dans
       `/etc/apt/preferences.d/no-firefox.pref` (`Pin-Priority: -1`), pour
       qu'APT ne le réinstalle jamais afin de satisfaire le `Recommends`
       d'`ubuntu-desktop-minimal` sur un futur `dist-upgrade`.
    3. **Purge du Snap** (`snap disable` + `snap remove --purge`).
    4. **Résidus utilisateur** : `~/.mozilla`, `~/.cache/mozilla`,
       `~/snap/firefox`.
    5. **Résidus système** : profil AppArmor
       (`/etc/apparmor.d/firefox`), lanceur `.desktop`, règle udev
       (`70-snap.firefox.rules`), unités systemd
       `snap-firefox-*.mount` orphelines, entrées `update-alternatives`
       (`x-www-browser`, `gnome-www-browser`) pointant vers le binaire
       disparu.

    `firefox` étant un `Recommends` (pas un `Depends` dur) de ces
    métapaquets, le purger ne casse rien côté GNOME/Ubuntu.

---

## Applications Snap — `postinstall/config/snap_packages.list`

| Snap | Option | Description |
|------|--------|-------------|
| `kolourpaint` | — | Éditeur graphique KDE simple et direct — équivalent de Paint pour GNOME. Retouche d'images, annotations, capture d'écran |
| `onlyoffice-desktopeditors` | — | Suite bureautique complète (Writer, Calc, Impress) avec haute compatibilité Microsoft Office. Rendu fidèle des fichiers `.docx`, `.xlsx`, `.pptx` |

---

## GSConnect — module `gsconnect`

| Paquet | Rôle |
|--------|------|
| `gnome-shell-extension-gsconnect` | Implémentation de KDE Connect pour GNOME Shell |
| `sshfs` | Montage du stockage du téléphone comme un dossier réseau |
| `python3-nautilus` | Intégration clic-droit « Envoyer vers un appareil mobile » |

Installé via APT par un module dédié plutôt que par
`packages_to_install.list`, car l'installation ne s'arrête pas au paquet :
le module ouvre aussi le port KDE Connect (`1716/tcp` + `1716/udp`) dans
ufw. L'activation effective de l'extension (impossible à faire de façon
fiable pendant le provisionnement, en l'absence de session GNOME live) est
différée au premier login — voir
[session-checks — 20-gsconnect](session-checks.md#le-controle-20-gsconnect).

---

## Outils installés hors APT — modules dédiés

| Outil | Méthode d'installation | Description |
|-------|----------------------|-------------|
| `uv` | Script officiel `astral.sh` | Gestionnaire de paquets et d'environnements Python ultra-rapide — remplace pip, venv, pipx |
| `xan` | Binaire GitHub (Rust) | Traitement et exploration de fichiers CSV en ligne de commande — tri, filtre, stats, SQL |
| `eza` | Binaire GitHub (Rust) | Remplacement de `ls` avec couleurs, icônes, arborescence Git et affichage étendu |
| Starship | Script officiel `starship.rs` | Invite de commandes contextuelle multi-shell — Git, Python, Node, Rust, durée d'exécution |
| `fzf` | Binaire GitHub | Sélecteur flou universel intégré à bash — historique, fichiers, branches Git |
| `rclone` | Script officiel `rclone.org` | Synchronisation cloud (Google Drive, S3…) — le paquet APT est trop en retard sur l'amont pour un outil qui suit des APIs cloud mouvantes |
| FiraCode Nerd Font | Script d'installation | Police à ligatures pour le code avec glyphes Nerd Font (icônes de terminaux) |
| JetBrains Mono | Script d'installation | Police monospace JetBrains avec ligatures — optimisée pour la lisibilité du code |
| Cascadia Code | Script d'installation | Police Microsoft avec ligatures et variante Nerd Font |
| Brave | Dépôt APT officiel Brave | Navigateur Chromium axé vie privée — bloqueur de publicités et traceurs intégré |
| `fnm` | Script officiel | Gestionnaire de versions Node.js — installation et basculement instantané entre versions |
| Node.js LTS | via `fnm` | Environnement d'exécution JavaScript côté serveur — version LTS courante |
| Zed | Script officiel `zed.dev` | Éditeur de code collaboratif en temps réel, GPU-accelerated, LSP et IA intégrés |
| kitty | Installeur officiel `sw.kovidgoyal.net` | Terminal GPU — binaires upstream dans `~/.local/kitty.app` (le paquet apt Noble est figé en 0.32.x) |
| Docker CE | Dépôt APT officiel Docker | Moteur de containers — `docker`, `docker compose`, buildx |
| VS Code | Dépôt APT officiel Microsoft | Éditeur de code extensible avec débogueur, terminal intégré et marketplace |
| Suite Proton | Dépôt APT officiel Proton | Proton Mail (client), Proton Pass (gestionnaire de mots de passe), Proton VPN |
| Steam | Dépôt Valve (multiverse i386) | Plateforme de jeux Valve — bibliothèque, Proton pour jeux Windows |
| YubiKey Manager | PPA `ppa:yubico/stable` | Gestion des YubiKeys — FIDO2, OTP, PIV, OpenPGP |
| Bruno | Dépôt APT officiel (GPG) | Client REST/GraphQL orienté fichiers — remplace Postman, collections versionnées dans Git |
| `ubuntu-restricted-extras` | APT (debconf pré-seedé) | Codecs audio/vidéo (MP3, AAC, H.264…) et polices Microsoft (Arial, Times…) |
| `ubuntu-restricted-addons` | APT (debconf pré-seedé) | Pilotes et greffons supplémentaires non libres complémentaires à restricted-extras |
| `nautilus-open-any-terminal` | `pip install --user` | Extension Nautilus pour ouvrir Kitty via le clic droit — contourne la limitation D-Bus de gnome-terminal |
| `devinit` | `uv tool install` (local) | Générateur de projets Python complets — scaffolding pyproject.toml, Makefile, MkDocs |
| `pioinit` | `uv tool install` (local) | Générateur de projets PlatformIO embarqués — Arduino, ESP32, STM32, Raspberry Pi Pico |
| `mkdocsinit` | `uv tool install` (local) | Configuration MkDocs Material idempotente sur un projet existant — mkdocs.yml, CSS, cibles Makefile |
| `vmforge` | `bash vmforge/install.sh` | Création et gestion de VMs Alpine Linux KVM avec COW QCOW2 et cloud-init |
