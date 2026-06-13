# alm_tools

`alm_tools` est un dépôt personnel d'outils et d'automatisation pour Ubuntu.

**Dépôt :** [github.com/namnetes/alm_tools](https://github.com/namnetes/alm_tools)

```
alm_tools/
├── postinstall/   ← configuration complète d'un poste Ubuntu (Makefile)
├── cli/           ← outils CLI : devinit, mkdocsinit, pioinit, vmforge
├── jobs/          ← scripts planifiables : runbg, backup Google Drive
├── lib/           ← bibliothèque commune (common.sh)
```

---

## postinstall

Configure un poste Ubuntu depuis un état vierge. Un seul point d'entrée :

```bash
cd ~/alm_tools/postinstall
sudo make all
```

<div class="grid cards" markdown>

-   :material-view-dashboard-outline: **[postinstall](postinstall/index.md)**

    Vue d'ensemble et démarrage rapide.

-   :material-make: **[Post-installation](postinstall/post-installation.md)**

    Makefile : groupes, cibles, scénarios.

-   :material-bug-outline: **[Déboguer](postinstall/deboguer.md)**

    Logs, exécution directe, mode DEBUG.

-   :material-tune: **[Personnaliser](postinstall/personnaliser.md)**

    Paquets, PPAs, Snaps.

-   :material-check-decagram-outline: **[Session-checks](postinstall/session-checks.md)**

    Framework de contrôles au démarrage GNOME.

-   :material-sitemap-outline: **[Architecture](postinstall/architecture.md)**

    Modules, `common.sh`, pattern `SUDO_USER`.

-   :material-package-variant: **[Packages et dépôts](postinstall/packages-et-depots.md)**

    Liste complète des paquets APT.

</div>

---

## Outils CLI et utilitaires

<div class="grid cards" markdown>

-   :material-toolbox-outline: **[Outils spécialisés](outils/index.md)**

    devinit, mkdocsinit, vmforge, runbg, backup Google Drive.

</div>
