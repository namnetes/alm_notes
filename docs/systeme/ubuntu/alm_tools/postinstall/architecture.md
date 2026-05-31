# Architecture

Cette page décrit le fonctionnement interne de `postinstall` : comment les
modules sont organisés, comment ils communiquent, et les conventions
importantes à connaître avant de modifier ou d'ajouter un module.

---

## Structure du projet

```
postinstall/
├── Makefile                        ← point d'entrée unique
├── config/
│   ├── packages_to_install.list
│   ├── packages_to_remove.list
│   ├── ppas.list
│   └── snap_packages.list
├── modules/
│   ├── system/                     ← groupe "system"
│   ├── cli/                        ← groupe "cli"
│   ├── apps/                       ← groupe "apps"
│   ├── desktop/                    ← groupe "desktop"
│   └── devtools/                   ← groupe "devtools"
└── session-checks/
    ├── run-session-checks
    ├── session-checks.desktop
    ├── 10-nautilus-terminal
    └── install.sh
```

---

## Le Makefile — macro `RUN`

Chaque cible individuelle du Makefile s'appuie sur une macro `RUN` :

```makefile
define RUN
@set -o pipefail; \
printf '\n\033[1;34m▶  %s\033[0m\n' '$@' && \
bash $(DIR)modules/$(1) 2>&1 | tee -a $(LOG) && \
printf '\033[0;32m✓  %s done\033[0m\n' '$@'
endef
```

Cette macro fait deux choses simultanément :

1. **Affiche** la sortie en temps réel dans le terminal (avec couleurs)
2. **Écrit** la même sortie dans `/var/log/postinstall_<timestamp>.log` via `tee -a`

Le nom du fichier de log est calculé une seule fois au démarrage de `make` :

```makefile
STAMP := $(shell date +%Y-%m-%d_%H-%M-%S)
LOG   := /var/log/postinstall_$(STAMP).log
```

Résultat : toutes les cibles d'une même invocation `sudo make all` écrivent
dans **le même fichier de log**.

---

## Le pattern `SUDO_USER`

Plusieurs outils (uv, fnm, node, zed, devinit, pioinit) s'installent dans
le HOME de l'utilisateur réel, pas dans celui de root.

**Pourquoi ?** Ces outils sont des gestionnaires de versions ou des outils
par utilisateur. Les installer dans `/root/.local/` les rendrait inaccessibles
au compte normal.

**Comment ?** Chaque module récupère le HOME réel via `$SUDO_USER` :

```bash
local original_user="${SUDO_USER}"
local original_user_home
original_user_home=$(getent passwd "${original_user}" | cut -d: -f6)
```

`$SUDO_USER` est une variable définie par `sudo` — elle contient le nom du
compte qui a lancé la commande `sudo`. `getent passwd` récupère le HOME
associé à ce compte depuis les bases de données du système (y compris LDAP
et NIS, pas seulement `/etc/passwd`).

!!! warning "Ne jamais lancer via `sudo su`"
    Si vous faites `sudo su` puis `make uv`, `$SUDO_USER` sera vide et le
    module ne pourra pas déterminer où installer. Toujours lancer directement :
    `sudo make uv`.

---

## Anatomie d'un module

Tous les modules suivent le même patron :

```bash
#!/usr/bin/env bash

set -euo pipefail           # mode strict : arrêt sur erreur, variable non définie,
                            # ou échec dans un pipe

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../../../lib/common.sh"   # fonctions partagées

trap handle_script_error ERR    # capture toute erreur et loggue le contexte

install_xxx() {
    # 1. Vérifier si déjà présent → idempotence
    if command -v xxx &>/dev/null; then
        log_info "[STATUT] xxx déjà installé."
        return 0
    fi

    # 2. Agir
    # ...

    # 3. Vérifier le résultat
    command -v xxx &>/dev/null \
        && log_success "xxx installé." \
        || log_error "Installation échouée."
}

# La garde BASH_SOURCE permet deux usages :
#   - exécution directe : sudo bash modules/cli/install_xxx.sh → le bloc s'exécute
#   - sourcing depuis un autre script → le bloc NE s'exécute PAS (évite les doublons)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    check_root
    install_xxx
fi
```

---

## `lib/common.sh` — fonctions partagées

Tous les modules sourcent `lib/common.sh`. Cette bibliothèque fournit :

### Fonctions de log

```bash
log_debug "message"    # visible seulement si DEBUG=true
log_info "message"     # progression normale
log_success "message"  # étape réussie
log_warning "message"  # anomalie non bloquante
log_error "message"    # échec d'opération
log_fatal "message"    # erreur critique — arrêt immédiat
```

### Gardes de sécurité

```bash
check_root             # arrête le script si pas root
lock_guard "$LOCK_FILE"  # empêche deux exécutions simultanées du même script
handle_script_error    # trap ERR — loggue le nom du script, la ligne, le code de retour
```

### Format des messages

```
[2026-05-28 14:30:05] [INFO]    [INSTALLATION] uv Python package manager.
[2026-05-28 14:30:06] [SUCCESS] [SUCCÈS] uv installé à /home/galan/.local/bin/uv.
```

---

## Cas particuliers notables

### fnm protège `~/.bashrc`

L'installeur officiel de fnm modifie automatiquement `~/.bashrc` pour y
ajouter `eval "$(fnm env)"`. Le module `install_fnm.sh` sauvegarde le
`.bashrc` avant l'installation et le restaure après — car `alm_dots` gère
déjà l'initialisation de fnm dans `.bash_env`.

### nautilus-terminal utilise session-checks

L'extension `nautilus-open-any-terminal` est installée par `install_nautilus_terminal.sh`,
mais la configuration (`gsettings set ... terminal kitty`) est **différée** au
premier démarrage de session via `session-checks/10-nautilus-terminal`.

Raison : Nautilus communique avec le terminal via D-Bus, pas via `PATH`.
La configuration `gsettings` doit être appliquée dans le contexte de la
session GNOME de l'utilisateur réel, pas pendant l'installation root.

### steam active l'architecture i386

`install_steam.sh` active `dpkg --add-architecture i386` et ajoute le
composant `multiverse` à `sources.list`. Ces opérations sont idempotentes
(vérifiées avant d'agir).

### docker ajoute l'utilisateur au groupe

`install_docker.sh` ajoute `$SUDO_USER` au groupe `docker`. Ce changement
ne prend effet qu'à la **prochaine session** (déconnexion/reconnexion requise).
