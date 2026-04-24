# Post-installation Ubuntu 24.04

---

## Cloner le dépôt

```bash
cd ~
git clone git@github.com:namnetes/alm-tools.git
```

---

## Lancer la post-installation

!!! warning "Point d'entrée unique"
    N'exécutez **jamais** `build.sh` directement. Le seul point d'entrée valide est `run_build.sh`.

```bash
cd ~/alm-tools/postinstall
sudo DEBUG=true ./run_build.sh
```

Les journaux sont écrits automatiquement dans :

```
/var/log/debug_build_ubuntu_YYYY-MM-DD_HH-MM-SS.log
```

---

## Les 20 étapes

| Étape | Module | Action |
|-------|--------|--------|
| 1 | `update_system` | `apt update` + `dist-upgrade` |
| 2 | `update_snap` | Mise à jour des snaps installés |
| 3 | `cleanup_packages` | Suppression des paquets indésirables |
| 4 | `add_ppas` | Ajout des dépôts PPA (Ansible) |
| 5 | `install_core_packages` | Installation de 150+ paquets APT |
| 6 | `install_uv` | Gestionnaire Python `uv` |
| 7 | `install_xan` | Outil de traitement CSV `xan` |
| 8 | `install_eza` | Remplacement de `ls` : `eza` |
| 9 | `install_starship` | Invite de commandes Starship |
| 10 | `install_githubcli` | CLI GitHub `gh` |
| 11 | `install_fzf` | Recherche floue `fzf` |
| 12 | `install_fonts` | FiraCode Nerd Font, Jetbrains Mono, Cascadia Code |
| 13 | `install_brave` | Navigateur Brave |
| 14 | `install_fnm` | Gestionnaire Node.js `fnm` |
| 15 | `install_node_lts` | Node.js LTS *(dépend de l'étape 14)* |
| 16 | `install_zed` | Éditeur Zed |
| 17 | `update_plocate_db` | Mise à jour de la base de données `locate` |
| 18 | `install_devinit` | Outil `devinit` *(dépend de l'étape 6)* |
| 19 | `install_vmforge` | Outil `vmforge` *(dépend de l'étape 5)* |
| 20 | `cleanup_system` | Nettoyage final du système |

---

## Dépendances critiques

Ces dépendances sont automatiquement respectées par l'orchestrateur, mais importantes à connaître si vous relancez des étapes individuellement :

| Étape dépendante | Requiert | Raison |
|-----------------|----------|--------|
| 15 `install_node_lts` | 14 `install_fnm` | fnm est le gestionnaire de Node.js |
| 18 `install_devinit` | 6 `install_uv` | devinit s'installe via `uv tool install` |
| 19 `install_vmforge` | 5 `install_core_packages` | libvirt, qemu-kvm, cloud-image-utils, acl sont nécessaires |

---

## Étapes manuelles post-installation

### Redémarrer libvirt (si KVM installé)

```bash
sudo systemctl restart libvirtd
sudo usermod -aG libvirt $USER
newgrp libvirt
```

### Déployer les dotfiles

```bash
cd ~/alm-dotfiles
stow .
source ~/.bashrc
```

### Configurer Git

```bash
git config --global user.name "Votre Nom"
git config --global user.email "votre@email.com"
```
