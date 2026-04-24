# Handshake TLS

Le handshake est la phase de négociation initiale entre client et serveur. Il établit :

- la version TLS et la suite cryptographique à utiliser
- le secret partagé (via échange de clés)
- l'identité du serveur (via son certificat)

---

## TLS 1.2 — Handshake complet

```mermaid
---
title: TLS 1.2 — Handshake complet (ECDHE_RSA)
---
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "actorBkg": "#e8eaf6", "actorBorder": "#1a237e", "signalColor": "#1a237e", "signalTextColor": "#000", "noteBkgColor": "#fff3e0", "noteBorderColor": "#e65100"}}}%%
sequenceDiagram
    participant C as Client
    participant S as Serveur

    Note over C,S: ── Phase 1 : Négociation ──

    C->>S: ClientHello<br/>versions supportées, cipher suites,<br/>client_random, extensions
    S->>C: ServerHello<br/>version choisie, cipher suite choisie,<br/>server_random

    Note over C,S: ── Phase 2 : Authentification serveur ──

    S->>C: Certificate<br/>certificat X.509 du serveur
    S->>C: ServerKeyExchange<br/>paramètres ECDHE (courbe, clé publique éphémère)<br/>signé avec la clé privée RSA
    S->>C: ServerHelloDone

    Note over C,S: ── Phase 3 : Échange de clés ──

    C->>C: Vérifie le certificat<br/>(chaîne, date, CN/SAN)
    C->>C: Génère sa clé ECDHE éphémère
    C->>C: Calcule le pre-master secret
    C->>S: ClientKeyExchange<br/>clé publique ECDHE du client

    Note over C,S: Les deux parties calculent indépendamment<br/>master_secret → clés de session

    Note over C,S: ── Phase 4 : Activation du chiffrement ──

    C->>S: ChangeCipherSpec<br/>passage au chiffrement convenu
    C->>S: Finished (chiffré)<br/>hash de tout le handshake

    S->>C: ChangeCipherSpec
    S->>C: Finished (chiffré)<br/>hash de tout le handshake

    Note over C,S: ── Données applicatives ──

    C->>S: Application Data (chiffrée)
    S->>C: Application Data (chiffrée)
```

### Points clés TLS 1.2

- **2 allers-retours (2-RTT)** avant l'envoi des données applicatives
- Le `ClientKeyExchange` contient la clé publique ECDHE éphémère du client
- Le `ServerKeyExchange` est signé par la clé privée du serveur → authentification
- `ChangeCipherSpec` signale l'activation du chiffrement — **pas** un message chiffré lui-même
- `Finished` est le premier message chiffré ; il contient un hash de tous les messages du handshake pour détecter toute falsification

---

## TLS 1.3 — Handshake 1-RTT

TLS 1.3 fusionne plusieurs étapes et démarre le chiffrement beaucoup plus tôt.

```mermaid
---
title: TLS 1.3 — Handshake 1-RTT
---
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "actorBkg": "#e8eaf6", "actorBorder": "#1a237e", "signalColor": "#1a237e", "signalTextColor": "#000", "noteBkgColor": "#fff3e0", "noteBorderColor": "#e65100"}}}%%
sequenceDiagram
    participant C as Client
    participant S as Serveur

    Note over C,S: ── Phase 1 : Négociation + échange de clés (1 RTT) ──

    C->>S: ClientHello<br/>versions, cipher suites, key_share<br/>(clé publique ECDHE + courbe), client_random

    Note over S: Calcule le Handshake Secret<br/>depuis le key_share client

    S->>C: ServerHello<br/>cipher suite choisie, key_share serveur

    Note over C: Calcule le Handshake Secret<br/>depuis le key_share serveur

    Note over C,S: ══ Tout ce qui suit est chiffré ══

    S->>C: EncryptedExtensions (chiffré)<br/>extensions ne devant pas être visibles
    S->>C: Certificate (chiffré)<br/>certificat X.509
    S->>C: CertificateVerify (chiffré)<br/>signature du transcript du handshake
    S->>C: Finished (chiffré)<br/>MAC sur tout le handshake

    Note over C: Vérifie le certificat<br/>et le CertificateVerify

    C->>S: Finished (chiffré)

    Note over C,S: ── Données applicatives ──

    C->>S: Application Data (chiffrée)
    S->>C: Application Data (chiffrée)
```

### Ce qui change par rapport à TLS 1.2

| Aspect | TLS 1.2 | TLS 1.3 |
|--------|---------|---------|
| Allers-retours | 2-RTT | **1-RTT** |
| Début du chiffrement | Après ChangeCipherSpec | Dès le ServerHello |
| Certificat visible | Oui (en clair) | **Non (chiffré)** |
| ChangeCipherSpec | Obligatoire | Supprimé (maintenu pour compatibilité uniquement) |
| Paramètres ECDHE | Échangés après ServerHello | **Inclus dans ClientHello** |

---

## TLS 1.3 — Reprise de session (0-RTT)

Lorsqu'une session précédente existe, TLS 1.3 permet au client d'envoyer des données applicatives **dans le premier message**, sans attendre le handshake complet.

```mermaid
---
title: TLS 1.3 — Reprise de session 0-RTT (Early Data)
---
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "actorBkg": "#e8eaf6", "actorBorder": "#1a237e", "signalColor": "#1a237e", "signalTextColor": "#000", "noteBkgColor": "#fff3e0", "noteBorderColor": "#e65100"}}}%%
sequenceDiagram
    participant C as Client
    participant S as Serveur

    Note over C,S: Session précédente terminée

    S-->>C: NewSessionTicket (PSK)<br/>clé pré-partagée pour la prochaine session

    Note over C,S: ── Nouvelle connexion ──

    C->>S: ClientHello<br/>+ extension pre_shared_key (PSK)<br/>+ early_data
    C->>S: Early Data (chiffré avec PSK)<br/>données applicatives envoyées immédiatement

    S->>C: ServerHello (PSK accepté)
    S->>C: EncryptedExtensions<br/>+ EarlyDataIndicated
    S->>C: Finished (chiffré)

    C->>S: EndOfEarlyData (chiffré)
    C->>S: Finished (chiffré)

    Note over C,S: ── Données applicatives ──
    C->>S: Application Data
    S->>C: Application Data
```

!!! warning "Risque de rejeu (Replay Attack) avec 0-RTT"
    Les données 0-RTT peuvent être rejouées par un attaquant qui a capturé le premier message. N'utilisez le 0-RTT que pour des **requêtes idempotentes** (GET, lectures) — jamais pour des opérations à effet de bord (paiement, modification de données).

---

## mTLS — Authentification mutuelle

Dans le TLS classique, seul le **serveur** s'authentifie. En mTLS (*mutual TLS*), le **client** présente également un certificat. C'est le standard pour les communications entre microservices, les API B2B et les VPN d'entreprise.

```mermaid
---
title: mTLS — Authentification mutuelle (basé sur TLS 1.3)
---
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff", "actorBkg": "#e8eaf6", "actorBorder": "#1a237e", "signalColor": "#1a237e", "signalTextColor": "#000", "noteBkgColor": "#fff3e0", "noteBorderColor": "#e65100"}}}%%
sequenceDiagram
    participant C as Client
    participant S as Serveur

    C->>S: ClientHello (key_share)

    S->>C: ServerHello (key_share)
    S->>C: EncryptedExtensions (chiffré)
    S->>C: CertificateRequest (chiffré)<br/>le serveur demande un cert client
    S->>C: Certificate — serveur (chiffré)
    S->>C: CertificateVerify — serveur (chiffré)
    S->>C: Finished (chiffré)

    Note over C: Vérifie le certificat serveur

    C->>S: Certificate — client (chiffré)<br/>certificat X.509 du client
    C->>S: CertificateVerify — client (chiffré)<br/>signature prouvant la possession de la clé privée
    C->>S: Finished (chiffré)

    Note over S: Vérifie le certificat client<br/>contre son CA de confiance

    C->>S: Application Data
    S->>C: Application Data
```

### Cas d'usage du mTLS

| Contexte | Exemple |
|----------|---------|
| Microservices | Service mesh (Istio, Linkerd) |
| API B2B | Partenaires bancaires (PSD2) |
| Accès VPN | Connexion à un réseau d'entreprise |
| Appareils IoT | Authentification d'un capteur auprès d'un serveur |
| CI/CD | Runner GitLab s'authentifiant auprès d'une API interne |

---

## Vérification du certificat

À chaque handshake, le client effectue plusieurs vérifications sur le certificat reçu :

```mermaid
---
title: Vérification du certificat par le client
---
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff"}}}%%
flowchart TD
    classDef startStop fill:#e1f5fe,stroke:#01579b,color:#000
    classDef logic     fill:#e8eaf6,stroke:#1a237e,color:#000
    classDef error     fill:#ffebee,stroke:#c62828,color:#000
    classDef data      fill:#fff3e0,stroke:#e65100,color:#000

    START([Certificat reçu]):::startStop
    CHAIN{Chaîne de confiance\nvalide jusqu'à un CA racine ?}:::logic
    DATE{Date actuelle dans\nla période de validité ?}:::logic
    REVOKE{Certificat révoqué ?\nCRL / OCSP}:::logic
    SAN{Domaine correspond\nau CN ou SAN ?}:::logic
    OK([Certificat valide\nHandshake continue]):::startStop
    ERR([Erreur TLS\nConnexion rejetée]):::error

    START --> CHAIN
    CHAIN -->|Non| ERR
    CHAIN -->|Oui| DATE
    DATE -->|Non — expiré ou pas encore valide| ERR
    DATE -->|Oui| REVOKE
    REVOKE -->|Révoqué| ERR
    REVOKE -->|Valide| SAN
    SAN -->|Non| ERR
    SAN -->|Oui| OK

    subgraph Legend["Légende"]
        direction LR
        L1([Début / Fin]):::startStop
        L2{Vérification}:::logic
        L3([Erreur]):::error
    end
```

### OCSP Stapling

Sans OCSP Stapling, le client interroge lui-même l'autorité de certification pour vérifier si le certificat a été révoqué — ce qui ajoute une requête réseau supplémentaire.

Avec OCSP Stapling, le **serveur** intègre directement la réponse OCSP (signée par le CA) dans le handshake TLS. Le client n'a plus besoin de contacter le CA.

```
# Nginx — activer OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 1.1.1.1 8.8.8.8;
```
