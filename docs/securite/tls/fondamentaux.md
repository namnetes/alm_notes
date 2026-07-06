# Fondamentaux TLS

---

## Historique des versions

| Version | Année | Statut |
|---------|-------|--------|
| SSL 2.0 | 1995 | Obsolète — vulnérabilités critiques |
| SSL 3.0 | 1996 | Obsolète — vulnérable à POODLE |
| TLS 1.0 | 1999 | Déprécié (RFC 8996, 2021) |
| TLS 1.1 | 2006 | Déprécié (RFC 8996, 2021) |
| TLS 1.2 | 2008 | **Encore largement utilisé** |
| TLS 1.3 | 2018 | **Standard recommandé** |

!!! warning "TLS 1.0 et 1.1"
    Tous les navigateurs modernes et la majorité des serveurs ont abandonné TLS 1.0 et 1.1. Un serveur qui les accepte encore doit être mis à jour.

---

## Briques cryptographiques

TLS assemble plusieurs algorithmes ayant chacun un rôle précis.

### Échange de clés

L'échange de clés permet aux deux parties de calculer un **secret partagé** sans jamais le transmettre sur le réseau.

| Algorithme | Description | TLS 1.2 | TLS 1.3 |
|------------|-------------|---------|---------|
| **RSA** | Le client chiffre le secret avec la clé publique du serveur | Oui | **Non** (supprimé) |
| **DHE** | Diffie-Hellman éphémère — génère une nouvelle clé à chaque session | Oui | Non |
| **ECDHE** | DHE sur courbes elliptiques — plus rapide, clés plus courtes | Oui | **Oui** (obligatoire) |
| **X25519** | ECDHE sur la courbe Curve25519 — très performant | Oui (rare) | **Oui** (recommandé) |

!!! info "Pourquoi RSA a été supprimé de TLS 1.3 ?"
    L'échange de clés RSA ne garantit pas la **confidentialité persistante** (*Forward Secrecy*). Si la clé privée du serveur est compromise ultérieurement, un attaquant ayant enregistré le trafic passé peut tout déchiffrer rétroactivement. ECDHE génère une nouvelle paire de clés éphémères à chaque session — la compromission de la clé longue terme du serveur ne compromet pas les sessions passées.

### Authentification

L'authentification prouve l'identité du serveur (et du client en mTLS).

| Algorithme | Description |
|------------|-------------|
| **RSA** | Signature avec clé RSA (2048 ou 4096 bits) |
| **ECDSA** | Signature sur courbes elliptiques — clés plus courtes, performance équivalente |
| **Ed25519** | ECDSA sur Curve25519 — très rapide, signature déterministe |

### Chiffrement symétrique

Une fois le secret partagé établi, les données sont chiffrées avec un algorithme symétrique.

| Algorithme | Mode | Description |
|------------|------|-------------|
| **AES-128-GCM** | AEAD | Rapide, authentifié — recommandé |
| **AES-256-GCM** | AEAD | Plus fort, légèrement plus lent |
| **ChaCha20-Poly1305** | AEAD | Excellent sur appareils sans accélération AES (mobiles) |
| AES-256-CBC | CBC | TLS 1.2 uniquement — vulnérable à certaines attaques si mal implémenté |
| 3DES | CBC | Obsolète — vulnérable à SWEET32 |

!!! info "AEAD — Authenticated Encryption with Associated Data"
    Les modes AEAD (GCM, Poly1305) combinent chiffrement et vérification d'intégrité en une seule opération. C'est obligatoire en TLS 1.3 — les modes CBC et RC4 sont interdits.

### Fonction de hachage et HMAC

Utilisées pour dériver les clés et vérifier l'intégrité des messages.

| Algorithme | Taille | Usage |
|------------|--------|-------|
| **SHA-256** | 256 bits | Standard TLS 1.2 et 1.3 |
| **SHA-384** | 384 bits | Suites haut de gamme |
| SHA-1 | 160 bits | Obsolète |
| MD5 | 128 bits | Obsolète — collisions connues |

---

## Suites cryptographiques (Cipher Suites)

Une suite cryptographique est un ensemble d'algorithmes convenu entre client et serveur lors du handshake.

### Notation TLS 1.2

```
TLS _ ECDHE_RSA _ WITH _ AES_256_GCM _ SHA384
 │       │    │         │     │    │      │
 │       │    │         │     │    │      └─ Fonction de hachage (HMAC)
 │       │    │         │     │    └──────── Mode de chiffrement
 │       │    │         │     └───────────── Taille de clé (bits)
 │       │    │         └─────────────────── Algorithme symétrique
 │       │    └───────────────────────────── Algorithme d'authentification
 │       └────────────────────────────────── Algorithme d'échange de clés
 └────────────────────────────────────────── Protocole
```

### Notation TLS 1.3

TLS 1.3 simplifie drastiquement la notation. L'échange de clés et l'authentification ne font plus partie du nom de la suite :

```
TLS _ AES_256_GCM _ SHA384
 │    │     │   │     │
 │    │     │   │     └─ Fonction de hachage (HKDF)
 │    │     │   └─────── Mode de chiffrement
 │    │     └─────────── Taille de clé (bits)
 │    └───────────────── Algorithme symétrique
 └────────────────────── Protocole
```

### Suites recommandées

=== "TLS 1.3 (5 suites seulement)"
    | Suite | Sécurité |
    |-------|---------|
    | `TLS_AES_256_GCM_SHA384` | Recommandée |
    | `TLS_CHACHA20_POLY1305_SHA256` | Recommandée (mobiles) |
    | `TLS_AES_128_GCM_SHA256` | Acceptable |

=== "TLS 1.2 (sélection sûre)"
    | Suite | Remarque |
    |-------|---------|
    | `TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384` | Meilleure |
    | `TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384` | Très bonne |
    | `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256` | Très bonne |
    | `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` | Bonne |

=== "Suites à interdire"
    | Suite | Raison |
    |-------|--------|
    | `TLS_RSA_WITH_*` | Pas de Forward Secrecy |
    | `*_WITH_RC4_*` | RC4 cassé |
    | `*_WITH_3DES_*` | Vulnérable à SWEET32 |
    | `*_WITH_NULL_*` | Pas de chiffrement |
    | `*_EXPORT_*` | Clés délibérément faibles (FREAK) |
    | `*_anon_*` | Pas d'authentification (MITM trivial) |

---

## TLS 1.2 vs TLS 1.3

| Aspect | TLS 1.2 | TLS 1.3 |
|--------|---------|---------|
| Aller-retours handshake | 2-RTT | **1-RTT** (0-RTT possible) |
| Échange de clés | RSA, DHE, ECDHE | ECDHE / X25519 uniquement |
| Chiffrement | AES-CBC, AES-GCM, ChaCha20 | AES-GCM, ChaCha20 uniquement (AEAD) |
| Forward Secrecy | Optionnel (selon suite) | **Obligatoire** |
| Renégociation | Possible (vulnérable) | Supprimée |
| Compression | Optionnelle (vulnérable à CRIME) | Supprimée |
| Nombre de suites | Des centaines | **5 seulement** |
| Résumé de session | Session ID, Session Ticket | PSK (Pre-Shared Key) |

---

## Dérivation de clés

### TLS 1.2 — PRF (Pseudo-Random Function)

TLS 1.2 utilise une PRF basée sur HMAC-SHA256 ou HMAC-SHA384 pour dériver les clés de session depuis le **pre-master secret** partagé.

```
pre_master_secret
       │
       ▼
master_secret = PRF(pre_master_secret, "master secret",
                    ClientHello.random + ServerHello.random)
       │
       ▼
key_block = PRF(master_secret, "key expansion",
                ServerHello.random + ClientHello.random)
       │
       ├── client_write_key  (chiffrement client → serveur)
       ├── server_write_key  (chiffrement serveur → client)
       ├── client_write_IV   (vecteur d'initialisation)
       └── server_write_IV
```

### TLS 1.3 — HKDF (HMAC-based Key Derivation Function)

TLS 1.3 remplace la PRF par HKDF (RFC 5869), une construction plus formellement sûre.

```
ECDHE shared secret
       │
       ▼  HKDF-Extract
Handshake Secret
       │
       ├──► client_handshake_traffic_secret
       └──► server_handshake_traffic_secret
       │
       ▼  HKDF-Expand
Master Secret
       │
       ├──► client_application_traffic_secret
       └──► server_application_traffic_secret
```

---

## Attaques classiques

| Attaque | Cible | Mitigation |
|---------|-------|------------|
| **POODLE** | SSL 3.0, AES-CBC | Désactiver SSL 3.0 et TLS 1.0 |
| **BEAST** | TLS 1.0, AES-CBC | Passer à TLS 1.2+ |
| **CRIME / BREACH** | Compression TLS/HTTP | Désactiver la compression |
| **HEARTBLEED** | OpenSSL ≤ 1.0.1f | Mettre à jour OpenSSL |
| **FREAK** | Suites EXPORT | Désactiver les suites EXPORT |
| **Logjam** | DHE 512 bits | Utiliser ECDHE, DHE ≥ 2048 bits |
| **SWEET32** | 3DES, RC4 | Désactiver 3DES |
| **DROWN** | SSLv2 sur même clé | Désactiver SSLv2 partout |
| **MITM** | Absence de validation cert | HSTS, certificate pinning |
