# Post-installation

Cette page décrit, dans l'ordre exact où `sudo make all` les exécute, les
42 étapes qui transforment une Ubuntu 24.04 LTS fraîche en poste
entièrement configuré. Objectif : pouvoir suivre — ou relancer — ce
processus « les yeux fermés », sans jamais être surpris par une dépendance
manquante.

!!! danger "À faire AVANT de lancer `sudo make all` : installer la CLI Claude Code"
    Le dernier module du groupe `cli` (étape 10, `claude-terminal`) **exige**
    que la commande `claude` soit déjà présente — il ne l'installe pas
    lui-même, il ne fait que vérifier l'environnement. S'il ne la trouve
    pas, il retourne une erreur fatale via `handle_script_error`.

    Comme chaque cible du Makefile est un **prérequis** de son groupe
    (`cli: check-root uv xan eza starship fzf fnm node rclone pass-cli
    claude-terminal`), un échec à ce stade arrête `make` immédiatement —
    **les groupes `apps`, `desktop` et `devtools` ne s'exécutent jamais**,
    même via `sudo make all`. Ce n'est pas une étape optionnelle qui échoue
    proprement en warning : c'est un arrêt complet du pipeline.

    **Installer avant toute chose :**

    ```bash
    curl -fsSL https://claude.ai/install.sh | bash
    claude    # puis /login pour l'abonnement Pro/Max
    ```

    Si vous ne voulez pas de Claude Code du tout, sautez la cible en lançant
    les cibles individuellement plutôt que le groupe :
    `sudo make uv xan eza starship fzf fnm node rclone pass-cli`, puis directement
    `sudo make apps desktop devtools`.

!!! note "Autres prérequis avant de commencer"
    - `alm_tools` cloné dans `~/alm_tools` et lancé **depuis**
      `~/alm_tools/postinstall` (chemins relatifs dans le Makefile).
    - `alm_dots` déjà déployé via `stow .` — pas strictement bloquant pour
      le postinstall lui-même, mais `claude-terminal` (étape 10) et
      `nautilus-terminal` (étape 32) ne trouveront pas certains fichiers
      sinon (`claude-switch`, le kitten `claude_ask.sh`) et se contentent
      d'un avertissement. Voir
      [Déploiement après installation fraîche](../../deploiement-post-installation.md)
      pour l'ordre complet recommandé (stow avant postinstall).
    - **Lancer `sudo make all` depuis un terminal ouvert dans une session
      GNOME graphique déjà active** (le cas normal après une install
      Ubuntu Desktop). Voir l'avertissement D-Bus de l'étape 30
      (`gnome-settings`) ci-dessous — certains réglages en dépendent, et
      un cas limite de ce module peut même faire échouer l'étape si aucune
      session live n'est détectée.

---

## Mécanisme d'idempotence commun

Chaque module vérifie l'état du système **avant** d'agir, selon l'un des
mécanismes suivants — décrits ici une seule fois, référencés ensuite par
mot-clé dans les tableaux ci-dessous plutôt que ré-expliqués à chaque
étape :

| Mot-clé | Mécanisme | Exemples |
|---------|-----------|----------|
| **`dpkg -s`** | Paquet APT déjà installé (`dpkg -s <paquet> &>/dev/null`) | `pkg-install`, `pkg-remove`, `restricted`, `steam`, `proton`, `gsconnect` |
| **`command -v` / chemin** | Binaire déjà résolu dans le `PATH`, ou exécutable présent à un chemin connu (`~/.local/bin/…`, `~/.local/kitty.app/…`) | `uv`, `xan`, `eza`, `fzf`, `brave`, `vscode`, `yubikey`, `zed`, `kitty`, `fnm`, `starship`, `devinit`, `pioinit`, `mkdocsinit`, `vmforge`, `open-sites`, `pass-cli`, `check-updates` |
| **`snap list`** | Paquet Snap déjà présent (`snap list \| grep`) | `snap-update`, `snap-apps` |
| **Fichier(s) cible** | Existence du ou des fichiers que le module doit produire | `nautilus-templates` (2 fichiers), `nautilus-terminal` (extension à 2 emplacements possibles) |
| **Sentinelle** | Fichier témoin dédié, utilisé quand il n'existe pas de commande simple pour lire l'état déjà appliqué | `gnome-settings` (`~/.config/alm_tools/gnome_settings_applied`), `fonts` (fichier échantillon + `fc-list` + `fc-match`, triple vérification) |
| **Toujours rejoué** | Pas de saut anticipé — la commande est idempotente par nature (rejouer ne duplique rien) | `apt-update`, `cleanup`, `plocate`, `session-checks` (recopie les fichiers, sans effet si identiques) |
| **Version amont** | Compare la version installée à la dernière publiée ; se **réinstalle** si en retard (le seul module « idempotent par mise à jour », pas par saut) | `rclone` |

---

## Groupe `system` (étapes 1 à 8)

| # | Cible | Action | Idempotence |
|---|-------|--------|-------------|
| 1 | `apt-update` | `apt-get update && apt-get dist-upgrade -y` | Toujours rejoué |
| 2 | `snap-update` | `snap refresh` + installe les snaps de `snap_packages.list` | `snap list` |
| 3 | `ppas` | Ajoute les PPAs de `ppas.list` | `grep` sur les sources APT existantes (repo déjà présent) |
| 4 | `pkg-remove` (`cleanup_packages.sh`) | Purge les paquets de `packages_to_remove.list` | `dpkg -s` |
| 5 | `pkg-install` | Installe les paquets de `packages_to_install.list` | `dpkg -s` |
| 6 | `restricted` | `ubuntu-restricted-extras` + `-addons`, licence pré-acceptée via `debconf-set-selections` | `dpkg -s` (les deux paquets) |
| 7 | `cleanup` | `autoremove --purge`, `clean`, `autoclean`, réduction rétention Snap, purge `/tmp` > 7j, vacuum journal | Toujours rejoué |
| 8 | `plocate` | `updatedb` | Toujours rejoué (`command -v plocate` en garde d'existence, pas de saut) |

!!! note "Pourquoi `system` doit précéder `cli` sans que ce soit déclaré dans le Makefile"
    `install_uv.sh` (étape 9) vérifie `python3` et le module `venv`, et
    échoue avec une erreur fatale s'ils sont absents — or `python3-full` et
    `python3-venv` viennent de `packages_to_install.list` (étape 5). Cette
    dépendance n'est **pas** déclarée explicitement dans le Makefile
    (contrairement à `node: fnm` ou `devinit: uv`) : elle n'est garantie que
    parce que `sudo make all` enchaîne `system` avant `cli`. Lancer
    `sudo make cli` seul sur une machine où `system` n'a jamais tourné peut
    échouer dès `uv`.

---

## Groupe `cli` (étapes 9 à 18)

| # | Cible | Action | Idempotence |
|---|-------|--------|-------------|
| 9 | `uv` | Installe `uv` via le script officiel `astral.sh`, dans `~/.local/bin` | Chemin (`~/.local/bin/uv` existe) |
| 10 | `xan` | Télécharge le dernier binaire GitHub (`medialab/xan`) vers `/usr/local/bin` | `command -v` (chemin exact `/usr/local/bin/xan`) |
| 11 | `eza` | Ajoute le dépôt APT `gierens.de`, installe via APT | `command -v` |
| 12 | `starship` | Script officiel `starship.rs` vers `/usr/local/bin`, puis ajoute `eval "$(starship init ...)"` dans le `.bashrc`/`.zshrc` de chaque compte ≥ UID 1000 | `command -v` (chemin exact) pour le binaire ; `grep` sur `starship init` par fichier rc pour l'injection |
| 13 | `fzf` | Télécharge le dernier binaire GitHub (`junegunn/fzf`) vers `/usr/local/bin` | `command -v` |
| 14 | `fnm` | Script officiel `fnm.vercel.app`, sauvegarde/restaure `.bashrc` autour de l'installation | Chemin (`~/.local/bin/fnm` exécutable) |
| 15 | `node` | Installe et active la LTS Node.js via `fnm` | Toujours rejoué (les commandes `fnm install/default/use` sont elles-mêmes idempotentes) |
| 16 | `rclone` | Script officiel `rclone.org` vers `/usr/bin/rclone` | **Version amont** — se réinstalle si la version installée diffère de la dernière publiée |
| 17 | `pass-cli` | Script officiel `proton.me` vers `~/.local/bin/pass-cli` ; si déjà présent, délègue à `pass-cli update --yes` (auto-update natif) | Chemin (`~/.local/bin/pass-cli` exécutable), puis délégation à `pass-cli update --yes` — idempotent en interne (« Already up to date » si à jour) |
| 18 | `claude-terminal` | Vérifie (ne les installe pas) : CLI `claude`, identifiants OAuth, `claude-switch`, permissions de `api.env`, kitten `claude_ask.sh`, crée `~/.claude/commands/` | Contrôles multiples, voir le détail ci-dessous |

!!! note "Prérequis explicite : `fnm` avant `install_node.sh`"
    Déclaré dans le Makefile (`node: check-root fnm`). `install_node.sh`
    vérifie directement l'exécutable `~/.local/bin/fnm` et échoue en fatal
    s'il est absent — utile seulement si vous lancez `sudo make node`
    isolément sans être passé par `sudo make cli` ou `all`.

!!! danger "Étape 18 : trois vérifications, une seule vraiment bloquante"
    `install_claude_terminal.sh` ne fait qu'auditer l'état, sans jamais
    installer quoi que ce soit lui-même :

    - **CLI `claude` absente** → erreur fatale, arrêt du pipeline (voir
      l'encadré tout en haut de cette page).
    - **Pas d'identifiants OAuth** (`~/.claude/.credentials.json`) →
      avertissement seulement ; l'utilisateur devra lancer `claude` puis
      `/login` pour s'authentifier — non bloquant pour le reste du
      provisioning.
    - **`claude-switch` ou le kitten `claude_ask.sh` absents** →
      avertissement seulement ; ces fichiers viennent du déploiement
      `stow .` d'`alm_dots`, pas de ce module.

---

## Groupe `apps` (étapes 19 à 29)

| # | Cible | Action | Idempotence |
|---|-------|--------|-------------|
| 19 | `remove-firefox` (`remove_firefox.sh`) | Purge le paquet APT `firefox`/`firefox-esr`, épingle `Pin-Priority: -1`, supprime le Snap + résidus utilisateur/système | `dpkg -s` par paquet, `snap list`, existence de fichier par résidu |
| 20 | `brave` | Dépôt APT officiel Brave | `command -v` |
| 21 | `zed` | Script officiel `zed.dev`, installé dans `~/.local/bin` pour l'utilisateur réel | Chemin (`~/.local/bin/zed` exécutable) |
| 22 | `kitty` | Installeur upstream `sw.kovidgoyal.net` vers `~/.local/kitty.app`, symlinks dans `~/.local/bin`, `.desktop` locaux qui masquent ceux d'apt | Chemin (`~/.local/kitty.app/bin/kitty` exécutable) |
| 23 | `bruno` | Dépôt APT officiel, puis pré-remplit `preferences.json` (`downloadUpdates: false`) pour désactiver l'auto-updater Electron interne avant le premier lancement | `command -v` pour le paquet ; existence de `preferences.json` pour ne pas écraser une config utilisateur |
| 24 | `docker` | Dépôt APT officiel Docker CE, ajoute l'utilisateur réel au groupe `docker` | `command -v docker` pour le paquet ; `groups \| grep -qw docker` pour l'appartenance au groupe |
| 25 | `vscode` | Dépôt APT officiel Microsoft | `command -v` |
| 26 | `proton` | VPN via dépôt `protonvpn-stable-release` ; Mail et Pass via `.deb` officiel signé (SHA512), **hors dépôt APT** — jamais distribués via `repo.protonvpn.com` (voir [Architecture](architecture.md#audit-dintegration-complet-2026-07-12-methodologie-et-5-bugs-trouves)) | `dpkg -s` (les 3 paquets, tout-ou-rien) ; vérifications séparées pour le dépôt VPN (paquet + fichier sources) et pour chaque `.deb` (SHA512 fail-closed) |
| 27 | `steam` | Active i386 + `multiverse` si nécessaire, installe `steam` | `dpkg -s steam` OU `steam:i386` ; vérifications séparées pour l'architecture et le composant |
| 28 | `yubikey` | PPA `yubico/stable`, installe `yubikey-manager` | `command -v ykman` ; `find` sur les sources APT pour le PPA |
| 29 | `snap-apps` (`install_snap_apps.sh`) | `kolourpaint`, `onlyoffice-desktopeditors` | `snap list` |

!!! warning "Docker : le groupe n'est actif qu'à la prochaine session"
    `usermod -aG docker` s'applique immédiatement en base, mais le jeton de
    groupe du shell courant ne se rafraîchit qu'à la reconnexion (ou
    `newgrp docker`). Non bloquant pour la suite du provisioning.

---

## Groupe `desktop` (étapes 30 à 35)

| # | Cible | Action | Idempotence |
|---|-------|--------|-------------|
| 30 | `gnome-settings` | Réglages `gsettings` (interface, dock) + profil d'énergie `performance` | **Sentinelle** (`~/.config/alm_tools/gnome_settings_applied`) |
| 31 | `fonts` | FiraCode Nerd Font, JetBrains Mono, Cascadia Code vers `/usr/local/share/fonts` | **Sentinelle** + `fc-list` + `fc-match` (triple vérification par police) |
| 32 | `nautilus-terminal` | Installe l'extension `nautilus-open-any-terminal` (pip, `--user --break-system-packages`) pour l'utilisateur réel | Fichier(s) cible (extension présente à l'un des deux emplacements possibles) |
| 33 | `nautilus-templates` | Crée deux fichiers vides dans `~/Modèles` (texte, ODT) | Fichier(s) cible (les deux fichiers) |
| 34 | `gsconnect` | `apt install gnome-shell-extension-gsconnect sshfs python3-nautilus` + règles ufw `1716/tcp+udp` | `dpkg -s` par paquet |
| 35 | `session-checks` | Installe `run-session-checks`, les contrôles statiques (`10-nautilus-terminal`, `20-gsconnect`), le déclencheur GNOME `/etc/xdg/autostart/session-checks.desktop` | Toujours rejoué (recopie de fichiers, sans effet si identiques) |

!!! warning "Étapes 30, 32 et 34 : nécessitent une session D-Bus active — différées via session-checks"
    `gsettings`, l'activation GSConnect et la configuration Nautilus→kitty
    ont besoin d'un bus D-Bus **utilisateur** live. Pendant le
    provisionnement (root, éventuellement sans session graphique
    utilisateur ouverte), ce n'est pas garanti. Chaque module gère ça
    différemment :

    - **Étape 30 (`gnome-settings`)** — teste directement
      `/run/user/<uid>/bus` : si le socket existe (cas normal, terminal
      ouvert dans une session GNOME déjà active), les réglages
      s'appliquent **immédiatement**, sans rien différer. Sinon, le module
      **génère lui-même** un contrôle `20-gnome-settings` dans
      `/usr/local/lib/session-checks/`, qui s'exécutera au prochain login
      (sentinelle incluse, un seul passage).
    - **Étape 32 (`nautilus-terminal`)** — installe toujours l'extension
      Python pendant le provisionnement, mais la commande `gsettings set
      ... terminal kitty` est **systématiquement** différée au contrôle
      statique `10-nautilus-terminal` (étape 35), qui demande confirmation
      via `zenity` avant d'agir — pas silencieux comme les deux autres.
    - **Étape 34 (`gsconnect`)** — installe les paquets et ouvre le port
      ufw pendant le provisionnement, mais `gnome-extensions enable` et la
      vérification du port `1716` sont **systématiquement** différés au
      contrôle statique `20-gsconnect` (étape 35), silencieux (pas de
      `zenity` : la décision d'installer a déjà été prise par
      l'administrateur via `sudo make gsconnect`).

!!! bug "Bug connu, non corrigé : ordre inversé au sein du groupe `desktop`"
    `gnome-settings` (étape 30) s'exécute avant `session-checks`
    (étape 35), qui crée le répertoire dont le premier a parfois besoin.
    Détail du symptôme, des scénarios de déclenchement réels et du
    correctif identifié :
    [Architecture — Bugs connus, non corrigés](architecture.md#bugs-connus-non-corriges).

---

## Groupe `devtools` (étapes 36 à 42)

| # | Cible | Action | Idempotence |
|---|-------|--------|-------------|
| 36 | `devinit` | `uv tool install --force ~/alm_tools/cli/devinit` | Chemin (`~/.local/bin/devinit` exécutable) |
| 37 | `pioinit` | `uv tool install --force ~/alm_tools/cli/pioinit` | Chemin (`~/.local/bin/pioinit` exécutable) |
| 38 | `mkdocsinit` | `uv tool install --force ~/alm_tools/cli/mkdocsinit` | Chemin (`~/.local/bin/mkdocsinit` exécutable) |
| 39 | `vmforge` | Installe le shim `~/.local/bin/vmforge`, applique la règle AppArmor libvirt-qemu | Chemin (shim) ; l'application AppArmor est toujours rejouée (pas de saut) |
| 40 | `open-sites` | `uv tool install --force ~/alm_tools/cli/open-sites`, puis génère et source la complétion bash (`~/.bash_completions/open-sites.sh`) | Chemin (`~/.local/bin/open-sites` exécutable) ; complétion regénérée à chaque run, ligne `.bashrc` ajoutée une seule fois |
| 41 | `pass-tool` | `uv tool install --force ~/alm_tools/cli/pass-tool` | Chemin (`~/.local/bin/pass-tool` exécutable) |
| 42 | `check-updates` | Crée le symlink `~/.local/bin/check_updates.sh` → `~/alm_tools/postinstall/check_updates.sh` | Chemin (symlink déjà présent et pointant vers la bonne source) |

!!! note "Prérequis explicite : `uv` avant les quatre scaffolders/outils"
    Déclaré dans le Makefile (`devinit: check-root uv`, idem `pioinit`,
    `mkdocsinit`, `open-sites`). Les quatre modules vérifient directement
    `~/.local/bin/uv` et échouent en fatal s'il est absent — utile
    seulement si vous lancez `sudo make devtools` isolément sans être
    passé par `system`/`cli` au préalable (`devtools` ne dépend QUE de
    `uv` dans le Makefile, pas de `system` — voir l'encadré `system` avant
    `cli` plus haut, même logique implicite ici pour les paquets KVM de
    `vmforge`, non bloquante celle-là).

!!! info "open-sites : dépendance fzf déjà couverte"
    `open-sites` s'appuie sur `fzf` (étape 13, groupe `cli`) pour choisir un
    site sans en taper le nom exact. Comme `cli` s'exécute avant `devtools`
    dans `sudo make all`, la dépendance est déjà satisfaite par l'ordre des
    groupes — aucune déclaration explicite supplémentaire nécessaire.

!!! warning "vmforge : deux étapes non automatisées après l'installation"
    - Si les paquets KVM (`qemu-kvm`, `libvirt-daemon-system`,
      `libvirt-clients`, `cloud-image-utils`, `acl`) manquent, le module se
      contente d'un avertissement — il ne les installe pas (ils sont déjà
      dans `packages_to_install.list`, donc présents dans le flux normal
      `system` → `devtools`, mais absents si `devtools` est lancé seul en
      tout premier).
    - Même en cas de succès de la règle AppArmor, `systemctl restart
      libvirtd` **n'est jamais exécuté automatiquement** — seulement
      loggé comme instruction à suivre.

---

## Récapitulatif des dépendances explicites (Makefile)

| Cible | Dépend de | Déclaré dans le Makefile ? |
|-------|-----------|------------------------------|
| `node` (15) | `fnm` (14) | ✅ Oui |
| `devinit` (36) | `uv` (9) | ✅ Oui |
| `pioinit` (37) | `uv` (9) | ✅ Oui |
| `mkdocsinit` (38) | `uv` (9) | ✅ Oui |
| `uv` (9) | `python3-full`/`python3-venv` de `pkg-install` (5) | ⚠️ Implicite (ordre des groupes dans `all` uniquement) |
| `vmforge` (39) | paquets KVM de `pkg-install` (5) | ⚠️ Implicite, non bloquant (avertissement seulement) |
| `open-sites` (40) | `uv` (9) | ✅ Oui |
| `open-sites` (40) | `fzf` (13) | ⚠️ Implicite (ordre des groupes dans `all` uniquement) |
| `claude-terminal` (18) | CLI `claude` installée manuellement | ❌ Non scriptée du tout — voir l'encadré en tête de page |

---

## Vérification des mises à jour upstream

`check_updates.sh` (à la racine de `postinstall/`) compare la version
installée de `fzf`, `xan`, `starship`, `fnm`, `uv`, `rclone`, `kitty` et
`pass-cli` — plus la LTS Node.js active via `fnm` — à la dernière version
publiée en amont. `zed` est volontairement exclu : il gère son propre
auto-update.

`pass-cli` publie sa dernière version sur un manifeste JSON dédié
(`https://proton.me/download/pass-cli/versions.json`, le même que celui
utilisé par son script d'installation officiel), pas via l'API GitHub —
binaire propriétaire proton.me, pas de dépôt public. `pass-cli` affiche
déjà spontanément une alerte de MAJ à chaque lancement (`New update
available: vX -> vY`) ; `check_updates.sh` la rend seulement visible sans
avoir à invoquer la commande.

```bash
~/alm_tools/postinstall/check_updates.sh --refresh   # exécute les checks, écrit le cache
~/alm_tools/postinstall/check_updates.sh              # affiche le cache, jamais de réseau
~/alm_tools/postinstall/check_updates.sh --apply      # rafraîchit puis propose, outil par outil, o/n/a/q
```

Câblé dans `alm_dots/.bash_env` par chemin complet, appelé à chaque
ouverture de shell. Le chemin sans argument ne fait qu'un `cat` du fichier
de cache (`~/.cache/alm-tools-updates`) — aucun appel réseau, donc jamais de
ralentissement au démarrage d'un terminal. Une fois par jour (fichier
témoin `~/.cache/alm-tools-update-check`), il relance lui-même `--refresh`
en tâche de fond pour que le *shell suivant* voie un résultat frais.

Depuis l'étape 42 (`check-updates`, groupe `devtools`), le script est aussi
disponible directement sur le `$PATH` via un symlink
`~/.local/bin/check_updates.sh` — plus besoin du chemin complet pour le
lancer à la main :

```bash
check_updates.sh --apply
```

!!! note "`--apply` n'est jamais automatique, par choix"
    `--apply` demande confirmation outil par outil (`o`/`n`/`a`/`q`) et
    n'est **jamais** appelé depuis un hook de démarrage — les invites
    `sudo` et les `rm` destructeurs doivent rester un geste volontaire.

Pour la liste complète de ce qui reste manuel après `sudo make all`, voir
[Étapes non scriptées actuellement](etapes-manuelles.md).
