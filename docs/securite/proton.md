# Proton

Proton est un écosystème de services numériques axés sur la confidentialité, fondé en 2014 par des chercheurs du CERN. Les serveurs sont hébergés en **Suisse**, soumis au droit suisse — l'une des législations les plus protectrices de la vie privée au monde.

Tous les services partagent un compte unique sur [proton.me](https://proton.me) et reposent sur un **chiffrement de bout en bout** : même Proton ne peut pas lire vos données.

---

## Vue d'ensemble des services

| Service | Description | Disponible sur |
|---------|-------------|----------------|
| [Proton VPN](#proton-vpn) | Réseau privé virtuel | Linux, Windows, macOS, Android, iOS |
| [Proton Mail](#proton-mail) | Messagerie chiffrée | Web, Linux (Bridge), Windows, macOS, Android, iOS |
| [Proton Calendar](#proton-calendar) | Agenda chiffré | Web, Android, iOS |
| [Proton Drive](#proton-drive) | Stockage cloud chiffré | Web, Linux, Windows, macOS, Android, iOS |
| [Proton Pass](#proton-pass) | Gestionnaire de mots de passe | Linux, Windows, macOS, Android, iOS, extensions navigateur |
| [Proton Docs](#proton-docs) | Traitement de texte collaboratif chiffré | Web |
| [Proton Wallet](#proton-wallet) | Portefeuille Bitcoin | Web, Android, iOS |

---

## Plans et tarifs

| Plan | Services inclus | Usage |
|------|----------------|-------|
| **Free** | VPN (serveurs limités), Mail (1 Go), Calendar, Drive (1 Go), Pass | Usage personnel basique |
| **Mail Plus** | Mail (15 Go), Calendar, 1 domaine personnalisé | Messagerie avancée |
| **VPN Plus** | VPN illimité (tous serveurs, 10 appareils) | Confidentialité réseau |
| **Pass Plus** | Pass (mots de passe illimités, partage, moniteur de fuites) | Gestion avancée des mots de passe |
| **Drive Plus** | Drive (200 Go) | Stockage cloud |
| **Unlimited** | Tous les services en version complète | Usage tout-en-un |
| **Business** | Suite complète pour équipes, gestion centralisée | Entreprises |

> Tarifs et détails : [proton.me/pricing](https://proton.me/pricing)

---

## Proton VPN

Proton VPN chiffre l'intégralité du trafic réseau et masque l'adresse IP. Il est le seul VPN grand public à avoir fait auditer son code source par des tiers indépendants.

**Liens :**

- [Télécharger Proton VPN (Linux)](https://protonvpn.com/download/linux)
- [Guide d'installation Linux](https://protonvpn.com/support/linux-vpn-setup/)
- [Code source (GitHub)](https://github.com/ProtonVPN)

### Installation sur Linux

=== "Application graphique (recommandée)"
    Téléchargez le paquet `.deb` depuis [protonvpn.com/download/linux](https://protonvpn.com/download/linux), puis installez-le :

    ```bash
    sudo apt install ./proton-vpn-gnome-desktop_*.deb
    ```

    Ouvrez l'application, connectez-vous à votre compte Proton, puis choisissez un serveur.

=== "Interface en ligne de commande"
    ```bash
    sudo apt install protonvpn-cli
    ```

    Connexion rapide au serveur le plus rapide :

    ```bash
    protonvpn-cli connect --fastest
    ```

    Déconnexion :

    ```bash
    protonvpn-cli disconnect
    ```

    Statut de la connexion :

    ```bash
    protonvpn-cli status
    ```

??? info "Protocoles disponibles"
    | Protocole | Caractéristiques |
    |-----------|-----------------|
    | **WireGuard** | Rapide, moderne, recommandé par défaut |
    | **OpenVPN** | Mature, très compatible, légèrement plus lent |
    | **Stealth** | Obfusqué — contourne la censure réseau |

---

## Proton Mail

Proton Mail est un service de messagerie chiffrée de bout en bout. Les messages entre utilisateurs Proton sont chiffrés automatiquement. Vers des destinataires externes, le chiffrement peut être activé avec un mot de passe.

**Liens :**

- [Accéder à Proton Mail (web)](https://mail.proton.me)
- [Télécharger l'application mobile](https://proton.me/mail/download)
- [Proton Mail Bridge — client de bureau](https://proton.me/mail/bridge)

### Proton Mail Bridge

Bridge permet d'utiliser Proton Mail avec n'importe quel client de messagerie local (Thunderbird, Apple Mail…). Il tourne en arrière-plan et expose Proton Mail via des interfaces IMAP/SMTP locales, en déchiffrant les messages à la volée.

```bash
# Installation sur Ubuntu (paquet DEB disponible sur la page Bridge)
sudo apt install ./proton-bridge_*.deb
```

Après installation, ouvrez Bridge, connectez-vous, puis configurez votre client de messagerie avec :

| Paramètre | Valeur |
|-----------|--------|
| Serveur IMAP | `127.0.0.1` — port `1143` |
| Serveur SMTP | `127.0.0.1` — port `1025` |
| Identifiant | Adresse Proton Mail |
| Mot de passe | Mot de passe Bridge (généré par l'application, distinct du mot de passe Proton) |

!!! info "Plan requis"
    Proton Mail Bridge nécessite un abonnement payant (Mail Plus ou Unlimited).

---

## Proton Calendar

Agenda chiffré intégré à Proton Mail. Les événements, participants et notes sont chiffrés — même Proton ne peut pas lire le contenu de votre agenda.

**Liens :**

- [Accéder à Proton Calendar (web)](https://calendar.proton.me)
- [Application Android / iOS](https://proton.me/calendar/download)

!!! info "Client de bureau"
    Proton Calendar n'a pas d'application Linux native. L'accès se fait via le navigateur ou l'application mobile.

---

## Proton Drive

Stockage cloud chiffré de bout en bout. Les fichiers sont chiffrés localement avant d'être envoyés sur les serveurs Proton.

**Liens :**

- [Accéder à Proton Drive (web)](https://drive.proton.me)
- [Télécharger l'application Linux](https://proton.me/drive/download)
- [Documentation](https://proton.me/support/drive)

### Synchronisation sur Linux

L'application Linux permet de synchroniser un répertoire local avec Proton Drive (similaire à Dropbox ou Google Drive Sync).

```bash
sudo apt install ./proton-drive_*.deb
```

---

## Proton Pass

Gestionnaire de mots de passe open source intégré à l'écosystème Proton. Stocke mots de passe, codes 2FA, notes sécurisées et informations de carte bancaire.

**Liens :**

- [Télécharger Proton Pass (Linux)](https://proton.me/pass/download)
- [Guide d'installation Linux](https://proton.me/support/set-up-proton-pass-linux)
- [Extensions navigateur](https://proton.me/pass/download#extension)
- [Code source (GitHub)](https://github.com/ProtonMail/WebClients)

### Installation sur Linux

```bash
sudo apt install ./proton-pass_*.deb
```

### Extensions navigateur

Proton Pass est disponible en extension pour :

- Firefox : [addons.mozilla.org](https://addons.mozilla.org/firefox/addon/proton-pass/)
- Chrome / Chromium / Brave : Chrome Web Store

??? info "Fonctionnalités Pass Plus"
    L'abonnement Pass Plus débloque :

    - Mots de passe illimités sur appareils illimités (le plan gratuit limite à 10 identifiants)
    - Partage sécurisé avec d'autres utilisateurs
    - Moniteur de fuites de données (surveillance des adresses e-mail sur les bases de données compromises)
    - Alias d'e-mail illimités (via SimpleLogin, racheté par Proton)

---

## Proton Docs

Traitement de texte collaboratif en temps réel, intégré à Proton Drive. Entièrement chiffré de bout en bout — les documents ne sont lisibles ni par Proton ni par des tiers.

**Liens :**

- [Accéder à Proton Docs](https://docs.proton.me)
- [Annonce officielle](https://proton.me/blog/docs-proton-drive)

!!! info "Accès"
    Proton Docs est accessible directement depuis l'interface Proton Drive en créant un nouveau document.

---

## Proton Wallet

Portefeuille Bitcoin non-custodial intégré à l'écosystème Proton. "Non-custodial" signifie que Proton ne détient jamais vos clés privées — vous seul contrôlez vos fonds.

Permet également d'envoyer des bitcoins à une adresse e-mail Proton Mail (Bitcoin via Email).

**Liens :**

- [Proton Wallet (web)](https://wallet.proton.me)
- [Présentation officielle](https://proton.me/wallet)
- [Application Android / iOS](https://proton.me/wallet/download)

!!! warning "Disponibilité"
    Proton Wallet est progressivement déployé. L'accès peut nécessiter une liste d'attente selon le plan souscrit.

---

## Sécurité du compte

### Proton Sentinel

Programme de protection renforcée pour les comptes à risque élevé (journalistes, activistes, dirigeants…). Il ajoute une surveillance manuelle par l'équipe Proton en cas de tentative de connexion suspecte.

Activation : **Paramètres → Sécurité → Proton Sentinel**

### Authentification à deux facteurs (2FA)

Proton supporte :

- **TOTP** (Google Authenticator, Proton Pass, Aegis…)
- **Clés de sécurité physiques** (YubiKey, FIDO2)

Activation : **Paramètres → Sécurité → Authentification à deux facteurs**

### Codes de récupération

!!! danger "À sauvegarder impérativement"
    En cas de perte d'accès au 2FA, les codes de récupération sont le seul moyen de retrouver l'accès au compte. Sauvegardez-les dans Proton Pass ou sur papier dans un endroit sûr.

---

## Liens utiles

| Ressource | URL |
|-----------|-----|
| Compte Proton | [account.proton.me](https://account.proton.me) |
| Tarifs | [proton.me/pricing](https://proton.me/pricing) |
| Centre d'aide | [proton.me/support](https://proton.me/support) |
| État des services | [proton.me/support/proton-status](https://proton.me/support/proton-status) |
| Blog (nouveautés) | [proton.me/blog](https://proton.me/blog) |
| Transparence | [proton.me/legal/transparency](https://proton.me/legal/transparency) |
| Code source | [github.com/ProtonMail](https://github.com/ProtonMail) |
