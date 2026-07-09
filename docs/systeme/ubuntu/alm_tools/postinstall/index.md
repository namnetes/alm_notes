# postinstall

`postinstall` est le sous-projet de `alm_tools` qui automatise la configuration
complète d'un poste Ubuntu depuis un état vierge.

**Répertoire :** `~/alm_tools/postinstall`

---

## Démarrage rapide

```bash
cd ~/alm_tools/postinstall
sudo make all
```

---

## Pages

<div class="grid cards" markdown>

-   :material-make: **[Post-installation](post-installation.md)**

    Les 42 étapes dans l'ordre exact, idempotence et points de rupture.

-   :material-hand-back-right-outline: **[Étapes manuelles](etapes-manuelles.md)**

    Ce qui n'est jamais scripté, et ce qui est différé puis auto-résolu.

-   :material-bug-outline: **[Déboguer](deboguer.md)**

    Logs, exécution directe d'un module, mode DEBUG.

-   :material-tune: **[Personnaliser](personnaliser.md)**

    Ajouter des paquets, PPAs, Snaps via les fichiers de config.

-   :material-check-decagram-outline: **[Session-checks](session-checks.md)**

    Framework de contrôles automatiques au démarrage GNOME.

-   :material-sitemap-outline: **[Architecture](architecture.md)**

    Modules, `common.sh`, pattern `SUDO_USER`.

-   :material-package-variant: **[Packages et dépôts](packages-et-depots.md)**

    Liste complète des paquets APT installés.

</div>
