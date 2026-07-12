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

Plusieurs outils (uv, fnm, node, zed, kitty, devinit, pioinit, open-sites)
s'installent dans le HOME de l'utilisateur réel, pas dans celui de root.

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

!!! warning "La garde n'a pas empêché un doublon réel (juillet 2026)"
    Malgré cette protection, un audit a trouvé `fnm` initialisé **deux
    fois** sur un poste en usage : une fois par `.bash_env` (complet,
    avec `--use-on-cd`), une fois par un bloc `eval "$(fnm env)"` présent
    dans `.bashrc` — probablement laissé par une installation antérieure
    à cette sauvegarde/restauration, ou par une réinstallation manuelle
    qui l'a contournée. Impact réel : ~92 dossiers orphelins accumulés
    dans `/run/user/<uid>/fnm_multishells/` (un par `fnm env` exécuté),
    sans casser le hook `cd` puisque le second appel ne le redéfinit pas.
    Le même défaut existait pour **starship** (`install_starship.sh`
    injecte aussi un `eval "$(starship init ...)"` dans `.bashrc` pour
    tous les comptes du système, sans savoir que `.bash_env` le fait déjà).
    Correction : bloc dupliqué retiré manuellement de `.bashrc` dans les
    deux cas — `.bash_env` reste la seule source d'initialisation.

    Correctif définitif appliqué depuis pour starship : `install_starship.sh`
    vérifie désormais aussi `~/.bash_env` avant d'écrire dans `.bashrc` — s'il
    y trouve déjà `starship init`, il n'ajoute rien. Voir
    [Starship — bug d'initialisation double](../../../../outils/cli/starship.md)
    pour l'historique complet (le premier correctif manuel avait régressé
    avant ce correctif au niveau du script lui-même).

    Troisième doublon trouvé, bénin celui-là : `~/.local/bin/env`
    (créé par l'installeur officiel `uv`) était sourcé à la fois par
    `.bashrc` et par la section `uv` de `.bash_env`. Contrairement à
    `fnm`, ce fichier est idempotent par construction (il vérifie déjà
    si `~/.local/bin` est dans le `PATH` avant de l'ajouter) — sourcer
    deux fois ne coûte rien et ne casse rien. Retiré quand même de
    `.bashrc` par cohérence avec les deux autres corrections — `.bash_env`
    reste la seule source, comme pour fnm et starship.

    Voir [fnm](../../../../outils/cli/fnm.md),
    [starship](../../../../outils/cli/starship.md) et la
    [vérification des mises à jour upstream](post-installation.md#verification-des-mises-a-jour-upstream).

### bruno embarque son propre auto-updater (conflit avec APT)

`install_bruno.sh` installe Bruno via le dépôt APT officiel
(`debian.usebruno.com`) — un canal qui suit normalement `apt upgrade`
sans problème, contrairement à `fzf`/`fnm`/`starship`. Mais l'application
elle-même embarque un auto-updater Electron (`electron-updater`)
**totalement indépendant** de ce dépôt : `/opt/Bruno/resources/app-update.yml`
pointe vers les releases GitHub (`usebruno/bruno`), pas vers le paquet APT
installé.

!!! danger "Un vrai gaspillage trouvé en audit (juillet 2026)"
    L'auto-updater interne, actif par défaut
    (`~/.config/bruno/preferences.json` → `autoupdate.downloadUpdates: true`),
    avait déjà téléchargé un `.deb` complet de **96 Mo** dans
    `~/.cache/bruno-updater/pending/`, avec `isAdminRightsRequired: false`
    dans son propre manifeste — une hypothèse fausse, puisque le binaire
    vit dans `/usr/bin`, propriété de root. Le fichier restait bloqué là
    indéfiniment, inutilisable sans droits admin que l'app ne demande
    jamais.

    Correction appliquée : `downloadUpdates` passé à `false` dans les
    préférences, cache de 96 Mo supprimé. APT reste la seule source de
    mise à jour pour Bruno — cohérent avec le fait que
    [`check_updates.sh`](post-installation.md#verification-des-mises-a-jour-upstream)
    ne couvre pas les outils apt-managés, censés se mettre à jour seuls
    via `apt upgrade`.

    `install_bruno.sh` pré-remplit désormais `preferences.json` avec
    `downloadUpdates: false` avant le premier lancement (sans écraser un
    fichier déjà présent) — une réinstallation complète du poste ne
    reproduit plus ce gaspillage.

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

### Audit d'intégration complet (2026-07-12) — méthodologie et 5 bugs trouvés

Premier test réel de `sudo make all` de bout en bout, jamais fait
jusque-là malgré la richesse de cette documentation : VM
[isoforge](../outils/isoforge.md) dédiée (Ubuntu Desktop fraîche, pas un
poste déjà provisionné), snapshot juste après le clone du dépôt (avant
tout postinstall), cycle complet rejoué **deux fois** depuis ce même
snapshot pour confirmer que chaque point d'arrêt trouvé était bien
reproductible et non un artefact ponctuel de la VM. Validation finale :
un troisième cycle, sur VM authentiquement neuve, sans aucune
intervention hormis les deux prérequis documentés (`make`, CLI `claude`)
— `EXIT_CODE:0` de bout en bout, les 5 bugs ci-dessous confirmés corrigés
simultanément.

5 bugs mécaniques trouvés et corrigés ce jour-là (un sixième,
`proton-mail`/`proton-pass` absents du dépôt APT ProtonVPN, a nécessité
une réécriture complète plutôt qu'un correctif ponctuel — détaillé à
part ci-dessous). Un septième point, un comportement de `pass-cli` après
reboot VM, reste documenté comme hors périmètre de ce dépôt dans
`postinstall/BACKLOG.md` (binaire tiers, pas un défaut de ce code).

#### claude-terminal introuvable sous `sudo` même correctement installé

**Symptôme exact** : `install_claude_terminal.sh` vérifiait `command -v
claude`. Sous `sudo`, `PATH` est réinitialisé par `secure_path`
(`/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin`)
— `~/.local/bin`, où l'installeur officiel
(`curl -fsSL https://claude.ai/install.sh | bash`) place le binaire,
n'y figure jamais. La CLI pouvait donc être installée et parfaitement
fonctionnelle pour l'utilisateur réel sans jamais être détectée par ce
module, qui échouait en fatal (voir l'encadré en tête de
[Post-installation](post-installation.md) — l'échec de l'étape 18 arrête
tout le pipeline, `apps`/`desktop`/`devtools` ne s'exécutent jamais).

**Correctif appliqué** : résolution directe du chemin
`${original_user_home}/.local/bin/claude` (même pattern que `zed_bin`/
`pass_cli_bin` dans les modules voisins), sans dépendre du `PATH` de root.
Validé en conditions réelles : `sudo make all` passe cette étape sans
aucun contournement (pas de symlink `/usr/local/bin/claude`), sur une VM
où `claude` venait d'être installé normalement pour l'utilisateur.

#### `install_zed.sh` exécutait `zed --version` en root sur la branche "installation fraîche"

**Symptôme exact** : la branche "déjà installé" de `install_zed.sh`
exécute correctement `zed --version` via `sudo -u "${original_user}"`,
avec un commentaire explicite ("Zed (GUI app) exits non-zero when invoked
as root"). Mais la branche "installation fraîche", juste après le
téléchargement, appelait `"${zed_bin}" --version` **directement en
root** — exactement le cas que le commentaire de la première branche
prévenait. Résultat : `make all` échouait systématiquement sur la toute
première installation de Zed sur une machine neuve, alors que le binaire
était en réalité installé correctement (seule la vérification échouait).

**Correctif appliqué** : même wrapper `sudo -u "${original_user}" HOME=
"${original_user_home}"` appliqué aux deux branches.

#### proton : fichier sources dupliqué (`.list` vs `.sources`)

**Symptôme exact** : le module vérifiait
`/etc/apt/sources.list.d/protonvpn-stable.list` avant de (re)créer le
fichier sources APT du dépôt ProtonVPN. Mais le postinst du paquet
`protonvpn-stable-release` écrit en réalité un fichier au format deb822,
`protonvpn-stable.sources` — jamais reconnu par ce check. Le module
recréait donc un `.list` dupliquant le `.sources` à **chaque** run,
produisant des warnings `apt-get update` ("configured multiple times")
dès la deuxième exécution.

**Correctif appliqué** : vérification des deux formats de fichier avant
d'en écrire un.

#### `fonts` — course `fc-cache` / `fc-list` systématique

**Symptôme exact** : `install_fonts.sh` appelle `fc-cache -fv` puis
vérifie immédiatement `fc-list | grep -qi "${font_name}"`. Sur un
répertoire de polices fraîchement créé (première installation de la
famille dans `/usr/local/share/fonts/<Famille>/`), `fc-cache` réussit
mais le cache que lit `fc-list` juste après ne reflète pas encore le
résultat — reproduit **6 fois sur 6** en conditions réelles (FiraCode
Nerd Font, JetBrains Mono, Cascadia Code, sur deux cycles de test
complets), alors que les fichiers `.ttf` étaient bel et bien copiés et
que `fc-list` les retrouvait correctement dès l'appel suivant.

**Correctif appliqué** : vérification directe de l'existence du fichier
sentinelle déjà copié (`sample_file`), au lieu de dépendre de `fc-list`
immédiatement après `fc-cache` — preuve immédiate et indépendante du
délai de rafraîchissement du cache fontconfig.

#### proton : `proton-mail`/`proton-pass` n'ont jamais été distribués via le dépôt APT ProtonVPN

**Symptôme exact** : `install_proton.sh` installait les trois paquets
(`proton-mail`, `proton-pass`, `proton-vpn-gnome-desktop`) via
`apt-get install` depuis `repo.protonvpn.com/debian`. Vérifié en direct
contre l'index APT réel : ce dépôt n'a jamais distribué que des paquets
liés à **ProtonVPN** — `apt-get install -y proton-mail proton-pass`
échouait systématiquement (`E: Unable to locate package`), quel que soit
l'état du reste du module.

Un second bug, purement mécanique celui-là, masquait le premier : le
`grep -A5 'Package: protonvpn-stable-release' ...` utilisé pour extraire
le champ `Filename:` de l'index ne trouvait jamais rien (l'index actuel a
11 lignes entre `Package:` et `Filename:`, contre 5 supposées à
l'écriture du script). Corriger uniquement ce `grep` n'aurait rien
débloqué : même un index correctement parsé ne contient pas
`proton-mail`/`proton-pass`.

**Correctif appliqué** : réécriture du module — ProtonVPN reste installé
via le dépôt APT (`grep -A5` remplacé par un parseur `awk` par stanza,
robuste au nombre de champs). Proton Mail et Proton Pass sont désormais
installés depuis leur `.deb` versionné officiel, téléchargé et vérifié
contre le SHA512 publié dans le manifeste `version.json` de Proton
(`proton.me/mail/download`, `proton.me/pass/download/linux`) — méthode
que Proton documente lui-même
(`sudo apt install ./ProtonMail-desktop-beta.deb`), pas un mécanisme
inventé pour l'occasion. Sélection explicite de la release
`"CategoryName": "Stable"` (jamais par position dans le JSON — l'ordre
Beta/EarlyAccess n'est pas garanti). Vérification **fail-closed** : un
`.deb` dont le hash ne correspond pas est supprimé immédiatement, jamais
laissé sur disque pour qu'un run ultérieur l'accepte silencieusement.

!!! bug "Bug additionnel trouvé en testant le correctif : mauvaise version ProtonVPN sélectionnée"
    Le nouveau parseur `awk` du dépôt ProtonVPN, testé une première fois,
    prenait la **première** stanza `Package: protonvpn-stable-release`
    trouvée dans l'index — la plus **ancienne** version listée
    (`1.0.3-2`), dont la clé GPG ne correspond plus à la signature
    actuelle du dépôt (`NO_PUBKEY`, `apt-get update` en échec). Corrigé
    en triant explicitement toutes les stanzas par version (`sort -V`)
    pour ne garder que la plus récente, plutôt que de supposer un ordre
    quelconque dans le fichier. Trouvé uniquement parce que le correctif a
    été testé sur VM fraîche plutôt que revu sur le seul code — l'index
    réel liste les versions dans un ordre qui n'a rien d'évident à la
    lecture.

Détail complet des 6 bugs (avec preuve, ligne de code, et le septième
point hors périmètre) : `postinstall/BACKLOG.md` dans le dépôt — vidé au
fur et à mesure des corrections, son historique git conserve chaque
entrée résolue.

---

## Bugs connus, non corrigés

Contrairement à la section précédente (des accrocs déjà résolus), ce qui
suit n'a **pas** été corrigé — recensé ici pour ne pas être redécouvert à
chaque audit.

### `install_gnome_settings.sh` peut écrire dans un répertoire inexistant

**Symptôme exact** : `_install_session_check()` (dans
`modules/desktop/install_gnome_settings.sh`) écrit le contrôle différé via
`cat > "${check_script}" << HEREDOC`, où `${check_script}` vaut
`/usr/local/lib/session-checks/20-gnome-settings` — sans jamais faire
`mkdir -p` sur ce répertoire au préalable. Or ce répertoire n'est créé que
par `install_session_checks.sh` (cible `session-checks`, **dernière** du
groupe `desktop`), alors que `gnome-settings` est la **première** cible du
même groupe. Si le répertoire n'existe pas encore et qu'aucune session
D-Bus utilisateur n'est active à ce moment (branche qui déclenche
`_install_session_check`), la redirection échoue ; sous `set -euo
pipefail` + `trap handle_script_error ERR`, le module s'arrête en erreur
fatale au lieu de simplement différer le réglage.

**Deux scénarios réels de déclenchement** (pas seulement théoriques) :

1. **Debug module par module**, workflow documenté par le projet lui-même
   ([Déboguer](deboguer.md)) : `sudo bash
   modules/desktop/install_gnome_settings.sh` ou `sudo make
   gnome-settings` lancé isolément, avant que `session-checks` ait jamais
   tourné sur cette machine.
2. **Provisionnement via SSH** (ou toute session non graphique) avant la
   toute première connexion GNOME — `/run/user/<uid>/bus` n'existe pas
   encore.

**Ne se déclenche pas** dans le chemin documenté comme normal : `sudo make
all` lancé depuis un terminal déjà ouvert dans une session GNOME active
(le bus D-Bus existe, la branche `_apply_gsettings` directe est prise, le
`cat >` fautif n'est jamais atteint).

**Correctif trivial identifié** : ajouter `mkdir -p "$(dirname
"${check_script}")"` juste avant le `cat >` dans `_install_session_check()`.

**Statut** : non corrigé, à corriger. Risque faible en usage courant
(chemin documenté épargné), mais touche un chemin de debug que le projet
recommande lui-même.
