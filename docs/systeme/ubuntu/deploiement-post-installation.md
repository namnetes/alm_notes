# Déploiement après installation fraîche

Tutoriel pas à pas pour passer d'une **Ubuntu fraîchement installée** à un
poste complètement opérationnel, en s'appuyant sur les quatre dépôts
personnels : [alm_tools](alm_tools/index.md) (provisionnement),
[alm_dots](alm_dots/index.md) (dotfiles), `alm_notes` (ce wiki) et
`alm_dashboard` (dashboard Homer).

!!! info "Prérequis"
    - Une Ubuntu fraîche avec accès Internet — pour réinstaller l'OS
      lui-même sur le TUXEDO, voir [Réinstallation WebFAI](webfai.md)
    - La **YubiKey** et son PIN : elle sert de point d'amorçage SSH,
      aucun fichier de clé à restaurer (voir
      [Sécurité — Réinstallation du poste](../../securite/yubikey/reinstallation.md))
    - Les dépôts `alm_*` **poussés sur GitHub** avant la réinstallation
      — tout ce qui n'est pas poussé est perdu avec le disque

---

## Vue d'ensemble

| # | Étape | Durée estimée |
|---|-------|---------------|
| 1 | Mise à jour du système | ~5 min |
| 2 | Amorçage : git, stow, clé SSH YubiKey | ~5 min |
| 3 | Clone des dépôts personnels | ~2 min |
| 4 | Déploiement des dotfiles (stow) | ~5 min |
| 5 | Provisionnement `postinstall` | **20 à 40 min** |
| 6 | Services systemd utilisateur | ~2 min |
| 7 | Finitions (terminal, libvirt, fonds d'écran) | ~5 min |
| 8 | Vérifications finales | ~5 min |
|   | **Total** | **~1 heure** |

---

## Étape 1 — Mettre à jour le système

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Étape 2 — Amorçage : git, stow et la clé SSH

Sur une Ubuntu Desktop fraîche, `git` et `stow` ne sont pas préinstallés :

```bash
sudo apt install -y git stow
```

Puis restaurer la clé SSH **depuis la YubiKey** — le credential résident
renaît en une commande, sans aucune sauvegarde à restaurer :

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cd ~/.ssh
ssh-keygen -K                              # PIN demandé
mv id_ed25519_sk_rk id_ed25519_sk
mv id_ed25519_sk_rk.pub id_ed25519_sk.pub
chmod 600 id_ed25519_sk
```

!!! note "Le détail complet est dans la section Sécurité"
    Pourquoi ça marche, le renommage `_rk`, les pièges (agent GNOME…) :
    voir [Sécurité — Réinstallation du poste](../../securite/yubikey/reinstallation.md)
    et le tutoriel
    [Clé SSH matérielle et GitHub](../../securite/yubikey/ssh-github.md).

---

## Étape 3 — Cloner les dépôts personnels

```bash
cd ~
git clone git@github.com:namnetes/alm_dots.git
git clone git@github.com:namnetes/alm_tools.git
git clone git@github.com:namnetes/alm_notes.git
git clone git@github.com:namnetes/alm_dashboard.git
```

Le PIN et un toucher de la YubiKey sont demandés à chaque clone, et SSH
fait valider l'empreinte de `github.com` au premier contact — les deux
sont normaux.

| Dépôt | Emplacement | Rôle | Documentation |
|-------|-------------|------|---------------|
| [namnetes/alm_dots](https://github.com/namnetes/alm_dots) | `~/alm_dots` | Dotfiles (GNU Stow) | [alm_dots](alm_dots/index.md) |
| [namnetes/alm_tools](https://github.com/namnetes/alm_tools) | `~/alm_tools` | Provisionnement + outils | [alm_tools](alm_tools/index.md) |
| [namnetes/alm_notes](https://github.com/namnetes/alm_notes) | `~/alm_notes` | Wiki personnel (MkDocs) | — |
| [namnetes/alm_dashboard](https://github.com/namnetes/alm_dashboard) | `~/alm_dashboard` | Dashboard Homer (bookmarks) + page de démarrage Brave | [alm_dashboard](alm_dashboard.md) |

---

## Étape 4 — Déployer les dotfiles

```bash
cd ~/alm_dots
stow --simulate --target="$HOME" .    # (1)!
stow --target="$HOME" .
bash bootstrap.sh                     # (2)!
source ~/.bashrc
```

1. Répétition générale sans toucher au disque. Une Ubuntu neuve possède
   ses propres `.bashrc` / `.profile` qui entrent en **conflit** avec
   ceux du dépôt : supprimer ou déplacer les fichiers d'origine signalés
   avant de lancer le vrai `stow .`.
2. `alm_dots` ne versionne pas `~/.bashrc` (squelette Ubuntu, propre à
   chaque machine) : ce script idempotent lui ajoute les blocs `source`
   de `.bash_env`/`.bash_functions`, sans lesquels ils resteraient
   déployés mais jamais chargés. Détail :
   [Étapes manuelles — prérequis
   fondamental](alm_tools/postinstall/etapes-manuelles.md#prerequis-fondamental-sourcer-bash_envbash_functions-dans-bashrc).

Ce déploiement met en place d'un coup : la configuration shell
(`.bash_env`, alias, fonctions), `~/.ssh/config`, `~/.gitconfig`,
les configurations Kitty / Zed / VS Code, et les unités systemd
utilisateur (activées à l'étape 6). Détail et vérification des liens :
[alm_dots — Installation](alm_dots/installation.md).

Le shell reste pleinement fonctionnel même si les outils (starship,
fnm, zoxide…) ne sont pas encore installés : `.bash_env` teste la
présence de chaque outil avant de l'initialiser.

!!! note "Recréer `~/.gitconfig.local`"
    Le `~/.gitconfig` stowé contient un `[include]` vers
    `~/.gitconfig.local` — les surcharges propres à la machine (email
    pro, clé de signature…). Ce fichier n'est **volontairement pas
    versionné** : le recréer à la main si la machine en a besoin.

!!! note "`system-config/` n'est pas déployé par stow"
    Le dossier `system-config/` du dépôt (réglages `sysctl`, etc.) est
    volontairement exclu de `stow` (`.stow-local-ignore`) : ce ne sont pas
    des dotfiles utilisateur mais des fichiers système, à copier
    manuellement avec les privilèges root :

    ```bash
    sudo cp ~/alm_dots/system-config/etc/sysctl.d/99-optimisation-sysctl.conf \
        /etc/sysctl.d/99-optimisation-sysctl.conf
    sudo sysctl --system
    ```

    Applique le tuning mémoire/réseau (swappiness, anti-spoofing, SYN
    cookies…) prévu pour ce poste. Vérification :
    `sysctl vm.swappiness` doit répondre `1`.

---

## Étape 5 — Provisionnement postinstall

!!! warning "Étape la plus longue : 20 à 40 min"
    Installation de tous les paquets APT/Snap, outils CLI et
    applications. La durée dépend surtout de la connexion Internet.

```bash
cd ~/alm_tools/postinstall
sudo make          # affiche l'aide et la liste des cibles
sudo make all      # provisionnement complet
```

`sudo make all` enchaîne les cinq groupes dans l'ordre :

| Groupe | Contenu |
|--------|---------|
| `system` | Mises à jour APT/Snap, PPAs, paquets, codecs, nettoyage |
| `cli` | uv, xan, eza, starship, fzf, fnm, node, rclone… |
| `apps` | Brave, Zed, Bruno, Docker, VSCode, Proton, Steam, YubiKey… |
| `desktop` | Réglages GNOME, polices, Nautilus, session-checks |
| `devtools` | devinit, pioinit, mkdocsinit, vmforge |

Chaque exécution écrit un journal horodaté :
`/var/log/postinstall_<timestamp>.log`.

!!! note "Brave installé, pas encore configuré"
    Le module `apps` installe Brave mais ne pousse aucun réglage de
    confidentialité : Shields, extensions, durcissement réseau… tout
    est à refaire manuellement. Procédure complète :
    [Sécurité — Brave, réinstallation du poste](../../securite/brave/reinstallation.md).

!!! note "rclone installé, config Google Drive à restaurer"
    Le module `cli` installe `rclone` mais pas sa configuration : le
    remote `google_drive` doit être restauré depuis le blob chiffré
    sauvegardé dans Proton Pass avant de pouvoir relancer les
    sauvegardes automatiques. Procédure complète :
    [Backup Google Drive — Sauvegarder la config pour une réinstallation rapide](alm_tools/outils/backup-googledrive.md#sauvegarder-la-config-pour-une-reinstallation-rapide).

!!! tip "Rejouable sans risque"
    Tous les modules sont **idempotents** : en cas d'interruption ou
    d'échec ponctuel, relancer `sudo make all` reprend sans dégât.
    Pour approfondir : [Post-installation](alm_tools/postinstall/post-installation.md),
    [Déboguer](alm_tools/postinstall/deboguer.md),
    [Personnaliser](alm_tools/postinstall/personnaliser.md).

---

## Étape 6 — Activer les services systemd utilisateur

Les unités sont déjà en place grâce à stow (étape 4) ; reste à les
activer :

```bash
systemctl --user daemon-reload

# Wiki personnel sur http://127.0.0.1:8000/
systemctl --user enable --now mkdocs.service

# Rotation automatique du fond d'écran (horaire)
systemctl --user enable --now change-wallpaper.timer
```

`mkdocs.service` lance `uv run mkdocs serve` dans `~/alm_notes` : il
suppose `uv` installé (groupe `cli` de l'étape 5) et synchronise
l'environnement Python du wiki au premier démarrage. Gestion au
quotidien via les alias `mkr` / `mks` / `mkl` :
[alm_dots — Service MkDocs](alm_dots/service-mkdocs.md).

---

## Étape 7 — Finitions

Les quatre réglages ci-dessous sont les indispensables ; la liste
complète des réglages manuels (Ubuntu Pro, thème GNOME Terminal,
Nautilus, Firefox…) est dans
[Finitions manuelles](finitions-manuelles.md).

**Kitty comme terminal par défaut** (sa configuration est déjà déployée
par stow ; Kitty lui-même est installé par `make kitty` — installeur
upstream, pas apt) : voir la commande `update-alternatives --install`
dans [Finitions manuelles](finitions-manuelles.md#kitty-comme-terminal-par-defaut) —
l'ancien `--config` ne liste plus Kitty depuis l'abandon du paquet apt.

**Polices** — vérifier que les Nerd Fonts installées par le groupe
`desktop` sont bien visibles :

```bash
fc-list | grep -i firacode
```

**libvirt / KVM** (seulement si les VMs [vmforge](alm_tools/outils/vmforge.md)
sont utilisées) :

```bash
sudo usermod -aG libvirt $USER
newgrp libvirt
```

**Dashboard Homer** (sert de page de démarrage à Brave — voir
[Sécurité — Brave](../../securite/brave/reinstallation.md) et
[alm_dashboard](alm_dashboard.md)) :

```bash
newgrp docker   # si le groupe docker vient d'être ajouté à l'étape 5
cd ~/alm_dashboard
make homer-start
```

**Fonds d'écran** — le timer de l'étape 6 pioche dans :

```bash
mkdir -p ~/.config/my_ubuntu/wallpapers
# y copier les images, puis premier tirage manuel :
~/.functions/bin/change_wallpaper.sh
```

---

## Étape 8 — Vérifications finales

| Vérification | Commande | Résultat attendu |
|---|---|---|
| GitHub via YubiKey | `ssh -T git@github.com` | `Hi namnetes!` (PIN + toucher) |
| YubiKey détectée | `ykman info` | Modèle et firmware affichés |
| Dépôts tous propres | `gsp` | Aucun dépôt en retard |
| Wiki accessible | ouvrir `http://127.0.0.1:8000/` | Le wiki s'affiche |
| Dashboard Homer | ouvrir `http://127.0.0.1:8080` | Le dashboard s'affiche |
| Alias git | `gst` | Statut git (sans préfixe `git`) |
| Outils CLI | `tl` | Inventaire des outils installés |

Si tout répond : le poste est opérationnel.
