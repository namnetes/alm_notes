# Smartphone ↔ Linux — pistes à explorer

> Point ouvert : liste des outils identifiés mais pas encore testés ni
> documentés en pages complètes dans le wiki. Déjà couverts et intégrés :
> [GSConnect](../docs/outils/gsconnect.md) et [scrcpy](../docs/outils/scrcpy.md).
> À revenir dessus un par un, dans l'ordre qui semble pertinent, en
> commençant par ceux qui répondent à un besoin concret plutôt que tous
> d'un coup.

| Outil | Usage |
|---|---|
| **Syncthing** | Synchronisation de dossiers continue et chiffrée pair-à-pair (photos, notes...), sans cloud tiers — complémentaire à l'usage Proton déjà documenté |
| **LocalSend** | Alternative moderne à AirDrop, transfert de fichiers en LAN, cross-plateforme, aucun compte requis |
| **Waydroid** | Fait tourner de vraies applications Android dans Ubuntu (conteneur), utile pour une appli sans équivalent Linux |
| **adb** (Android Debug Bridge) | Contrôle bas niveau : logs, installation d'APK, shell Android depuis le terminal Linux — déjà installé comme dépendance de scrcpy, mais pas utilisé pour lui-même |
| **Termux + SSH** | Transformer le téléphone en mini-terminal Linux, s'y connecter en SSH depuis le PC (ou l'inverse) |
| **Téléphone comme webcam/micro** (`droidcam`, ou l'appli native GNOME « Webcam distante » récente) | Meilleure qualité vidéo que la webcam intégrée pour la visio |
| **YubiKey via NFC sur le téléphone** | Approcher la clé du dos du téléphone pour valider une connexion — déjà documenté dans [YubiKey](../docs/securite/yubikey/index.md), à vérifier/tester concrètement avec le S26 Ultra |

## Pistes de classement une fois testé

- Un outil qui s'installe et se documente seul (comme scrcpy) → nouvelle page
  dans `docs/outils/`.
- Un outil déjà en partie couvert ailleurs (YubiKey NFC) → simple
  complément/exemple concret dans la page existante plutôt qu'une nouvelle
  page.
- Voir si certains de ces outils se recoupent avec la section
  [alm_tools](../docs/systeme/ubuntu/alm_tools/postinstall/index.md) —
  potentiel module d'installation automatisée si l'outil est adopté
  durablement.
