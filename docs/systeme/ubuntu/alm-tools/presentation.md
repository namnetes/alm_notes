# Présentation

`alm-tools` automatise la mise en place d'un environnement de développement complet sur Ubuntu 24.04. Il regroupe un système de post-installation en 20 étapes et plusieurs outils complémentaires.

---

## Composants

| Composant | Emplacement | Description |
|-----------|-------------|-------------|
| Post-installation | `postinstall/` | 20 étapes séquentielles et idempotentes |
| Lanceur arrière-plan | `jobs/runbg.sh` | Lance un script en tâche de fond avec journalisation |
| Sauvegarde Google Drive | `jobs/backup_googledrive.sh` | Synchronisation et archivage déterministe |
| Sandbox Python | `python/sandbox.sh` | Environnement JupyterLab isolé |
| devinit | `devinit/` | Générateur de projets Python |
| vmforge | `vmforge/` | Automatisation de VMs KVM/Alpine Linux |

---

## Architecture en couches

```
postinstall/run_build.sh          ← seul point d'entrée (wrapper sécurisé)
    └── postinstall/build.sh      ← orchestrateur des 20 étapes
            └── modules/*.sh      ← 22 modules mono-fonction
                    └── lib/common.sh  ← librairie partagée
```

| Couche | Fichier | Rôle |
|--------|---------|------|
| 1 — Librairie | `lib/common.sh` | Logs, gestion d'erreurs, mutex (`lock_guard()`) |
| 2 — Modules | `postinstall/modules/*.sh` | Un module = un outil installé |
| 3 — Orchestrateur | `postinstall/build.sh` | Séquence les 20 étapes |
| 4 — Point d'entrée | `postinstall/run_build.sh` | Journalisation, `sudo -E`, validation |

---

## Principes de conception

| Principe | Description |
|----------|-------------|
| **Idempotence** | Chaque module vérifie l'état avant d'agir — relancer est sans danger |
| **Responsabilité unique** | Un module = une fonction = un outil installé |
| **Configuration externalisée** | Listes de paquets dans `postinstall/config/`, pas dans le code |
| **Sécurité** | `set -euo pipefail`, gestionnaires d'erreurs, verrous fichier |
| **Journalisation complète** | Logs horodatés dans `/var/log/debug_build_ubuntu_*.log` |
| **Contexte utilisateur préservé** | `sudo -E` + `$SUDO_USER` maintient les variables d'environnement |
