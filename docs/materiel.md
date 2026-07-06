# Matériel

Ma configuration personnelle sous Linux.

## TUXEDO InfinityBook Pro 14 — Gen10 AMD

!!! info "Commande"
    | Champ | Valeur |
    |---|---|
    | N° de commande | 1125051696 |
    | Date de commande | 18 octobre 2025 |
    | Numéro de série | 2510SN02114 |
    | Statut | Livré (UPS, tracking `1ZEW3266DK43565742`) |
    | Expédition | 13 novembre 2025 |
    | Garantie | 2 ans (pièces, main d'œuvre, transport) |
    | Prix total | 2 136,81 € (dont TVA 20 % : 356,13 €) |

### Configuration

| Composant | Détail |
|---|---|
| Écran | Omnia Display 3K (2880×1800), 16:10, jusqu'à 120 Hz, 500 nits |
| Couleur | Infinity gray |
| Processeur | AMD Ryzen AI 9 HX 370 (12 cœurs / 24 threads, jusqu'à 5,1 GHz, 36 Mo cache) |
| RAM | 128 Go (2×64 Go) DDR5 5600 MHz Crucial |
| Stockage | 2× 2 To Samsung 990 PRO (NVMe PCIe 4.0) |
| Clavier | FR AZERTY rétroéclairé, touche TUX |
| Wi-Fi / Bluetooth | Intel Wi-Fi 6 AX210 (802.11ax, 2,4 & 5 GHz) / Bluetooth 5.3 |
| OS livré | Ubuntu 24.04 (sans Windows) |

### Fiche technique détaillée

#### Écran

| Caractéristique | Valeur |
|---|---|
| Dalle | IPS Omnia, 14", 16:10, mate (anti-reflet) |
| Angles de vision | 89°/89°/89°/89° |
| Taux de rafraîchissement | 60 Hz / 120 Hz |
| Résolution | 2880 × 1800 px |
| Gamut sRGB | 100 % |
| Luminosité | 500 nits |
| Contraste | 1500:1 |
| PWM | Aucun (pas de scintillement) |
| Angle d'ouverture | ~180° |

!!! note "Bandes lumineuses sur les bords"
    Les dalles IPS modernes présentent des zones plus lumineuses sur le
    pourtour de l'écran — c'est une caractéristique normale, présente chez
    tous les fabricants, sans réel impact en usage quotidien (les écrans
    sont optimisés pour un usage en lumière du jour).

#### Châssis

| Caractéristique | Valeur |
|---|---|
| Capot, base, dessous | Aluminium |
| Cadre d'écran | Plastique |
| Couleur | Infinity gray |
| Dimensions | 311 × 17 × 220 mm (L × H × P) |
| Poids | 1,45 kg (batterie incluse) |

!!! tip "Maintenabilité"
    Après dépose des vis du panneau inférieur, la RAM, la carte Wi-Fi, les
    SSD et les ventilateurs sont facilement accessibles — entretien et
    remplacement aisés.

#### Clavier et pavé tactile

- Clavier rubberdome (membrane), silencieux
- Rétroéclairage blanc, luminosité réglable et désactivable au clavier
- Touche TUX (super-key) sur tous les layouts
- Pavé tactile en verre, précision, 123 × 77,5 mm, boutons intégrés,
  multi-gestes et défilement

#### Sécurité

- Kensington Lock
- Cache webcam physique (shutter)
- Wi-Fi et Bluetooth désactivables directement depuis l'UEFI (*Unified
  Extensible Firmware Interface* — le successeur du BIOS)
- TPM 2.0 (*Trusted Platform Module*, ici en version fTPM — implémentation
  logicielle/firmware plutôt que puce physique dédiée), activable/
  désactivable depuis l'UEFI
- Secure Boot, activable/désactivable depuis l'UEFI

!!! tip "Accéder au BIOS/UEFI ou au menu de démarrage"
    D'après la documentation officielle TUXEDO, juste après la mise sous
    tension :

    - **BIOS/UEFI** : presser **F2** (ou **Échap/ESC** selon le modèle) de
      façon répétée jusqu'à l'entrée dans le setup.
    - **Menu de démarrage** (choix du périphérique de boot, ex. clé USB) :
      presser **F7** (ou **Suppr/DEL**) de façon répétée jusqu'à
      l'apparition du menu.

    La touche exacte peut varier légèrement selon le modèle / la révision
    du firmware — si aucune de ces touches ne fonctionne, se référer au
    manuel du modèle précis ou au support TUXEDO. À noter aussi : pendant
    la mise à jour du BIOS, TUXEDO précise qu'un clavier en disposition
    anglaise (QWERTY) est utilisé — les touches Y et Z sont inversées par
    rapport à l'AZERTY.

    Procédure complète de mise à jour : voir
    [Mise à jour du BIOS/UEFI et de l'EC](mise-a-jour-bios-ec.md).

#### Batterie et alimentation

| Caractéristique | Valeur |
|---|---|
| Batterie | 80 Wh, Lithium polymère, vissée (non amovible) |
| Alimentation | 150 W \| 20 V / 7,5 A \| USB-C Power Delivery DC-In |
| Dimensions bloc secteur | 114 × 65 × 23 mm, ~500 g câble inclus |
| Autonomie annoncée | Jusqu'à 7 h (streaming vidéo, Wi-Fi on / BT off, 60 Hz, luminosité 50 %, rétroéclairage clavier off, iGPU) |

#### Processeur

Gamme disponible sur ce modèle — **AMD Ryzen AI 9 HX 370** est le processeur
de ma configuration. Colonnes **TDP** (*Thermal Design Power*, l'enveloppe
de puissance/chaleur dissipée) et **NPU** (*Neural Processing Unit*, un
processeur dédié aux calculs d'IA) :

| Processeur | Cœurs / Threads | Fréquence max | Cache L3 | TDP | NPU |
|---|---|---|---|---|---|
| AMD Ryzen 7 H 255 | 8 / 16 | 4,9 GHz | 16 Mo | 25–65 W* | Non |
| AMD Ryzen AI 7 350 | 8 / 16 | 5 GHz | 16 Mo | 25–65 W* | Oui |
| AMD Ryzen AI 9 365 | 10 / 20 | 5 GHz | 24 Mo | 25–65 W* | Oui |
| **AMD Ryzen AI 9 HX 370** (le mien) | 12 / 24 | 5,1 GHz | 24 Mo | 25–65 W* | Oui |

\* Limites de puissance réglables en 3 paliers (25 W / 35 W / 65 W) via le
TUXEDO Control Center.

Pâte thermique : Honeywell PTM7958.

#### Carte graphique

GPU intégré au CPU, selon le modèle de processeur — **Radeon 890M**
correspond à ma configuration (HX 370) :

| Processeur associé | GPU intégré | Cœurs GPU | Fréquence max |
|---|---|---|---|
| Ryzen 7 H 255 | Radeon 780M | 12 | 2,7 GHz |
| Ryzen AI 7 350 | Radeon 860M | 8 | 3 GHz |
| Ryzen AI 9 365 | Radeon 880M | 12 | 2,9 GHz |
| **Ryzen AI 9 HX 370** (le mien) | **Radeon 890M** | 16 | 2,9 GHz |

Jusqu'à 4 écrans simultanés (écran interne + 3 externes) :

- 1× écran interne
- 1× HDMI 2.1
- 2× USB-C (DisplayPort)

| Sortie | Résolution max |
|---|---|
| HDMI 2.0 | 3840 × 2160 @ 60 Hz |
| HDMI 2.1 | 3840 × 2160 @ 120 Hz |
| DisplayPort 1.4a (32,4 Gbit/s) | 7680 × 4320 @ 60 Hz ou 3840 × 2160 @ 120 Hz |
| DisplayPort 2.1 | 7680 × 4320 @ 85 Hz ou 2× 3840 × 2160 @ 60 Hz |

#### Mémoire et stockage

| Caractéristique | Valeur |
|---|---|
| Mémoire | DDR5-5600 MHz, 2 emplacements, max. 128 Go, dual channel |
| Stockage | 2× M.2 2280 NVMe (PCIe 4.0 x4) |

#### Communication / réseau

| Interface | Détail |
|---|---|
| LAN filaire | 1 Gigabit (Motorcomm YT6801, 10/100/1000 Mbit/s) |
| Wi-Fi (le mien) | Intel Wi-Fi 6 AX210, M.2 2230, 802.11 ax/a/b/g/n, 2,4 & 5 GHz, 2×2, jusqu'à 2,4 Gbit/s (5 GHz) |
| Bluetooth (le mien) | 5.3, intégré à l'AX210 |
| Wi-Fi (option) | AMD RZ616 / MediaTek MT7922, M.2 2230, 802.11 ax/a/b/g/n, 2,4 / 5 / **6 GHz**, 2×2, jusqu'à 2,4 Gbit/s |
| Bluetooth (option) | 5.2, intégré au RZ616 / MT7922 |

!!! note "Bande 6 GHz (Wi-Fi 6E)"
    La bande 6 GHz n'est disponible que sur le module optionnel AMD RZ616 /
    MediaTek MT7922 — l'Intel AX210 (mon module) ne couvre que 2,4 et 5 GHz.

#### Webcam et audio

- Webcam 2 Mpx (1920 × 1080), avec cache obturateur physique
- Caméra infrarouge pour reconnaissance faciale
- Audio HD, 2 haut-parleurs intégrés
- Microphone intégré avec réduction de bruit

#### Ports

**Côté gauche** (de gauche à droite) :

- Kensington Lock NanoSaver
- USB-A 2.0 (480 Mbit/s)
- USB-C 3.2 Gen2 (10 Gbit/s, DisplayPort 1.4a, Power Delivery DC-In*)
- Jack audio 2-en-1 (casque + micro)

**Côté droit** (de gauche à droite) :

- Lecteur de carte full-size (SD/SDHC/SDXC/SD Express/UHS-II)
- 2× USB-A 3.2 Gen1

**Côté arrière** (de gauche à droite) :

- HDMI 2.1 sous Windows (32 Gbit/s, max 4K/120Hz) — HDMI 2.0b sous Linux
  (18 Gbit/s, max 4K/60Hz)
- USB4 (40 Gbit/s, DisplayPort 2.1, Power Delivery DC-In*, **DC-Out : 15 W
  max (5 V / 3 A)**)
- RJ45 1 Gbit (LAN)

\* Minimum 20 V / 3 A (60 W) | Recommandé / maximum 20 V / 5 A (100 W).

!!! tip "Port USB qui alimente un appareil même PC éteint ?"
    Le port **USB4** (face arrière) dispose d'une sortie **DC-Out de 15 W
    max (5 V / 3 A)**, distincte de l'entrée Power Delivery — c'est ce type
    de port qui permet en général de recharger un appareil externe (téléphone,
    écouteurs...) même PC éteint ou en veille, comme les ports USB-C
    « always-on » / « power share » sur d'autres machines. La fiche
    technique TUXEDO ne précise toutefois pas explicitement ce comportement
    à l'arrêt complet — à confirmer dans le BIOS/UEFI (option souvent
    nommée *USB Power Share* ou équivalente) ou auprès du support TUXEDO si
    besoin de certitude avant usage.

!!! note "USB4 = équivalent Thunderbolt sur plateforme AMD"
    Le port **USB4** (face arrière) est l'équivalent fonctionnel de
    Thunderbolt sur cette plateforme AMD, sans porter le badge propriétaire
    Intel.

    | Caractéristique | USB4 (ce port) | Thunderbolt 4 (Intel) |
    |---|---|---|
    | Norme de base | USB4 (intègre le protocole Thunderbolt 3) | Thunderbolt 4 |
    | Bande passante | 40 Gbit/s | 40 Gbit/s |
    | Tunneling vidéo | DisplayPort 2.1, jusqu'à 7680×4320 @ 85 Hz | DisplayPort |
    | Tunneling PCIe | Oui (en théorie : eGPU, docks haut débit) | Oui, garanti par certification |
    | Power Delivery | DC-In (charge du PC) + **DC-Out 15 W max** (5 V / 3 A) | Charge garantie ≥ 15 W |
    | Daisy-chaining | Non garanti | Garanti par certification |
    | Certification "Thunderbolt" | **Non** — programme propriétaire Intel, non accessible aux plateformes AMD | Oui |

    En pratique, ce port reste compatible avec la grande majorité des
    accessoires et docks Thunderbolt 3/4 (vidéo, données, charge), mais sans
    les garanties strictes du programme de certification Intel (eGPU,
    daisy-chain, débit minimal assuré sur toute la chaîne).

#### Lecteur de carte SD

| Caractéristique | Valeur |
|---|---|
| Modèle | Genesys Logic GL9767 |
| SD Express | jusqu'à 900/500 Mo/s |
| SDXC UHS-II | jusqu'à 270/230 Mo/s |

#### Refroidissement

| Caractéristique | Valeur |
|---|---|
| Ventilateurs | 2 × 47 mm × 7 mm |
| Caloducs | 2 |
| Capacité de refroidissement (CPU + GPU, 100 % ventilateurs) | 65 W |

Ventilation thermo-régulée : à faible charge, les ventilateurs ralentissent
ou s'arrêtent. Le TUXEDO Control Center permet de personnaliser performance
et comportement des ventilateurs — y compris un mode quasi passif (sans
bruit) en réduisant fortement la performance.

### Demandes à la commande

!!! note "Message envoyé au fabricant"
    - Vérification de l'écran (pixels morts) avant expédition.
    - Usage prévu : IA, développement intensif sous Linux, virtualisation (VMs)
      — optimisation du BIOS demandée (VT-x/AMD-V — les technologies de
      virtualisation matérielle Intel/AMD — activé, options inutiles
      désactivées).
    - Usage mobile (voiture, extérieur) — vérification de la luminosité
      maximale.

### Historique de commande

| Date | Étape |
|---|---|
| 18.10.2025 | Ouverte |
| 22.10.2025 | En préparation |
| 23.10.2025 | En production |
| 13.11.2025 | Expédiée (UPS) |

### Exploitation du AMD Ryzen AI 9 HX 370 selon l'OS

La puce combine trois blocs distincts (CPU, iGPU, NPU), chacun avec un niveau
de support différent selon l'OS et la version du noyau.

| Bloc | Ubuntu 24.04 LTS | Ubuntu 26.04 LTS | Windows 11 |
|---|---|---|---|
| CPU (12 cœurs / 24 threads) | 100 % — noyau ≥ 6.8 suffit | 100 % | 100 % |
| iGPU Radeon 890M (RDNA 3.5) | Bon (certifié, ex. ThinkPad P16s Gen 4) | Meilleur — gains significatifs vs 24.04 (Mesa 26.0, surtout en Vulkan ray-tracing) | Complet depuis le lancement |
| NPU XDNA2 (50 TOPS — *Tera Operations Per Second*, une mesure de puissance de calcul IA) | Partiel — driver `amdxdna` stabilisé seulement à partir du noyau 6.10 (HWE requis) | Plus mature (noyau ~6.17+), mais écosystème logiciel encore jeune | Complet via la pile "Ryzen AI Software" (Copilot+) |

!!! note "Détails"
    - **CPU** : architecture x86 standard (4 cœurs Zen 5 + 8 cœurs Zen 5c),
      le scheduler Linux gère nativement les 12 cœurs / 24 threads dès le
      noyau 6.8 — aucune perte de performance par rapport à Windows.
    - **iGPU** (GPU intégré, ici architecture RDNA 3.5 — *Radeon DNA*) :
      Ubuntu 24.04 LTS (même avec la pile HWE — *Hardware Enablement*, qui
      apporte un noyau et des pilotes plus récents sur une base LTS) reste
      en retrait par rapport à Ubuntu 26.04 LTS (noyau plus récent + Mesa
      26.0), notamment sur le ray-tracing Vulkan. Windows 11 dispose du
      pilote AMD officiel complet dès la sortie de la puce.
    - **NPU** : c'est le point faible sous Linux. Le driver `amdxdna` est
      bien mainliné, mais le support XDNA2 (la génération du HX 370) ne
      s'est stabilisé qu'à partir du noyau 6.10 — Ubuntu 24.04 par défaut
      (noyau 6.8) n'en bénéficie pas pleinement, il faut la pile HWE
      (24.04.1+, noyau 6.11+). Ubuntu 26.04 est nettement plus mature sur
      ce point, sans toutefois atteindre la complétude logicielle de
      "Ryzen AI Software" sous Windows 11 (accélération native dans les
      fonctionnalités Copilot+).
    - **Conclusion pratique** : pour exploiter au mieux la puce sous Linux,
      privilégier Ubuntu 26.04 LTS (ou a minima 24.04 avec la pile HWE et
      un noyau ≥ 6.11) plutôt que l'installation par défaut de 24.04 LTS.

    Sources :

    - [AMD Ryzen AI 9 HX 370 NPU in Linux: Introduction](https://www.linuxlinks.com/amd-ryzen-ai-9-hx-370-npu-linux/)
    - [Ubuntu 26.04 Delivers Great Performance Improvements For AMD Strix Point — Phoronix](https://www.phoronix.com/review/ubuntu-2604-strix-point)
    - [Lenovo ThinkPad P16s Gen 4 AMD certified with Ubuntu 24.04 LTS](https://ubuntu.com/certified/202503-36575/24.04%20LTS)
    - [Ubuntu 26.04 shows significant graphics performance gains on AMD Strix Point](https://www.igorslab.de/en/ubuntu-26-04-shows-significant-graphics-performance-gains-on-the-amd-strix-point-not-due-to-new-hardware-but-because-the-software-has-finally-caught-up/)
