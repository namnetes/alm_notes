# Étapes non scriptées actuellement

Cette page recense, indépendamment du récit séquentiel de
[Post-installation](post-installation.md), **tout ce que `sudo make all` ne
termine pas tout seul** — que ce soit résolu automatiquement un peu plus
tard (par `session-checks`, par un simple redémarrage de shell) ou que ce
soit une action humaine qui restera toujours nécessaire.

Chaque ligne précise explicitement lequel des deux cas s'applique.

---

## Prérequis fondamental : sourcer `.bash_env`/`.bash_functions` dans `~/.bashrc`

!!! success "Automatisé — une commande, idempotente, à exécuter une fois par machine"
    `alm_dots` ne versionne **pas** `~/.bashrc` — c'est le fichier
    squelette standard d'Ubuntu (`/etc/skel/.bashrc`), propre à chaque
    machine. `stow .` déploie `.bash_env` et `.bash_functions` dans
    `$HOME`, mais ne les fait jamais sourcer tout seul : le `.bashrc` par
    défaut d'Ubuntu ne connaît que `.bash_aliases` (comportement
    standard), pas `.bash_env` ni `.bash_functions`. Sans correctif, ce
    trou est **silencieux** : aucun alias/outil de `.bash_env` (starship,
    fzf, zoxide, fnm, eza, uv...) ni aucune fonction de `.bash_functions`
    (`ve`, `gsp`, `csvc`, `shims`...) ne fonctionne, sans le moindre
    message d'erreur — et cela invalide aussi une partie des entrées de la
    table suivante : « ouvrir un nouveau terminal » ne suffit à activer
    `uv`/`fnm`/`zed` dans le `PATH` que si `.bash_env` est effectivement
    sourcé.

    **`bootstrap.sh`** (racine d'`alm_dots`) ferme ce trou : il vérifie
    d'abord que `.bash_env`/`.bash_functions` existent bien dans `$HOME`
    (sinon il s'arrête avec un message clair plutôt que de patcher dans le
    vide), puis ajoute les deux blocs `source` à `~/.bashrc` — chacun
    protégé par un `grep -qF` qui saute le bloc s'il est déjà présent :
    relancer le script ne duplique jamais rien.

Intégré au tutoriel de déploiement, juste après `stow` (voir [Déploiement
après installation fraîche — étape
4](../../deploiement-post-installation.md#etape-4-deployer-les-dotfiles)) :

```bash
cd ~/alm_dots
stow --target="$HOME" .
bash bootstrap.sh
source ~/.bashrc
```

Vérification : `tl` (alias de `shims`) doit afficher l'inventaire des
outils sans erreur « commande introuvable ».

---

## Différées par `session-checks` — vraiment auto-résolues

Ces étapes nécessitent une session D-Bus utilisateur live, absente pendant
le provisionnement root. Le framework
[session-checks](session-checks.md) les termine automatiquement à la
prochaine ouverture de session GNOME, sans action de configuration de la
part de l'utilisateur.

| Étape différée | Se résout comment | Silencieux ? |
|---|---|---|
| `gsettings` (dock, interface, accent) | Contrôle `20-gnome-settings`, généré dynamiquement par `install_gnome_settings.sh` **seulement si** aucune session D-Bus n'était active à l'installation. Sentinelle : un seul passage. | ✅ Oui |
| Config Nautilus → kitty (`gsettings set ... terminal kitty`) | Contrôle statique `10-nautilus-terminal`, **systématiquement** différé (jamais appliqué pendant le provisionnement, même avec un bus live) | ⚠️ Non — demande confirmation via `zenity` |
| Activation de l'extension GSConnect (`gnome-extensions enable` + vérif port 1716) | Contrôle statique `20-gsconnect`, **systématiquement** différé | ✅ Oui — aucune fenêtre |

!!! note "Nuance sur `gnome-settings`"
    C'est le seul des trois où le différé est **conditionnel** : si vous
    lancez `sudo make all` depuis un terminal ouvert dans une session
    GNOME déjà active (le cas normal), les réglages s'appliquent
    **immédiatement**, sans jamais passer par `session-checks`. Voir le
    cas limite documenté dans
    [Post-installation — groupe desktop](post-installation.md#groupe-desktop-etapes-30-a-35).

---

## Nécessitent une nouvelle session ou un nouveau shell — auto-résolues sans configuration

Rien à faire de particulier ici au-delà d'ouvrir un nouveau terminal ou de
se reconnecter — mais ce n'est pas instantané, donc listé pour ne pas
surprendre.

| Étape | Pourquoi ce n'est pas immédiat | Action utilisateur |
|---|---|---|
| Accès Docker sans `sudo` (`usermod -aG docker`) | Le jeton de groupe du shell courant ne se rafraîchit pas à chaud | Se déconnecter/reconnecter, ou `newgrp docker` |
| `uv`, `fnm`/Node.js, `zed` dans le `PATH` | `.bash_env` charge conditionnellement chaque outil s'il est présent | Ouvrir un nouveau terminal |
| kitty (nouvelles fenêtres) | Binaires mis à jour dans `~/.local/kitty.app`, les fenêtres déjà ouvertes gardent l'ancien process | Relancer les fenêtres kitty |

---

## Jamais scriptées — action humaine réellement nécessaire

Ces étapes ne seront **jamais** automatisées par `postinstall`, soit parce
que le module se contente d'auditer sans installer, soit parce que
l'action est intrinsèquement humaine (décision, secret, geste physique).

| Étape | Pourquoi ce n'est pas scripté | Où agir |
|---|---|---|
| **Installer la CLI Claude Code** (`claude`) | `install_claude_terminal.sh` (étape 18) vérifie sa présence mais ne l'installe jamais — et son absence **arrête tout le pipeline** `make all` dès le groupe `cli`. Voir l'avertissement en tête de [Post-installation](post-installation.md). | `curl -fsSL https://claude.ai/install.sh \| bash` |
| **Authentification Claude Code** (`claude` puis `/login`) | Vérifiée (avertissement seulement, non bloquant) mais jamais réalisée par le module | Manuel, dans un terminal |
| **Appairage GSConnect avec un téléphone** | Handshake de confiance entre deux appareils — aucun script ne peut valider ça à la place de l'utilisateur | App KDE Connect sur le téléphone + confirmation des deux côtés, voir [GSConnect](../../../../outils/gsconnect.md#appairage-avec-un-telephone-android) |
| **`systemctl restart libvirtd`** après la règle AppArmor de `vmforge` (étape 39) | Loggé comme instruction (`log_info "[NOTE] ..."`), jamais exécuté par le module | `sudo systemctl restart libvirtd` |
| **Paquets KVM manquants** si `devtools` est lancé avant `system` | `install_vmforge.sh` avertit mais n'installe rien (les paquets sont censés déjà venir de `packages_to_install.list`) | `sudo apt install -y qemu-kvm libvirt-daemon-system libvirt-clients cloud-image-utils acl`, ou relancer dans le bon ordre |
| **Kitty comme `x-terminal-emulator` système** | `install_kitty.sh` installe les binaires upstream et les `.desktop` locaux, mais ne touche jamais à `update-alternatives` | Voir [Finitions manuelles](../../finitions-manuelles.md#kitty-comme-terminal-par-defaut) |
| **Thème Catppuccin pour GNOME Terminal** | Hors du périmètre de `postinstall` par choix — script tiers + sélection manuelle du profil | Voir [Finitions manuelles](../../finitions-manuelles.md#theme-catppuccin-pour-gnome-terminal) |
| **Libellé « Taille » sous les dossiers Nautilus** | Aucune clé `gsettings` scriptée pour cette préférence — réglage UI pur | Nautilus → Préférences → Libellés de la vue grille |
| **Fournir les images de fond d'écran** | Le timer `change-wallpaper.timer` et le script de rotation sont déployés par `stow`, mais aucune image n'est fournie par un dépôt | Copier des images dans `~/.config/my_ubuntu/wallpapers/` |
| **`~/.gitconfig.local`** | Volontairement non versionné (email pro, clé de signature propres à la machine) | Recréer à la main si besoin, voir [Présentation d'alm_dots](../../alm_dots/presentation.md) |
| **Ubuntu Pro (`pro attach`)** | Nécessite un compte personnel et un token — ne peut pas être scripté à l'avance | Voir [Finitions manuelles](../../finitions-manuelles.md#1-ubuntu-pro-optionnel) |
| **Liste personnelle `data/open-sites.csv`** (étape 40, `open-sites`) | Fichier gitignoré par choix — révèle l'inventaire de comptes personnels (banques, mutuelle, employeur...), jamais commité donc jamais restauré par le module. Un fichier absent est géré proprement (liste vide, pas de crash) | Restaurer depuis sa propre sauvegarde, ou reconstruire au fil de l'eau avec `open-sites add` |
| **Clé SSH YubiKey** (`ssh-keygen -K`) | PIN + toucher physique de la clé | Voir [Sécurité — Réinstallation du poste](../../../../securite/yubikey/reinstallation.md) |
| **`check_updates.sh --apply`** | Détecte les outils upstream en retard mais ne met jamais à jour tout seul, par choix de conception (les `sudo`/`rm` doivent rester un geste volontaire) | `check_updates.sh --apply` (symlink `~/.local/bin`, étape 42) ou `~/alm_tools/postinstall/check_updates.sh --apply` |

---

## Hors du périmètre strict d'`alm_tools/postinstall`

Ces deux étapes relèvent d'`alm_dots` (unités systemd utilisateur) plutôt
que du postinstall lui-même, mais font partie du parcours complet de
réinstallation — voir
[Déploiement après installation fraîche — étape 6](../../deploiement-post-installation.md#etape-6-activer-les-services-systemd-utilisateur) :

```bash
systemctl --user enable --now mkdocs.service
systemctl --user enable --now change-wallpaper.timer
```

`stow .` dépose les fichiers `.service`/`.timer`, mais ne les active
jamais — l'activation reste une commande manuelle, unique, à lancer après
le déploiement des dotfiles.
