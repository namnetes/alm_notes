# pioinit

**pioinit** est un générateur de projets PlatformIO embarqués.
Une seule commande crée la structure complète d'un projet :
code C/C++, Makefile, configuration Zed, et documentation MkDocs + Doxygen.

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
├── .gitignore            # exclut .pio/, compile_commands.json, site/
├── Makefile              # build, upload, monitor, flash, compiledb,
│                         # doxygen, docs, docs-start, docs-stop, docs-build
├── pyproject.toml        # dépendances MkDocs uniquement (pas un projet Python)
├── mkdocs.yml            # documentation projet (Material theme)
├── Doxyfile              # documentation API C/C++ (Doxygen)
├── README.md             # tableau matériel + instructions d'utilisation
├── .zed/
│   ├── settings.json     # clangd comme LSP C/C++
│   └── tasks.json        # 9 tâches PlatformIO + docs
└── docs/
    ├── index.md
    ├── materiel.md       # composants et câblage
    ├── configuration.md  # platformio.ini expliqué
    └── stylesheets/
        └── extra.css
```

---

## Installation

### Prérequis

- `uv` installé (`uv --version`)
- Le dépôt `alm_tools` cloné sur la machine

### Installer pioinit

```bash
cd ~/alm_tools/pioinit
uv tool install .
```

Vérifier :

```bash
pioinit --version
# pioinit 0.1.0

pioinit --help
```

### Mettre à jour

```bash
cd ~/alm_tools/pioinit
git pull
uv tool install . --force
```

### Désinstaller

```bash
uv tool uninstall pioinit
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
