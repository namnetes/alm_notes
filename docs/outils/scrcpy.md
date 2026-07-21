# scrcpy

[scrcpy](https://github.com/Genymobile/scrcpy) (contraction de *screen copy*,
projet open source de Genymobile) affiche l'écran d'un smartphone Android
**dans une fenêtre sur le PC**, et permet de le contrôler avec la souris et
le clavier du PC — chaque clic devient un tap, chaque glisser devient un
geste tactile.

!!! tip "Analogie pour les débutants"
    C'est l'inverse de [GSConnect](gsconnect.md) : GSConnect permet
    d'utiliser le **téléphone** comme télécommande du **PC**. scrcpy fait
    l'inverse — il permet de piloter l'**écran du téléphone** depuis le
    **PC**, comme si on avait le téléphone posé dans une fenêtre, en beaucoup
    plus précis qu'avec un doigt.

Aucune installation côté téléphone n'est nécessaire (pas d'application à
poser sur le Play Store) — tout passe par le **débogage USB**, une fonction
native d'Android destinée aux développeurs, mais utilisable par n'importe
qui.

---

## Installation (Ubuntu)

=== "Via snap (recommandé)"
    ```bash
    sudo apt install adb
    sudo snap install scrcpy
    ```

    `adb` n'existe pas en tant que snap séparé — il reste installé via apt.
    Seul `scrcpy` a besoin du snap : le paquet apt d'Ubuntu 24.04 (`universe`)
    est figé en version **1.25** (2021) — trop ancien pour dialoguer avec
    les versions récentes d'Android (voir [Dépannage](#depannage)). Le snap
    suit les sorties upstream et est nettement plus à jour (3.3.x au moment
    de la rédaction).

    !!! note "Connexions content snap"
        Le snap `scrcpy` déclare plusieurs interfaces de type *content*
        (bibliothèques GPU/thème partagées entre snaps confinés) qui ne se
        connectent pas toujours automatiquement à l'installation. Si
        `scrcpy` refuse de démarrer avec une erreur du type `Content snap
        command-chain for .../gpu-2404/... not found`, voir
        [Dépannage](#depannage).

=== "Via apt (déconseillé)"
    ```bash
    sudo apt install scrcpy adb
    ```

    Fonctionne uniquement avec d'anciennes versions d'Android — la version
    packagée pour Ubuntu 24.04 plante sur Android 15/16 avec des erreurs
    `NoSuchMethodException` (API internes Android disparues entre-temps).
    À réserver aux appareils Android plus anciens, ou à défaut de pouvoir
    installer un snap.

`adb` (*Android Debug Bridge*) est l'outil qui établit la connexion avec le
téléphone — `scrcpy` s'appuie dessus.

---

## Prérequis : activer le débogage USB sur le téléphone

Cette manipulation ne se fait qu'**une seule fois**.

1. Ouvrir **Paramètres** → **À propos du téléphone**.
2. Chercher **Numéro de build** (ou *Numéro de version*) et taper dessus
   **7 fois de suite** — un message confirme que le mode développeur est
   activé.
3. Revenir à l'écran **Paramètres**, un nouveau menu **Options pour les
   développeurs** est maintenant visible (souvent sous *Système* ou
   *Paramètres avancés*).
4. Dans ce menu, activer **Débogage USB**.

!!! note "Ce menu ne « déverrouille » rien de dangereux"
    Les *Options pour les développeurs* donnent accès à des réglages
    avancés, mais les activer ne modifie rien tant qu'on ne change pas les
    options une par une. Le débogage USB seul ne permet que la connexion
    avec un ordinateur — il peut être redésactivé à tout moment une fois
    l'utilisation terminée.

!!! warning "Samsung : désactiver Auto Blocker au préalable"
    Sur les Galaxy récents (One UI 6+), la fonction de sécurité **Auto
    Blocker** grise le menu développeur et bloque toute commande USB
    (y compris ADB) tant qu'elle est active. **Paramètres** → **Sécurité et
    confidentialité** → **Auto Blocker** → désactiver, effectuer les étapes
    ci-dessus, puis réactiver Auto Blocker après usage si souhaité. Sans
    cette étape, `adb devices` renvoie une liste vide alors même que
    `lsusb` détecte bien le téléphone côté Linux.

---

## Première connexion

1. Brancher le téléphone au PC avec un câble USB (données, pas seulement
   charge).
2. Une popup apparaît sur le téléphone : **« Autoriser le débogage USB ? »**
   — cocher éventuellement *Toujours autoriser depuis cet ordinateur*, puis
   valider.
3. Dans un terminal :

    ```bash
    scrcpy
    ```

4. La fenêtre s'ouvre avec l'écran du téléphone affiché en direct.

!!! warning "Rien ne se passe, ou erreur « device unauthorized »"
    Voir la section [Dépannage](#depannage) plus bas.

---

## Exercice pas à pas : réorganiser ses applications avec la souris

Mise en pratique directe du problème de départ : trier les icônes du
téléphone en catégories, sans les manipuler au doigt.

1. Lancer `scrcpy` (voir ci-dessus) et attendre que la fenêtre affiche
   l'écran d'accueil du téléphone.
2. **Repérer deux applications** à regrouper (par exemple deux jeux, ou deux
   applications bancaires).
3. Dans la fenêtre scrcpy, **cliquer et maintenir** sur la première icône
   avec la souris, comme si le doigt restait posé dessus.
4. **Glisser** (sans relâcher le clic) l'icône jusqu'à ce qu'elle recouvre
   la seconde icône, puis **relâcher** : un dossier se crée automatiquement,
   contenant les deux applications — exactement le geste tactile habituel,
   mais avec un pointeur plus précis qu'un doigt.
5. Le dossier s'ouvre : **cliquer sur son nom** (généralement en haut de
   l'aperçu) pour le renommer, puis taper le nouveau nom **au clavier du
   PC** — bien plus rapide qu'un clavier tactile.
6. Cliquer en dehors du dossier pour valider et revenir à l'écran d'accueil.
7. **Répéter** l'opération pour glisser d'autres icônes dans ce dossier, ou
   en créer d'autres, jusqu'à obtenir l'organisation voulue.
8. Une fois terminé, fermer simplement la fenêtre scrcpy (ou `Ctrl+C` dans
   le terminal) — aucune sauvegarde particulière n'est nécessaire, tout est
   déjà appliqué directement sur le téléphone au fur et à mesure des gestes.

!!! tip "Glisser une icône vers un autre écran d'accueil"
    Glisser l'icône jusqu'au **bord de la fenêtre** (gauche ou droite) et
    patienter une seconde sans relâcher : le téléphone bascule sur l'écran
    d'accueil suivant, comme au doigt.

---

## Autres usages

| Fonction | Description |
|---|---|
| **Enregistrement d'écran** | `scrcpy --record fichier.mp4` enregistre la session dans un fichier vidéo |
| **Glisser-déposer un fichier** | Glisser un fichier depuis le PC dans la fenêtre scrcpy pour l'envoyer sur le téléphone (dossier *Download*) |
| **Glisser-déposer un APK** | Glisser un fichier `.apk` dans la fenêtre pour l'installer directement |
| **Presse-papiers partagé** | `Ctrl+C` / `Ctrl+V` fonctionnent entre le PC et le téléphone dans la fenêtre scrcpy |
| **Sans fil (Wi-Fi)** | Après un premier branchement USB : `scrcpy --tcpip` pour continuer sans câble, tant que les deux appareils sont sur le même réseau |
| **Garder l'écran du téléphone éteint** | `scrcpy --turn-screen-off` économise la batterie du téléphone tout en gardant le contrôle actif depuis le PC |

### Raccourcis clavier utiles

| Raccourci | Effet |
|---|---|
| `Ctrl+H` | Bouton **Accueil** |
| `Ctrl+B` (ou clic droit) | Bouton **Retour** |
| `Ctrl+S` | Bouton **Applications récentes** |
| `Ctrl+P` | Bouton **Power** (verrouille l'écran) |
| `Ctrl+R` | Fait pivoter l'affichage |
| `Ctrl+F` | Basculer en plein écran |

### Mode OTG — clavier/souris du PC en périphérique USB direct

Le **mode OTG** (*On-The-Go*) fait passer le clavier et la souris du PC
pour de **vrais périphériques USB branchés sur le téléphone**, au niveau le
plus bas possible — sans passer par ADB ni par l'affichage mirroré. Utile
en particulier quand l'écran tactile du téléphone est cassé ou
inaccessible : on peut toujours déverrouiller l'appareil et taper au
clavier physique du PC.

Activation unique de l'interface snap nécessaire :

```bash
sudo snap connect scrcpy:raw-usb
```

!!! example "Exercice : taper du texte sur le téléphone sans le toucher"
    1. Sur le téléphone, ouvrir une application avec un champ de texte
       (par exemple **Notes** ou l'application **Messages**) et taper une
       fois dessus pour faire apparaître le clavier virtuel.
    2. Sur le PC, lancer :

        ```bash
        scrcpy --otg
        ```

    3. Aucune fenêtre de mirroring ne s'ouvre — c'est normal, le mode OTG
       ne transmet que le clavier et la souris, pas la vidéo.
    4. Taper une phrase au clavier du PC : le texte apparaît sur l'écran
       du téléphone, en le regardant directement, comme si un clavier
       physique venait d'être branché dessus.
    5. `Ctrl+C` dans le terminal pour arrêter le mode OTG.

### Mode manette — jouer avec un contrôleur physique

Le **mode manette** transmet une manette de jeu branchée sur le PC vers le
téléphone, comme si elle était directement connectée dessus — pratique
pour les jeux Android qui supportent les manettes, ou les émulateurs.

Activation unique de l'interface snap nécessaire :

```bash
sudo snap connect scrcpy:joystick
```

!!! example "Exercice : vérifier qu'une manette est bien transmise"
    1. Brancher une manette de jeu (filaire ou son dongle Bluetooth) sur le
       **PC**.
    2. Lancer scrcpy avec le support manette activé :

        ```bash
        scrcpy --gamepad=uhid
        ```

    3. La fenêtre de mirroring s'ouvre normalement (contrairement au mode
       OTG, l'affichage reste actif ici).
    4. Ouvrir un jeu ou une application qui détecte les manettes (beaucoup
       de jeux d'action/course affichent une icône ou une notification
       « Manette connectée »).
    5. Appuyer sur les boutons de la manette **côté PC** : l'action doit se
       refléter dans le jeu affiché dans la fenêtre scrcpy, comme si la
       manette était branchée directement sur le téléphone.

    Même sans jeu compatible sous la main, le simple fait qu'Android
    affiche une manette comme connectée (notification système, ou dans
    **Paramètres → Appareils connectés**) suffit à confirmer que le mode
    fonctionne.

---

## Dépannage

### « device unauthorized » ou fenêtre qui reste noire

Le téléphone n'a pas encore validé la popup d'autorisation. Débrancher puis
rebrancher le câble, et surveiller l'écran du téléphone pour accepter la
demande **« Autoriser le débogage USB ? »**.

### Rien ne se passe, commande introuvable

Vérifier que les paquets sont bien installés :

```bash
dpkg -s adb            # adb (toujours via apt)
snap list scrcpy       # scrcpy (via snap, voir Installation)
```

### `adb devices` vide alors que le téléphone est bien branché

```bash
adb devices -l
lsusb                  # le téléphone apparaît-il au niveau USB ?
```

- Si `lsusb` **ne voit pas** le téléphone : essayer un **autre câble USB**
  — certains câbles ne transmettent que la charge, pas les données.
- Si `lsusb` **voit** le téléphone (souvent en mode *MTP*) mais `adb
  devices` reste vide : le débogage USB n'est probablement pas activé côté
  téléphone — voir [Prérequis](#prerequis-activer-le-debogage-usb-sur-le-telephone),
  et sur Samsung en particulier vérifier qu'**Auto Blocker** est bien
  désactivé (cause la plus fréquente sur les Galaxy récents).
- Si le débogage USB est bien activé et que ça ne fonctionne toujours pas :
  redébrancher/rebrancher le câble — l'activation en cours de session n'est
  pas toujours prise en compte à chaud.

### Erreur `NoSuchMethodException` / `AssertionError` au lancement

```text
[server] ERROR: Could not invoke method
java.lang.NoSuchMethodException: android.content.IClipboard$Stub$Proxy...
```

Le paquet **apt** de scrcpy (figé en version 1.25) utilise des méthodes
internes Android qui n'existent plus sur les versions récentes d'Android
(observé avec Android 16). Passer à l'installation **snap**, voir
[Installation](#installation-ubuntu).

### `Content snap command-chain for .../gpu-2404/... not found`

Le snap `scrcpy` a besoin de trois snaps de contenu (bibliothèques
GPU/thème partagées, sans risque pour le reste du système — voir
[Installation](#installation-ubuntu)) :

```bash
sudo snap install mesa-2404
sudo snap install gnome-46-2404
sudo snap install gtk-common-themes
sudo snap connect scrcpy:gpu-2404 mesa-2404:gpu-2404
sudo snap connect scrcpy:gnome-46-2404 gnome-46-2404:gnome-46-2404
sudo snap connect scrcpy:gtk-3-themes gtk-common-themes:gtk-3-themes
sudo snap connect scrcpy:icon-themes gtk-common-themes:icon-themes
sudo snap connect scrcpy:sound-themes gtk-common-themes:sound-themes
```

Si les 3 snaps sont déjà installés (message « déjà installé, voir snap
help refresh »), il ne manque en général que les 5 commandes `snap
connect` — vérifier avec `snap connections scrcpy` : la colonne *Prise*
doit être renseignée pour chaque ligne `content[...]`.

### Une fenêtre « Notice » s'affiche au premier lancement au lieu de l'écran du téléphone

Message ponctuel d'un mainteneur du snap (changement de packaging), sans
rapport avec un dysfonctionnement. Cliquer dans la fenêtre puis appuyer sur
**Entrée** pour valider — la vraie fenêtre scrcpy s'ouvre juste après. Pour
ne plus la revoir :

```bash
echo 'export SNAP_LAUNCHER_NOTICE_ENABLED=false' >> ~/.bashrc
```

!!! info "Sur cette installation"
    Chaîne de blocages rencontrée dans l'ordre sur ce poste — Ubuntu 24.04,
    TUXEDO InfinityBook Pro 14 Gen10 AMD, Galaxy S26 Ultra (Android 16),
    testé le 2026-07-21 :

    1. `adb devices` vide malgré `lsusb` détectant le téléphone → **Auto
       Blocker** activé sur le Galaxy S26 Ultra, bloquant le débogage USB.
    2. Une fois débloqué, `scrcpy` (apt, 1.25) plantait avec
       `NoSuchMethodException` / `AssertionError` → Android 16 trop récent
       pour cette version, migration vers le **snap**.
    3. Le snap refusait de démarrer (`Content snap command-chain ... not
       found`) → connexions `content` manquantes (`gpu-2404`,
       `gnome-46-2404`, `gtk-3-themes`, `icon-themes`, `sound-themes`),
       résolu en installant les 3 snaps fournisseurs et en les connectant.
    4. Une fenêtre *Notice* du nouveau mainteneur du snap s'affichait au
       lancement, à valider une fois (`Entrée`).

    Après ces quatre étapes : fonctionnel, miroir d'écran confirmé.

---

## Référence rapide

| Besoin | Commande |
|---|---|
| Installer (snap, recommandé) | `sudo apt install adb` puis `sudo snap install scrcpy` |
| Lancer scrcpy | `scrcpy` |
| Vérifier que le téléphone est détecté | `adb devices -l` |
| Vérifier les connexions content du snap | `snap connections scrcpy` |
| Enregistrer la session en vidéo | `scrcpy --record fichier.mp4` |
| Passer en sans-fil après un premier branchement | `scrcpy --tcpip` |
| Éteindre l'écran du téléphone pendant le contrôle | `scrcpy --turn-screen-off` |
| Désactiver la notice snap au démarrage | `export SNAP_LAUNCHER_NOTICE_ENABLED=false` |
