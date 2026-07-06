# Intégration dans Zed Editor

Ce guide configure Zed Editor pour travailler confortablement avec PlatformIO :
**autocomplétion C/C++ complète** via `clangd`, **tâches de build/upload** en un raccourci,
et **moniteur série** dans le terminal intégré de Zed.

!!! info "Prérequis"
    PlatformIO Core (`pio`) doit être installé. Voir [Installation](index.md).

---

## Vue d'ensemble

Zed ne dispose pas d'extension PlatformIO native. On compense avec trois éléments :

```
┌─────────────────────────────────────────────────────────┐
│  Zed Editor                                             │
│                                                         │
│  ┌─────────────────┐  ┌──────────────────────────────┐ │
│  │ Éditeur C/C++   │  │ Tasks (tasks.json)           │ │
│  │ + clangd LSP    │  │ · build                      │ │
│  │ (autocomplétion,│  │ · upload                     │ │
│  │  diagnostics)   │  │ · monitor                    │ │
│  └────────┬────────┘  └──────────────┬───────────────┘ │
│           │                          │                  │
└───────────┼──────────────────────────┼──────────────────┘
            │                          │
            ▼                          ▼
   compile_commands.json          pio run / pio device monitor
   (généré par pio)               (exécuté dans terminal Zed)
```

---

## Étape 1 — Activer l'autocomplétion C/C++ avec clangd

### Pourquoi `compile_commands.json` ?

`clangd` (le serveur de langage C/C++) a besoin de savoir **comment votre code est
compilé** : quels chemins d'include, quelles macros, quelle version du C++. PlatformIO
peut générer ce fichier automatiquement.

### Générer `compile_commands.json`

Depuis le répertoire de votre projet :

```bash
pio run --target compiledb
```

PlatformIO génère `.pio/build/<env>/compile_commands.json`.

Pour que `clangd` le trouve depuis la racine du projet, créez un lien symbolique :

```bash
ln -s .pio/build/uno/compile_commands.json compile_commands.json
```

Remplacez `uno` par le nom de votre environment (celui défini dans `platformio.ini`).

!!! tip "Regénérer après ajout de bibliothèque"
    À chaque fois que vous ajoutez une bibliothèque dans `platformio.ini`, relancez
    `pio run --target compiledb` puis recréez le lien symbolique.
    Clangd redémarre automatiquement dès qu'il détecte le changement.

### Vérifier que clangd fonctionne dans Zed

Ouvrez `src/main.cpp` dans Zed. Si clangd est actif, vous verrez :

- Autocomplétion des fonctions Arduino (`Serial.`, `digitalWrite(`, etc.)
- Soulignement rouge sur les erreurs de syntaxe
- Survol d'une fonction → affiche sa signature et sa documentation

Si rien ne s'affiche, vérifiez que `clangd` est bien installé sur votre système :

```bash
which clangd
# /usr/bin/clangd  ← OK
```

Si absent :

```bash
sudo apt install clangd
```

---

## Étape 2 — Configurer les tâches Zed

Les **tâches** Zed permettent de lancer des commandes (`pio run`, `pio device monitor`,
etc.) directement depuis l'éditeur, sans quitter le clavier.

### Créer le fichier de tâches du projet

Dans votre projet PlatformIO, créez le dossier `.zed/` et le fichier `tasks.json` :

```bash
mkdir -p .zed
```

Puis créez `.zed/tasks.json` avec ce contenu :

```json
[
  {
    "label": "PIO: Build",
    "command": "pio run",
    "cwd": "$ZED_WORKTREE_ROOT",
    "allow_concurrent_runs": false,
    "reveal": "always"
  },
  {
    "label": "PIO: Upload",
    "command": "pio run --target upload",
    "cwd": "$ZED_WORKTREE_ROOT",
    "allow_concurrent_runs": false,
    "reveal": "always"
  },
  {
    "label": "PIO: Clean",
    "command": "pio run --target clean",
    "cwd": "$ZED_WORKTREE_ROOT",
    "allow_concurrent_runs": false,
    "reveal": "always"
  },
  {
    "label": "PIO: Monitor série (9600)",
    "command": "pio device monitor --baud 9600",
    "cwd": "$ZED_WORKTREE_ROOT",
    "allow_concurrent_runs": false,
    "reveal": "always"
  },
  {
    "label": "PIO: Upload + Monitor",
    "command": "pio run --target upload && pio device monitor --baud 9600",
    "cwd": "$ZED_WORKTREE_ROOT",
    "allow_concurrent_runs": false,
    "reveal": "always"
  },
  {
    "label": "PIO: Générer compile_commands.json",
    "command": "pio run --target compiledb && ln -sf .pio/build/uno/compile_commands.json compile_commands.json",
    "cwd": "$ZED_WORKTREE_ROOT",
    "allow_concurrent_runs": false,
    "reveal": "always"
  }
]
```

!!! note "Adapter le nom d'environment"
    Dans la dernière tâche, remplacez `uno` par le nom de votre environment.
    Si vous avez `[env:esp32dev]` dans `platformio.ini`, utilisez `.pio/build/esp32dev/`.

### Explication de chaque champ

| Champ | Rôle |
|-------|------|
| `label` | Nom affiché dans le menu des tâches |
| `command` | Commande shell exécutée |
| `cwd` | Répertoire de travail (`$ZED_WORKTREE_ROOT` = racine du projet ouvert) |
| `allow_concurrent_runs` | `false` = une seule instance à la fois (évite les conflits de port) |
| `reveal` | `"always"` = ouvre le panneau terminal à chaque lancement |

---

## Étape 3 — Lancer une tâche

### Depuis le menu

1. Ouvrez la palette de commandes : ++ctrl+shift+p++
2. Tapez `task` puis sélectionnez **Tasks: Spawn Task**
3. Choisissez votre tâche dans la liste (ex : `PIO: Upload`)

### Avec un raccourci clavier personnalisé

Éditez `~/.config/zed/keymap.json` et ajoutez :

```json
[
  {
    "context": "Workspace",
    "bindings": {
      "ctrl-shift-b": "task: spawn (PIO: Build)",
      "ctrl-shift-u": "task: spawn (PIO: Upload)",
      "ctrl-shift-m": "task: spawn (PIO: Monitor série (9600))"
    }
  }
]
```

---

## Le terminal intégré de Zed comme moniteur série

Pour les sessions de débogage longues, le **terminal intégré de Zed** est plus pratique
que d'ouvrir un terminal séparé.

### Ouvrir le terminal intégré

- Raccourci : ++ctrl+grave++ (la touche `` ` `` sous `Échap`)
- Ou : menu **View → Terminal**

Un panneau s'ouvre en bas de l'éditeur avec un shell complet.

### Lancer le moniteur série dans le terminal intégré

```bash
# Dans le terminal intégré de Zed
pio device monitor --baud 9600
```

Vous verrez les messages de votre Arduino défiler directement dans Zed, sans quitter
l'éditeur. Appuyez sur ++ctrl+c++ pour quitter le moniteur.

!!! tip "Avantage du terminal intégré vs tâche"
    Utiliser une **tâche** pour le moniteur ferme le panneau dès que vous appuyez sur
    ++ctrl+c++. Utiliser le **terminal intégré** laisse le shell ouvert — pratique pour
    enchaîner des commandes.

---

## Réinstallation from scratch

Voici la procédure complète pour retrouver un environnement fonctionnel après une
réinstallation du système ou sur une nouvelle machine.

### 1. Réinstaller PlatformIO Core

```bash
uv tool install platformio
pio --version   # vérifier
```

### 2. Réinstaller clangd

```bash
sudo apt install clangd
which clangd    # /usr/bin/clangd
```

### 3. Rouvrir votre projet dans Zed

```bash
cd ~/projets/blink-led
zed .
```

Si le projet vient d'un dépôt Git, le fichier `.zed/tasks.json` est déjà présent.
Les tâches sont immédiatement disponibles.

### 4. Régénérer `compile_commands.json`

Le fichier `compile_commands.json` et le dossier `.pio/` ne sont **pas** versionnés
(ils figurent dans `.gitignore`). Il faut les régénérer :

```bash
pio run --target compiledb
ln -sf .pio/build/uno/compile_commands.json compile_commands.json
```

Ou lancez directement la tâche `PIO: Générer compile_commands.json` depuis Zed.

### 5. Vérifier les droits sur le port série

```bash
groups | grep dialout
```

Si `dialout` n'apparaît pas :

```bash
sudo usermod -aG dialout $USER
# Déconnexion/reconnexion requise
```

### Récapitulatif — ce qui est versionné vs ce qui est régénéré

| Fichier / Dossier | Versionner ? | Remarque |
|-------------------|:------------:|----------|
| `platformio.ini` | ✅ Oui | Configuration du projet |
| `src/` | ✅ Oui | Votre code source |
| `.zed/tasks.json` | ✅ Oui | Tâches Zed partagées avec le projet |
| `compile_commands.json` | ❌ Non | Régénéré par `pio run --target compiledb` |
| `.pio/` | ❌ Non | Fichiers de build générés |
| `lib/` | Selon cas | Oui si bibliothèques privées, non sinon |

Ajoutez ces lignes à votre `.gitignore` si elles n'y sont pas déjà :

```gitignore
.pio/
compile_commands.json
```

---

## Résolution des problèmes courants

### `clangd` ne trouve pas les headers Arduino

Vérifiez que `compile_commands.json` est présent à la racine du projet :

```bash
ls -la compile_commands.json
# compile_commands.json -> .pio/build/uno/compile_commands.json
```

Si le lien est cassé (`.pio/` a été supprimé), régénérez :

```bash
pio run --target compiledb
ln -sf .pio/build/uno/compile_commands.json compile_commands.json
```

### La tâche ne trouve pas `pio`

Zed hérite du `PATH` au moment où il est lancé. Si vous avez installé PlatformIO
avec `pipx` après avoir ouvert Zed, redémarrez Zed.

Vérifiez aussi que `~/.local/bin` est dans votre `PATH` :

```bash
echo $PATH | grep -o "\.local/bin"
```

Si absent, ajoutez dans `~/.bashrc` :

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Upload échoue avec "Permission denied"

```bash
sudo chmod a+rw /dev/ttyACM0
# Ou, solution permanente :
sudo usermod -aG dialout $USER
```

### Le port change après redémarrage

Linux peut assigner `/dev/ttyACM0` ou `/dev/ttyACM1` selon l'ordre de connexion.
Pour forcer un port stable, créez une règle udev :

```bash
# Trouver les attributs de votre carte
udevadm info -a -n /dev/ttyACM0 | grep -E "idVendor|idProduct|serial"
```

Puis créez `/etc/udev/rules.d/99-arduino.rules` :

```
SUBSYSTEM=="tty", ATTRS{idVendor}=="2341", ATTRS{idProduct}=="0043", \
SYMLINK+="arduino"
```

Rechargez les règles :

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

Votre carte sera désormais accessible via `/dev/arduino` en plus de `/dev/ttyACM*`.
Mettez à jour `upload_port = /dev/arduino` dans `platformio.ini`.
