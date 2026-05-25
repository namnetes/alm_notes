# Outils spécialisés

---

## devinit — Générateur de projets Python

`devinit` génère la structure complète d'un projet Python aux standards du projet.
Il supporte cinq **types de projets** via l'option `--type`.

### Types de projets

| Type | Description | Dépendances ajoutées |
|------|-------------|---------------------|
| `generic` | Projet Python générique | — |
| `cli` | Outil en ligne de commande | Typer, Rich |
| `fastapi` | API REST | FastAPI, uvicorn, pydantic-settings |
| `streamlit` | Application web | Streamlit |
| `nicegui` | Application web | NiceGUI |

### Installation

**Post-installation automatique** (étape 18) — non éditable, pour l'usage :

```bash
cd ~/alm_tools
uv tool install ./cli/devinit
```

**Mode développement** — les modifications du code source sont actives immédiatement :

```bash
cd ~/alm_tools/cli/devinit
uv tool install --editable .
```

!!! warning "Le flag `--force` utilise le cache"
    `uv tool install --force` réutilise un wheel en cache et ne reflète pas les
    dernières modifications du code source. Pour une réinstallation propre :

    ```bash
    uv tool uninstall devinit
    uv tool install --no-cache /path/to/devinit
    ```

### Désinstallation

```bash
uv tool uninstall devinit
```

Supprime le shim `~/.local/bin/devinit` et l'environnement isolé
`~/.local/share/uv/tools/devinit/`.

### Utilisation

```bash
# Créer un projet dans un sous-répertoire (workflow standard)
devinit mon-api --type fastapi

# Initialiser dans le répertoire courant (nom déduit du dossier)
mkdir mon-api && cd mon-api
devinit . --type fastapi

# Sans prompts interactifs (idéal pour scripts)
devinit mon-cli --type cli --yes --no-venv

# Lister les options
devinit --help
```

### Options principales

| Option | Description |
|--------|-------------|
| `--type TYPE` | `generic`, `cli`, `fastapi`, `streamlit`, `nicegui` (défaut : `generic`) |
| `--description TEXT` | Description courte du projet |
| `--python VERSION` | Version Python cible (défaut : `3.12`) |
| `--no-notebooks` | Ne pas créer `notebooks/` |
| `--no-scripts` | Ne pas créer `scripts/` |
| `--no-pre-commit` | Pas de hooks pre-commit |
| `--no-pyright` | Pas de `pyrightconfig.json` |
| `--no-venv` | Ne pas créer le virtualenv (CI, tests) |
| `--yes` / `-y` | Accepter tous les défauts sans prompts |

### Structure générée

La **base commune** est générée pour tous les types. Les types web
(`fastapi`, `streamlit`, `nicegui`) ajoutent les fichiers Docker.

```
mon-projet/
├── pyproject.toml             # runtime + dev (MkDocs toujours inclus)
├── ruff.toml                  # linting/formatage 88 car.
├── .gitignore / .editorconfig / .gitlint
├── pyrightconfig.json
├── .pre-commit-config.yaml    # ruff + gitlint
├── .envrc                     # direnv + PYTHONPATH
├── .env.example
├── Makefile                   # install, test, lint, docs, run*, docker-*
├── mkdocs.yml                 # documentation MkDocs (toujours présent)
├── src/mon_projet/
│   └── main.py                # adapté au type choisi
├── tests/
├── data/
├── docs/
│   └── stylesheets/extra.css
├── .vscode/                   # settings, launch.json (debug adapté), tasks.json
└── .zed/                      # settings.json + tasks.json (toutes les cibles)
```

**Fichiers supplémentaires par type :**

| Type | Ajouts |
|------|--------|
| `cli` | `src/*/cli.py`, `docs/cli.md` |
| `fastapi` | `src/*/routers/`, `src/*/models/`, `src/*/config.py`, `Dockerfile`, `docker-compose.yml`, `docs/endpoints.md` |
| `streamlit` | `src/*/app.py`, `src/*/pages/`, `Dockerfile`, `docker-compose.yml`, `docs/guide.md` |
| `nicegui` | `src/*/components/`, `Dockerfile`, `docker-compose.yml`, `docs/guide.md` |

### Cibles Makefile notables

```bash
make help          # liste toutes les cibles disponibles
make run           # lancer l'app (generic, cli, streamlit, nicegui)
make run-dev       # FastAPI : uvicorn avec hot-reload
make run-prod      # FastAPI : mode production
make docker-build  # construire l'image Docker
make docker-up     # démarrer les conteneurs (prompt si déjà actifs)
make docker-down   # arrêter les conteneurs
make docker-clean  # supprimer conteneurs, volumes et images locales
make docs          # serveur MkDocs en local
```

Documentation complète : [devinit/README.md](https://github.com/namnetes/alm_tools/blob/main/cli/devinit/README.md)

---

## vmforge — Automatisation de VMs KVM/Alpine Linux

`vmforge` crée et gère des machines virtuelles légères Alpine Linux sous KVM avec `cloud-init`.

### Prérequis

Installés automatiquement à l'étape 5 : `qemu-kvm`, `libvirt-daemon-system`, `libvirt-clients`, `cloud-image-utils`, `acl`, `virtiofsd`.

### Installation

L'installateur supporte trois modes :

```bash
cd ~/alm_tools/cli/vmforge

# Mode utilisateur (défaut) — shim dans ~/.local/bin, pas de sudo
bash install.sh

# Mode système — shim dans /usr/local/bin, requiert sudo
sudo bash install.sh system

# AppArmor seul — reconfigurer la règle libvirt-qemu (requiert sudo)
sudo bash install.sh apparmor
```

L'installateur :

1. Crée un **shim** dans le répertoire cible (lien vers `bin/vmforge`)
2. Configure les **ACL** (`setfacl`) pour que `libvirt-qemu` accède aux images
3. Ajoute la **règle AppArmor** dans `/etc/apparmor.d/local/abstractions/libvirt-qemu`

### Désinstallation

```bash
cd ~/alm_tools/cli/vmforge

# Désinstallation utilisateur (shim dans ~/.local/bin)
bash uninstall.sh

# Désinstallation système (shim dans /usr/local/bin)
sudo bash uninstall.sh system
```

!!! info "Données non supprimées"
    La désinstallation ne supprime que le shim. Les VMs et l'image de base
    restent intactes. Pour tout supprimer :

    ```bash
    rm -rf ~/.local/share/vmforge
    rm -f  ~/alm_tools/cli/vmforge/lib/images/alpine-base.qcow2
    ```

### Commandes

```bash
vmforge create nom-vm        # Créer une nouvelle VM
vmforge list                 # Lister toutes les VMs
vmforge ssh nom-vm           # Se connecter en SSH à une VM
vmforge delete nom-vm        # Supprimer une VM
vmforge inventory            # Générer un inventaire Ansible
vmforge help                 # Aide complète
```

### Caractéristiques

- Disques Copy-on-Write (empreinte disque minimale)
- `cloud-init` pour la personnalisation au premier démarrage
- Injection automatique de la clé SSH
- Règles AppArmor pour la sécurité

### Documentation

| Document | Sujet |
|----------|-------|
| [vmforge/README.md](https://github.com/namnetes/alm_tools/blob/main/cli/vmforge/README.md) | Vue d'ensemble |
| [vmforge/USAGE.md](https://github.com/namnetes/alm_tools/blob/main/cli/vmforge/USAGE.md) | Guide d'utilisation |
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
