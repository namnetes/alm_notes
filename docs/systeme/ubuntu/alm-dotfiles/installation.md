# Installation

!!! info "Prérequis"
    La plupart des outils listés ci-dessous sont installés automatiquement par [alm-tools post-installation](../alm-tools/post-installation.md). Seul `stow` et `git` sont nécessaires avant cette étape.

---

## Prérequis manuels

| Outil | Commande |
|-------|----------|
| GNU Stow | `sudo apt install -y stow` |
| Git | `sudo apt install -y git` |
| Kitty | `sudo apt install -y kitty` |
| FZF | `sudo apt install -y fzf` |
| ripgrep | `sudo apt install -y ripgrep` |
| bat | `sudo apt install -y bat` |
| zoxide | `sudo apt install -y zoxide` |
| Starship | via [alm-tools](../alm-tools/post-installation.md) — étape 9 |
| eza | via [alm-tools](../alm-tools/post-installation.md) — étape 8 |
| fnm / Node.js | via [alm-tools](../alm-tools/post-installation.md) — étapes 14-15 |
| uv | via [alm-tools](../alm-tools/post-installation.md) — étape 6 |
| Zed | via [alm-tools](../alm-tools/post-installation.md) — étape 16 |

---

## Étape 1 — Cloner le dépôt

```bash
cd ~
git clone git@github.com:namnetes/alm_dots.git
```

---

## Étape 2 — Déployer avec Stow

```bash
cd ~/alm_dots
stow --target="$HOME" .
```

??? tip "Simulation à sec"
    Prévisualisez sans créer de liens :
    ```bash
    stow --target="$HOME" --simulate .
    ```

??? tip "Supprimer tous les liens"
    Pour nettoyer un déploiement existant :
    ```bash
    stow --target="$HOME" -D .
    ```

---

## Étape 3 — Activer l'environnement

```bash
source ~/.bashrc
```

Ou fermez et rouvrez le terminal.

---

## Étape 4 — Vérifier les liens symboliques

```bash
ls -la ~/.bash_env ~/.bash_aliases ~/.bash_functions
ls -la ~/.config/starship.toml ~/.config/kitty ~/.config/zed
ls -la ~/.functions/bin ~/.functions/tools
```

Chaque entrée doit pointer vers le dépôt (`→ /home/<user>/alm_dots/...`).

---

## Étape 5 — Installer les plugins Yazi

Les plugins Yazi ne sont pas stowés (générés localement). À installer une seule fois :

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

## Étape 6 — Activer le timer fond d'écran

```bash
systemctl --user enable --now change-wallpaper.timer
```

Le fond d'écran changera automatiquement toutes les heures et au prochain démarrage de session.

---

## Étape 7 — Fonds d'écran (optionnel)

```bash
mkdir -p ~/.config/my_ubuntu/wallpapers
# Copiez vos images .jpg / .png / .webp dans ce dossier
~/.functions/bin/change_wallpaper.sh
```
