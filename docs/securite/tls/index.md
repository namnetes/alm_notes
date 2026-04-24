# TLS / SSL

TLS (*Transport Layer Security*) est le protocole qui sécurise la quasi-totalité des communications sur Internet : HTTPS, SMTP, IMAP, LDAPS, et bien d'autres. Son prédécesseur SSL (*Secure Sockets Layer*) est aujourd'hui obsolète et abandonné.

TLS garantit trois propriétés fondamentales :

| Propriété | Signification |
|-----------|---------------|
| **Confidentialité** | Les données échangées sont chiffrées — un attaquant qui intercepte le trafic ne peut pas le lire |
| **Intégrité** | Toute modification des données en transit est détectable |
| **Authentification** | Le serveur (et optionnellement le client) prouve son identité via un certificat |

## Pages

| Page | Description |
|------|-------------|
| [Fondamentaux](fondamentaux.md) | Versions, algorithmes, suites cryptographiques |
| [Handshake](handshake.md) | Déroulement détaillé de la négociation TLS 1.2, TLS 1.3 et mTLS |
| [Débogage CLI](debug.md) | Outils et commandes pour inspecter, tracer et auditer TLS |
| [Exercices](exercices.md) | Cas pratiques guidés |
