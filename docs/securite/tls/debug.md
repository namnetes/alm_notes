# Débogage TLS en ligne de commande

Cette page recense les outils disponibles sur Linux et macOS pour inspecter, tracer et auditer les connexions TLS.

---

## openssl s_client

C'est l'outil de référence. Il simule un client TLS et affiche tous les détails de la connexion.

### Connexion basique

```bash
openssl s_client -connect exemple.com:443
```

Utilisez `Ctrl+C` ou envoyez `Q` pour quitter.

### Inspecter le certificat d'un site

```bash
openssl s_client -connect exemple.com:443 -servername exemple.com \
    </dev/null 2>/dev/null \
    | openssl x509 -noout -text
```

`-servername` active la SNI (*Server Name Indication*) — indispensable sur les serveurs hébergeant plusieurs domaines.

### Forcer une version TLS spécifique

```bash
# TLS 1.3 uniquement
openssl s_client -connect exemple.com:443 -tls1_3

# TLS 1.2 uniquement
openssl s_client -connect exemple.com:443 -tls1_2

# TLS 1.1 (pour vérifier si le serveur l'accepte encore — à signaler)
openssl s_client -connect exemple.com:443 -tls1_1
```

### Forcer une suite cryptographique

```bash
# Tester une suite TLS 1.2 spécifique
openssl s_client -connect exemple.com:443 \
    -cipher "ECDHE-RSA-AES256-GCM-SHA384"

# Tester si le serveur accepte les suites sans Forward Secrecy (à éviter)
openssl s_client -connect exemple.com:443 \
    -cipher "AES256-SHA"
```

### Vérifier les dates d'expiration

```bash
openssl s_client -connect exemple.com:443 -servername exemple.com \
    </dev/null 2>/dev/null \
    | openssl x509 -noout -dates
```

```
notBefore=Jan  1 00:00:00 2024 GMT
notAfter=Apr  1 00:00:00 2025 GMT
```

### Afficher la chaîne de certificats complète

```bash
openssl s_client -connect exemple.com:443 -showcerts \
    </dev/null 2>/dev/null
```

Chaque certificat de la chaîne (serveur + intermédiaires) est affiché.

### Vérifier les domaines couverts (SANs)

```bash
openssl s_client -connect exemple.com:443 -servername exemple.com \
    </dev/null 2>/dev/null \
    | openssl x509 -noout -ext subjectAltName
```

```
X509v3 Subject Alternative Name:
    DNS:exemple.com, DNS:www.exemple.com, DNS:api.exemple.com
```

### Tester avec un CA personnalisé (mTLS, PKI interne)

```bash
# Serveur avec CA auto-signé ou CA interne
openssl s_client -connect mon-serveur.local:8443 \
    -CAfile /chemin/vers/ca.pem \
    -servername mon-serveur.local

# mTLS — présenter un certificat client
openssl s_client -connect mon-serveur.local:8443 \
    -CAfile ca.pem \
    -cert client.pem \
    -key client-key.pem
```

### Interpréter la sortie

```
CONNECTED(00000005)
depth=2 C=US, O=Let's Encrypt, CN=ISRG Root X1        ← CA racine
depth=1 C=US, O=Let's Encrypt, CN=R10                  ← CA intermédiaire
depth=0 CN=exemple.com                                  ← Certificat serveur
verify return:1                                         ← Chaîne valide

---
...
New, TLSv1.3, Cipher is TLS_AES_256_GCM_SHA384         ← Version et suite
Server public key is 2048 bit                           ← Taille de clé RSA
Secure Renegotiation IS NOT supported                   ← (normal en TLS 1.3)
...
SSL-Session:
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    Session-ID: AB12...                                 ← ID de session
    TLS session ticket lifetime hint: 7200 (seconds)
```

---

## curl

`curl` affiche les détails TLS en mode verbeux.

### Afficher les informations TLS

```bash
curl -v https://exemple.com 2>&1 | grep -E "TLS|SSL|cipher|issuer|expire"
```

### Verbose complet

```bash
curl -vvv https://exemple.com
```

Extrait de sortie :
```
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* Server certificate:
*  subject: CN=exemple.com
*  start date: Jan  1 00:00:00 2024 GMT
*  expire date: Apr  1 00:00:00 2025 GMT
*  issuer: C=US; O=Let's Encrypt; CN=R10
*  SSL certificate verify ok.
```

### Forcer une version TLS

```bash
curl --tlsv1.3 --tls-max 1.3 https://exemple.com
curl --tlsv1.2 --tls-max 1.2 https://exemple.com
```

### Ignorer les erreurs de certificat (tests uniquement)

```bash
curl -k https://mon-serveur-local.example
```

!!! danger "Ne jamais utiliser `-k` en production"
    `-k` désactive la vérification du certificat et rend la connexion vulnérable aux attaques MITM.

### Utiliser un CA personnalisé

```bash
curl --cacert /chemin/vers/ca.pem https://mon-serveur.local
```

### mTLS avec curl

```bash
curl --cert client.pem --key client-key.pem \
     --cacert ca.pem \
     https://mon-api.local/endpoint
```

---

## nmap

`nmap` peut énumérer toutes les suites acceptées par un serveur.

```bash
# Lister toutes les suites supportées, avec évaluation de sécurité
nmap --script ssl-enum-ciphers -p 443 exemple.com
```

Extrait de sortie :
```
PORT    STATE SERVICE
443/tcp open  https
| ssl-enum-ciphers:
|   TLSv1.2:
|     ciphers:
|       TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 (ecdh_x25519) - A
|       TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 (ecdh_x25519) - A
|       TLS_RSA_WITH_AES_256_GCM_SHA384 (rsa 2048) - B        ← pas de FS
|   TLSv1.3:
|     ciphers:
|       TLS_AES_256_GCM_SHA384 - A
|     cipher preference: server
|_  least strength: B
```

Les notes A, B, C reflètent la sécurité de chaque suite (Forward Secrecy, taille de clé, algorithme).

---

## testssl.sh

`testssl.sh` est le scanner TLS le plus complet disponible en ligne de commande. Il teste les versions, suites, vulnérabilités et génère un rapport détaillé.

### Installation

```bash
git clone --depth 1 https://github.com/drwetter/testssl.sh.git
cd testssl.sh
```

### Audit complet d'un serveur

```bash
./testssl.sh exemple.com
```

### Tests ciblés

```bash
# Versions supportées uniquement
./testssl.sh --protocols exemple.com

# Suites cryptographiques
./testssl.sh --ciphers exemple.com

# Vulnérabilités connues (POODLE, BEAST, Heartbleed…)
./testssl.sh --vulnerabilities exemple.com

# En-têtes HTTP de sécurité (HSTS, CSP…)
./testssl.sh --headers exemple.com

# Rapport complet au format JSON
./testssl.sh --jsonfile rapport.json exemple.com
```

Extrait de sortie :
```
 Testing protocols via sockets

 SSLv2      not offered (OK)
 SSLv3      not offered (OK)
 TLS 1      not offered (OK)
 TLS 1.1    not offered (OK)
 TLS 1.2    offered (OK)
 TLS 1.3    offered (OK)
 ...

 Testing vulnerabilities

 Heartbleed (CVE-2014-0160)           not vulnerable (OK)
 CCS (CVE-2014-0224)                  not vulnerable (OK)
 POODLE, SSL (CVE-2014-3566)          not vulnerable (OK)
 BEAST (CVE-2011-3389)                not vulnerable (OK)
 SWEET32 (CVE-2016-2183)              not vulnerable (OK)
```

---

## sslyze

`sslyze` est un scanner TLS en Python, orienté automatisation.

```bash
pip install sslyze
```

### Scan basique

```bash
python -m sslyze exemple.com
```

### Avec rapport JSON

```bash
python -m sslyze --json_out rapport.json exemple.com
```

### Tester plusieurs serveurs

```bash
python -m sslyze exemple.com autre-serveur.com:8443
```

---

## Wireshark / tshark

Pour capturer et analyser le handshake TLS paquet par paquet.

### Capturer le trafic TLS avec tshark

```bash
# Capturer sur l'interface réseau principale
sudo tshark -i eth0 -w capture.pcap \
    -f "host exemple.com and port 443"
```

### Filtrer les paquets TLS dans tshark

```bash
# Afficher uniquement les messages du handshake
tshark -r capture.pcap -Y "tls.handshake"

# Afficher les ClientHello
tshark -r capture.pcap -Y "tls.handshake.type == 1"

# Afficher la suite choisie dans le ServerHello
tshark -r capture.pcap -Y "tls.handshake.type == 2" \
    -T fields -e tls.handshake.ciphersuite
```

### Déchiffrer le trafic TLS dans Wireshark

Si vous disposez de la **clé de session** (variable d'environnement `SSLKEYLOGFILE`), Wireshark peut déchiffrer le trafic capturé.

```bash
# Demander à Firefox/Chrome de journaliser les clés de session
export SSLKEYLOGFILE=~/tls-keys.log
firefox &

# Capturer le trafic
sudo tshark -i eth0 -w capture.pcap

# Ouvrir dans Wireshark avec les clés
wireshark -r capture.pcap
# Edit → Preferences → Protocols → TLS → (Pre)-Master-Secret log filename
```

!!! warning "Usage réservé aux tests"
    `SSLKEYLOGFILE` exporte les clés de session en clair. N'utilisez cette technique que dans un environnement de test isolé.

---

## Récapitulatif des outils

| Outil | Usage principal | Linux | macOS |
|-------|----------------|-------|-------|
| `openssl s_client` | Inspection manuelle, tests rapides | ✓ | ✓ |
| `curl -v` | Test HTTP/HTTPS avec contexte applicatif | ✓ | ✓ |
| `nmap ssl-enum-ciphers` | Énumération des suites supportées | ✓ | ✓ |
| `testssl.sh` | Audit complet, détection de vulnérabilités | ✓ | ✓ |
| `sslyze` | Audit automatisé, intégration CI/CD | ✓ | ✓ |
| `tshark` / Wireshark | Analyse réseau paquet par paquet | ✓ | ✓ |

---

## Diagnostics courants

### Erreur : `SSL_ERROR_RX_RECORD_TOO_LONG`

Le serveur répond en HTTP clair sur un port HTTPS. Vérifiez la configuration du vhost.

### Erreur : `certificate verify failed`

```bash
# Inspecter la chaîne reçue
openssl s_client -connect exemple.com:443 -showcerts </dev/null

# Vérifier manuellement la chaîne
openssl verify -CAfile ca-bundle.pem certificat.pem
```

### Erreur : `no shared cipher`

Le client et le serveur n'ont aucune suite en commun. Vérifiez la configuration `SSLCipherSuite` côté serveur et la version OpenSSL côté client.

```bash
# Lister les suites supportées par votre OpenSSL
openssl ciphers -v 'ALL:!aNULL' | column -t
```

### Vérifier si un certificat est révoqué (OCSP)

```bash
# Extraire l'URL OCSP du certificat
openssl x509 -in certificat.pem -noout -ocsp_uri

# Vérifier la révocation
openssl ocsp \
    -issuer intermediaire.pem \
    -cert certificat.pem \
    -url http://ocsp.example.com \
    -resp_text
```
