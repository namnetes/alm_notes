# zbar — lecture de codes-barres et QR codes en CLI

[zbar](https://github.com/mchehab/zbar) fournit deux outils complémentaires
pour décoder codes-barres et QR codes en ligne de commande : **`zbarimg`**
pour une image déjà capturée (capture d'écran, photo, PDF), **`zbarcam`**
pour un flux webcam en direct. Version installée : **0.23** (paquet Ubuntu
`zbar-tools`).

---

## Installation

Installé par le process de post-installation via la **liste de paquets
APT** (`config/packages_to_install.list` dans
[alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)) —
un simple paquet APT sans logique d'activation particulière (contrairement
à [GSConnect](../gsconnect.md), qui a besoin d'un port ufw et d'un contrôle
`session-checks` : `zbar-tools` n'en a besoin d'aucun).

```bash
zbarimg --version
```

---

## `zbarimg` ou `zbarcam` ?

| Outil | Usage |
|---|---|
| `zbarimg <fichier>` | Décode un ou plusieurs codes depuis une image déjà capturée (capture d'écran, photo, PDF/scan — rasterisé automatiquement via ImageMagick) |
| `zbarcam` | Décode en direct depuis une webcam (`/dev/video0` par défaut), affiche le flux à l'écran et imprime chaque code détecté sur stdout au fur et à mesure |

Format de sortie par défaut : `<type>:<données décodées>` (ex.
`QR-Code:...`), suivi d'une ligne de statistiques sur **stderr** (pas
stdout — ne pollue donc pas un traitement scripté). L'option `--raw` retire
en plus le préfixe de type et n'imprime que les données, une ligne par code
détecté.

---

## Cas d'usage par type de contenu

Un QR code est juste un conteneur — ce qu'il encode change complètement ce
qu'il est prudent d'en faire une fois décodé en clair dans un terminal.

### QR code de connexion à un service (ex. Proton)

Le QR code de connexion Proton (voir [Runbook 1 — Se connecter avec un QR
code](../../securite/proton/runbooks-recuperation.md#runbook-1-se-connecter-avec-un-qr-code))
encode une URL de session à usage unique, pas un secret durable. Décoder un
tel QR par curiosité ou pour du dépannage :

```console
$ zbarimg qr-connexion.png
QR-Code:https://account.proton.me/login?flow=qr&code=AB12CD34EF56
scanned 1 barcode symbols from 1 images in 0 seconds
```

Ce n'est pas la façon normale de se connecter (l'app scanne elle-même le
QR) — utile seulement pour inspecter ce qu'un QR encode réellement, en
dépannage.

!!! note "Exemple, pas une vraie session"
    L'URL ci-dessus est une forme plausible à titre d'exemple, pas un vrai
    QR de connexion capturé — générer et scanner un vrai QR Proton pour une
    simple capture de doc créerait une session d'authentification active
    pour rien.

### QR code de configuration Wi-Fi

Format standard `WIFI:S:<ssid>;T:<type>;P:<mot de passe>;;` :

```console
$ zbarimg --raw wifi.png 2>/dev/null
WIFI:S:MonReseau;T:WPA;P:MotDePasseWifi;;
```

Extraire le SSID et le mot de passe :

```console
$ zbarimg --raw wifi.png 2>/dev/null | sed -n 's/^WIFI:S:\([^;]*\);T:[^;]*;P:\([^;]*\);.*/SSID=\1  MDP=\2/p'
SSID=MonReseau  MDP=MotDePasseWifi
```

!!! danger "QR code de secret 2FA/TOTP — ne pas décoder à la légère"
    Format `otpauth://totp/<Émetteur>:<compte>?secret=<SECRET_BASE32>&issuer=<Émetteur>` :

    ```console
    $ zbarimg --raw totp.png 2>/dev/null
    otpauth://totp/Exemple:moi@exemple.com?secret=JBSWY3DPEHPK3PXP&issuer=Exemple
    ```

    (`JBSWY3DPEHPK3PXP` est le secret d'exemple standard des RFC/librairies
    TOTP — pas un vrai secret.)

    Décoder ce type de QR affiche le **secret TOTP en clair** dans le
    terminal — et potentiellement dans l'historique shell selon la
    configuration (`HISTCONTROL`, logs de terminal persistants). C'est le
    même risque que documenté pour l'export non chiffré de [Proton
    Pass](../../securite/proton/runbooks-recuperation.md#21-exporter-proton-pass) —
    un secret réutilisable et durable, pas un jeton de session à usage
    unique comme le cas Proton ci-dessus.

    Ne jamais lancer cette commande dans un terminal partagé ou partagé à
    l'écran. Pour importer un secret 2FA sans jamais l'afficher en clair,
    préférer un import direct depuis l'app d'authentification (scan du QR
    par l'app elle-même) à un décodage manuel en CLI.

### QR code générique (URL, texte libre, vCard)

Le cas le plus anodin :

```console
$ zbarimg --raw url.png 2>/dev/null
https://example.com/page
```

---

## Scanner en direct depuis la webcam

`zbarcam` évite l'étape de capture d'écran quand le code est affiché sur un
autre appareil (téléphone, écran externe) face à la webcam du poste :

```bash
zbarcam --raw
```

Le flux vidéo s'affiche à l'écran, chaque code détecté est imprimé sur
stdout au fur et à mesure ; `Ctrl+C` pour arrêter. `-1`/`--oneshot` arrête
après le premier code détecté plutôt que de tourner en continu.

!!! note "Pas un substitut au scan applicatif"
    Pour la connexion QR code Proton documentée dans [Configuration Android
    — solution de repli](../../securite/proton/configuration-android.md#solution-de-repli-webcam-indisponible),
    c'est l'app Proton elle-même qui scanne (pas `zbarcam`) — `zbarcam` sert
    ici au dépannage ou à l'inspection généraliste d'un code, pas comme
    remplacement du flux applicatif normal.

---

## Références

- [Dépôt zbar](https://github.com/mchehab/zbar)
- `man zbarimg`, `man zbarcam`
- [Runbook 1 — Se connecter avec un QR code](../../securite/proton/runbooks-recuperation.md#runbook-1-se-connecter-avec-un-qr-code)
- [Configuration Android — solution de repli](../../securite/proton/configuration-android.md#solution-de-repli-webcam-indisponible)
