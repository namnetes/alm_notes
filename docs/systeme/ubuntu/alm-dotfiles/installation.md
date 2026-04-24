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
git clone git@github.com:namnetes/alm-dotfiles.git
```

---

## Étape 2 — Déployer avec Stow

```bash
cd ~/alm-dotfiles
stow .
```

??? tip "Simulation à sec"
    Prévisualisez sans créer de liens :
    ```bash
    stow --simulate .
    ```

??? tip "Supprimer tous les liens"
    Pour nettoyer un déploiement existant :
    ```bash
    stow -D .
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

Chaque entrée doit pointer vers le dépôt (`→ /home/<user>/alm-dotfiles/...`).

---

## Étape 5 — Configurer Git

`.gitconfig` est exclu de Stow. Configurez-le manuellement :

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```

Consultez le fichier `.gitconfig` du dépôt pour reproduire les alias et options recommandés.

---

## Étape 6 — Fonds d'écran (optionnel)

```bash
mkdir -p ~/.config/my_ubuntu/wallpapers
# Copiez vos images .jpg / .png / .webp dans ce dossier
~/.functions/bin/change_wallpaper.sh
```
