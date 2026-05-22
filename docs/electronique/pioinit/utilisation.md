# Guide d'utilisation

## Créer un projet

### Workflow recommandé — init dans le répertoire courant

```bash
mkdir ~/projets/mon-blink && cd ~/projets/mon-blink
pioinit . --board uno
```

### Créer dans un sous-répertoire

```bash
cd ~/projets
pioinit mon-blink --board uno
cd mon-blink
```

### Sans prompts interactifs

```bash
pioinit mon-blink --board esp32dev --description "Capteur de température" --yes
```

### Toutes les options

```
pioinit .                                     # init dans le répertoire courant
pioinit mon-projet --board uno                # Arduino Uno
pioinit mon-projet --board esp32dev           # ESP32 DevKit
pioinit mon-projet --board pico               # Raspberry Pi Pico
pioinit mon-projet --board my_board \         # carte non répertoriée
    --platform atmelavr --monitor-speed 9600
pioinit mon-projet --board uno \
    --framework arduino \
    --description "Description" \
    --yes
```

---

## Workflow quotidien

### Compiler

```bash
make build
# ou : pio run
```

### Flasher sur la carte

```bash
make upload
# ou : pio run --target upload
```

### Moniteur série

```bash
make monitor
# ou : pio device monitor --baud 9600
```

### Flasher puis moniteur en une commande

```bash
make flash
```

### Nettoyer les fichiers de build

```bash
make clean
```

### Voir toutes les cibles disponibles

```bash
make
# ou : make help
```

---

## Activer l'autocomplétion C/C++ dans Zed

### Première fois (ou après ajout de bibliothèque)

```bash
make compiledb
```

Cette commande :

1. Lance `pio run --target compiledb` — PlatformIO compile et génère
   `.pio/build/<env>/compile_commands.json`
2. Crée un lien symbolique `compile_commands.json` à la racine du projet
3. Clangd (le LSP C/C++ de Zed) détecte le changement et redémarre

Résultat dans Zed : autocomplétion des fonctions Arduino, `Serial.`, GPIO, etc.,
et soulignement des erreurs de syntaxe en temps réel.

!!! note "compile_commands.json n'est pas versionné"
    `.gitignore` exclut ce fichier — il est régénéré à la demande.
    À refaire après chaque `git clone` ou ajout de bibliothèque dans `platformio.ini`.

---

## Utiliser les tâches Zed

Ouvrez le projet dans Zed, puis lancez une tâche via la palette de commandes :

1. ++ctrl+shift+p++ → taper `task` → **Tasks: Spawn Task**
2. Choisissez parmi les 7 tâches disponibles :

| Tâche | Équivalent make |
|-------|----------------|
| `PIO: Build` | `make build` |
| `PIO: Upload` | `make upload` |
| `PIO: Monitor (9600 baud)` | `make monitor` |
| `PIO: Flash (upload + monitor)` | `make flash` |
| `PIO: Clean` | `make clean` |
| `PIO: Generate compile_commands.json` | `make compiledb` |
| `Docs: Doxygen` | `make doxygen` |

### Ajouter des raccourcis clavier

Éditez `~/.config/zed/keymap.json` :

```json
[
  {
    "context": "Workspace",
    "bindings": {
      "ctrl-shift-b": "task: spawn (PIO: Build)",
      "ctrl-shift-u": "task: spawn (PIO: Upload)",
      "ctrl-shift-m": "task: spawn (PIO: Monitor (9600 baud))"
    }
  }
]
```

---

## Documentation du projet

### Doxygen (documentation API C/C++)

```bash
make doxygen
# Ouvre doxygen_output/html/index.html
```

Doxygen extrait les commentaires `/** @brief ... */` de `src/` et `include/`
pour générer une référence HTML de l'API. Exemple dans le `main.cpp` généré :

```cpp
/**
 * @brief Lit la température depuis un DHT22.
 *
 * @param pin  Broche GPIO connectée au DHT22.
 * @return     Température en °C, ou NAN si lecture échouée.
 */
float readTemperature(uint8_t pin);
```

---

## Réinstallation from scratch

Procédure complète après réinstallation du système ou sur une nouvelle machine.

### 1. Réinstaller les dépendances système

```bash
# PlatformIO
uv tool install platformio
pio --version

# clangd (autocomplétion C/C++ dans Zed)
sudo apt install clangd
which clangd

# Doxygen (optionnel, pour la doc API)
sudo apt install doxygen
```

### 2. Réinstaller pioinit

```bash
cd ~/alm_tools/pioinit
uv tool install .
pioinit --version
```

### 3. Rouvrir votre projet

```bash
cd ~/projets/mon-blink
zed .
```

Le `.zed/tasks.json` est versionné — les tâches sont immédiatement disponibles.

### 4. Régénérer les fichiers non versionnés

```bash
make compiledb              # génère compile_commands.json
```

### 5. Vérifier les droits sur le port série

```bash
groups | grep dialout
# Si absent :
sudo usermod -aG dialout $USER
# Puis déconnexion/reconnexion
```

### Ce qui est versionné vs ce qui est régénéré

| Fichier / Dossier | Versionner ? | Comment |
|-------------------|:------------:|---------|
| `platformio.ini` | ✅ | Config carte + framework |
| `src/`, `include/`, `lib/` | ✅ | Code source |
| `Makefile` | ✅ | Cibles de workflow |
| `.zed/tasks.json` | ✅ | Tâches partagées avec le projet |
| `Doxyfile` | ✅ | Config documentation API |
| `.pio/` | ❌ | Build artifacts — `pio run` les régénère |
| `compile_commands.json` | ❌ | `make compiledb` le régénère |
| `doxygen_output/` | ❌ | `make doxygen` le régénère |

`.gitignore` exclut automatiquement tous les fichiers ❌.
