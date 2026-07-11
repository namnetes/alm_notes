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
    | **OpenVPN** | Mature, très compatible, légèrement plus lent — disponible uniquement sur le client **Linux (GUI)**, absent des apps mobiles |
    | **Stealth** | Obfusqué — contourne la censure réseau |

### Fonctionnalités avancées

Fonctionnalités transversales à toutes les plateformes Proton VPN
(nécessitent un plan payant VPN Plus ou Unlimited, sauf mention contraire) :

**Kill Switch** — coupe *tout accès Internet* si le tunnel VPN tombe, pour
éviter une fuite de trafic en clair.

- **Standard** (activé par défaut) : protège en cas de coupure accidentelle
  du tunnel.
- **Advanced** : bloque tout accès Internet tant que le VPN n'est pas
  explicitement reconnecté — y compris au redémarrage de l'appareil.

!!! danger "Kill Switch Advanced peut vous couper l'accès à vos propres procédures de récupération"
    Si le Kill Switch **Advanced** est actif et que le tunnel VPN tombe (ou
    n'est pas encore établi au démarrage), **tout accès réseau est bloqué sur
    cet appareil** — y compris l'accès nécessaire pour effectuer une
    connexion par [QR code](runbooks-recuperation.md#runbook-1-se-connecter-avec-un-qr-code)
    ou consulter `account.proton.me` depuis ce même appareil. Se retrouver
    bloqué au moment précis où l'on cherche à récupérer l'accès à son compte
    est le pire moment pour découvrir cette interaction.

    Avant d'entamer une procédure de connexion ou de récupération (voir
    [Runbooks connexion et sauvegarde](runbooks-recuperation.md)) depuis un
    appareil où le Kill Switch Advanced est actif, désactivez-le
    temporairement ou utilisez un second appareil non soumis à cette
    restriction.

**Split Tunneling** — exclut ou inclut certaines apps du tunnel VPN (utile
pour une app bancaire qui bloque les IP VPN, par exemple). Deux modes :
*Exclude* (tout passe par le VPN sauf les apps listées) ou *Include* (rien ne
passe par le VPN sauf les apps listées). Un changement nécessite de
reconnecter le VPN pour être pris en compte.

!!! warning "Incompatibilité connue avec le Kill Switch"
    Kill Switch et Split Tunneling **ne sont pas compatibles simultanément**
    sur la plupart des plateformes. Activer l'un désactive l'autre — c'est
    une limitation connue du produit, sans date de résolution confirmée à ce
    jour.

**NetShield** — filtrage DNS côté serveur VPN (pas un DNS custom classique) :
bloque malwares, publicités et trackers directement dans le tunnel. Trois
niveaux : désactivé / bloquer malware seul / bloquer malware + pub +
trackers.

!!! note "Cohabitation avec un DNS privé configuré au niveau OS"
    Un DNS privé/personnalisé configuré au niveau du système (Android, par
    exemple) entre en conflit avec NetShield sur la résolution DNS. Pour
    garantir que c'est bien le tunnel Proton qui gère la résolution, repasser
    ce réglage sur *Automatique* (ou le désactiver) plutôt que de forcer un
    fournisseur DNS tiers quand le VPN Proton est actif.

**Secure Core** (plan payant supérieur) — achemine le trafic via un serveur
intermédiaire dans un pays à forte protection de la vie privée (Suisse,
Islande, Suède) avant le serveur de sortie. Utile en cas de modèle de menace
élevé (journalisme, dissidence) ; coût en latence non négligeable, à réserver
aux cas d'usage le justifiant.

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

### pass-cli (CLI)

CLI officielle Proton Pass, pour scripter la gestion des mots de passe
depuis le terminal. Pas de paquet APT — installée et maintenue à jour
automatiquement par le module `postinstall`, voir
[Post-installation — groupe cli](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#groupe-cli-etapes-9-a-18).

Pour un usage quotidien plus ergonomique (tableaux Rich, recherche
cross-vaults, mode interactif), voir
[pass-tool](../../systeme/ubuntu/alm_tools/outils/pass-tool.md).

**Authentification** (non gérée par le module d'installation, étape
manuelle unique après la première installation) :

```bash
pass-cli login
```

#### Authentification : `pass-cli login` vs Personal Access Token (PAT)

`pass-cli` propose deux modes d'authentification, pas interchangeables
selon le contexte :

- **`pass-cli login` (web login, par défaut)** — ouvre le navigateur, crée
  une session complète liée au compte utilisateur. **Seul mode supporté**
  si le compte est protégé par SSO ou par une clé matérielle (YubiKey) :
  impossible de créer une session initiale autrement dans ce cas.
- **Personal Access Token (PAT)** — identifiant scopé, créé via
  `pass-cli pat create` (ou directement depuis
  [pass.proton.me](https://pass.proton.me), sans passer par le CLI).
  Restreint explicitement à des vaults/items précis, expiration
  **obligatoire**, révocable indépendamment de la session principale. Ne
  peut effectuer aucune opération d'administration de vault — protection
  native, pas une convention à respecter soi-même.

!!! tip "Choix sur ce poste : `pass-cli login`"
    Le compte est protégé par une clé matérielle (YubiKey) — la
    documentation officielle Proton est explicite : c'est le **seul** flux
    d'authentification supporté dans ce cas, un PAT ne permet pas de
    contourner cette exigence pour l'authentification initiale. Raison
    secondaire : usage interactif quotidien (`pass-cli` directement ou via
    [pass-tool](../../systeme/ubuntu/alm_tools/outils/pass-tool.md))
    nécessitant l'accès à l'ensemble des vaults — un PAT à scope restreint
    serait de toute façon inadapté à cet usage.

!!! note "Un PAT serait préférable pour : tout script non interactif"
    Récupération d'un secret dans un script de dotfiles, un cron, une CI —
    tout contexte où une session complète serait disproportionnée par
    rapport au besoin. Le PAT limite le rayon de compromission (accès
    restreint aux seuls vaults nécessaires, expiration forcée)
    contrairement à une session complète. Non mis en œuvre à ce jour sur
    ce poste. Nécessite quand même une authentification complète préalable
    du compte pour créer le token (via `pass-cli pat create` ou
    directement sur pass.proton.me).

!!! danger "Deux commandes qui révèlent des secrets sans confirmation"
    - `pass-cli item view` (sans `--field`) affiche **le mot de passe en
      clair par défaut**, sans aucune confirmation ni avertissement — ce
      n'est pas un mode « masqué » à débloquer avec un flag, c'est le
      comportement par défaut de la commande.
    - `pass-cli item list --show-secrets --output json` dump le contenu
      complet (tous les mots de passe inclus) de **tous les items d'un
      vault en un seul appel**.

    Ne jamais lancer l'une de ces deux commandes dans un terminal partagé,
    partagé à l'écran, ou dans un script sans confirmation explicite de
    l'utilisateur au préalable. Pour un usage scripté sûr, préférer
    `pass-cli item view --field <champ>` (un seul champ, rien d'autre) —
    voir [Automatiser pass-cli en Python](../../developpement/python/pass-cli-subprocess.md).

#### Exemples de commandes courantes

Référence exhaustive : [Commands Reference](https://protonpass.github.io/pass-cli/commands/login/).

!!! note "Syntaxe non re-testée sur ce poste"
    Les exemples ci-dessous viennent de la documentation officielle du CLI,
    pas d'une exécution vérifiée ici (contrairement aux exemples de
    [Automatiser pass-cli en Python](../../developpement/python/pass-cli-subprocess.md),
    testés en conditions réelles). `pass-cli` étant en développement actif,
    vérifier avec `pass-cli <commande> --help` en cas de doute.

**Session**

```bash
pass-cli login                          # Connexion interactive (ouvre le navigateur)
pass-cli logout                         # Ferme la session, purge les données locales
pass-cli logout --force                 # Déconnexion forcée si la révocation distante échoue
```

**Vaults**

```bash
pass-cli vault list --output json                    # Lister les vaults, sortie JSON
pass-cli vault create --name "Perso"                  # Créer un nouveau vault
```

**Items**

```bash
pass-cli item list Perso --output json                                       # Lister les items d'un vault
pass-cli item view --vault-name Perso --item-title Netflix --field password  # Révéler UN champ, jamais l'item entier
pass-cli item create login --vault-name Perso --title Netflix \
  --username moi@example.com --generate-password                            # Créer un identifiant, mot de passe généré
pass-cli item update --vault-name Perso --item-title Netflix \
  --field password=NouveauMotDePasse                                        # Modifier un champ existant
pass-cli item delete --share-id <SHARE_ID> --item-id <ITEM_ID>               # Supprimer un item (irréversible)
pass-cli item totp --vault-name Perso --item-title GitHub                    # Générer le code TOTP courant
```

**Mots de passe**

```bash
pass-cli password generate random --length 24 --symbols true   # Générer un mot de passe fort
pass-cli password score "MonMotDePasse123!"                    # Évaluer la robustesse d'un mot de passe
```

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

2FA, phrase/fichier de récupération, connexion par QR code : voir les
procédures pas à pas dans [Runbooks connexion et
sauvegarde](runbooks-recuperation.md).

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
