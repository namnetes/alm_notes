# alm_tools

`alm_tools` est un dépôt personnel d'outils et d'automatisation pour Ubuntu.

**Dépôt :** [github.com/namnetes/alm_tools](https://github.com/namnetes/alm_tools)

```
alm_tools/
├── postinstall/   ← configuration complète d'un poste Ubuntu (Makefile)
├── cli/           ← outils CLI : devinit, pioinit, vmforge
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

| Page | Contenu |
|------|---------|
| [postinstall](postinstall/index.md) | Vue d'ensemble et démarrage rapide |
| [Post-installation](postinstall/post-installation.md) | Makefile : groupes, cibles, scénarios |
| [Déboguer](postinstall/deboguer.md) | Logs, exécution directe, mode DEBUG |
| [Personnaliser](postinstall/personnaliser.md) | Paquets, PPAs, Snaps |
| [Session-checks](postinstall/session-checks.md) | Framework GNOME au démarrage |
| [Architecture](postinstall/architecture.md) | Modules, common.sh, SUDO_USER |
| [Packages et dépôts](postinstall/packages-et-depots.md) | Liste des paquets APT |

---

## Outils CLI et utilitaires

| Page | Contenu |
|------|---------|
| [Outils spécialisés](outils/index.md) | devinit, vmforge, runbg, backup Google Drive |
