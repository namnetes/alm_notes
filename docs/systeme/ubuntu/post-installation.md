# Configuration manuelle

Cette page couvre uniquement les étapes **manuelles** restantes après avoir
exécuté `sudo make all` depuis `~/alm_tools/postinstall`.

!!! info "Ce qu'`alm_tools/postinstall` prend en charge automatiquement"
    - Mise à jour APT + codecs et polices Microsoft (`restricted`)
    - Paramètres GNOME : dock, batterie, hot corners, accent bleu (`gnome-settings`)
    - Polices FiraCode, JetBrains Mono, Cascadia Code (`fonts`)
    - Starship prompt (`starship`)
    - Extensions Nautilus : wipe, admin, image-converter (`pkg-install`)
    - Modèles Nautilus dans `~/Modèles` (`nautilus-templates`)
    - Ouvrir Kitty depuis Nautilus (`nautilus-terminal`)
    - Suppression de Firefox Snap (`remove-firefox`)

    → Voir [alm_tools — Post-installation](alm_tools/postinstall/post-installation.md)

---

## 1. Ubuntu Pro (optionnel)

Ubuntu Pro est gratuit pour usage personnel (jusqu'à 5 machines).
Il donne accès aux mises à jour de sécurité étendues (ESM).

1. Connectez-vous sur [ubuntu.com/pro](https://ubuntu.com/pro)
2. Copiez la commande `pro attach <token>` depuis le tableau de bord
3. Exécutez-la dans le terminal
4. Relancez la mise à jour : `sudo apt update && sudo apt upgrade -y`

---

## 2. Terminal

### Kitty comme terminal par défaut

`alm_tools` installe Kitty, mais la désignation comme terminal par défaut
reste manuelle (choix interactif) :

```bash
sudo update-alternatives --config x-terminal-emulator
```

Sélectionnez le numéro correspondant à Kitty dans la liste.

### Thème Catppuccin pour GNOME Terminal

```bash
curl -L https://raw.githubusercontent.com/catppuccin/gnome-terminal/v0.3.0/install.py \
    | python3 -
```

Ouvrez ensuite **GNOME Terminal** → **Édition** → **Préférences**, puis
activez le profil *Catppuccin Frappé* comme profil par défaut.

---

## 3. Nautilus

### Afficher le nombre d'éléments sous les dossiers

Dans Nautilus : **Édition** → **Préférences** → section **Libellés de la
vue grille** → sélectionnez **Taille** pour le premier libellé.

---

## 4. Firefox

Firefox Snap est supprimé par `sudo make remove-firefox`.
Cette section couvre la configuration manuelle du navigateur.

### uBlock Origin

uBlock Origin peut bloquer la sauvegarde automatique sur certains sites
(dont GitHub). Pour corriger :

1. Icône uBlock Origin → **Tableau de bord** → onglet **Listes blanches**
2. Ajouter `github.com` sur une nouvelle ligne
3. Cliquer **Appliquer les changements**

### Exporter et importer les exceptions de cookies

??? info "Scripts disponibles"
    Deux scripts sont disponibles dans [github.com/namnetes/Scripts](https://github.com/namnetes/Scripts) :

    - `firefox_export_cookie_exceptions.sh`
    - `firefox_restore_cookie_exceptions.sh`

**Trouver le chemin du profil :** saisir `about:profiles` dans la barre
d'adresse. Le chemin est sur la ligne **Répertoire racine** du profil actif.

**Exporter :**

```bash
firefox_export_cookie_exceptions.sh /home/galan/.mozilla/firefox/lr55u01n.default-release
```

**Restaurer :**

```bash
./firefox_restore_cookie_exceptions.sh \
    /home/galan/.mozilla/firefox/lr55u01n.default-release \
    except.txt
```

!!! warning
    Les exceptions présentes dans le profil mais **absentes du fichier**
    de sauvegarde seront supprimées.

---

## 5. SSH et GitHub

Référence officielle : [Connexion à GitHub avec SSH](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh).

### Générer une clé SSH

```bash
ssh-keygen -t ed25519 -C "galan.marchand@outlook.fr"
```

### Activer ssh-agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Ajoutez ensuite la clé publique sur GitHub :
[guide officiel](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

### Dépôts personnels

| Dépôt | Description |
|-------|-------------|
| [namnetes/alm_dots](https://github.com/namnetes/alm_dots) | Dotfiles |
| [namnetes/alm_tools](https://github.com/namnetes/alm_tools) | Outils post-installation |
| [namnetes/alm_notes](https://github.com/namnetes/alm_notes) | Wiki personnel |
| [namnetes/Scripts](https://github.com/namnetes/Scripts) | Scripts utilitaires |
