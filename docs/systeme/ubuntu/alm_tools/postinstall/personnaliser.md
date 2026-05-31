# Personnaliser

Le dossier `config/` contient quatre fichiers texte qui contrôlent ce
qu'installe le groupe `system`. Modifier ces fichiers suffit — aucun
script n'est à toucher.

```
postinstall/config/
├── packages_to_install.list   ← paquets APT à installer
├── packages_to_remove.list    ← paquets APT à supprimer
├── ppas.list                  ← dépôts PPA à ajouter
└── snap_packages.list         ← paquets Snap à installer
```

---

## Format commun

Tous les fichiers suivent les mêmes règles :

- Un élément par ligne
- Les lignes vides sont ignorées
- Les lignes commençant par `#` sont des commentaires — ignorées

```
# Ceci est un commentaire
mon-paquet      # commentaire en fin de ligne (ignoré aussi)
```

---

## `packages_to_install.list` — Paquets APT

Ajouter un paquet APT à installer lors de `sudo make pkg-install` :

```
# Mon outil personnalisé
htop
ncdu
```

Pour vérifier qu'un paquet existe avant de l'ajouter :

```bash
apt-cache show <paquet>
```

Pour appliquer les changements :

```bash
sudo make pkg-install
```

!!! note "Paquets avec interaction manuelle"
    Certains paquets comme `ubuntu-restricted-extras` affichent une licence
    via une interface interactive pendant l'installation. Ils ne peuvent pas
    être ajoutés tels quels dans la liste. Une préconfiguration de `debconf`
    est nécessaire pour accepter automatiquement la licence avant l'installation.

---

## `packages_to_remove.list` — Paquets à supprimer

Lister les paquets indésirables sur un poste vierge Ubuntu. Exemple :
`screen` est retiré par défaut car remplacé par `tmux`.

```
screen
# thunderbird
```

Pour appliquer :

```bash
sudo make pkg-remove
```

---

## `ppas.list` — Dépôts PPA

Format : `ppa:auteur/nom`.

```
ppa:ansible/ansible
```

!!! warning "Vérifier la compatibilité avec votre version d'Ubuntu"
    Un PPA conçu pour Ubuntu 24.04 ne fonctionnera pas forcément sur 26.04.
    Vérifier avant d'activer :

    ```bash
    # Remplacer "resolute" par le nom de code de votre Ubuntu
    # (lsb_release -cs pour le connaître)
    curl -s https://launchpad.net/~ansible/+archive/ubuntu/ansible \
      | grep -i "$(lsb_release -cs)"
    ```

    Si le nom de code n'apparaît pas, le PPA ne supporte pas votre version.

Pour appliquer :

```bash
sudo make ppas
```

---

## `snap_packages.list` — Paquets Snap

Un paquet par ligne. Les options Snap (`--classic`, `--channel`) suivent
le nom sur la même ligne.

```
yazi --classic
kolourpaint
onlyoffice-desktopeditors
```

!!! info "Pourquoi `--classic` pour Yazi ?"
    Le mode `--classic` désactive le sandboxing Snap. Yazi en a besoin
    pour accéder librement au système de fichiers. Sans ce flag, le
    gestionnaire de fichiers serait sévèrement limité.

Pour appliquer :

```bash
sudo make snap-update
```

---

## Ajouter un nouveau module (usage avancé)

Pour ajouter l'installation d'un outil qui n'est pas couvert par les
fichiers de config (logiciel avec dépôt propriétaire, binaire GitHub,
installeur custom), créer un module dans le groupe approprié.

Structure minimale d'un module :

```bash
#!/usr/bin/env bash
# install_mon_outil.sh — installe Mon Outil depuis <source>

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../../../lib/common.sh"

trap handle_script_error ERR

install_mon_outil() {
    log_info "[INSTALLATION] Mon Outil."

    # 1. Vérifier si déjà installé (idempotence)
    if command -v mon-outil &>/dev/null; then
        log_info "[STATUT] mon-outil déjà installé."
        return 0
    fi

    # 2. Installer
    # ...

    # 3. Vérifier
    command -v mon-outil &>/dev/null \
        && log_success "mon-outil installé." \
        || log_error "Installation échouée."
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_root
    install_mon_outil
fi
```

Ensuite, ajouter la cible dans le Makefile et l'inclure dans le groupe
souhaité. Voir [Architecture](architecture.md) pour la structure complète.
