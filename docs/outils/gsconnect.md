# GSConnect

[GSConnect](https://github.com/GSConnect/gnome-shell-extension-gsconnect) est
une implémentation complète de **KDE Connect** pour GNOME Shell. Il permet
d'échanger des fichiers, notifications et presse-papier avec un smartphone
Android sur le même réseau local, sans passer par le cloud.

!!! tip "Analogie pour les débutants"
    C'est l'équivalent de l'app **KDE Connect** que vous installez sur votre
    téléphone Android — GSConnect est simplement la version « côté PC »,
    intégrée directement dans GNOME Shell au lieu d'être une application à
    part.

---

## Installation

=== "Via alm_tools (recommandé)"
    ```bash
    sudo make -C ~/alm_tools/postinstall gsconnect
    ```

    Installe `gnome-shell-extension-gsconnect`, `sshfs`,
    `python3-nautilus`, et ouvre le port `1716/tcp+udp` dans ufw.
    L'activation de l'extension est finalisée automatiquement au premier
    login (framework `session-checks`) — voir
    [alm_tools — Packages et dépôts](../systeme/ubuntu/alm_tools/postinstall/packages-et-depots.md#gsconnect-module-gsconnect)
    et
    [session-checks — 20-gsconnect](../systeme/ubuntu/alm_tools/postinstall/session-checks.md#le-controle-20-gsconnect).

    Cette cible fait partie du groupe `desktop`, lui-même inclus dans
    `sudo make all` — sur un poste déjà provisionné en entier (ou via `sudo
    make desktop`), GSConnect est donc **déjà installé**. La commande
    individuelle ci-dessus n'est utile que pour une (ré)installation ciblée
    de ce seul module.

=== "Manuelle"
    ```bash
    sudo apt install gnome-shell-extension-gsconnect sshfs python3-nautilus
    gnome-extensions enable gsconnect@andyholmes.github.io
    sudo ufw allow 1716/tcp
    sudo ufw allow 1716/udp
    nautilus -q
    ```

    Une déconnexion/reconnexion GNOME est nécessaire après l'installation
    du paquet pour que GNOME Shell scanne la nouvelle extension.

---

## Appairage avec un téléphone Android

1. Installer l'application **KDE Connect** sur le téléphone (Play Store).
2. S'assurer que le téléphone est sur le **même réseau Wi-Fi** que le PC.
3. Ouvrir l'application KDE Connect — le PC apparaît dans la liste des
   appareils détectés, sous son **nom d'hôte** (ex. `coruscant`).
4. Taper sur le nom du PC → **Demande d'association**.
5. Valider des deux côtés : le PC affiche une notification de demande
   d'appairage, le téléphone affiche un code — confirmer sur les deux.

!!! warning "Le PC n'apparaît pas dans la liste"
    Voir la section [Dépannage](#depannage) ci-dessous — la cause la plus
    fréquente sur cette installation est une extension GNOME Shell
    installée mais pas réellement activée.

Autant en profiter pour cocher directement les deux cases de
synchronisation du presse-papiers (**Vers l'appareil** / **Depuis
l'appareil**) à ce moment-là, plutôt que de les découvrir en cherchant plus
tard — voir [Presse-papier partagé](#presse-papier-partage).

---

## Transférer des fichiers

### Du PC vers le téléphone

Clic droit sur un fichier dans **Nautilus** → **Envoyer vers un appareil
mobile** → sélectionner l'appareil associé. Une notification apparaît sur
le téléphone.

### Du téléphone vers le PC

Depuis l'application KDE Connect sur le téléphone : sélectionner l'appareil
(le PC), puis **Envoyer fichier**. Le fichier arrive en notification côté
GNOME.

### Monter le stockage du téléphone comme un dossier

`sshfs` (installé avec GSConnect) permet de parcourir le stockage du
téléphone directement dans Nautilus, comme un partage réseau — l'option
apparaît dans le menu de l'appareil associé une fois SSH activé côté
téléphone dans l'app KDE Connect.

---

## Presse-papier partagé

Copier sur l'un des deux appareils, coller sur l'autre — mais les deux sens
ne se comportent pas de la même façon.

**Prérequis** : dans les préférences de l'extension GSConnect sur le PC, onglet
**Partage → Synchronisation du presse-papiers**, les **deux cases** doivent
être cochées : **« Vers l'appareil »** et **« Depuis l'appareil »** — une
seule case cochée ne suffit pas, la synchro échoue silencieusement dans le
sens manquant.

### Du PC vers le téléphone

Automatique une fois les deux cases cochées : `Ctrl+C` sur le PC, puis appui
long sur un champ de saisie du téléphone → **Coller**.

### Du téléphone vers le PC

Ce sens ne se déclenche pas automatiquement de façon fiable — un geste
manuel côté Android est nécessaire :

=== "Android 14+"
    1. Copier le texte sur le téléphone.
    2. Glisser vers le bas depuis le haut de l'écran pour ouvrir les
       réglages rapides.
    3. Appuyer sur la tuile **Envoyer le presse-papiers** — si elle n'est
       pas encore présente, l'ajouter une seule fois : icône
       crayon/**Modifier** → repérer la tuile dans la liste → la glisser
       dans la zone active.
    4. Coller (`Ctrl+V`) côté PC.

=== "Android 10 à 13"
    Pas de tuile de réglages rapides sur ces versions : le déclenchement se
    fait via un bouton dans la **notification persistante** de KDE Connect
    plutôt que dans le volet de réglages rapides.

!!! info "Sur cette installation"
    Les deux sens confirmés fonctionnels — Ubuntu 24.04, GSConnect version
    57 (visible dans « À propos » de l'extension), Galaxy S26 Ultra (Android
    14+), testé le 2026-07-11 — une fois les deux cases de synchronisation
    cochées. Exemple d'application concrète (connexion Proton par code
    manuel sans webcam) : [Configuration Android — solution de
    repli](../securite/proton/configuration-android.md#solution-de-repli-webcam-indisponible).

---

## Autres usages

| Fonction | Description |
|----------|-------------|
| **Notifications partagées** | Les notifications Android (SMS, appels, WhatsApp…) s'affichent sur le PC, avec possibilité de les rejeter depuis GNOME |
| **Presse-papier partagé** | Copier sur l'un, coller sur l'autre — [voir le détail](#presse-papier-partage) (le sens téléphone → PC demande un geste manuel) |
| **Répondre aux SMS** | Lecture et envoi de SMS depuis l'app GSConnect desktop (accès aux contacts du téléphone) |
| **Trouver le téléphone** | Déclenche une sonnerie sur le téléphone depuis le PC, même en mode silencieux |
| **Contrôle du volume média** | Le téléphone sert de télécommande (lecture/pause/suivant) pour ce qui joue sur le PC |
| **Souris/clavier virtuels** | Le téléphone devient un trackpad virtuel pour le PC — glisser déplace le curseur, tap court fait un clic (gauche/droit/milieu selon la zone), appui long maintient le clic. Plugin indépendant du presse-papiers, activé séparément dans les préférences de l'appareil |
| **Exécution de commandes** | Déclencher un script/une commande sur le PC depuis le téléphone (ex. verrouiller l'écran) |
| **Verrouillage à distance** | Verrouiller l'écran du PC depuis le téléphone |

Chaque fonction se configure individuellement dans les paramètres de
l'appareil associé (icône GSConnect dans le tiroir des extensions, ou
`gnome-extensions-app`). Certaines (SMS, notifications) demandent
d'accorder des permissions supplémentaires côté Android.

!!! info "Sur cette installation"
    Le plugin *Remote Input* (souris/clavier virtuels) nécessite une
    session **X11**, ou une session **Wayland avec support Pipewire** — non
    pris en charge sous Wayland historiquement (mentionné jusqu'à Ubuntu
    20.04 sur le wiki GSConnect). Testé le 2026-07-11 sur ce poste (Ubuntu
    24.04, GSConnect 57, **session Wayland**) avec un Galaxy S26 Ultra :
    **confirmé fonctionnel** malgré la limitation historique — le curseur
    Ubuntu répond bien au glissement du doigt sur le téléphone.

---

## Dépannage

### Le PC n'apparaît pas dans la liste des appareils du téléphone

Le symptôme le plus trompeur : l'extension **semble** installée et activée,
mais ne tourne pas réellement. Vérifier dans cet ordre :

1. **Le port 1716 est-il en écoute ?** C'est le signal fiable — pas
   `gnome-extensions info`, qui interroge un service D-Bus séparé
   (`org.gnome.Shell.Extensions`, un script `gjs` autonome activé à la
   demande) et non le processus `gnome-shell` réellement en cours
   d'exécution. Il peut afficher un état générique qui ne reflète pas la
   réalité de la session live.

    ```bash
    ss -tuln | grep 1716
    ```

    Rien ne s'affiche → l'extension n'est pas réellement active, malgré ce
    que peut dire `gnome-extensions info`.

2. **Le kill-switch global des extensions est-il actif ?** Ce réglage
   désactive silencieusement *toutes* les extensions GNOME Shell, quel que
   soit le contenu de `enabled-extensions` :

    ```bash
    gsettings get org.gnome.shell disable-user-extensions
    ```

    S'il renvoie `true`, c'est la cause : `gsettings set
    org.gnome.shell disable-user-extensions false`.

3. **L'extension a-t-elle été scannée par la session en cours ?**

    ```bash
    gnome-extensions list | grep gsconnect
    ```

    Absente → une déconnexion/reconnexion GNOME est nécessaire (Wayland ne
    recharge pas les extensions à chaud).

4. **ufw bloque-t-il le port ?** Sans effet si ufw est inactif
   (`sudo ufw status`), mais à vérifier s'il est activé :

    ```bash
    sudo ufw status | grep 1716
    ```

!!! info "Sur cette installation"
    Ces trois premiers points ont été rencontrés en conditions réelles :
    l'extension était bien installée, `enabled-extensions` la listait
    correctement, mais `disable-user-extensions` était resté à `true` suite
    à une session de dépannage antérieure sans rapport — bloquant
    silencieusement l'activation. Le contrôle
    [session-checks — 20-gsconnect](../systeme/ubuntu/alm_tools/postinstall/session-checks.md#le-controle-20-gsconnect)
    corrige ce point automatiquement à chaque login.

### Nautilus n'affiche pas « Envoyer vers un appareil mobile »

```bash
nautilus -q
```

Nautilus doit redémarrer pour charger l'intégration `python3-nautilus`. Si
l'option reste absente après redémarrage, vérifier que le paquet est bien
installé (`dpkg -s python3-nautilus`).

### Le presse-papiers ne fonctionne que dans un sens

Cause la plus fréquente : une seule des deux cases **« Vers l'appareil »** /
**« Depuis l'appareil »** est cochée dans **Partage → Synchronisation du
presse-papiers** (préférences de l'appareil associé) — la synchro échoue
silencieusement dans le sens de la case manquante, sans message d'erreur.
Cocher les deux cases résout le problème dans la quasi-totalité des cas.

Si le sens téléphone → PC ne fonctionne toujours pas une fois les deux cases
cochées : ce sens ne se déclenche pas automatiquement, voir la procédure
manuelle dans [Presse-papier partagé](#presse-papier-partage).

---

## Référence rapide

| Besoin | Commande / emplacement |
|--------|------------------------|
| Installer (via alm_tools) | `sudo make -C ~/alm_tools/postinstall gsconnect` |
| Vérifier que le service tourne | `ss -tuln \| grep 1716` |
| Vérifier le kill-switch extensions | `gsettings get org.gnome.shell disable-user-extensions` |
| Activer l'extension manuellement | `gnome-extensions enable gsconnect@andyholmes.github.io` |
| Envoyer un fichier (PC → téléphone) | Clic droit → *Envoyer vers un appareil mobile* |
| Envoyer un fichier (téléphone → PC) | App KDE Connect → *Envoyer fichier* |
| Ouvrir le pare-feu | `sudo ufw allow 1716/tcp` + `sudo ufw allow 1716/udp` |
| Recharger Nautilus après install | `nautilus -q` |
