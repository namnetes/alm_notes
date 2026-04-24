# Post-Installation Ubuntu 24.04

Ce guide couvre les étapes à réaliser après une installation fraîche d'Ubuntu 24.04 : mise à jour du système, personnalisation de l'environnement, outils essentiels et configuration de Firefox.

---

## 1. Mise à jour du système

```bash
sudo apt update && sudo apt upgrade -y
```

### Ubuntu Pro (optionnel)

Ubuntu Pro est un abonnement gratuit pour usage personnel (jusqu'à 5 machines). Il donne accès à des mises à jour de sécurité étendues (ESM).

??? info "Activer Ubuntu Pro"
    1. Rendez-vous sur [ubuntu.com/pro](https://ubuntu.com/pro) et connectez-vous à votre compte Ubuntu.
    2. Dans le tableau de bord, section **Free Personal Token**, copiez la commande `pro attach <token>`.
    3. Collez-la dans votre terminal et exécutez-la.
    4. Relancez la mise à jour : `sudo apt update && sudo apt upgrade -y`

### Paquets multimédia

Ces paquets incluent des codecs audio/vidéo et des polices Microsoft non libres.

```bash
sudo apt install -y ubuntu-restricted-extras ubuntu-restricted-addons
```

!!! warning "Interface interactive"
    L'installation s'interrompt pour afficher le contrat de licence des polices Microsoft (`ttf-mscorefonts-installer`). Lisez-le et acceptez-le pour continuer.

---

## 2. Personnalisation de Gnome

Ouvrez **Paramètres** via le menu système (coin supérieur droit) ou avec `Super` + `A` puis recherchez « Paramètres ».

??? note "Énergie"
    - **Mode d'énergie** → Performance
    - **Afficher le pourcentage de batterie** → Activer

??? note "Multi-tâches"
    - **Coin actif** → Activer
    - **Bords de l'écran actifs** → Activer

??? note "Apparence"
    - **Style couleur** → Bleu

??? note "Bureau Ubuntu — Dock"
    - **Afficher le dossier personnel** → Désactiver
    - **Masquer automatiquement le dock** → Activer
    - **Mode panneau** → Désactiver
    - **Position à l'écran** → Bas
    - **Afficher les volumes** → Désactiver
    - **Afficher la corbeille** → Désactiver

---

## 3. Terminal

### Terminal par défaut

Pour définir Kitty (ou tout autre émulateur) comme terminal par défaut :

```bash
sudo update-alternatives --config x-terminal-emulator
```

Sélectionnez le numéro correspondant à Kitty dans la liste affichée.

### Police FiraCode Nerd Font

Les Nerd Fonts sont des polices enrichies avec des icônes. Elles sont nécessaires pour Starship et certains thèmes de terminal.

```bash
git clone --depth 1 https://github.com/ryanoasis/nerd-fonts.git
cd nerd-fonts/
./install.sh FiraCode
fc-cache -fv
```

Vérifiez que les icônes s'affichent correctement :

```bash
echo -e "\ue0a0 \ue0a1 \ue0a2 FiraCode Nerd Font"
```

Si des symboles apparaissent (et non des carrés), la police est installée. Activez-la dans les préférences de votre terminal.

### Starship

Starship est un prompt de terminal rapide et personnalisable. Il affiche des informations contextuelles : branche Git, répertoire courant, état du dépôt, etc.

!!! info "Prérequis"
    Une police Nerd Font doit être installée et activée dans le terminal avant de configurer Starship.

**Installation :**

```bash
curl -sS https://starship.rs/install.sh | sh
```

**Activation dans Bash** — ajoutez cette ligne à la fin de `~/.bashrc` :

```bash
eval "$(starship init bash)"
```

Rechargez votre shell : `source ~/.bashrc`

### Thème Catppuccin pour Gnome Terminal

```bash
curl -L https://raw.githubusercontent.com/catppuccin/gnome-terminal/v0.3.0/install.py | python3 -
```

Ouvrez ensuite **Gnome Terminal** → **Édition** → **Préférences**, puis activez le profil *Catppuccin Frappé* (ou un autre au choix) comme profil par défaut.

---

## 4. Gestionnaire de fichiers (Nautilus)

### Afficher le nombre d'éléments sous les dossiers

Dans Nautilus : **Édition** → **Préférences** → section **Libellés de la vue grille** → sélectionnez **Taille** pour le premier libellé.

### Créer un nouveau document via clic droit

Nautilus n'affiche le menu « Nouveau document » que si le répertoire `~/Modèles` contient des fichiers. Créez des modèles vides :

```bash
touch ~/Modèles/"Nouveau Fichier Texte.txt"
touch ~/Modèles/"Nouveau Document.odt"
```

### Extensions

```bash
sudo apt install nautilus-wipe                          # Suppression sécurisée de fichiers
sudo apt install imagemagick nautilus-image-converter   # Redimensionnement et rotation d'images
sudo apt install nautilus-admin                         # Actions avec droits administrateur via clic droit
```

Redémarrez Nautilus pour activer les extensions :

```bash
nautilus -q
```

### Ouvrir dans un terminal personnalisé

L'extension standard `nautilus-extension-gnome-terminal` ne supporte que le terminal GNOME. Pour utiliser Kitty ou un autre émulateur, installez `nautilus-open-any-terminal`.

!!! warning "Conflit avec l'extension existante"
    Si `nautilus-extension-gnome-terminal` est déjà installée, désinstallez-la d'abord, sinon elle continuera à forcer l'ouverture du terminal GNOME :
    ```bash
    sudo apt remove nautilus-extension-gnome-terminal
    ```

**Dépendances :**

```bash
sudo apt install python3-nautilus gir1.2-gtk-4.0
```

**Installation :**

=== "Pour l'utilisateur courant (recommandé)"
    ```bash
    pip install --user nautilus-open-any-terminal --break-system-packages
    ```

=== "Pour tout le système"
    ```bash
    sudo pip install nautilus-open-any-terminal --break-system-packages
    ```

**Configuration :**

```bash
sudo glib-compile-schemas /usr/share/glib-2.0/schemas
glib-compile-schemas ~/.local/share/glib-2.0/schemas/
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal 'kitty'
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal keybindings '<Ctrl><Alt>t'
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal new-tab true
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal flatpak 'system'
```

---

## 5. Firefox

Ubuntu 24.04 installe Firefox via Snap par défaut. Cette section explique comment le remplacer par un paquet DEB depuis les dépôts officiels de Mozilla, pour de meilleures performances et une intégration plus native.

??? tip "Référence officielle"
    Instructions complètes disponibles sur [mozilla.org/fr/firefox/linux](https://www.mozilla.org/fr/firefox/linux/).

### Désinstaller Firefox Snap

```bash
sudo snap disable firefox
sudo snap remove --purge firefox
```

Supprimez les fichiers résiduels :

```bash
rm -rf ~/snap/firefox/
rm -rf ~/.mozilla/firefox/
```

### Ajouter le dépôt Mozilla

```bash
sudo install -d -m 0755 /etc/apt/keyrings

wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- \
    | sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
```

Vérifiez l'empreinte de la clé (doit correspondre exactement) :

```bash
gpg -n -q --import --import-options import-show /etc/apt/keyrings/packages.mozilla.org.asc \
    | awk '/pub/{getline; gsub(/^ +| +$/,""); \
      if($0 == "35BAA0B33E9EB396F59CA838C0BA5CE6DC6315A3") \
        print "Empreinte valide : "$0; \
      else \
        print "ERREUR — empreinte invalide : "$0}'
```

Ajoutez le dépôt et donnez-lui la priorité sur les autres sources :

```bash
echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] \
    https://packages.mozilla.org/apt mozilla main" \
    | sudo tee /etc/apt/sources.list.d/mozilla.list > /dev/null

echo 'Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000' | sudo tee /etc/apt/preferences.d/mozilla
```

### Installer Firefox

```bash
sudo apt update && sudo apt install firefox firefox-l10n-fr
```

Le dictionnaire orthographique français est disponible comme extension : [Dictionnaire français par Olivier R.](https://addons.mozilla.org/fr/firefox/addon/dictionnaire-fran%C3%A7ais1/)

### uBlock Origin

uBlock Origin peut bloquer la sauvegarde automatique de certains sites (dont GitHub). Pour corriger cela, ajoutez le domaine à la liste des sites de confiance :

1. Cliquez sur l'icône uBlock Origin dans la barre d'outils.
2. Ouvrez le **Tableau de bord** → onglet **Listes blanches**.
3. Ajoutez `github.com` sur une nouvelle ligne et cliquez sur **Appliquer les changements**.

### Exporter et importer les exceptions de cookies

??? info "Scripts disponibles"
    Deux scripts sont disponibles dans le dépôt [github.com/namnetes/Scripts](https://github.com/namnetes/Scripts) :

    - `firefox_export_cookie_exceptions.sh`
    - `firefox_restore_cookie_exceptions.sh`

**Trouver le chemin du profil Firefox :**

Saisissez `about:profiles` dans la barre d'adresse. Le chemin est indiqué sur la ligne **Répertoire racine** du profil actif (mention « en cours d'utilisation »).

**Exporter les exceptions :**

```bash
firefox_export_cookie_exceptions.sh /home/galan/.mozilla/firefox/lr55u01n.default-release
```

Le script produit une liste de domaines à rediriger dans un fichier :

```
aistudio.google.com
chat.mistral.ai
copilot.microsoft.com
github.com
notebooklm.google.com
outlook.live.com
www.netflix.com
www.perplexity.ai
```

**Restaurer les exceptions :**

```bash
./firefox_restore_cookie_exceptions.sh \
    /home/galan/.mozilla/firefox/lr55u01n.default-release \
    except.txt
```

!!! warning
    Les exceptions présentes dans le profil mais **absentes du fichier** de sauvegarde seront supprimées.

---

## 6. SSH et GitHub

Référence officielle : [Connexion à GitHub avec SSH](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh).

### Générer une clé SSH

```bash
ssh-keygen -t ed25519 -C "galan.marchand@outlook.fr"
```

Ed25519 est un algorithme à courbe elliptique — plus sûr et plus compact que RSA.

### Activer ssh-agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Ajoutez ensuite la clé publique à votre compte GitHub en suivant le [guide officiel](https://docs.github.com/fr/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).

### Dépôts personnels

| Dépôt | Description |
|-------|-------------|
| [namnetes/tiddlywiki](https://github.com/namnetes/tiddlywiki) | Documentation personnelle TiddlyWiki |
| [namnetes/dotfiles](https://github.com/namnetes/dotfiles) | Fichiers de configuration |
| [namnetes/own_scripts](https://github.com/namnetes/own_scripts) | Scripts administratifs personnels |
