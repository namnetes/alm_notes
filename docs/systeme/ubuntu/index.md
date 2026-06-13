# Ubuntu

Notes de référence pour la mise en place et la maintenance d'un poste de
travail Ubuntu : réinstallation système, configuration post-installation et
les deux projets personnels qui automatisent l'ensemble (`alm_dots` pour les
fichiers de configuration, `alm_tools` pour le post-install).

## Mise en place du système

<div class="grid cards" markdown>

-   :material-usb-flash-drive: **[Réinstallation WebFAI](webfai.md)**

    Réinstaller un TUXEDO de zéro depuis une clé USB bootable.

-   :material-cog-outline: **[Configuration manuelle](post-installation.md)**

    Étapes manuelles restantes après `sudo make all` : Ubuntu Pro, SSH,
    Firefox, terminal.

-   :material-rocket-launch-outline: **[Déploiement après installation fraîche](deploiement-post-installation.md)**

    Guide complet de l'ordre de mise en place sur un système neuf.

</div>

## Projets personnels

<div class="grid cards" markdown>

-   :material-folder-cog-outline: **[alm_dots](alm_dots/index.md)**

    Gestion des fichiers de configuration (*dotfiles*) via GNU Stow.

-   :material-toolbox-outline: **[alm_tools](alm_tools/index.md)**

    Automatisation de la post-installation Ubuntu.

</div>
