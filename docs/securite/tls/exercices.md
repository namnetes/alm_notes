# Exercices TLS

Exercices pratiques pour maîtriser l'inspection et l'audit de connexions TLS depuis un terminal Linux ou macOS.

**Prérequis :** `openssl`, `curl`, `nmap` installés. `testssl.sh` cloné localement.

---

## Exercice 1 — Inspecter le certificat d'un site

**Objectif :** récupérer et lire le certificat d'un site public.

```bash
openssl s_client -connect wikipedia.org:443 -servername wikipedia.org \
    </dev/null 2>/dev/null \
    | openssl x509 -noout -text
```

**Questions :**

1. Quelle est l'autorité de certification (champ `Issuer`) ?
2. Quels domaines sont couverts (champ `Subject Alternative Name`) ?
3. Quelle est la date d'expiration ?
4. Quelle est la taille de la clé publique ?

??? success "Éléments de réponse"
    ```bash
    # Issuer uniquement
    openssl s_client -connect wikipedia.org:443 -servername wikipedia.org \
        </dev/null 2>/dev/null \
        | openssl x509 -noout -issuer

    # SANs uniquement
    openssl s_client -connect wikipedia.org:443 -servername wikipedia.org \
        </dev/null 2>/dev/null \
        | openssl x509 -noout -ext subjectAltName

    # Dates uniquement
    openssl s_client -connect wikipedia.org:443 -servername wikipedia.org \
        </dev/null 2>/dev/null \
        | openssl x509 -noout -dates
    ```

---

## Exercice 2 — Identifier la version TLS et la suite négociée

**Objectif :** déterminer quelle version TLS et quelle suite cryptographique sont utilisées.

```bash
openssl s_client -connect github.com:443 -servername github.com </dev/null 2>&1 \
    | grep -E "Protocol|Cipher"
```

**Questions :**

1. Quelle version TLS est négociée ?
2. Quelle suite cryptographique est choisie ?
3. Quel algorithme d'échange de clés est utilisé ? Y a-t-il Forward Secrecy ?

??? success "Éléments de réponse"
    La sortie devrait ressembler à :
    ```
    Protocol  : TLSv1.3
    Cipher    : TLS_AES_256_GCM_SHA384
    ```
    En TLS 1.3, toutes les suites garantissent le Forward Secrecy (ECDHE obligatoire).

---

## Exercice 3 — Vérifier si un serveur accepte des versions obsolètes

**Objectif :** tester si un serveur accepte TLS 1.0 ou TLS 1.1 (qui doivent être désactivés).

```bash
# Tester TLS 1.1
openssl s_client -connect exemple.com:443 -tls1_1 2>&1 | grep -E "Protocol|handshake failure|alert"

# Tester TLS 1.0
openssl s_client -connect exemple.com:443 -tls1 2>&1 | grep -E "Protocol|handshake failure|alert"
```

**Résultat attendu sur un serveur correctement configuré :**
```
140...handshake failure
```
ou
```
alert handshake failure
```

**Résultat problématique (à signaler) :**
```
Protocol  : TLSv1.1
```

??? success "Avec testssl.sh"
    ```bash
    ./testssl.sh --protocols exemple.com
    ```

    Résultat attendu :
    ```
    TLS 1      not offered (OK)
    TLS 1.1    not offered (OK)
    TLS 1.2    offered (OK)
    TLS 1.3    offered (OK)
    ```

---

## Exercice 4 — Énumérer les suites supportées

**Objectif :** lister toutes les suites acceptées par un serveur et identifier les éventuelles suites faibles.

```bash
nmap --script ssl-enum-ciphers -p 443 badssl.com
```

Le site `badssl.com` propose intentionnellement des configurations TLS incorrectes pour les tests.

**Questions :**

1. Y a-t-il des suites notées B ou C ?
2. Y a-t-il des suites sans Forward Secrecy (`TLS_RSA_WITH_*`) ?
3. Y a-t-il des suites avec RC4 ou 3DES ?

??? tip "Sites de test TLS"
    | Site | Description |
    |------|-------------|
    | `badssl.com` | Configurations TLS volontairement incorrectes |
    | `tls13.cloudflare.com` | Serveur TLS 1.3 uniquement |
    | `expired.badssl.com` | Certificat expiré |
    | `self-signed.badssl.com` | Certificat auto-signé |
    | `wrong.host.badssl.com` | CN ne correspond pas au domaine |

---

## Exercice 5 — Générer un certificat auto-signé et tester la connexion

**Objectif :** créer une PKI minimale, démarrer un serveur HTTPS de test, et s'y connecter.

### Étape 1 — Générer la clé et le certificat

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout serveur.key \
    -out serveur.crt \
    -days 30 \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

### Étape 2 — Démarrer un mini-serveur HTTPS

```bash
openssl s_server \
    -key serveur.key \
    -cert serveur.crt \
    -accept 4443 \
    -www
```

### Étape 3 — Se connecter et inspecter (dans un autre terminal)

```bash
# Connexion brute
openssl s_client -connect localhost:4443 -CAfile serveur.crt

# Via curl
curl --cacert serveur.crt https://localhost:4443/

# Sans vérification (affiche l'erreur normalement bloquée)
curl -k https://localhost:4443/
```

**Questions :**

1. Que se passe-t-il sans `-CAfile` ou `--cacert` ?
2. Quelle suite est négociée ?
3. Modifiez le CN du certificat en `autre.domaine` — que se passe-t-il lors de la connexion à `localhost` ?

---

## Exercice 6 — Simuler un mTLS

**Objectif :** créer une PKI avec CA, certificat serveur et certificat client, puis tester l'authentification mutuelle.

### Étape 1 — Créer le CA

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
    -keyout ca.key -out ca.crt -days 365 \
    -subj "/CN=Mon CA de test"
```

### Étape 2 — Créer et signer le certificat serveur

```bash
# Générer la clé et la CSR
openssl req -newkey rsa:2048 -nodes \
    -keyout serveur.key -out serveur.csr \
    -subj "/CN=localhost" \
    -addext "subjectAltName=DNS:localhost"

# Signer avec le CA
openssl x509 -req -in serveur.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out serveur.crt -days 30 \
    -extfile <(echo "subjectAltName=DNS:localhost")
```

### Étape 3 — Créer et signer le certificat client

```bash
openssl req -newkey rsa:2048 -nodes \
    -keyout client.key -out client.csr \
    -subj "/CN=client-test"

openssl x509 -req -in client.csr \
    -CA ca.crt -CAkey ca.key -CAcreateserial \
    -out client.crt -days 30
```

### Étape 4 — Démarrer le serveur en mode mTLS

```bash
openssl s_server \
    -key serveur.key -cert serveur.crt \
    -CAfile ca.crt \
    -Verify 1 \
    -accept 4443 \
    -www
```

`-Verify 1` exige un certificat client (mTLS).

### Étape 5 — Tester

```bash
# Sans certificat client → doit échouer
openssl s_client -connect localhost:4443 -CAfile ca.crt

# Avec certificat client → doit réussir
openssl s_client -connect localhost:4443 \
    -CAfile ca.crt \
    -cert client.crt \
    -key client.key
```

**Question :** Que se passe-t-il si vous présentez un certificat client signé par un CA différent ?

---

## Exercice 7 — Audit complet avec testssl.sh

**Objectif :** produire un rapport d'audit complet et identifier les axes d'amélioration.

```bash
# Audit d'un serveur public
./testssl.sh --html rapport.html exemple.com

# Ouvrir le rapport
xdg-open rapport.html
```

**Checklist d'un serveur bien configuré :**

- [ ] SSL 2.0, SSL 3.0, TLS 1.0, TLS 1.1 : `not offered`
- [ ] TLS 1.2 et/ou TLS 1.3 : `offered`
- [ ] Aucune suite avec RC4, 3DES, NULL, EXPORT, anon
- [ ] Toutes les suites TLS 1.2 ont Forward Secrecy (ECDHE ou DHE)
- [ ] Heartbleed : `not vulnerable`
- [ ] POODLE : `not vulnerable`
- [ ] BEAST : `not vulnerable`
- [ ] HSTS : `yes`
- [ ] OCSP Stapling : `yes` (recommandé)

---

## Exercice 8 — Décoder une suite cryptographique

**Objectif :** lire et comprendre une suite TLS 1.2.

Décodez les suites suivantes en identifiant chaque composant :

| Suite | Échange de clés | Auth | Chiffrement | Hash |
|-------|----------------|------|-------------|------|
| `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` | ? | ? | ? | ? |
| `TLS_DHE_RSA_WITH_AES_256_CBC_SHA384` | ? | ? | ? | ? |
| `TLS_RSA_WITH_AES_128_CBC_SHA` | ? | ? | ? | ? |
| `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256` | ? | ? | ? | ? |

**Question bonus :** laquelle offre le moins de sécurité et pourquoi ?

??? success "Réponses"
    | Suite | Échange de clés | Auth | Chiffrement | Hash |
    |-------|----------------|------|-------------|------|
    | `TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256` | ECDHE ✓ FS | RSA | AES-128-GCM | SHA-256 |
    | `TLS_DHE_RSA_WITH_AES_256_CBC_SHA384` | DHE ✓ FS | RSA | AES-256-CBC | SHA-384 |
    | `TLS_RSA_WITH_AES_128_CBC_SHA` | RSA ✗ pas de FS | RSA | AES-128-CBC | SHA-1 |
    | `TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256` | ECDHE ✓ FS | ECDSA | ChaCha20-Poly1305 | SHA-256 |

    **`TLS_RSA_WITH_AES_128_CBC_SHA`** est la plus faible : pas de Forward Secrecy, SHA-1 déprécié, mode CBC.
