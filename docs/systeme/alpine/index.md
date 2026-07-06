# Alpine Linux

Alpine Linux est une distribution Linux légère et sécurisée, basée sur musl libc et BusyBox.

Ces pages couvrent l'exploitation d'Alpine dans des machines virtuelles
(créées avec [vmforge](../ubuntu/alm_tools/outils/vmforge.md)) : configuration
initiale, partage de fichiers avec l'hôte et conteneurs Docker.

## Pages

<div class="grid cards" markdown>

-   :material-rocket-launch-outline: **[Post-Installation](post-installation.md)**

    Étapes essentielles après la première connexion : sudo, paquets, hostname.

-   :material-folder-network-outline: **[Partage de répertoires](creation-dun-partage-de-repertoires.md)**

    Partage hôte ↔ VM via VirtioFS.

-   :material-docker: **[Docker sur Alpine](docker.md)**

    Installation et configuration de Docker.

-   :material-view-dashboard-variant-outline: **[Lazydocker](lazydocker.md)**

    Interface TUI pour gérer Docker.

-   :material-console-network-outline: **[Compatibilité des terminaux](compatibilite-terminal.md)**

    Résoudre les problèmes de terminal via SSH.

</div>
