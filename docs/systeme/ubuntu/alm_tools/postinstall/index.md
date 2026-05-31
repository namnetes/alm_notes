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

| Page | Contenu |
|------|---------|
| [Post-installation](post-installation.md) | Makefile : groupes, cibles, scénarios, idempotence |
| [Déboguer](deboguer.md) | Logs, exécution directe d'un module, mode DEBUG |
| [Personnaliser](personnaliser.md) | Ajouter des paquets, PPAs, Snaps via les fichiers de config |
| [Session-checks](session-checks.md) | Framework de contrôles automatiques au démarrage GNOME |
| [Architecture](architecture.md) | Modules, common.sh, pattern SUDO_USER |
| [Packages et dépôts](packages-et-depots.md) | Liste complète des paquets APT installés |
