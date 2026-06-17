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

### Demandes à la commande

!!! note "Message envoyé au fabricant"
    - Vérification de l'écran (pixels morts) avant expédition.
    - Usage prévu : IA, développement intensif sous Linux, virtualisation (VMs)
      — optimisation du BIOS demandée (VT-x/AMD-V activé, options inutiles
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
| NPU XDNA2 (50 TOPS) | Partiel — driver `amdxdna` stabilisé seulement à partir du noyau 6.10 (HWE requis) | Plus mature (noyau ~6.17+), mais écosystème logiciel encore jeune | Complet via la pile "Ryzen AI Software" (Copilot+) |

!!! note "Détails"
    - **CPU** : architecture x86 standard (4 cœurs Zen 5 + 8 cœurs Zen 5c),
      le scheduler Linux gère nativement les 12 cœurs / 24 threads dès le
      noyau 6.8 — aucune perte de performance par rapport à Windows.
    - **iGPU** : Ubuntu 24.04 LTS (même avec la pile HWE) reste en retrait
      par rapport à Ubuntu 26.04 LTS (noyau plus récent + Mesa 26.0),
      notamment sur le ray-tracing Vulkan. Windows 11 dispose du pilote
      AMD officiel complet dès la sortie de la puce.
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
