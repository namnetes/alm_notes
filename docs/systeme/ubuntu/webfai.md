# TUXEDO WebFAI — Réinstallation système

Réinstallation complète d'un TUXEDO depuis une clé USB bootable. Le processus télécharge et installe la distribution choisie sans intervention humaine une fois lancé.

---

## 1. Prérequis

!!! danger "Perte de données irréversible"
    L'installation formate **tous les disques internes** sans confirmation.
    Débranchez tout support de stockage externe (clés USB, disques, cartes SD) avant de démarrer.
    Sauvegardez vos données avant de commencer.

- Ordinateur TUXEDO — WebFAI fonctionne exclusivement sur ce matériel
- UEFI activé dans le BIOS (activé par défaut sur tous les modèles TUXEDO)
- Câble réseau LAN — le Wi-Fi n'est pas supporté pendant l'installation
- Clé USB disponible — **son contenu sera entièrement effacé**

!!! note "Pas de port Ethernet ?"
    Utilisez un adaptateur USB-Ethernet.

---

## 2. Créer la clé WebFAI

### Avec TUXEDO WebFAI Creator (recommandé)

1. Insérez la clé USB
2. Lancez **TUXEDO WebFAI Creator**
3. Cliquez sur **`+`** → sélectionnez **TUXEDO WebFAI**
4. Cliquez sur l'icône disque dur → choisissez votre clé USB
5. Cliquez sur **Flash!** et attendez la fin du processus

### En ligne de commande

Réservé aux utilisateurs avancés ou sur instruction du support TUXEDO.

```bash
# Remplacez /dev/sdX par le périphérique exact de votre clé USB
wget https://webfai.tuxedocomputers.com/webfai-current.img
sudo dd if=webfai-current.img of=/dev/sdX bs=4M status=progress && sync
```

!!! warning "Identifier le bon périphérique"
    Vérifiez avec `lsblk` avant d'exécuter `dd`. Une erreur de cible détruirait un autre disque.

---

## 3. Lancer l'installation

1. Éteignez l'ordinateur
2. Débranchez tous les supports de stockage externes
3. Branchez le câble LAN
4. Insérez la clé WebFAI
5. Allumez et accédez au **boot menu** en appuyant sur :

    | Touche | Modèles concernés |
    |---|---|
    | `F7` | La plupart des portables TUXEDO |
    | `F10` / `F11` | Certains modèles |
    | `ESC` | Selon le firmware |

    Si vous n'êtes pas sûr, essayez `F7` en premier.

6. Sélectionnez la clé USB → **Entrée**
7. Choisissez la distribution souhaitée → **Entrée**

À partir de là, **l'installation est entièrement automatique**. Ne coupez pas l'alimentation, ne débranchez pas le câble réseau.

Si l'écran s'éteint en cours de route, appuyez sur `Alt` pour le réactiver — l'installation continue en arrière-plan.

Une fois terminée, appuyez sur une touche pour redémarrer, puis suivez l'assistant de première configuration.

---

## 4. Distributions disponibles

L'offre évolue ; voici les distributions présentes au moment de la rédaction.

| Distribution | Environnement de bureau |
|---|---|
| TUXEDO OS | KDE Plasma |
| Ubuntu LTS | GNOME |
| Kubuntu | KDE Plasma |
| Xubuntu | Xfce |
| Ubuntu MATE | MATE |
| Linux Mint | Cinnamon |
| Debian | GNOME ou KDE Plasma |
| Fedora | GNOME ou KDE Plasma |
