# Déploiement après installation fraîche

Guide complet pour configurer un poste Ubuntu 24.04 après une installation fraîche, en s'appuyant sur [alm-tools](alm-tools/index.md) et [alm-dotfiles](alm-dotfiles/index.md).

---

## Étape 1 — Mettre à jour le système

```bash
sudo apt update -y && sudo apt upgrade -y
```

---

## Étape 2 — Créer une clé SSH pour GitHub

Voir [SSH et GitHub](post-installation.md#6-ssh-et-github).

```bash
ssh-keygen -t ed25519 -C "votre@email.com"
cat ~/.ssh/id_ed25519.pub
# Ajoutez la clé dans https://github.com/settings/keys
```

---

## Étape 3 — Cloner les dépôts personnels

```bash
cd ~
git clone git@github.com:namnetes/alm-tools.git
git clone git@github.com:namnetes/alm-dotfiles.git
```

| Dépôt | Rôle | Documentation |
|-------|------|---------------|
| [namnetes/alm-tools](https://github.com/namnetes/alm-tools) | Post-installation + outils système | [alm-tools](alm-tools/index.md) |
| [namnetes/alm-dotfiles](https://github.com/namnetes/alm-dotfiles) | Fichiers de configuration | [alm-dotfiles](alm-dotfiles/index.md) |

---

## Étape 4 — Lancer la post-installation alm-tools

!!! warning "Étape la plus longue"
    Cette étape installe 150+ paquets et tous les outils de développement. Durée : 20 à 40 min selon la connexion internet.

```bash
cd ~/alm-tools/postinstall
sudo DEBUG=true ./run_build.sh
```

Journaux disponibles dans `/var/log/debug_build_ubuntu_*.log`.

Voir le détail des 20 étapes dans [alm-tools — Post-installation](alm-tools/post-installation.md).

---

## Étape 5 — Configurer libvirt (si KVM requis)

```bash
sudo systemctl restart libvirtd
sudo usermod -aG libvirt $USER
newgrp libvirt
```

---

## Étape 6 — Déployer les dotfiles

```bash
cd ~/alm-dotfiles
stow .
source ~/.bashrc
```

Voir [alm-dotfiles — Installation](alm-dotfiles/installation.md) pour la vérification et la configuration Git manuelle.

---

## Étape 7 — Configurer Git

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

---

## Étape 8 — Vérifier les polices

L'étape 12 de la post-installation installe FiraCode Nerd Font, Jetbrains Mono et Cascadia Code.

```bash
fc-list | grep -i firacode
```

---

## Étape 9 — Configurer le terminal Kitty

La configuration est déjà déployée par `alm-dotfiles`. Pour définir Kitty comme terminal par défaut :

```bash
sudo update-alternatives --config x-terminal-emulator
```

---

## Étape 10 — Fonds d'écran (optionnel)

```bash
mkdir -p ~/.config/my_ubuntu/wallpapers
# Copiez vos images ici
~/.functions/bin/change_wallpaper.sh
```

---

## Récapitulatif et durée estimée

| Étapes | Durée estimée |
|--------|--------------|
| 1 à 3 | ~5 min |
| 4 (post-installation) | 20 à 40 min |
| 5 à 10 | ~10 min |
| **Total** | **~1 heure** |
