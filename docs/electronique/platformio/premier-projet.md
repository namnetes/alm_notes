# Premier projet pas à pas

Ce tutoriel vous guide de zéro jusqu'à faire clignoter une LED sur un **Arduino Uno**.
C'est le "Hello World" de l'électronique embarquée — simple, mais il valide toute
la chaîne : compilation, transfert sur la carte, et communication série.

!!! info "Matériel nécessaire"
    - Un Arduino Uno (ou compatible)
    - Un câble USB-B (le câble carré côté Arduino)
    - Un ordinateur avec PlatformIO installé (voir [Installation](index.md))

---

## 1. Créer un nouveau projet

Choisissez un répertoire de travail et créez un dossier pour votre projet :

```bash
mkdir ~/projets/blink-led
cd ~/projets/blink-led
pio project init --board uno
```

PlatformIO crée automatiquement la structure du projet et télécharge la platform
`atmelavr` si elle n'est pas encore installée (patientez lors du premier lancement).

---

## 2. Comprendre la structure du projet

```text
blink-led/
├── platformio.ini   # Configuration du projet (carte, framework, options)
├── src/             # Votre code source
│   └── main.cpp     # Fichier principal (créez-le, il est vide au départ)
├── include/         # Vos fichiers d'en-tête (.h) personnels
├── lib/             # Bibliothèques privées au projet
└── .pio/            # Fichiers générés par PlatformIO (ne pas modifier)
```

### Le fichier `platformio.ini`

Ouvrez `platformio.ini` — il contient déjà la configuration de base :

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
```

| Clé | Signification |
|-----|---------------|
| `[env:uno]` | Nom de l'environment (vous choisissez librement) |
| `platform` | Famille de microcontrôleurs (ici AVR d'Atmel) |
| `board` | Carte précise (ici Arduino Uno) |
| `framework` | Bibliothèque haut niveau (ici Arduino) |

---

## 3. Écrire le code

Créez le fichier `src/main.cpp` avec ce contenu :

```cpp
#include <Arduino.h>

void setup() {
    // pinMode configure la broche 13 comme une sortie.
    // La broche 13 est connectée à la LED intégrée sur l'Arduino Uno.
    pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    digitalWrite(LED_BUILTIN, HIGH);  // LED allumée
    delay(1000);                      // Attendre 1 seconde
    digitalWrite(LED_BUILTIN, LOW);   // LED éteinte
    delay(1000);                      // Attendre 1 seconde
}
```

!!! note "Différence avec l'IDE Arduino"
    Avec PlatformIO, il faut ajouter `#include <Arduino.h>` en haut du fichier.
    L'IDE Arduino l'inclut silencieusement ; PlatformIO est plus explicite.

---

## 4. Compiler le projet

```bash
pio run
```

PlatformIO compile le code et affiche le résultat :

```text
Building in .pio/build/uno
Compiling .pio/build/uno/src/main.cpp.o
Linking .pio/build/uno/firmware.elf
Building .pio/build/uno/firmware.hex
RAM:   [=         ]  6.8% (used 140 bytes from 2048 bytes)
Flash: [=         ]  3.2% (used 1040 bytes from 32256 bytes)
```

Les deux dernières lignes indiquent l'espace mémoire utilisé :

- **RAM** — mémoire volatile (variables, pile d'exécution)
- **Flash** — mémoire permanente (le programme lui-même)

---

## 5. Brancher et identifier la carte

Branchez l'Arduino Uno avec le câble USB. Vérifiez que Linux l'a bien détecté :

```bash
pio device list
```

Exemple de sortie :

```text
/dev/ttyACM0
------------
Hardware ID: USB VID:PID=2341:0043
Description: Arduino Uno
```

!!! warning "Droits d'accès au port série"
    Si la commande ne retourne rien ou si l'upload échoue avec une erreur de permission,
    votre utilisateur n'est pas dans le groupe `dialout` :

    ```bash
    sudo usermod -aG dialout $USER
    # Puis déconnectez-vous et reconnectez-vous pour appliquer
    ```

### Découvrir son matériel quand la détection automatique échoue

Si `pio device list` ne retourne rien ou si vous ne savez pas quel port utiliser,
voici comment investiguer au niveau du système.

**Étape 1 — Vérifier que le système voit la carte**

Débranchez la carte, puis rebranchez-la. Immédiatement après :

```bash
dmesg | tail -20
```

Cherchez une ligne comme :

```text
usb 1-2: new full-speed USB device number 5 using xhci_hcd
usb 1-2: New USB device found, idVendor=2341, idProduct=0043
cdc_acm 1-2:1.0: ttyACM0: USB ACM device
```

Le `ttyACM0` à la fin est votre port. Notez-le.

**Étape 2 — Identifier la carte avec `lsusb`**

```bash
lsusb
```

Chaque ligne correspond à un périphérique USB. Cherchez votre carte :

```text
Bus 001 Device 005: ID 2341:0043 Arduino SA Uno R3 (CDC ACM)
```

Le format est `idVendor:idProduct`. Les identifiants courants :

| Identifiant | Carte |
|-------------|-------|
| `2341:0043` | Arduino Uno (puce ATmega16U2) |
| `2341:0001` | Arduino Uno (puce FTDI) |
| `10c4:ea60` | ESP32 via CP2102 |
| `1a86:7523` | ESP32 / ESP8266 via CH340 |
| `0403:6001` | Clone Arduino via FTDI FT232 |

**Étape 3 — Lister les ports série disponibles**

```bash
ls -la /dev/tty{ACM,USB}* 2>/dev/null
```

Exemple :

```text
crw-rw---- 1 root dialout 166, 0 mai 22 14:31 /dev/ttyACM0
```

**Étape 4 — Forcer le port dans `platformio.ini`**

Si PlatformIO ne détecte pas automatiquement le port, forcez-le :

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
upload_port = /dev/ttyACM0
monitor_port = /dev/ttyACM0
monitor_speed = 9600
```

!!! tip "Cartes avec puce CH340 (clones chinois)"
    Les clones Arduino bon marché utilisent souvent la puce CH340.
    Vérifiez qu'elle est reconnue :
    ```bash
    lsmod | grep ch341
    # Si rien n'apparaît, le module n'est pas chargé
    sudo modprobe ch341
    ```
    Sur Ubuntu récent, le module est inclus dans le noyau et chargé automatiquement.

---

## 6. Uploader le programme sur la carte

```bash
pio run --target upload
```

PlatformIO compile (si nécessaire) puis transfère le programme :

```text
Uploading .pio/build/uno/firmware.hex
avrdude: AVR device initialized and ready to accept instructions
avrdude: writing flash (1040 bytes):
avrdude: 1040 bytes of flash written
avrdude done.  Thank you.
```

La LED orange sur l'Arduino Uno clignote pendant le transfert, puis votre LED se
met à clignoter une fois par seconde.

---

## 7. Moniteur série

Le moniteur série permet de **lire les messages** envoyés par la carte et de **lui
envoyer des données**. C'est votre outil de débogage principal.

Ajoutez une sortie série dans votre code :

```cpp
#include <Arduino.h>

void setup() {
    Serial.begin(9600);    // Démarre la communication série à 9600 bauds
    pinMode(LED_BUILTIN, OUTPUT);
}

void loop() {
    Serial.println("LED allumée");
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);

    Serial.println("LED éteinte");
    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
}
```

Re-compilez, uploadez, puis ouvrez le moniteur :

```bash
pio run --target upload && pio device monitor --baud 9600
```

Vous verrez s'afficher :

```text
--- Terminal on /dev/ttyACM0 | 9600 8-N-1
LED allumée
LED éteinte
LED allumée
...
```

Appuyez sur ++ctrl+c++ pour quitter le moniteur.

!!! tip "Raccourci combiné"
    La commande suivante compile, uploade et ouvre le moniteur en une seule fois :
    ```bash
    pio run -t upload && pio device monitor
    ```

---

## 8. Gérer les bibliothèques

PlatformIO dispose d'un registre de bibliothèques. Pour chercher une bibliothèque :

```bash
pio pkg search "DHT sensor"
```

Pour l'installer dans votre projet :

```bash
pio pkg install --library "adafruit/DHT sensor library"
```

PlatformIO ajoute automatiquement la bibliothèque à `platformio.ini` :

```ini
[env:uno]
platform = atmelavr
board = uno
framework = arduino
lib_deps =
    adafruit/DHT sensor library@^1.4.6
```

!!! tip "Partager un projet"
    Grâce à `lib_deps`, n'importe qui peut récupérer votre projet et lancer `pio run` —
    PlatformIO téléchargera automatiquement les bibliothèques nécessaires.
    Il suffit de versionner `platformio.ini` mais **pas** le dossier `.pio/`.

---

## Récapitulatif des commandes essentielles

| Commande | Action |
|----------|--------|
| `pio project init --board uno` | Créer un projet pour Arduino Uno |
| `pio run` | Compiler |
| `pio run --target upload` | Compiler et uploader |
| `pio run --target clean` | Nettoyer les fichiers compilés |
| `pio device list` | Lister les cartes connectées |
| `pio device monitor` | Ouvrir le moniteur série |
| `pio pkg search <nom>` | Chercher une bibliothèque |
| `pio pkg install --library <nom>` | Installer une bibliothèque |

---

## Exemple avec un ESP32

Le processus est identique, seul `platformio.ini` change :

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
```

```bash
mkdir ~/projets/blink-esp32 && cd ~/projets/blink-esp32
pio project init --board esp32dev
# Puis même workflow : créer src/main.cpp, pio run, pio run -t upload
```

!!! note "Première fois avec ESP32"
    La platform `espressif32` pèse environ 300 Mo (compilateur + SDK).
    Le premier téléchargement prend quelques minutes.
