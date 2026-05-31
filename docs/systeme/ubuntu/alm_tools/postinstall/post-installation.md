# Post-installation

Ce guide explique comment utiliser le Makefile de `postinstall` pour configurer
un poste Ubuntu depuis zéro, ou pour réinstaller un outil précis.

---

## Prérequis

- Ubuntu (testé sur 22.04 et 26.04)
- Connexion internet active
- Le dépôt `alm_tools` cloné dans `~/alm_tools`

```bash
cd ~/alm_tools/postinstall
sudo make          # affiche l'aide et toutes les cibles disponibles
```

!!! warning "Toujours se placer dans `postinstall/`"
    Le Makefile utilise des chemins relatifs. Lancer `sudo make` depuis un autre
    répertoire provoque des erreurs de fichiers introuvables.

---

## Pourquoi un Makefile ?

Le Makefile est le **seul point d'entrée**. Il apporte trois avantages concrets
par rapport à un script monolithique :

- **Ordre garanti** : les dépendances entre cibles sont déclarées explicitement
  (`node` attend `fnm`, `devtools` attend `uv`).
- **Journalisation automatique** : chaque exécution crée un fichier de log horodaté
  dans `/var/log/postinstall_<date>.log` via `tee`.
- **Granularité** : on peut relancer un seul outil sans tout rejouer.

---

## Scénario 1 — Provisioning complet (poste vierge)

```bash
cd ~/alm_tools/postinstall
sudo make all
```

`all` enchaîne les cinq groupes dans l'ordre correct :

```
system → cli → apps → desktop → devtools
```

Durée estimée : **15 à 40 minutes** selon la connexion et l'état du système.

Si une étape échoue, `make` s'arrête immédiatement. Le fichier de log indique
exactement quelle commande a échoué. Corriger le problème et relancer uniquement
le groupe ou la cible concernée suffit — les outils déjà installés ne seront
pas réinstallés (voir [Idempotence](#idempotence)).

---

## Scénario 2 — Par groupe

Utile pour mettre à jour ou reconfigurer un ensemble sans tout rejouer.

```bash
sudo make system    # APT + Snap + PPAs + paquets + codecs + nettoyage
sudo make cli       # outils en ligne de commande
sudo make apps      # applications desktop
sudo make desktop   # GNOME, polices, Nautilus, session-checks
sudo make devtools  # outils de développement personnels
```

### Détail des groupes

=== "system"

    | Cible | Action |
    |-------|--------|
    | `apt-update` | `apt-get update` + `dist-upgrade` |
    | `snap-update` | Refresh Snap + install depuis `snap_packages.list` |
    | `ppas` | Ajoute les PPAs de `ppas.list` |
    | `pkg-remove` | Purge les paquets de `packages_to_remove.list` |
    | `pkg-install` | Installe les paquets de `packages_to_install.list` |
    | `restricted` | Codecs audio/vidéo + polices Microsoft (EULA pré-acceptée) |
    | `cleanup` | `autoremove`, nettoyage Snap, `/tmp`, vacuum journal |
    | `plocate` | `updatedb` — rafraîchit l'index de recherche |

=== "cli"

    | Cible | Outil installé | Destination |
    |-------|----------------|-------------|
    | `uv` | Gestionnaire Python uv | `~/.local/bin/uv` |
    | `eza` | Remplacement de `ls` | `/usr/local/bin/eza` |
    | `starship` | Prompt cross-shell | `/usr/local/bin/starship` |
    | `fzf` | Fuzzy finder | `/usr/local/bin/fzf` |
    | `fnm` | Fast Node Manager | `~/.local/bin/fnm` |
    | `node` | Node.js LTS via fnm | géré par fnm |
    | `xan` | CSV Magician | `/usr/local/bin/xan` |
    | `glow` | Rendu Markdown en terminal | via APT (dépôt charm.sh) |
    | `claude-terminal` | Vérifie l'intégration Claude AI terminal (API key, kitten, `~/.claude/commands/`) | — |

=== "apps"

    | Cible | Application | Source |
    |-------|-------------|--------|
    | `remove-firefox` | Supprime Firefox Snap + résidus | — |
    | `brave` | Navigateur Brave | APT (dépôt officiel) |
    | `zed` | Éditeur Zed | Script zed.dev |
    | `bruno` | Client API REST/GraphQL | APT (dépôt officiel) |
    | `docker` | Docker CE + CLI + Compose | APT (dépôt officiel) |
    | `vscode` | Visual Studio Code | APT (dépôt Microsoft) |
    | `proton` | Mail, Pass, VPN Proton | APT (dépôt Proton) |
    | `steam` | Steam | APT multiverse (i386) |
    | `yubikey` | YubiKey Manager | PPA yubico/stable |
    | `snap-apps` | Yazi, KolourPaint, OnlyOffice | Snap |

=== "desktop"

    | Cible | Action |
    |-------|--------|
    | `gnome-settings` | Paramètres GNOME : dock, batterie, hot corners, accent bleu |
    | `fonts` | FiraCode Nerd Font, JetBrains Mono, Cascadia Code |
    | `nautilus-terminal` | Ouvre Kitty depuis Nautilus (clic droit) |
    | `nautilus-templates` | Crée `~/Modèles/` pour le menu « Nouveau document » |
    | `session-checks` | Framework de contrôles GNOME au démarrage |

=== "devtools"

    | Cible | Outil | Prérequis |
    |-------|-------|-----------|
    | `devinit` | Scaffolder de projets Python | `uv` |
    | `pioinit` | Scaffolder de projets PlatformIO | `uv` |
    | `mkdocsinit` | Configuration MkDocs Material (idempotent) | `uv` |
    | `vmforge` | Automatisation de VMs KVM | — |

---

## Scénario 3 — Cible individuelle

Pour réinstaller ou mettre à jour un seul outil :

```bash
sudo make uv            # réinstaller uv uniquement
sudo make brave         # réinstaller Brave uniquement
sudo make fonts         # réinstaller les polices uniquement
sudo make plocate       # mettre à jour l'index de recherche
```

---

## Dépendances entre cibles

Deux dépendances explicites sont déclarées dans le Makefile.
Si la cible amont échoue, la cible aval ne s'exécute pas :

| Cible | Dépend de | Raison |
|-------|-----------|--------|
| `node` | `fnm` | Node.js est installé et géré par fnm |
| `devinit` | `uv` | devinit est un outil uv (`uv tool install`) |
| `pioinit` | `uv` | pioinit est un outil uv (`uv tool install`) |
| `mkdocsinit` | `uv` | mkdocsinit est un outil uv (`uv tool install`) |

!!! tip "Vérifier avant de lancer `devtools`"
    Si `uv` n'est pas encore installé, `sudo make devtools` échouera sur
    `devinit` et `pioinit`. Lancer d'abord `sudo make uv`, ou laisser
    `sudo make all` gérer l'ordre automatiquement.

---

## Idempotence

Chaque module vérifie si l'outil est déjà présent avant d'agir.
Relancer `sudo make all` sur un poste déjà configuré est sans risque :

```
[INFO]    [STATUT] eza déjà installé (eza v0.20.1 ...)
[INFO]    ✓  eza done
```

L'outil est détecté, aucune action n'est effectuée, et la cible est marquée
comme terminée. C'est utile pour reprendre un `sudo make all` interrompu.

---

## Ce qui nécessite une action manuelle après installation

Certaines installations modifient des permissions ou des variables
d'environnement qui ne prennent effet qu'à la prochaine session.

| Outil | Action requise | Raison |
|-------|----------------|--------|
| Docker | Se déconnecter et reconnecter | L'ajout au groupe `docker` n'est actif qu'à la prochaine session |
| fnm / Node.js | Ouvrir un nouveau terminal | `~/.bash_env` initialise fnm, ce qui requiert un nouveau shell |
| uv | Ouvrir un nouveau terminal | `~/.local/bin` doit être dans le `PATH` |
| Zed | Ouvrir un nouveau terminal | Zed s'installe dans `~/.local/bin` du compte réel |

!!! info "Pourquoi certains outils s'installent dans votre `~` et non dans `/usr/local` ?"
    Les modules qui utilisent un installeur officiel (`uv`, `fnm`, `zed`) s'installent
    dans le HOME du compte utilisateur réel, pas dans celui de root. Le script détecte
    automatiquement votre compte via la variable `$SUDO_USER` (le nom de l'utilisateur
    qui a invoqué `sudo`). Voir [Architecture](architecture.md) pour les détails.
