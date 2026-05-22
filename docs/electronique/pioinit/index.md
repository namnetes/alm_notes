# pioinit

**pioinit** est un générateur de projets PlatformIO embarqués.
Une seule commande crée la structure complète d'un projet :
code C/C++, Makefile, configuration Zed, et documentation Doxygen.

!!! tip "Analogie avec devinit"
    pioinit est à l'électronique ce que `devinit` est au Python :
    un initialiseur de projet opinionné qui applique les standards du dépôt.

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
cd ~/alm_tools/pioinit
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
cd ~/alm_tools/pioinit
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

| Board ID | Plateforme | Moniteur |
|----------|-----------|---------|
| `uno` | `atmelavr` | 9600 |
| `nano` | `atmelavr` | 9600 |
| `mega2560` | `atmelavr` | 9600 |
| `esp32dev` | `espressif32` | 115200 |
| `nodemcuv2` | `espressif8266` | 115200 |
| `d1_mini` | `espressif8266` | 115200 |
| `pico` | `raspberrypi` | 115200 |
| `nucleo_f401re` | `ststm32` | 115200 |
| `teensy40` | `teensy` | 115200 |

Pour toute carte hors catalogue, utilisez `--platform` :

```bash
pioinit mon-projet --board my_custom_board --platform atmelavr
```

---

## Page suivante

| Page | Contenu |
|------|---------|
| [Guide d'utilisation](utilisation.md) | Workflow complet, Makefile, Zed, réinstallation |
