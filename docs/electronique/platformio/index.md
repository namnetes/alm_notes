# PlatformIO

PlatformIO est une **chaîne de compilation universelle** pour microcontrôleurs.
Là où l'IDE Arduino ne supporte que les cartes Arduino, PlatformIO supporte plus de
**1 000 cartes** (Arduino, ESP32, STM32, Raspberry Pi Pico, etc.) avec une interface
unique et cohérente.

!!! tip "Pas besoin de VS Code"
    PlatformIO est souvent présenté comme une extension VS Code, mais son cœur —
    **PlatformIO Core** — est un outil en ligne de commande (`pio`) indépendant de tout
    éditeur. C'est ce que nous allons utiliser ici, avec une intégration dans Zed Editor.

---

## Pourquoi PlatformIO plutôt que l'IDE Arduino ?

| Critère | IDE Arduino | PlatformIO CLI |
|---------|-------------|----------------|
| Cartes supportées | Arduino principalement | 1 000+ cartes |
| Intégration éditeur | IDE dédié ou VS Code | N'importe quel éditeur |
| Gestion des bibliothèques | Manuel | `pio pkg install` |
| Build reproductible | Non | Oui (`platformio.ini`) |
| Autocomplétion C/C++ | Limitée | Complète via `clangd` |
| Ligne de commande | Non | Oui (`pio run`, `pio device monitor`) |

---

## Concepts fondamentaux

Avant d'installer quoi que ce soit, voici les quatre concepts clés de PlatformIO :

### Platform

La **platform** (plateforme) est la famille de microcontrôleurs.
Elle contient le compilateur, le chargeur de programme (uploader) et les outils bas niveau.

Exemples : `atmelavr` (Arduino Uno), `espressif32` (ESP32), `ststm32` (STM32).

### Board

La **board** (carte) est votre matériel physique précis.
Une platform peut contenir des centaines de boards différentes.

Exemples : `uno` (Arduino Uno), `esp32dev` (ESP32 DevKit), `nucleo_f401re` (STM32 Nucleo).

### Framework

Le **framework** est la bibliothèque de haut niveau qui abstrait le matériel.

Exemples : `arduino` (le plus courant), `espidf` (SDK natif Espressif), `cmsis` (ARM bas niveau).

### Environment (`platformio.ini`)

L'**environment** est la configuration d'un projet, définie dans `platformio.ini`.
Un projet peut avoir plusieurs environments (ex : une config pour l'Arduino Uno et une pour l'ESP32).

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
```

---

## Installation

### Prérequis

- `uv` installé — si ce n'est pas le cas :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Puis redémarrer le terminal
```

### Installer PlatformIO Core

`uv tool install` installe PlatformIO dans un environnement isolé et l'expose
dans le `PATH`, exactement comme `pipx` — mais sans dépendance supplémentaire.

```bash
uv tool install platformio
```

Vérifier que l'installation a fonctionné :

```bash
pio --version
# PlatformIO Core, version 6.x.x
```

!!! note "Mise à jour"
    Pour mettre à jour PlatformIO plus tard :
    ```bash
    uv tool upgrade platformio
    ```

### Première utilisation : installer une platform

Lors du premier projet, PlatformIO télécharge automatiquement la platform nécessaire.
Vous pouvez aussi l'installer manuellement :

```bash
# Pour Arduino Uno
pio pkg install --global --tool toolchain-atmelavr

# Lister les platforms installées
pio platform list
```

---

## Pages suivantes

| Page | Contenu |
|------|---------|
| [Premier projet](premier-projet.md) | Créer, compiler, uploader et déboguer un projet pas à pas |
| [Intégration Zed](zed.md) | Autocomplétion C/C++ et tâches de build dans Zed Editor |
