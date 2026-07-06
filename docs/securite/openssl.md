# OpenSSL

OpenSSL est une boîte à outils cryptographique en ligne de commande, open source et disponible sur tous les systèmes Unix. Elle couvre un large spectre : chiffrement symétrique, gestion de clés et de certificats, hachage, génération de données aléatoires.

---

## Installation

```bash
sudo apt install openssl
```

Vérifiez la version :

```bash
openssl version
```

```
OpenSSL 3.0.13 30 Jan 2024
```

---

## Chiffrement symétrique

Le chiffrement symétrique utilise le **même mot de passe** pour chiffrer et déchiffrer. C'est l'approche idéale pour protéger des fichiers à archiver ou à transférer.

### Chiffrer un fichier

```bash
openssl aes-256-cbc -a -salt -pbkdf2 -iter 100000 \
    -in fichier.txt \
    -out fichier.enc
```

Le mot de passe est demandé interactivement (deux fois). Le fichier original reste inchangé — supprimez-le manuellement si nécessaire.

??? info "Détail des options"
    | Option | Rôle |
    |--------|------|
    | `aes-256-cbc` | Algorithme de chiffrement (AES 256 bits, mode CBC) |
    | `-a` | Encode la sortie en Base64 (fichier texte lisible) |
    | `-salt` | Ajoute un sel aléatoire pour renforcer la dérivation de clé |
    | `-pbkdf2` | Utilise PBKDF2 pour dériver la clé depuis le mot de passe |
    | `-iter 100000` | Nombre d'itérations PBKDF2 (plus c'est élevé, plus c'est résistant aux attaques par force brute) |

### Déchiffrer un fichier

```bash
openssl aes-256-cbc -d -a -pbkdf2 -iter 100000 \
    -in fichier.enc \
    -out fichier_dechiffre.txt
```

!!! warning "Cohérence des options"
    Les options `-pbkdf2` et `-iter` doivent être **identiques** entre le chiffrement et le déchiffrement. Si vous chiffrez avec `-iter 100000`, déchiffrez avec `-iter 100000`.

### Chiffrer un répertoire

OpenSSL ne gère pas les répertoires directement. La procédure est : archiver → chiffrer.

**Chiffrement :**

```bash
tar -czf - mon_repertoire/ \
    | openssl aes-256-cbc -a -salt -pbkdf2 -iter 100000 \
    -out repertoire.enc
```

**Déchiffrement :**

```bash
openssl aes-256-cbc -d -a -pbkdf2 -iter 100000 \
    -in repertoire.enc \
    | tar -xzf -
```

??? tip "Alternative avec fichier intermédiaire"
    Si vous préférez deux étapes distinctes :

    ```bash
    # Chiffrement
    tar -czf archive.tar.gz mon_repertoire/
    openssl aes-256-cbc -a -salt -pbkdf2 -iter 100000 \
        -in archive.tar.gz -out archive.enc
    rm archive.tar.gz

    # Déchiffrement
    openssl aes-256-cbc -d -a -pbkdf2 -iter 100000 \
        -in archive.enc -out archive.tar.gz
    tar -xzf archive.tar.gz
    rm archive.tar.gz
    ```

---

## Gestion des clés RSA

Le chiffrement asymétrique utilise une **paire de clés** : une clé privée (secrète) et une clé publique (partageable). Ce qui est chiffré avec l'une ne peut être déchiffré qu'avec l'autre.

### Générer une paire de clés RSA

```bash
openssl genrsa -out cle_privee.pem 4096
```

Extraire la clé publique depuis la clé privée :

```bash
openssl rsa -in cle_privee.pem -pubout -out cle_publique.pem
```

!!! warning "Protéger la clé privée"
    La clé privée ne doit jamais être partagée. Pour la chiffrer avec un mot de passe :

    ```bash
    openssl genrsa -aes256 -out cle_privee.pem 4096
    ```

### Inspecter une clé RSA

```bash
openssl rsa -in cle_privee.pem -text -noout
```

### Chiffrer un fichier avec une clé publique

```bash
openssl rsautl -encrypt -pubin -inkey cle_publique.pem \
    -in secret.txt -out secret.enc
```

Déchiffrer avec la clé privée :

```bash
openssl rsautl -decrypt -inkey cle_privee.pem \
    -in secret.enc -out secret.txt
```

!!! info "Limite du chiffrement RSA"
    RSA ne peut chiffrer que de petits messages (quelques centaines d'octets selon la taille de clé). Pour des fichiers plus grands, on chiffre le fichier avec AES puis on chiffre la clé AES avec RSA — c'est le principe des enveloppes chiffrées.

---

## Certificats

### Créer un certificat auto-signé

Utile pour les environnements de test ou les réseaux internes.

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout cle.pem \
    -out certificat.pem \
    -days 365 \
    -subj "/C=FR/ST=IDF/L=Paris/O=MonOrg/CN=mon-serveur.local"
```

| Champ | Signification |
|-------|---------------|
| `C` | Pays (code ISO à 2 lettres) |
| `ST` | État ou région |
| `L` | Ville |
| `O` | Organisation |
| `CN` | *Common Name* — nom de domaine ou nom du serveur |

### Créer une CSR (Certificate Signing Request)

Une CSR est une demande de signature à soumettre à une autorité de certification (Let's Encrypt, DigiCert…).

```bash
openssl req -newkey rsa:4096 -nodes \
    -keyout cle.pem \
    -out demande.csr \
    -subj "/C=FR/O=MonOrg/CN=mon-domaine.fr"
```

Vérifier le contenu de la CSR :

```bash
openssl req -in demande.csr -text -noout
```

### Inspecter un certificat

```bash
openssl x509 -in certificat.pem -text -noout
```

Vérifier les dates de validité :

```bash
openssl x509 -in certificat.pem -noout -dates
```

Vérifier les domaines couverts :

```bash
openssl x509 -in certificat.pem -noout -ext subjectAltName
```

Inspecter le certificat d'un serveur en ligne :

```bash
openssl s_client -connect mon-domaine.fr:443 -servername mon-domaine.fr \
    </dev/null 2>/dev/null | openssl x509 -noout -dates
```

!!! tip "Pour aller plus loin"
    La page [Certificats SSL/TLS](certificats.md) détaille les formats (PEM, DER, PFX) et les conversions entre formats.

---

## Hachage et vérification d'intégrité

Un hash (empreinte) est une signature numérique d'un fichier. Si un seul octet change, le hash change complètement. Cela permet de vérifier qu'un fichier n'a pas été modifié ou corrompu.

### Calculer le hash d'un fichier

=== "SHA-256 (recommandé)"
    ```bash
    openssl dgst -sha256 fichier.iso
    ```

=== "SHA-512"
    ```bash
    openssl dgst -sha512 fichier.iso
    ```

=== "MD5 (déconseillé)"
    ```bash
    openssl dgst -md5 fichier.iso
    ```

    !!! warning "MD5 est obsolète"
        MD5 est vulnérable aux collisions. Utilisez SHA-256 ou SHA-512 pour tout usage sécuritaire.

### Vérifier l'intégrité d'un fichier téléchargé

Comparez le hash calculé avec celui fourni par l'éditeur :

```bash
openssl dgst -sha256 ubuntu-24.04.iso
# SHA2-256(ubuntu-24.04.iso)= a1b2c3d4...

# Comparez manuellement avec la valeur officielle
```

### Calculer le hash d'une chaîne de caractères

```bash
echo -n "ma_chaine" | openssl dgst -sha256
```

`-n` empêche l'ajout d'un saut de ligne, qui modifierait le hash.

---

## Génération de données aléatoires

### Générer un mot de passe aléatoire

=== "Base64 (caractères alphanumériques + +/)"
    ```bash
    openssl rand -base64 32
    ```

=== "Hexadécimal"
    ```bash
    openssl rand -hex 32
    ```

Le nombre indique la **longueur en octets** avant encodage. `32` octets donnent 43 caractères en Base64 ou 64 caractères en hexadécimal.

??? tip "Générer un mot de passe lisible uniquement avec tr"
    Pour supprimer les caractères spéciaux et obtenir un mot de passe purement alphanumérique :

    ```bash
    openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 32
    ```

### Générer un token d'API ou un secret

```bash
openssl rand -hex 64
```

---

## Référence rapide

| Besoin | Commande |
|--------|----------|
| Chiffrer un fichier | `openssl aes-256-cbc -a -salt -pbkdf2 -iter 100000 -in f.txt -out f.enc` |
| Déchiffrer un fichier | `openssl aes-256-cbc -d -a -pbkdf2 -iter 100000 -in f.enc -out f.txt` |
| Générer une clé RSA 4096 | `openssl genrsa -out cle.pem 4096` |
| Extraire la clé publique | `openssl rsa -in cle.pem -pubout -out pub.pem` |
| Certificat auto-signé | `openssl req -x509 -newkey rsa:4096 -nodes -keyout cle.pem -out cert.pem -days 365` |
| Créer une CSR | `openssl req -newkey rsa:4096 -nodes -keyout cle.pem -out req.csr` |
| Inspecter un certificat | `openssl x509 -in cert.pem -text -noout` |
| Hash SHA-256 | `openssl dgst -sha256 fichier` |
| Mot de passe aléatoire | `openssl rand -base64 32` |
| Token hexadécimal | `openssl rand -hex 64` |
