# Installation

!!! info "Prérequis"
    La plupart des outils listés ci-dessous sont installés automatiquement par [alm_tools post-installation](../alm_tools/postinstall/post-installation.md). Seul `stow` et `git` sont nécessaires avant cette étape.

---

## Prérequis manuels

| Outil | Installation |
|-------|--------------|
| GNU Stow | `sudo apt install -y stow` |
| Git | `sudo apt install -y git` |
| Kitty | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cible `kitty` (binaires upstream, plus le paquet apt) |
| FZF | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cible `fzf` (binaire upstream, plus le paquet apt) |
| Starship | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cible `starship` |
| eza | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cible `eza` |
| fnm / Node.js | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cibles `fnm` puis `node` |
| uv | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cible `uv` |
| Zed | via [alm_tools](../alm_tools/postinstall/post-installation.md) — cible `zed` |

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
bash bootstrap.sh
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

!!! note "Pourquoi `bootstrap.sh` en plus de `stow` ?"
    `~/.bashrc` n'est **pas** versionné dans `alm_dots` (squelette Ubuntu,
    propre à chaque machine) — `stow` ne peut donc pas le patcher. Sans
    ce script, `.bash_env` et `.bash_functions` seraient déployés mais
    jamais sourcés : aucun outil ni fonction ne fonctionnerait, sans
    erreur visible. `bootstrap.sh` ajoute les deux blocs `source`
    manquants à `~/.bashrc`, de façon idempotente — le relancer ne
    duplique rien. Détail :
    [Étapes manuelles — prérequis
    fondamental](../alm_tools/postinstall/etapes-manuelles.md#prerequis-fondamental-sourcer-bash_envbash_functions-dans-bashrc).

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

## Étape 5 — Activer le timer fond d'écran

```bash
systemctl --user enable --now change-wallpaper.timer
```

Le fond d'écran changera automatiquement toutes les heures et au prochain démarrage de session.

---

## Étape 6 — Fonds d'écran (optionnel)

```bash
mkdir -p ~/.config/my_ubuntu/wallpapers
# Copiez vos images .jpg / .png / .webp dans ce dossier
~/.functions/bin/change_wallpaper.sh
```
