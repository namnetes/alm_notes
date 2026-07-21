# FAQ TUXEDO InfinityBook Pro 14 — Gen10 AMD

!!! info "Points importants"
    - Support clavier **N-Key Rollover incomplet** — certaines combinaisons
      Fn ne fonctionnent pas, limitation matérielle sans solution logicielle
      (voir [ci-dessous](#pourquoi-certaines-combinaisons-fn-ne-fonctionnent-pas)).
    - **Noyau recommandé : 6.17 ou plus récent** pour une distribution
      personnalisée — voir [Version de noyau recommandée](#version-de-noyau-recommandee)
      et [installation WebFAI](https://www.tuxedocomputers.com/en/TUXEDO-WebFAI.tuxedo).
    - Bande **Wi-Fi 6 GHz (Wi-Fi 6E) non supportée** avec le module Intel
      AX210 associé à un CPU AMD — voir
      [Wi-Fi 6E](#pourquoi-les-appareils-amd-ne-supportent-pas-le-wi-fi-6e-6-ghz).
    - Pilote **LAN Motorcomm YT6801** absent de certaines distributions —
      packages `.deb`/`.rpm` fournis ci-dessous, voir
      [Pilote pour chipset LAN](#pilote-pour-chipset-lan-motorcomm-yt6801).
    - Voir aussi la page [Matériel](materiel.md) (configuration détaillée)
      et [Mise à jour du BIOS/UEFI et de l'EC](mise-a-jour-bios-ec.md).

Traduction de la FAQ officielle TUXEDO pour le
[TUXEDO InfinityBook Pro 14 — Gen10 AMD](https://www.tuxedocomputers.com/en/FAQ-TUXEDO-InfinityBook-Pro-14-Gen10-AMD.tuxedo),
modèle correspondant à la configuration décrite sur la page
[Matériel](materiel.md).

## Pourquoi certaines combinaisons Fn ne fonctionnent pas ?

L'appareil ne supporte pas le *N-Key Rollover* complet (la capacité d'un
clavier à enregistrer un grand nombre de touches pressées simultanément). La
conception physique de la matrice de touches empêche l'enregistrement
simultané de certaines combinaisons multi-touches.

Les combinaisons courantes comme **Ctrl+Alt+Suppr** fonctionnent sans
problème. En revanche, des combinaisons comme **Fn+Tux+Haut/Bas** posent
problème : la touche Fn convertit Haut/Bas en Page Préc/Page Suiv, mais agit
également comme une touche indépendante, ce qui crée des conflits d'entrée.

!!! warning "Aucune solution technique"
    Il n'existe pas de solution technique à ce comportement. La limitation
    est matérielle et ne peut pas être résolue via des mises à jour du
    micrologiciel ou des pilotes. Aucune variante de clavier alternative
    n'est disponible pour ce modèle.

### Contournement sous KDE Plasma

Sous KDE Plasma, la gestion des fenêtres utilise typiquement Page
Préc/Page Suiv pour ancrer les fenêtres, alors que d'autres environnements
(GNOME, Windows) utilisent directement Tux+Haut/Bas. Dans TUXEDO OS,
Tux+Haut/Bas est utilisé par défaut pour ancrer les fenêtres à la moitié
supérieure ou inférieure de l'écran.

!!! tip "Réattribuer les raccourcis dans KDE"
    1. Ouvrir **Paramètres Système**.
    2. Naviguer vers **Clavier** › **Raccourcis** › **Gestion des fenêtres**.
    3. Ajuster :
        - *Maximize Window* › [Meta]+[Up]
        - *Minimize Window* › [Meta]+[Down]

## Version de noyau recommandée

Pour un fonctionnement optimal du portable, un noyau actuel doit être
utilisé.

**Recommandation : version 6.17 ou plus récente** pour une distribution
personnalisée — de nombreux ajustements de compatibilité sont déjà intégrés
dans le noyau standard à partir de cette version.

Les correctifs de compatibilité sont automatiquement appliqués via
l'[installation WebFAI](https://www.tuxedocomputers.com/en/TUXEDO-WebFAI.tuxedo)
de TUXEDO OS ou d'un Ubuntu optimisé par TUXEDO. Pour les autres
distributions, la stabilité maximale s'obtient avec un noyau récent.

## Problèmes connus avec d'autres distributions / anciens noyaux

!!! bug "Clavier interne inopérant après réveil de la veille"
    Affecte uniquement les appareils avec processeurs AMD. Le correctif a
    déjà été soumis en amont et est inclus dans le noyau principal depuis
    la version **6.17**.

    Pour les distributions autres que TUXEDO OS, ou les systèmes installés
    sans WebFAI, installer un noyau suffisamment récent. Sur un noyau plus
    ancien, les paramètres kernel suivants permettent de contourner le
    problème :

    ```text
    i8042.nomux i8042.reset i8042.noloop i8042.nopnp
    ```

!!! bug "Artefacts graphiques"
    Artefacts graphiques, par exemple lors du défilement dans l'interface
    utilisateur (comme dans le terminal).

!!! bug "CPU bloqué en mode basse consommation"
    Le CPU reste en permanence en mode basse consommation, quelle que soit
    la charge de travail.

## Pourquoi les appareils AMD ne supportent pas le Wi-Fi 6E (6 GHz) ?

Lorsqu'un processeur AMD est associé à un module Wi-Fi Intel, la bande
6 GHz n'est actuellement pas supportée.

**Raison** : Intel n'active pas cette plage de fréquences pour ses modules
Wi-Fi utilisés avec des CPU AMD. En conséquence, aucune certification
correspondante d'Intel et de la Wi-Fi Alliance ne peut être obtenue.

!!! note "Alternative technique"
    Le Wi-Fi 6E serait techniquement possible sur les systèmes AMD
    utilisant des modules Wi-Fi MediaTek, mais ceux-ci présentent leurs
    propres limitations et problèmes.

    Voir aussi la section [Wi-Fi / Bluetooth](materiel.md#communication-reseau)
    de la page Matériel, où le module Intel Wi-Fi 6 AX210 (2,4 et 5 GHz
    uniquement) équipe la configuration de cette machine.

## Pilote pour chipset LAN Motorcomm YT6801

Le chipset LAN Motorcomm YT6801 installé dans l'appareil nécessite un
pilote déjà intégré dans TUXEDO OS, mais souvent absent des autres
distributions.

!!! warning "Prérequis : Secure Boot désactivé"
    Le Secure Boot doit être désactivé dans le BIOS/UEFI pour que le
    pilote se charge correctement — voir la section
    [Sécurité](materiel.md#securite) de la page Matériel.

**Packages disponibles :**

| Distribution | Paquet | Lien |
|---|---|---|
| Debian / Ubuntu | `tuxedo-yt6801_1.0.28-1_all.deb` | [Télécharger](https://gitlab.com/-/project/56425584/uploads/18931d803861b6b18cbe2ed07c72ec7b/tuxedo-yt6801_1.0.28-1_all.deb) |
| Fedora / RHEL | `tuxedo-yt6801-1.0.28-1.noarch.rpm` | [Télécharger](https://gitlab.com/-/project/56425584/uploads/d1d6fe84826272e061c5fb3bd2e2a261/tuxedo-yt6801-1.0.28-1.noarch.rpm) |

## Support et service

| Contact | Détail |
|---|---|
| Horaires | Lundi à vendredi, 9h–13h et 14h–17h |
| Téléphone | +49 (0) 821 / 8998 2992 |

- [FAQ générale TUXEDO](https://www.tuxedocomputers.com/en/Infos/Help-and-Support/Frequently-asked-questions.tuxedo)
- [Instructions et guides](https://www.tuxedocomputers.com/en/Infos/Help-and-Support/Instructions)

---

Source : [FAQ officielle TUXEDO InfinityBook Pro 14 — Gen10 AMD](https://www.tuxedocomputers.com/en/FAQ-TUXEDO-InfinityBook-Pro-14-Gen10-AMD.tuxedo)
