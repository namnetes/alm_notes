# Packages et dépôts

---

## Dépôts PPA — `postinstall/config/ppas.list`

| PPA | Outil installé |
|-----|---------------|
| `ppa:ansible/ansible` | Ansible |

---

## Paquets APT — `postinstall/config/packages_to_install.list`

150+ paquets organisés par catégorie.

### Outils système essentiels

`build-essential`, `sudo`, `gnome-tweaks`, `curl`, `wget`, `unzip`, `tar`, `rsync`, `htop`, `btop`, `tree`, `plocate`, `acl`

### Outils CLI modernes

`bat`, `fd-find`, `ripgrep` — remplacements respectifs de `cat`, `find`, `grep`

### Développement

`git`, `gdb`, `python3-full`, `python3-pip`, `python3-venv`, `stow`, `shellcheck`, `pandoc`

### KVM / Virtualisation

`qemu-kvm`, `libvirt-daemon-system`, `libvirt-clients`, `cloud-image-utils`, `virtiofsd`, `virt-manager`

### Multimédia

`ffmpeg`, `vlc`, `shotcut`, `imagemagick`

### Documentation

`texlive`, `graphviz`, `pandoc`

---

## Paquets supprimés — `postinstall/config/packages_to_remove.list`

Les paquets indésirables présents après une installation fraîche d'Ubuntu 24.04 sont supprimés à l'étape 3. Consultez le fichier dans le dépôt pour la liste complète.

---

## Outils installés hors APT

| Outil | Méthode | Étape |
|-------|---------|-------|
| `uv` | Script officiel `astral.sh` | 6 |
| `xan` | Cargo ou binaire | 7 |
| `eza` | Binaire GitHub | 8 |
| Starship | Script officiel `starship.rs` | 9 |
| `gh` (GitHub CLI) | Dépôt officiel | 10 |
| `fzf` | Binaire GitHub | 11 |
| FiraCode, Jetbrains Mono, Cascadia Code | Script d'installation | 12 |
| Brave | Dépôt officiel | 13 |
| `fnm` | Script officiel | 14 |
| Node.js LTS | via `fnm` | 15 |
| Zed | Script officiel | 16 |
| `devinit` | `uv tool install ./devinit` | 18 |
| `vmforge` | `bash vmforge/install.sh` | 19 |
