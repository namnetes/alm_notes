# Framework session-checks

Le framework **session-checks** exécute automatiquement des scripts de
vérification à chaque ouverture de session GNOME. Si l'environnement n'est
pas conforme (paquet manquant, configuration absente…), le framework le
détecte et propose une correction interactive à l'utilisateur.

!!! tip "Analogie pour les débutants"
    Imaginez un agent de sécurité qui vérifie votre badge à l'entrée du
    bureau chaque matin. S'il manque quelque chose, il vous prévient
    immédiatement — mais seulement quand c'est nécessaire. C'est exactement
    ce que fait session-checks à l'ouverture de votre session.

---

## Pourquoi ce framework ?

Sans ce système, garantir l'état d'un poste de travail après une
réinstallation ou une mise à jour imposait soit de mémoriser une liste
d'actions manuelles, soit d'écrire un script monolithique difficile à
maintenir.

session-checks résout les trois problèmes classiques :

| Problème | Solution apportée |
|----------|-------------------|
| Un paquet se désinstalle par erreur | Détecté au prochain login, réparation proposée |
| Ajouter un nouveau contrôle | Déposer un fichier dans un répertoire, c'est tout |
| Comprendre ce qui s'est passé | Journaux centralisés dans systemd (`journalctl`) |

---

## Architecture

```mermaid
flowchart TD
    A([Ouverture de session GNOME]) --> B["/etc/xdg/autostart/\nsession-checks.desktop"]
    B --> C["/usr/local/bin/\nrun-session-checks\norchestre"]
    C --> D["/usr/local/lib/session-checks/"]
    D --> E["10-nautilus-terminal"]
    D --> F["20-gsconnect"]
    E -->|OK| H([Journaux — tout va bien])
    E -->|Échec| I([Notification zenity])
    F -->|OK| H
    F -->|Échec| I

    classDef startStop fill:#e1f5fe,stroke:#01579b
    classDef logic fill:#e8eaf6,stroke:#1a237e
    classDef data fill:#fff3e0,stroke:#e65100
    classDef error fill:#ffebee,stroke:#c62828

    class A,H startStop
    class B,C logic
    class D,E,F data
    class I error
```

### Ce qui se passe, étape par étape

1. **GNOME lit `/etc/xdg/autostart/`** au démarrage de chaque session
   utilisateur. Ce répertoire est l'équivalent système du dossier
   *Applications au démarrage* de l'interface graphique.

2. **Le fichier `.desktop`** indique à GNOME de lancer l'orchestrateur
   `/usr/local/bin/run-session-checks`.

3. **L'orchestrateur** parcourt tous les scripts exécutables de
   `/usr/local/lib/session-checks/` dans l'ordre alphabétique (les
   préfixes `10-`, `20-`… garantissent cet ordre).

4. **Chaque script de contrôle** :
   - Vérifie si tout est en ordre.
   - Ne fait rien si tout va bien (pas de fenêtre, pas de bruit).
   - Propose une correction — graphique (zenity) si une décision utilisateur
     a du sens (ex. `10-nautilus-terminal`), silencieuse si l'action a déjà
     été explicitement demandée à l'installation et qu'il ne reste qu'à la
     finaliser (ex. `20-gsconnect`).

5. **Les résultats** sont écrits dans les journaux système (journald)
   sous l'identifiant `session-checks`, consultables à tout moment.

6. Si des contrôles ont échoué, **une fenêtre récapitulative** liste les
   problèmes rencontrés.

---

## Fichiers du système

### Vue d'ensemble

```
alm_tools/postinstall/
└── session-checks/                     ← sources versionnées dans Git
    ├── install.sh                      ← installation complète (sudo bash install.sh)
    ├── run-session-checks              ← copié vers /usr/local/bin/
    ├── session-checks.desktop          ← copié vers /etc/xdg/autostart/
    ├── 10-nautilus-terminal            ← contrôle : Nautilus ouvre kitty
    └── 20-gsconnect                    ← contrôle : extension GSConnect activée

/usr/local/bin/
└── run-session-checks                  ← orchestrateur
/usr/local/lib/session-checks/          ← contrôles actifs
├── 10-nautilus-terminal
└── 20-gsconnect
/etc/xdg/autostart/session-checks.desktop ← déclencheur GNOME (tous les utilisateurs)
```

!!! info "Deux endroits, un seul rôle"
    Les **sources** (dans `alm_tools`) sont versionnées sous Git — c'est là
    que vous modifiez le code. Les **fichiers installés** (dans
    `/usr/local/`) sont ceux que GNOME et le système utilisent réellement.
    `install.sh` synchronise les deux.

---

### L'orchestrateur — `run-session-checks`

C'est le chef d'orchestre. Il ne contient aucune logique métier : il sait
seulement *comment* exécuter les contrôles et *comment* rapporter les
résultats.

{% raw %}
```bash
#!/usr/bin/env bash
# Orchestrateur du framework session-checks.
#
# Exécute tous les scripts exécutables du répertoire
# /usr/local/lib/session-checks/ dans l'ordre lexicographique
# (convention run-parts de Debian/Ubuntu).

set -uo pipefail

CHECKS_DIR="/usr/local/lib/session-checks"
LOG_TAG="session-checks"
FAILED=()

log() {
    local priority="${2:-info}"
    echo "$1" | systemd-cat -t "$LOG_TAG" -p "$priority"
}

if [ ! -d "$CHECKS_DIR" ]; then
    log "Répertoire $CHECKS_DIR introuvable — aucun contrôle exécuté." \
        "warning"
    exit 0
fi

log "Démarrage des contrôles de session."

while IFS= read -r -d '' script; do
    name=$(basename "$script")
    log "Contrôle : $name — démarrage"

    if "$script"; then
        log "Contrôle : $name — OK"
    else
        FAILED+=("$name")
        log "Contrôle : $name — ÉCHEC" "warning"
    fi
done < <(
    find "$CHECKS_DIR" \
        -maxdepth 1 \
        -type f \
        -executable \
        -print0 \
    | sort -z
)

if [ ${#FAILED[@]} -eq 0 ]; then
    log "Tous les contrôles ont réussi."
else
    log "Contrôles en échec : ${FAILED[*]}" "err"
    zenity --warning \
        --title="Contrôles de session" \
        --text="Les contrôles suivants ont échoué :\n$(
            printf '• %s\n' "${FAILED[@]}"
        )\n\nConsultez les journaux :\njournalctl -t session-checks" \
        --width=420
fi
```
{% endraw %}

**Points clés :**

- `set -uo pipefail` — le script s'arrête proprement en cas d'erreur
  interne, mais continue en cas d'échec d'un contrôle individuel (géré
  par le `if "$script"`).
- `systemd-cat` — écrit dans journald avec l'identifiant `session-checks`,
  ce qui permet de filtrer les logs facilement.
- `sort -z` — trie les noms de fichiers par ordre alphabétique, ce qui
  respecte l'ordre des préfixes numériques (`10-`, `20-`…).
- `zenity --warning` — n'est affiché que si au moins un contrôle a échoué.
  Session silencieuse si tout va bien.

---

### Le contrôle — `10-nautilus-terminal`

Ce contrôle garantit que Nautilus dispose de l'option *Ouvrir dans Kitty*
et que l'extension est correctement configurée.

#### Pourquoi pas un simple wrapper ?

On pourrait croire qu'il suffit de placer un script nommé `gnome-terminal`
dans `/usr/local/bin/` (prioritaire dans le `PATH`) pour que Nautilus
ouvre kitty à la place. **Ce n'est pas possible.**

`nautilus-extension-gnome-terminal` ne lance **pas** `gnome-terminal` en
tant que processus fils. Elle envoie un **message D-Bus** au service
`org.gnome.Terminal`. Quand ce service n'est pas en cours d'exécution, le
démon D-Bus l'active directement via son fichier de service système :

```
/usr/share/dbus-1/services/org.gnome.Terminal.service
    → Exec=/usr/libexec/gnome-terminal-server
```

Le `PATH` n'est **jamais consulté**. Aucun wrapper dans `/usr/local/bin/`
ne sera jamais appelé par cette extension.

```mermaid
flowchart LR
    N([Nautilus]) -->|message D-Bus| B["org.gnome.Terminal\n(session bus)"]
    B -->|activation| S["/usr/libexec/\ngnome-terminal-server"]
    S --> G([gnome-terminal])

    classDef startStop fill:#e1f5fe,stroke:#01579b
    classDef data fill:#fff3e0,stroke:#e65100
    classDef error fill:#ffebee,stroke:#c62828

    class N,G startStop
    class B data
    class S error
```

#### La solution : `nautilus-open-any-terminal`

[nautilus-open-any-terminal](https://github.com/Stunkymonkey/nautilus-open-any-terminal)
est une extension Python pour Nautilus. Elle ajoute l'entrée *Ouvrir dans
le terminal* dans le menu contextuel et se configure via `gsettings` — sans
aucune dépendance à gnome-terminal ni à D-Bus.

```bash
# Installation (utilisateur courant, pas besoin de sudo)
pip3 install --user --break-system-packages nautilus-open-any-terminal

# Compiler les schémas GSettings installés par le paquet
glib-compile-schemas ~/.local/share/glib-2.0/schemas

# Configurer kitty comme terminal cible
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal kitty
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal new-tab false

# Redémarrer Nautilus pour charger l'extension
nautilus -q
```

Le contrôle `10-nautilus-terminal` automatise l'ensemble de ces étapes :

```bash
#!/usr/bin/env bash
# Contrôle : extension Nautilus "Ouvrir dans Kitty".
#
# nautilus-extension-gnome-terminal communique avec gnome-terminal via D-Bus
# (org.gnome.Terminal) — un wrapper PATH est sans effet car l'extension
# n'exécute jamais gnome-terminal en tant que processus fils.
#
# Ce contrôle vérifie que nautilus-open-any-terminal est installé et configuré
# pour ouvrir kitty. L'extension s'appuie sur l'API Python de Nautilus
# (nautilus-python), indépendante de D-Bus.
#
# Retourne :
#   0  — extension présente et configurée, ou refus de l'utilisateur
#   1  — installation tentée mais échouée

set -euo pipefail

# Le paquet pip (>= 0.7) installe nautilus_open_any_terminal.py — voir
# modules/desktop/install_nautilus_terminal.sh, qui applique la même
# convention de nommage et vérifie déjà les deux emplacements possibles.
EXTENSION_NAME="nautilus_open_any_terminal.py"
EXTENSION_FILE="$HOME/.local/share/nautilus-python/extensions/${EXTENSION_NAME}"
SYSTEM_EXTENSION_FILE="/usr/local/share/nautilus-python/extensions/${EXTENSION_NAME}"
SCHEMAS_DIR="$HOME/.local/share/glib-2.0/schemas"
SYSTEM_SCHEMAS_DIR="/usr/local/share/glib-2.0/schemas"
SCHEMA="com.github.stunkymonkey.nautilus-open-any-terminal"

_extension_installed() {
    [ -f "$EXTENSION_FILE" ] || [ -f "$SYSTEM_EXTENSION_FILE" ]
}

_schema_ready() {
    gsettings get "$SCHEMA" terminal 2>/dev/null | grep -q "'kitty'"
}

# Le schéma peut être présent sur disque (paquet pip installé) sans être
# encore compilé/découvrable par gsettings — arrive notamment quand
# l'extension a été installée en système (/usr/local) par une exécution
# antérieure du postinstall sans compilation immédiate des schémas.
_compile_missing_schemas() {
    if [ -d "$SCHEMAS_DIR" ]; then
        glib-compile-schemas "$SCHEMAS_DIR" 2>/dev/null || true
    fi
    if [ -d "$SYSTEM_SCHEMAS_DIR" ] \
        && ! gsettings list-schemas | grep -qx "$SCHEMA"; then
        pkexec glib-compile-schemas "$SYSTEM_SCHEMAS_DIR" 2>/dev/null || true
    fi
}

_ready() {
    _extension_installed || return 1
    _schema_ready && return 0
    _compile_missing_schemas
    _schema_ready
}

_ready && exit 0

zenity --question \
    --title="Extension Nautilus manquante" \
    --text="L'option <b>Ouvrir dans Kitty</b> n'est pas disponible.\
\n\nautilus-extension-gnome-terminal utilise D-Bus et ne peut pas être\
\nredirigé vers kitty via un simple wrapper dans le PATH.\
\n\nSolution : <b>nautilus-open-any-terminal</b>, une extension Python\
\nindépendante de gnome-terminal, configurable via gsettings.\
\n\nVoulez-vous l'installer et la configurer maintenant ?" \
    --width=540 || {
    # Refus explicite de l'utilisateur : distinct d'un vrai succès dans les
    # journaux, même si le code de sortie (0) reste identique par design.
    logger -t session-checks \
        "10-nautilus-terminal : ignoré (refus de l'utilisateur)"
    exit 0
}

# Supprimer l'ancienne extension si présente (évite deux entrées dans le menu)
if dpkg -s nautilus-extension-gnome-terminal >/dev/null 2>&1; then
    pkexec apt-get remove -y nautilus-extension-gnome-terminal || true
fi

# Installer via pip — pas besoin de sudo (installation utilisateur)
if ! pip3 install --user --break-system-packages nautilus-open-any-terminal; then
    zenity --error \
        --title="Échec de l'installation" \
        --text="L'installation de nautilus-open-any-terminal a échoué.\
\nConsultez les journaux :\njournalctl -t session-checks" \
        --width=420
    exit 1
fi

# Compiler les schémas GSettings installés par le paquet
[ -d "$SCHEMAS_DIR" ] && glib-compile-schemas "$SCHEMAS_DIR" 2>/dev/null || true

# Configurer kitty comme terminal cible
gsettings set "$SCHEMA" terminal kitty
gsettings set "$SCHEMA" new-tab false

zenity --info \
    --title="Extension installée" \
    --text="nautilus-open-any-terminal installé et configuré pour kitty.\
\nNautilus va redémarrer." \
    --width=420

nautilus -q
```

**Points clés :**

- `_extension_installed()` — vérifie **deux emplacements** : `~/.local/`
  (installation utilisateur normale, via ce contrôle ou `install.sh`) et
  `/usr/local/` (installation système, si `pip3 install` a été lancé sans
  `--user` — arrive avec d'anciennes exécutions manuelles). Ignorer le
  second emplacement fait croire à tort que l'extension est absente.
- `_compile_missing_schemas()` — le fichier `.gschema.xml` peut exister sur
  disque sans être **compilé/découvrable** par gsettings
  (`gsettings list-schemas` ne le liste pas). Le contrôle recompile
  `~/.local/share/glib-2.0/schemas` directement, et — si l'extension est en
  système — `/usr/local/share/glib-2.0/schemas` via `pkexec` (fenêtre
  PolicyKit, sans `sudo`, car ce répertoire appartient à root).
- `pkexec apt-get remove` — supprime `nautilus-extension-gnome-terminal`
  pour éviter deux entrées *Ouvrir un terminal* dans le menu contextuel.
  L'élévation est graphique (fenêtre PolicyKit), sans `sudo`.
- `pip3 install --user --break-system-packages` — installation dans
  `~/.local/`, sans droits root.
- Refus de l'utilisateur (`zenity --question` → Non) : le contrôle écrit un
  message explicite via `logger` avant de sortir en `0`, pour que
  `journalctl -t session-checks` distingue un vrai `OK` d'un refus — voir
  l'encadré ci-dessous sur le faux positif corrigé.
- `nautilus -q` — redémarre Nautilus pour charger l'extension Python.

!!! warning "Faux positif corrigé (2026-07-05)"
    Un audit a révélé que ce contrôle pouvait journaliser **« OK »** alors
    que l'extension n'était en réalité pas fonctionnelle. Deux causes
    cumulées :

    1. `EXTENSION_FILE` cherchait `open_any_terminal.py` (ancien nom, paquet
       pip < 0.7), alors que la version installée (0.8.1) fournit
       `nautilus_open_any_terminal.py`. Le fichier réel n'était donc jamais
       trouvé.
    2. L'extension avait été installée en **système** (`/usr/local/`, sans
       `--user`) lors d'une exécution antérieure — emplacement que l'ancien
       `_ready()` ne vérifiait pas du tout — et son schéma GSettings n'avait
       jamais été compilé, donc introuvable par `gsettings`.

    Résultat concret sur ce poste : le clic droit *Ouvrir dans Kitty*
    n'apparaissait pas dans Nautilus, sans qu'aucun journal ne le signale.
    Le script ci-dessus (vérification des deux emplacements + compilation
    de schéma à la demande, y compris côté système via `pkexec`) corrige
    les deux causes et répare l'état existant au prochain login, sans
    réinstallation.

---

### Le contrôle — `20-gsconnect`

Ce contrôle finalise l'activation de l'extension GNOME Shell
[GSConnect](https://github.com/GSConnect/gnome-shell-extension-gsconnect)
(implémentation de KDE Connect), installée en amont par
`sudo make gsconnect` (`modules/desktop/install_gsconnect.sh`).

#### Pourquoi un contrôle silencieux, sans zenity ?

Contrairement à `10-nautilus-terminal`, ce contrôle ne pose **aucune
question** à l'utilisateur. La différence de contexte :

- `10-nautilus-terminal` peut découvrir que l'extension n'a **jamais été
  installée** (postinstall jamais lancé) — une vraie décision à proposer.
- `20-gsconnect` intervient seulement **après** un `sudo make gsconnect`
  explicite : les paquets sont déjà là par décision assumée de
  l'administrateur. Il ne reste qu'une activation technique — root ne
  peut pas l'effectuer de façon fiable pendant le provisionnement, faute
  de session D-Bus utilisateur live à ce moment-là — sans nouvelle
  décision à faire valider.

```bash
#!/usr/bin/env bash
set -euo pipefail

EXTENSION_UUID="gsconnect@andyholmes.github.io"

if [ ! -d "/usr/share/gnome-shell/extensions/${EXTENSION_UUID}" ]; then
    exit 0
fi

_gsconnect_running() {
    ss -tuln 2>/dev/null | grep -q ':1716 '
}

_gsconnect_running && exit 0

if [ "$(gsettings get org.gnome.shell disable-user-extensions)" = "true" ]; then
    gsettings set org.gnome.shell disable-user-extensions false
    logger -t session-checks \
        "20-gsconnect : disable-user-extensions était à true, corrigé"
fi

if ! gnome-extensions list 2>/dev/null | grep -qx "${EXTENSION_UUID}"; then
    exit 0
fi

gnome-extensions enable "${EXTENSION_UUID}" 2>/dev/null || true
sleep 2

if _gsconnect_running; then
    logger -t session-checks "20-gsconnect : activé (port 1716 en écoute)"
    exit 0
fi

logger -t session-checks -p user.warning \
    "20-gsconnect : activation tentée, port 1716 toujours fermé"
exit 1
```

**Points clés :**

- `_gsconnect_running()` — vérifie le **port 1716 réellement en écoute**,
  pas la sortie de `gnome-extensions info`. Cette dernière s'est révélée
  peu fiable en conditions réelles : elle interroge un service D-Bus
  activable séparé (`org.gnome.Shell.Extensions`, un script `gjs`
  autonome), pas le processus `gnome-shell` effectivement en cours
  d'exécution — elle peut donc afficher un état générique qui ne reflète
  pas la réalité de la session live.
- **Garde-fou `disable-user-extensions`** — ce réglage GNOME Shell global
  désactive silencieusement *toutes* les extensions, quel que soit le
  contenu de `enabled-extensions`. Observé à `true` en conditions réelles
  sur ce poste (mis là par une session de dépannage antérieure sans
  rapport avec GSConnect) — ce contrôle le remet à `false` par précaution
  à chaque passage, plutôt que de supposer qu'il est correct.
- **Extension pas encore scannée** — si `gnome-extensions list` ne la
  liste pas du tout, ce n'est pas un échec : l'extension existe sur disque
  mais GNOME Shell ne l'a pas encore découverte (typiquement juste après
  l'installation, avant la première déconnexion/reconnexion). Le contrôle
  sort en `0` et retentera au login suivant.
- Pas de correction proposée si les paquets sont absents (`exit 0`
  immédiat) — ce n'est pas le rôle de ce contrôle de les installer ;
  c'est celui de `sudo make gsconnect`.

---

### Le fichier `.desktop` — déclencheur GNOME

```ini
[Desktop Entry]
Type=Application
Name=Session Checks
Name[fr_FR]=Contrôles de session
Comment=Vérifie la conformité de l'environnement au démarrage de session GNOME
Comment[en]=Verifies environment compliance at GNOME session start
Exec=/usr/local/bin/run-session-checks
Hidden=false
NoDisplay=true
X-GNOME-Autostart-enabled=true
```

- `NoDisplay=true` — n'apparaît pas dans la liste des *Applications au
  démarrage* de l'interface graphique (évite la confusion).
- `X-GNOME-Autostart-enabled=true` — active le déclenchement automatique.
- Placé dans `/etc/xdg/autostart/` (et non `~/.config/autostart/`), il
  s'applique à **tous les utilisateurs** du système.

---

## Écrire un nouveau contrôle

Un contrôle est un script Bash ordinaire qui respecte trois règles :

1. **Son nom ne contient pas de point** (convention `run-parts` Debian).
2. **Il est exécutable** (`chmod +x`).
3. **Il retourne 0** si tout va bien, **non-zéro** en cas d'échec réel.

### Modèle de départ

```bash
#!/usr/bin/env bash
# Contrôle : description courte de ce que fait ce script.
#
# Comportement attendu :
#   - Retourne 0 si l'état est conforme (ou si l'utilisateur refuse).
#   - Retourne 1 si une correction était nécessaire mais a échoué.

set -euo pipefail

# 1. Vérifier si l'état est déjà conforme
if <condition_déjà_ok>; then
    exit 0
fi

# 2. Proposer la correction à l'utilisateur
zenity --question \
    --title="Titre de la fenêtre" \
    --text="Description du problème.\nVoulez-vous corriger ?" \
    --width=420 || exit 0  # Refus = pas une erreur

# 3. Appliquer la correction (avec élévation si nécessaire)
if pkexec <commande_de_correction>; then
    zenity --info --title="Succès" --text="Correction appliquée." --width=300
else
    zenity --error --title="Échec" \
        --text="La correction a échoué.\nVoir : journalctl -t session-checks" \
        --width=380
    exit 1
fi
```

### Étapes concrètes

1. **Créer le fichier** dans `alm_tools/postinstall/session-checks/` :

    ```bash
    touch ~/alm_tools/postinstall/session-checks/20-mon-controle
    chmod +x ~/alm_tools/postinstall/session-checks/20-mon-controle
    ```

2. **Écrire la logique** en suivant le modèle ci-dessus.

3. **Tester manuellement** avant de l'intégrer :

    ```bash
    bash ~/alm_tools/postinstall/session-checks/20-mon-controle
    echo "Code de retour : $?"
    ```

4. **Installer** pour que le framework le prenne en compte :

    ```bash
    sudo install -m 755 \
        ~/alm_tools/postinstall/session-checks/20-mon-controle \
        /usr/local/lib/session-checks/20-mon-controle
    ```

5. **Tester via l'orchestrateur** :

    ```bash
    /usr/local/bin/run-session-checks
    ```

---

## Consulter les journaux

Tous les événements sont écrits dans journald sous l'identifiant
`session-checks`.

```bash
# Tous les messages du framework (session en cours et précédentes)
journalctl -t session-checks

# En temps réel (utile lors d'un test)
journalctl -t session-checks -f

# Depuis le dernier démarrage uniquement
journalctl -t session-checks -b

# Uniquement les erreurs et avertissements
journalctl -t session-checks -p warning
```

!!! tip "Lire un journal systemd quand on débute"
    Chaque ligne commence par un horodatage, le nom de la machine, puis le
    message. Lisez de bas en haut pour voir les événements les plus récents
    en premier. L'option `-f` ("follow") affiche les nouvelles lignes en
    temps réel, comme `tail -f`.

---

## Tester sans rouvrir de session

Exécutez l'orchestrateur directement dans un terminal :

```bash
/usr/local/bin/run-session-checks
```

Il se comportera exactement comme lors d'un vrai démarrage de session :
fenêtres graphiques, journaux, notification en cas d'échec.

---

## Installation après une réinstallation du système

### Prérequis

- `alm_tools` cloné dans `~/alm_tools`

    ```bash
    git clone git@github.com:namnetes/alm_tools.git ~/alm_tools
    ```

### Option A — Via le postinstall (recommandée)

Les modules `install_session_checks` et `install_nautilus_terminal` sont
intégrés au postinstall (groupe `desktop`, cibles `session-checks` et
`nautilus-terminal`). Lancer le groupe suffit :

```bash
cd ~/alm_tools/postinstall
sudo make desktop            # ou : sudo make session-checks nautilus-terminal
```

Le framework est installé automatiquement, sans action supplémentaire.
La configuration de kitty comme terminal par défaut sera effectuée
automatiquement au premier login via `session-checks`.

### Option B — Installation standalone

Si vous souhaitez installer uniquement le framework, sans relancer
tout le postinstall :

```bash
sudo bash ~/alm_tools/postinstall/session-checks/install.sh
```

Ce script installe en une seule commande :

- l'orchestrateur (`run-session-checks`)
- tous les contrôles (`10-nautilus-terminal`…)
- `nautilus-open-any-terminal` pour l'utilisateur courant
- le déclencheur GNOME (`.desktop`)
- nettoyage de l'ancien autostart utilisateur si présent

---

## Dépannage

### Nautilus ouvre quand même gnome-terminal

Vérifiez que `nautilus-extension-gnome-terminal` est bien supprimé :

```bash
dpkg -l nautilus-extension-gnome-terminal
```

Si encore installé, supprimez-le :

```bash
sudo apt-get remove nautilus-extension-gnome-terminal
nautilus -q
```

Vérifiez ensuite l'état complet — l'extension peut être installée côté
utilisateur **ou** côté système, selon l'historique du poste :

```bash
# Extension Python présente ? (les deux emplacements possibles)
ls ~/.local/share/nautilus-python/extensions/nautilus_open_any_terminal.py
ls /usr/local/share/nautilus-python/extensions/nautilus_open_any_terminal.py

# Schémas compilés ?
gsettings get com.github.stunkymonkey.nautilus-open-any-terminal terminal

# Doit afficher : 'kitty'
```

Si `gsettings get` renvoie une erreur de schéma introuvable, recompilez le
répertoire correspondant à l'emplacement où l'extension a été trouvée
ci-dessus (le second nécessite `pkexec` : il appartient à root) :

```bash
glib-compile-schemas ~/.local/share/glib-2.0/schemas
# ou, si l'extension est installée en système :
pkexec glib-compile-schemas /usr/local/share/glib-2.0/schemas

gsettings set com.github.stunkymonkey.nautilus-open-any-terminal terminal kitty
gsettings set com.github.stunkymonkey.nautilus-open-any-terminal new-tab false
nautilus -q
```

### Le framework ne se lance pas au démarrage

Vérifiez que le fichier `.desktop` est bien présent et actif :

```bash
ls -la /etc/xdg/autostart/session-checks.desktop
cat /etc/xdg/autostart/session-checks.desktop
```

Vérifiez que l'orchestrateur est exécutable :

```bash
ls -la /usr/local/bin/run-session-checks
```

### Un contrôle échoue sans raison apparente

Consultez les journaux pour voir le détail :

```bash
journalctl -t session-checks -b --no-pager
```

Testez le contrôle individuellement :

```bash
bash /usr/local/lib/session-checks/10-nautilus-terminal
echo "Code retour : $?"
```

### `zenity` ne s'affiche pas

`zenity` a besoin de la variable `DISPLAY` ou `WAYLAND_DISPLAY`. Si vous
lancez l'orchestrateur depuis un terminal SSH (sans session graphique),
ces variables sont absentes. C'est normal : le framework est conçu pour
s'exécuter uniquement dans une session graphique GNOME.

---

## Référence rapide

| Commande | Description |
|----------|-------------|
| `/usr/local/bin/run-session-checks` | Lancer manuellement le framework |
| `journalctl -t session-checks` | Voir tous les journaux |
| `journalctl -t session-checks -f` | Journaux en temps réel |
| `ls /usr/local/lib/session-checks/` | Lister les contrôles installés |
| `gsettings get com.github.stunkymonkey.nautilus-open-any-terminal terminal` | Vérifier le terminal configuré |
| `sudo install -m 755 <fichier> /usr/local/lib/session-checks/` | Ajouter un contrôle |
| `sudo rm /usr/local/lib/session-checks/<nom>` | Supprimer un contrôle |
| `sudo bash ~/alm_tools/postinstall/session-checks/install.sh` | Réinstaller le framework complet |
