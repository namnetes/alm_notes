# Certificats SSL/TLS

Un certificat numérique est un document électronique qui prouve l'identité d'un serveur (ou d'une personne). Il contient une clé publique et des informations sur son propriétaire, le tout signé par une autorité de confiance.

Lorsque votre navigateur affiche le cadenas vert sur un site HTTPS, c'est qu'il a vérifié et validé le certificat du serveur.

---

## La chaîne de confiance

Les certificats fonctionnent en hiérarchie. Chaque certificat est signé par un certificat parent, jusqu'à remonter à une **autorité racine** (Root CA) que votre système ou navigateur considère comme fiable par défaut.

```mermaid
---
title: Hiérarchie des certificats
---
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff"}}}%%
flowchart TD
    classDef startStop fill:#e1f5fe,stroke:#01579b,color:#000
    classDef logic     fill:#e8eaf6,stroke:#1a237e,color:#000
    classDef data      fill:#fff3e0,stroke:#e65100,color:#000
    classDef external  fill:#f3e5f5,stroke:#6a1b9a,color:#000

    ROOT([Autorité Racine\nRoot CA]):::startStop
    INTER[Autorité Intermédiaire\nIntermediate CA]:::logic
    END[/Certificat final\nserveur ou utilisateur/]:::data

    ROOT -->|signe| INTER
    INTER -->|signe| END

    subgraph Legend["Légende"]
        direction LR
        L1([Autorité racine]):::startStop
        L2[Autorité intermédiaire]:::logic
        L3[/Certificat final/]:::data
    end
```

| Niveau | Rôle |
|--------|------|
| **Root CA** | Autorité racine. Son certificat est auto-signé et pré-installé dans les systèmes d'exploitation et navigateurs (Mozilla, Microsoft, Apple…). |
| **Intermediate CA** | Autorité intermédiaire. Elle signe les certificats finaux au nom de la Root CA. Limite l'exposition de la Root CA. |
| **Certificat final** | Certificat du serveur ou de l'utilisateur. C'est celui que vous installez sur votre serveur web. |

!!! info "Pourquoi des intermédiaires ?"
    La clé privée d'une Root CA est conservée hors ligne dans des coffres physiques ultra-sécurisés. En cas de compromission d'une autorité intermédiaire, on peut la révoquer sans toucher à la Root CA.

---

## Ce que contient un certificat

| Champ | Contenu |
|-------|---------|
| **Subject** | Identité du propriétaire (domaine, organisation, pays) |
| **Issuer** | Identité de l'autorité qui a signé ce certificat |
| **Validity** | Dates de début et de fin de validité |
| **Public Key** | Clé publique du propriétaire |
| **SANs** | *Subject Alternative Names* — liste des domaines couverts |
| **Signature** | Empreinte cryptographique signée par l'autorité |
| **Serial Number** | Identifiant unique du certificat chez l'autorité émettrice |

---

## Formats de certificats

### Tableau comparatif

| Format | Extension(s) | Encodage | Contient | Usage principal |
|--------|-------------|----------|----------|-----------------|
| **PEM** | `.pem`, `.crt`, `.cer`, `.key` | Texte (Base64) | Certificat, clé, chaîne | Linux, serveurs web |
| **DER** | `.der`, `.cer` | Binaire | Certificat seul | Windows, Java, embarqué |
| **PFX / P12** | `.pfx`, `.p12` | Binaire (PKCS#12) | Certificat + clé privée + chaîne | Import/export Windows, mobile |

### PEM (Privacy-Enhanced Mail)

C'est le format le plus répandu sur Linux. Il est encodé en Base64 et lisible dans un éditeur de texte.

```
-----BEGIN CERTIFICATE-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAzKmp9/f9QnRgFvnWrr1c
...
HJNdVvYIfgZ6JGxBWcK0L4o6
-----END CERTIFICATE-----
```

Un fichier PEM peut contenir plusieurs blocs à la suite : le certificat du serveur, les intermédiaires, et même la clé privée.

??? info "Identifier le contenu d'un bloc PEM"
    | En-tête | Contenu |
    |---------|---------|
    | `-----BEGIN CERTIFICATE-----` | Certificat |
    | `-----BEGIN PRIVATE KEY-----` | Clé privée (PKCS#8) |
    | `-----BEGIN RSA PRIVATE KEY-----` | Clé privée RSA (PKCS#1) |
    | `-----BEGIN CERTIFICATE REQUEST-----` | CSR (demande de signature) |

### DER (Distinguished Encoding Rules)

Version binaire du PEM — même structure, encodage différent. Non lisible dans un éditeur de texte. Utilisé principalement dans les environnements Windows, Java et les systèmes embarqués.

### PFX / P12 (PKCS#12)

Archive binaire qui regroupe dans un seul fichier :

- le certificat du serveur,
- la clé privée associée,
- les certificats intermédiaires.

Peut être protégé par un mot de passe. Format privilégié pour transférer un certificat complet entre systèmes, notamment sur Windows et les appareils mobiles.

!!! warning "Clé privée incluse"
    Un fichier `.pfx` ou `.p12` contient la clé privée. Protégez-le toujours par un mot de passe fort et ne le transmettez jamais en clair.

### Note sur les extensions `.crt` et `.cer`

Ces extensions désignent un fichier contenant un certificat, mais **n'indiquent pas le format**. Un fichier `.crt` peut être en PEM (texte) ou en DER (binaire). Pour savoir lequel, ouvrez-le dans un éditeur : s'il commence par `-----BEGIN`, c'est du PEM ; sinon, c'est du DER.

---

## Convertir entre formats

### PEM ↔ DER

```bash
# PEM → DER
openssl x509 -in certificat.pem -outform der -out certificat.der

# DER → PEM
openssl x509 -in certificat.der -inform der -out certificat.pem
```

### PEM → PFX (avec clé privée)

```bash
openssl pkcs12 -export \
    -in certificat.pem \
    -inkey cle-privee.pem \
    -certfile intermediaires.pem \
    -out certificat.pfx
```

Le mot de passe d'export vous sera demandé interactivement.

### PFX → PEM

??? example "Extraire le certificat"
    ```bash
    openssl pkcs12 -in certificat.pfx -clcerts -nokeys -out certificat.pem
    ```

??? example "Extraire la clé privée"
    ```bash
    openssl pkcs12 -in certificat.pfx -nocerts -nodes -out cle-privee.pem
    ```

??? example "Extraire les certificats intermédiaires"
    ```bash
    openssl pkcs12 -in certificat.pfx -cacerts -nokeys -out intermediaires.pem
    ```

---

## Inspecter un certificat

### Lire un certificat PEM

```bash
openssl x509 -in certificat.pem -text -noout
```

Affiche tous les champs : sujet, émetteur, dates, SANs, clé publique, extensions.

### Vérifier les dates de validité

```bash
openssl x509 -in certificat.pem -noout -dates
```

```
notBefore=Jan  1 00:00:00 2024 GMT
notAfter=Jan  1 00:00:00 2025 GMT
```

### Vérifier le domaine couvert

```bash
openssl x509 -in certificat.pem -noout -ext subjectAltName
```

### Vérifier le certificat d'un serveur en ligne

```bash
openssl s_client -connect exemple.com:443 -servername exemple.com </dev/null 2>/dev/null \
    | openssl x509 -noout -text
```

??? tip "Vérifier uniquement la date d'expiration d'un site"
    ```bash
    openssl s_client -connect exemple.com:443 -servername exemple.com </dev/null 2>/dev/null \
        | openssl x509 -noout -dates
    ```

### Vérifier une chaîne de certificats

```bash
openssl verify -CAfile autorite-racine.pem -untrusted intermediaire.pem certificat.pem
```

Résultat attendu : `certificat.pem: OK`

---

## Référence rapide

| Besoin | Commande |
|--------|----------|
| Lire un certificat PEM | `openssl x509 -in cert.pem -text -noout` |
| Vérifier les dates | `openssl x509 -in cert.pem -noout -dates` |
| Vérifier les domaines couverts | `openssl x509 -in cert.pem -noout -ext subjectAltName` |
| Inspecter un site en ligne | `openssl s_client -connect host:443 -servername host` |
| PEM → DER | `openssl x509 -in cert.pem -outform der -out cert.der` |
| DER → PEM | `openssl x509 -in cert.der -inform der -out cert.pem` |
| PEM → PFX | `openssl pkcs12 -export -in cert.pem -inkey key.pem -out cert.pfx` |
| PFX → PEM (certificat) | `openssl pkcs12 -in cert.pfx -clcerts -nokeys -out cert.pem` |
| PFX → PEM (clé privée) | `openssl pkcs12 -in cert.pfx -nocerts -nodes -out key.pem` |
