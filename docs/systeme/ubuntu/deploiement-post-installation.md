# Déploiement après installation fraîche

Guide complet pour configurer un poste Ubuntu 26.04 après une installation fraîche, en s'appuyant sur [alm-tools](alm-tools/index.md) et [alm-dotfiles](alm-dotfiles/index.md).

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
git clone git@github.com:namnetes/alm_tools.git
git clone git@github.com:namnetes/alm_dots.git
git clone git@github.com:namnetes/alm_notes.git
```

| Dépôt | Emplacement local | Rôle | Documentation |
|-------|-------------------|------|---------------|
| [namnetes/alm_tools](https://github.com/namnetes/alm_tools) | `~/alm_tools` | Post-installation + outils système | [alm-tools](alm-tools/index.md) |
| [namnetes/alm_dots](https://github.com/namnetes/alm_dots) | `~/alm_dots` | Fichiers de configuration (dotfiles) | [alm-dotfiles](alm-dotfiles/index.md) |
| [namnetes/alm_notes](https://github.com/namnetes/alm_notes) | `~/alm_notes` | Wiki personnel MkDocs | — |

---

## Étape 4 — Lancer la post-installation alm-tools

!!! warning "Étape la plus longue"
    Cette étape installe 150+ paquets et tous les outils de développement. Durée : 20 à 40 min selon la connexion internet.

```bash
cd ~/alm_tools/postinstall
sudo DEBUG=true ./run_build.sh
```

Journaux disponibles dans `/var/log/debug_build_ubuntu_*.log`.

Voir le détail des 22 étapes dans [alm-tools — Post-installation](alm-tools/post-installation.md).

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
cd ~/alm_dots
stow --target="$HOME" .
source ~/.bashrc
```

!!! info "`.gitconfig` déjà en place"
    Stow déploie également `~/.gitconfig` (nom, email, alias, options). Aucune configuration Git manuelle n'est nécessaire.

Voir [alm-dotfiles — Installation](alm-dotfiles/installation.md) pour la vérification des liens symboliques.

---

## Étape 7 — Installer les plugins Yazi

Les plugins Yazi ne sont pas inclus dans Stow (générés localement). À installer une seule fois :

```bash
ya pack -a yazi-rs/plugins#git
ya pack -a yazi-rs/plugins#archive
ya pack -a yazi-rs/plugins#miller
ya pack -a yazi-rs/plugins#hexyl
ya pack -a yazi-rs/plugins#nbpreview
ya pack -a yazi-rs/plugins#full-border
ya pack -a yazi-rs/plugins#smart-filter
ya pack -a yazi-rs/plugins#jump-to-char
ya pack -a yazi-rs/plugins#relative-motions
ya pack -a yazi-rs/plugins#max-preview
ya pack -a yazi-rs/plugins#hide-preview
ya pack -a yazi-rs/plugins#starship
ya pack -a yazi-rs/plugins#diff
ya pack -a yazi-rs/plugins#chmod
```

---

## Étape 8 — Activer les services systemd

Les fichiers `.service` et `.timer` sont déjà en place grâce à Stow (étape 6). Il reste à les activer :

```bash
systemctl --user daemon-reload

# Wiki personnel (http://127.0.0.1:8000/)
systemctl --user enable --now mkdocs.service

# Fond d'écran automatique (rotation horaire)
systemctl --user enable --now change-wallpaper.timer
```

Voir [alm-dotfiles — Service MkDocs](alm-dotfiles/service-mkdocs.md) pour les commandes de gestion.

---

## Étape 9 — Vérifier les polices

L'étape 12 de la post-installation installe FiraCode Nerd Font, Jetbrains Mono et Cascadia Code.

```bash
fc-list | grep -i firacode
```

---

## Étape 10 — Configurer le terminal Kitty

La configuration est déjà déployée par `alm_dots`. Pour définir Kitty comme terminal par défaut :

```bash
sudo update-alternatives --config x-terminal-emulator
```

---

## Étape 11 — Fonds d'écran (optionnel)

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
| 5 à 12 | ~15 min |
| **Total** | **~1 heure** |
