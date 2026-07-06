# pioinit

**pioinit** est un générateur de projets PlatformIO embarqués.
Une seule commande crée la structure complète d'un projet :
code C/C++, Makefile, configuration Zed, et documentation Doxygen.

!!! tip "Analogie avec devinit"
    pioinit est à l'électronique ce que `devinit` est au Python :
    un initialiseur de projet opinionné qui applique les standards du dépôt.

!!! info "Dépôt source"
    pioinit fait partie du dépôt [alm_tools](../../systeme/ubuntu/alm_tools/index.md) — `cli/pioinit/`.

---

## Ce que pioinit génère

```
mon-projet/
├── platformio.ini        # carte, framework, vitesse moniteur
├── src/main.cpp          # boilerplate C++ avec commentaires Doxygen
├── include/README        # répertoire pour les headers .h
├── lib/README            # répertoire pour les bibliothèques privées
├── .gitignore            # exclut .pio/, compile_commands.json, doxygen_output/
├── Makefile              # build, upload, monitor, flash, compiledb, doxygen
├── Doxyfile              # documentation API C/C++ (Doxygen)
├── README.md             # tableau matériel + instructions d'utilisation
└── .zed/
    ├── settings.json     # clangd comme LSP C/C++
    └── tasks.json        # 7 tâches PlatformIO + Doxygen
```

---

## Installation

### Prérequis

- `uv` installé — vérifier : `uv --version`
- Le dépôt `alm_tools` cloné sur la machine : `~/alm_tools/`

Si `uv` est absent :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Puis redémarrer le terminal
```

### Ce que fait `uv tool install`

`uv tool install` crée un **environnement Python isolé** pour pioinit et ses
dépendances, puis pose un **shim** — un petit fichier exécutable — dans
`~/.local/bin/pioinit`. Ce shim est le seul fichier visible dans votre PATH ;
il redirige vers le vrai programme dans l'environnement isolé.

```
Vous tapez : pioinit . --board uno
     ↓
Votre shell cherche "pioinit" dans le PATH
     ↓
Il trouve : ~/.local/bin/pioinit        ← le shim
     ↓
Le shim appelle l'environnement isolé   ← ~/.local/share/uv/tools/pioinit/
     ↓
pioinit s'exécute
```

### Étape 1 — Vérifier que `~/.local/bin` est dans le PATH

```bash
echo $PATH | tr ':' '\n' | grep local/bin
```

Si ce répertoire n'apparaît pas, ajoutez cette ligne dans `~/.bashrc` :

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Puis rechargez le shell :

```bash
source ~/.bashrc
```

### Étape 2 — Installer pioinit

```bash
cd ~/alm_tools/cli/pioinit
uv tool install .
```

Sortie attendue :

```
Installed 1 executable: pioinit
```

### Étape 3 — Vérifier l'installation

```bash
which pioinit
# /home/votre-nom/.local/bin/pioinit

pioinit --version
# pioinit 0.1.0

pioinit --help
```

Si `which pioinit` ne retourne rien, le shim n'est pas dans le PATH —
revérifiez l'étape 1.

### Mettre à jour

Après un `git pull` sur `alm_tools` :

```bash
cd ~/alm_tools/cli/pioinit
uv tool install --no-cache .
pioinit --version
```

!!! warning "Toujours utiliser `--no-cache`"
    `uv tool install --force` réutilise le wheel mis en cache par uv et
    **n'installe pas les modifications du code source**. L'option `--no-cache`
    force un rebuild complet du wheel depuis les sources — indispensable après
    toute modification de pioinit.

### Désinstaller

```bash
uv tool uninstall pioinit
```

Cela supprime le shim (`~/.local/bin/pioinit`) et l'environnement isolé.
Votre machine retrouve son état initial.

### Consulter les outils installés via uv

```bash
uv tool list
# pioinit v0.1.0
#  - pioinit
```

---

## Cartes supportées (détection automatique)

Pour ces cartes, la plateforme et la vitesse du moniteur série sont déduites
automatiquement — aucune option supplémentaire requise.

| Board ID | Carte | Plateforme | Moniteur |
|----------|-------|-----------|---------|
| `uno` | Arduino Uno | `atmelavr` | 9600 |
| `nano` | Arduino Nano | `atmelavr` | 9600 |
| `nano_every` | Arduino Nano Every | `megaavr` | 9600 |
| `mega2560` | Arduino Mega 2560 | `atmelavr` | 9600 |
| `leonardo` | Arduino Leonardo | `atmelavr` | 9600 |
| `micro` | Arduino Micro | `atmelavr` | 9600 |
| `esp32dev` | ESP32 DevKit | `espressif32` | 115200 |
| `esp32-s3-devkitc-1` | ESP32-S3 DevKitC-1 | `espressif32` | 115200 |
| `esp32-c3-devkitm-1` | ESP32-C3 DevKitM-1 | `espressif32` | 115200 |
| `lolin32` | WEMOS LOLIN32 | `espressif32` | 115200 |
| `nodemcuv2` | NodeMCU v2 (ESP8266) | `espressif8266` | 115200 |
| `d1_mini` | WEMOS D1 Mini (ESP8266) | `espressif8266` | 115200 |
| `pico` / `rpipico` | Raspberry Pi Pico | `raspberrypi` | 115200 |
| `nucleo_f401re` | STM32 Nucleo F401RE | `ststm32` | 115200 |
| `nucleo_f103rb` | STM32 Nucleo F103RB | `ststm32` | 115200 |
| `blackpill_f103c8` | STM32 Black Pill F103C8 | `ststm32` | 115200 |
| `teensy40` | Teensy 4.0 | `teensy` | 115200 |
| `teensy41` | Teensy 4.1 | `teensy` | 115200 |

Pour toute carte hors catalogue, utilisez `--platform` :

```bash
pioinit mon-projet --board my_custom_board --platform atmelavr
```

---

## Page suivante

<div class="grid cards" markdown>

-   :material-book-open-page-variant-outline: **[Guide d'utilisation](utilisation.md)**

    Workflow complet, Makefile, Zed, réinstallation.

</div>
