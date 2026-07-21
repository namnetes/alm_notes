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

```bash
sudo apt install scrcpy adb
```

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

---

## Dépannage

### « device unauthorized » ou fenêtre qui reste noire

Le téléphone n'a pas encore validé la popup d'autorisation. Débrancher puis
rebrancher le câble, et surveiller l'écran du téléphone pour accepter la
demande **« Autoriser le débogage USB ? »**.

### Rien ne se passe, commande introuvable

Vérifier que les deux paquets sont bien installés :

```bash
dpkg -s scrcpy adb
```

### Le téléphone n'apparaît dans aucune liste (`adb devices` vide)

```bash
adb devices
```

Si la liste est vide :

- Essayer un **autre câble USB** — certains câbles ne transmettent que la
  charge, pas les données.
- Vérifier que le mode de connexion USB du téléphone est bien réglé sur
  **Transfert de fichiers** (et non *Charge uniquement*) dans la
  notification USB qui apparaît lors du branchement.
- Redébrancher/rebrancher après avoir activé le débogage USB si
  l'activation a eu lieu pendant que le câble était déjà branché.

---

## Référence rapide

| Besoin | Commande |
|---|---|
| Installer | `sudo apt install scrcpy adb` |
| Lancer scrcpy | `scrcpy` |
| Vérifier que le téléphone est détecté | `adb devices` |
| Enregistrer la session en vidéo | `scrcpy --record fichier.mp4` |
| Passer en sans-fil après un premier branchement | `scrcpy --tcpip` |
| Éteindre l'écran du téléphone pendant le contrôle | `scrcpy --turn-screen-off` |
