# Outils spécialisés

---

## devinit — Générateur de projets Python

`devinit` crée la structure complète d'un projet Python aux standards du projet.

### Installation manuelle

```bash
cd ~/alm-tools/devinit
uv tool install .
```

### Utilisation

```bash
devinit mon-projet
```

Crée la structure suivante dans le répertoire courant :

```
mon-projet/
├── pyproject.toml             # uv + pytest + mypy
├── ruff.toml                  # linting/formatage (88 car., style Black)
├── .gitignore
├── .editorconfig
├── pyrightconfig.json
├── .pre-commit-config.yaml    # hooks ruff + gitlint
├── .envrc                     # direnv avec PYTHONPATH
├── Makefile                   # cibles test, lint, docs
├── src/
├── tests/
├── data/
├── docs/
└── .vscode/
    ├── settings.json
    ├── launch.json
    └── tasks.json
```

Documentation complète : [devinit/README.md](https://github.com/namnetes/alm-tools/blob/main/devinit/README.md)

---

## vmforge — Automatisation de VMs KVM/Alpine Linux

`vmforge` crée et gère des machines virtuelles légères Alpine Linux sous KVM avec `cloud-init`.

### Prérequis

Installés automatiquement à l'étape 5 : `qemu-kvm`, `libvirt-daemon-system`, `libvirt-clients`, `cloud-image-utils`, `acl`, `virtiofsd`.

### Installation manuelle

```bash
cd ~/alm-tools/vmforge
bash install.sh
```

L'installateur crée un shim dans le PATH, configure les ACL et applique les règles AppArmor.

### Commandes

```bash
vmforge create nom-vm        # Créer une nouvelle VM
vmforge list                 # Lister toutes les VMs
vmforge ssh nom-vm           # Se connecter en SSH à une VM
vmforge delete nom-vm        # Supprimer une VM
vmforge inventory            # Générer un inventaire Ansible
```

### Caractéristiques

- Disques Copy-on-Write (empreinte disque minimale)
- `cloud-init` pour la personnalisation au premier démarrage
- Injection automatique de la clé SSH
- Règles AppArmor pour la sécurité

### Documentation

| Document | Sujet |
|----------|-------|
| [vmforge/README.md](https://github.com/namnetes/alm-tools/blob/main/vmforge/README.md) | Vue d'ensemble |
| [vmforge/USAGE.md](https://github.com/namnetes/alm-tools/blob/main/vmforge/USAGE.md) | Guide d'utilisation |
| `doc/01-concepts.md` | Architecture et concepts |
| `doc/02-installation.md` | Installation détaillée |
| `doc/03-configuration.md` | Options de configuration |
| `doc/04-commands.md` | Référence des commandes |
| `doc/05-cloud-init.md` | Personnalisation cloud-init |
| `doc/06-networking.md` | Configuration réseau |
| `doc/07-ansible.md` | Intégration Ansible |
| `doc/08-zed.md` | Intégration avec l'éditeur Zed |
| `doc/09-internals.md` | Fonctionnement interne |
| `doc/10-troubleshooting.md` | Résolution de problèmes |
| `doc/11-installation-shim.md` | Installation du shim |
| `doc/12-apparmor.md` | Règles AppArmor |

---

## runbg.sh — Lanceur de tâches en arrière-plan

Lance n'importe quel script en arrière-plan avec journalisation automatique.

```bash
./jobs/runbg.sh --name mon-job /chemin/vers/script.sh
./jobs/runbg.sh --name mon-job --notify script.sh
./jobs/runbg.sh --name mon-job --env /chemin/vars.env script.sh
```

| Option | Description |
|--------|-------------|
| `--name NAME` | Nom du job (utilisé dans le fichier de log) |
| `--notify` | Envoie une notification bureau à la fin |
| `--env FILE` | Source un fichier de variables d'environnement avant l'exécution |

Les journaux sont écrits dans `~/.nohups/<nom>_YYYY-MM-DD_HH-MM-SS.out`.

---

## backup_googledrive.sh — Sauvegarde Google Drive

Synchronise Google Drive localement et crée des archives compressées déterministes avec déduplication SHA256.

!!! info "Prérequis"
    `rclone` configuré avec un accès Google Drive, `pv`, `hashdeep`.

```bash
./jobs/backup_googledrive.sh
```

### Processus

1. Synchronisation rclone → `~/backups/googledrive/`
2. Création d'une archive `tar.gz` déterministe (fichiers triés par nom, métadonnées fixées, compression sans métadonnées)
3. Calcul du hash SHA256 via `hashdeep`
4. Déduplication : skip si l'archive est identique à la dernière sauvegarde
5. Verrou fichier pour éviter les exécutions parallèles
