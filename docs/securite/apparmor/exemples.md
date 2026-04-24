# Exemples et exercices

Cette page présente des profils concrets, commentés ligne par ligne, suivis d'exercices guidés
pour apprendre en pratiquant.

---

## Exemple 1 — `ping` : comprendre les capabilities

`ping` est l'exemple parfait pour illustrer les capabilities. Il a besoin d'envoyer des paquets
ICMP bruts, ce qui nécessite un accès réseau de bas niveau normalement réservé à `root`.

### Le profil

Créez le fichier `/etc/apparmor.d/bin.ping` :

```
#include <tunables/global>

profile /bin/ping {

    #include <abstractions/base>

    # ping a besoin de créer des sockets ICMP bruts (raw)
    # sans cette capability, il ne peut pas fonctionner du tout
    capability net_raw,

    # ping doit pouvoir se délester de ses privilèges root après démarrage
    capability setuid,

    # Sockets réseau bruts IPv4 et IPv6
    network inet  raw,
    network inet6 raw,

    # Le binaire lui-même
    /bin/ping mr,

    # Résolution de noms
    /etc/hosts        r,
    /etc/resolv.conf  r,

    # Refus explicite de tout le reste du réseau
    # (ping n'a pas besoin d'ouvrir des connexions TCP ou UDP)
    deny network inet  tcp,
    deny network inet  udp,
    deny network inet6 tcp,
    deny network inet6 udp,

}
```

### Ce qu'il faut retenir

Sans `capability net_raw,`, `ping` échoue même lancé en tant que `root`. La capability est
nécessaire indépendamment de l'identité de l'utilisateur — c'est tout l'intérêt du MAC.

---

## Exercice 1 — Observer le mode Complain sur `ping`

Cet exercice montre concrètement la différence entre Complain et Enforce.

**Étape 1 : Créer et charger le profil en mode Complain**

```bash
sudo nano /etc/apparmor.d/bin.ping
# (copiez le profil ci-dessus)

sudo apparmor_parser -r /etc/apparmor.d/bin.ping
sudo aa-complain /bin/ping
```

**Étape 2 : Lancer ping et vérifier qu'il fonctionne**

```bash
ping -c 3 8.8.8.8
```

Il doit fonctionner normalement. Pendant ce temps, les accès sont journalisés.

**Étape 3 : Lire les journaux**

```bash
grep "ping" /var/log/syslog | grep apparmor | tail -20
```

Vous devriez voir des lignes `ALLOWED` (mode Complain ne bloque pas, il note).

**Étape 4 : Passer en mode Enforce**

```bash
sudo aa-enforce /bin/ping
ping -c 3 8.8.8.8
```

`ping` doit toujours fonctionner car notre profil est correct.

**Étape 5 : Retirer temporairement la capability et observer l'échec**

```bash
sudo nano /etc/apparmor.d/bin.ping
# Commentez la ligne : # capability net_raw,
sudo apparmor_parser -r /etc/apparmor.d/bin.ping
ping -c 3 8.8.8.8
```

```
ping: socket: Operation not permitted
```

**Étape 6 : Lire le refus dans les journaux**

```bash
grep "ping" /var/log/syslog | grep "DENIED" | tail -5
```

Vous devriez voir `operation="capable" capname="net_raw"`.

**Étape 7 : Restaurer le profil**

```bash
sudo nano /etc/apparmor.d/bin.ping
# Décommentez la ligne capability net_raw,
sudo apparmor_parser -r /etc/apparmor.d/bin.ping
ping -c 3 8.8.8.8
```

---

## Exemple 2 — Script PHP : isoler un script des données sensibles

Un script PHP malveillant ou compromis pourrait lire vos clés SSH, votre fichier `/etc/shadow`,
ou d'autres données sensibles. Ce profil l'en empêche.

### Le scénario

Le script `/var/www/html/traitement.php` est exécuté par le serveur web. Il ne doit avoir accès
qu'aux fichiers du site et au répertoire temporaire.

### Le profil

```
#include <tunables/global>

profile php-script /usr/bin/php* {

    #include <abstractions/base>
    #include <abstractions/nameservice>

    # L'interpréteur PHP et ses bibliothèques
    /usr/bin/php*                           mr,
    /usr/lib/php/**                         mr,
    /etc/php/**                             r,

    # Le script lui-même et le contenu du site
    /var/www/html/                          r,
    /var/www/html/**                        r,

    # Répertoire temporaire PHP
    /tmp/                                   r,
    /tmp/php*                               rw,
    /var/lib/php/sessions/                  rw,
    /var/lib/php/sessions/**                rw,

    # Sessions et uploads
    /var/www/html/uploads/                  rw,
    /var/www/html/uploads/**                rw,

    # ----------------------------------------------------------------
    # REFUS EXPLICITES — les données sensibles
    # ----------------------------------------------------------------

    # Clés SSH de tous les utilisateurs
    deny @{HOME}/.ssh/**                    r,
    deny /root/.ssh/**                      r,

    # Mots de passe système
    deny /etc/shadow                        r,
    deny /etc/sudoers                       r,
    deny /etc/sudoers.d/**                  r,

    # Trousseau GPG
    deny @{HOME}/.gnupg/**                  r,

    # Configurations sensibles d'applications
    deny @{HOME}/.config/chromium/**        r,
    deny @{HOME}/.mozilla/**                r,

}
```

!!! info "La règle du double verrou"
    Notez la structure : d'abord une règle large qui autorise ce dont le programme a besoin,
    puis des `deny` précis pour les exceptions. Cette approche est plus robuste qu'essayer
    de tout prévoir avec des règles d'autorisation ultra-précises.

---

## Exemple 3 — Nginx : un serveur web bien cadenassé

Nginx est un service exposé à Internet. Un profil solide limite les dégâts en cas de
vulnérabilité exploitée.

### Le profil

Créez `/etc/apparmor.d/usr.sbin.nginx` :

```
#include <tunables/global>

profile nginx /usr/sbin/nginx {

    #include <abstractions/base>
    #include <abstractions/nameservice>
    #include <abstractions/ssl_certs>

    # --- Capabilities ---
    # Écouter sur les ports 80 et 443 (< 1024)
    capability net_bind_service,
    # Passer de root à www-data après démarrage
    capability setuid,
    capability setgid,
    # Lire les fichiers de configuration même si ownership root
    capability dac_read_search,

    # --- Réseau ---
    network inet  tcp,
    network inet6 tcp,
    network unix  stream,   # Communication avec PHP-FPM via socket Unix

    # --- Binaire et bibliothèques ---
    /usr/sbin/nginx             mr,
    /usr/lib/**                 mr,
    /lib/**                     mr,
    /lib64/**                   mr,

    # --- Configuration ---
    /etc/nginx/                 r,
    /etc/nginx/**               r,

    # --- Contenu web (lecture seule) ---
    /var/www/                   r,
    /var/www/**                 r,

    # --- Journaux (ajout uniquement) ---
    /var/log/nginx/             rw,
    /var/log/nginx/**           a,

    # --- Fichiers de fonctionnement ---
    /run/nginx.pid              rw,
    /var/lib/nginx/             rw,
    /var/lib/nginx/**           rw,
    /tmp/nginx*                 rw,

    # --- Worker processes ---
    # Nginx master relance des workers sous son propre profil
    /usr/sbin/nginx             ix,

    # --- Socket PHP-FPM ---
    /run/php/*.sock             rw,

    # --- Refus explicites ---
    deny @{HOME}/.ssh/**        r,
    deny /root/**               r,
    deny /etc/shadow            r,
    deny /etc/sudoers           r,

}
```

### Ajouter des règles locales sans toucher au profil

Si vous hébergez un site dans un répertoire non standard (ex. `/data/sites/mon-site/`) :

```bash
sudo nano /etc/apparmor.d/local/usr.sbin.nginx
```

Contenu :

```
# Accès à mon site en dehors de /var/www/
/data/sites/mon-site/   r,
/data/sites/mon-site/** r,
```

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx
```

!!! note "Vérifiez l'inclusion locale"
    ```bash
    grep "local/usr.sbin.nginx" /etc/apparmor.d/usr.sbin.nginx
    ```
    Si la ligne `include if exists <local/usr.sbin.nginx>` est absente, vous devrez l'ajouter
    manuellement à la fin du bloc du profil.

---

## Exercice 2 — Créer un profil depuis zéro avec `aa-genprof`

Cet exercice vous guide pas à pas dans la création d'un profil pour un script simple.

**Étape 1 : Créer un script de test**

```bash
cat > /usr/local/bin/info-sys.sh << 'EOF'
#!/bin/bash
echo "=== Hostname ==="
hostname

echo "=== Uptime ==="
uptime

echo "=== Disques ==="
df -h

echo "=== Réseau ==="
ip addr show

echo "=== Journal ==="
date >> /tmp/info-sys.log
EOF

chmod +x /usr/local/bin/info-sys.sh
```

**Étape 2 : Lancer aa-genprof**

```bash
sudo aa-genprof /usr/local/bin/info-sys.sh
```

**Étape 3 : Dans un second terminal, exécuter le script**

```bash
/usr/local/bin/info-sys.sh
```

**Étape 4 : Retourner dans le premier terminal, appuyer sur `S` (Scan)**

Pour chaque accès détecté, choisissez judicieusement :
- Les fichiers système nécessaires → `A` (Allow)
- Les accès larges proposés → préférez un glob raisonnable avec `G`
- Les accès inutiles → `D` (Deny)

**Étape 5 : Appuyer sur `F` pour terminer**

**Étape 6 : Vérifier le profil généré**

```bash
cat /etc/apparmor.d/usr.local.bin.info-sys.sh
```

**Étape 7 : Passer en mode Enforce et tester**

```bash
sudo aa-enforce /usr/local/bin/info-sys.sh
/usr/local/bin/info-sys.sh
```

Si quelque chose ne fonctionne plus :

```bash
grep "info-sys" /var/log/syslog | grep DENIED
sudo aa-logprof
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.info-sys.sh
```

---

## Exemple 4 — MkDocs : isoler le générateur de documentation

Ce profil confine MkDocs pour qu'il ne puisse accéder qu'au répertoire de documentation.
Même si une extension malveillante était installée, elle ne pourrait pas lire vos clés SSH
ou vos mots de passe.

### Le profil

Créez `/etc/apparmor.d/usr.local.bin.mkdocs` :

```
#include <tunables/global>

# Variables spécifiques à ce projet
@{WIKI_DIR} = /home/galan/workspaces/wikinotes

profile mkdocs /usr/local/bin/mkdocs {

    #include <abstractions/base>
    #include <abstractions/python>
    #include <abstractions/nameservice>
    #include <abstractions/ssl_certs>

    # --- Python et MkDocs ---
    /usr/bin/python3*                           ix,
    /usr/local/bin/mkdocs                       r,

    # Environnement virtuel du projet
    @{WIKI_DIR}/.venv/                          r,
    @{WIKI_DIR}/.venv/**                        mr,

    # --- Documentation (lecture) ---
    @{WIKI_DIR}/docs/                           r,
    @{WIKI_DIR}/docs/**                         r,
    @{WIKI_DIR}/mkdocs.yml                      r,
    @{WIKI_DIR}/README.md                       r,

    # --- Site généré (écriture) ---
    @{WIKI_DIR}/site/                           rw,
    @{WIKI_DIR}/site/**                         rw,

    # --- Cache Python ---
    @{WIKI_DIR}/**/__pycache__/                 rw,
    @{WIKI_DIR}/**/__pycache__/**               rw,
    @{HOME}/.cache/pip/                         rw,
    @{HOME}/.cache/pip/**                       rw,

    # --- Réseau (pour mkdocs serve) ---
    network inet  tcp,
    network inet6 tcp,

    # --- Temporaire ---
    /tmp/                                       r,
    /tmp/mkdocs*/                               rw,
    /tmp/mkdocs*/**                             rw,

    # ----------------------------------------------------------------
    # REFUS EXPLICITES
    # ----------------------------------------------------------------

    # Clés SSH et GPG
    deny @{HOME}/.ssh/**                        r,
    deny @{HOME}/.gnupg/**                      r,

    # Mots de passe et secrets
    deny /etc/shadow                            r,
    deny @{HOME}/.config/chromium/**            r,
    deny @{HOME}/.mozilla/**                    r,
    deny @{HOME}/.config/keepass*/              r,

    # Autres projets (MkDocs n'a pas à les lire)
    deny @{HOME}/workspaces/vmforge/**          r,

}
```

### Charger et tester le profil

```bash
# Charger en mode Complain pour commencer
sudo apparmor_parser -r /etc/apparmor.d/usr.local.bin.mkdocs
sudo aa-complain /usr/local/bin/mkdocs

# Lancer MkDocs normalement
cd ~/workspaces/wikinotes
mkdocs build
mkdocs serve

# Analyser les journaux et affiner
sudo aa-logprof

# Passer en Enforce quand tout fonctionne
sudo aa-enforce /usr/local/bin/mkdocs
```

!!! tip "Commencez toujours par Complain"
    MkDocs charge des extensions Python dynamiquement. Un premier passage en mode Complain
    pendant un `mkdocs build` complet révèle tous les accès nécessaires, y compris ceux
    des extensions. Passer directement en Enforce avant cette étape provoque des erreurs
    difficiles à diagnostiquer.

---

## Exercice 3 — Déboguer un profil qui bloque trop

Cet exercice simule une situation réelle : un profil Enforce bloque une opération que vous
n'aviez pas prévue.

**Étape 1 : Créer un profil intentionnellement incomplet**

```bash
cat > /etc/apparmor.d/usr.bin.curl << 'EOF'
#include <tunables/global>

profile curl /usr/bin/curl {
    #include <abstractions/base>
    #include <abstractions/nameservice>
    #include <abstractions/ssl_certs>

    /usr/bin/curl    mr,

    # Réseau HTTP/HTTPS
    network inet  tcp,
    network inet6 tcp,

    # Intentionnellement incomplet : pas de capability ni de /tmp
}
EOF

sudo apparmor_parser -r /etc/apparmor.d/usr.bin.curl
sudo aa-enforce /usr/bin/curl
```

**Étape 2 : Tenter d'utiliser curl**

```bash
curl -o /tmp/test.html https://example.com
```

Si curl échoue ou se comporte étrangement, passez à l'étape suivante.

**Étape 3 : Identifier le problème dans les journaux**

```bash
grep "curl" /var/log/syslog | grep "DENIED" | tail -10
```

Lisez attentivement le champ `operation` et `name` dans chaque ligne DENIED.

**Étape 4 : Utiliser aa-logprof pour corriger**

```bash
sudo aa-logprof
```

Acceptez les suggestions pertinentes.

**Étape 5 : Recharger et retester**

```bash
sudo apparmor_parser -r /etc/apparmor.d/usr.bin.curl
curl -o /tmp/test.html https://example.com
echo $?   # Doit afficher 0 (succès)
```

---

## Erreurs fréquentes

### "Le profil est chargé mais le programme ignore les restrictions"

Vérifiez que le profil cible bien le bon chemin de binaire :

```bash
which mon-programme         # Chemin réel
sudo aa-status | grep mon   # Profil chargé pour ce chemin ?
```

Un profil pour `/usr/bin/python3` ne s'applique pas à `/usr/bin/python3.12` si vous avez
spécifié le chemin exact. Utilisez un glob : `/usr/bin/python3*`.

### "Le programme fonctionne en root mais pas en utilisateur normal"

Ce n'est généralement pas AppArmor. Le profil s'applique indépendamment de l'utilisateur.
Vérifiez les permissions DAC classiques avec `ls -la`.

### "Le profil cause des erreurs mais je ne vois rien dans les journaux"

Le programme utilise peut-être un chemin différent selon la configuration.
Passez en mode Complain et relancez :

```bash
sudo aa-complain /chemin/programme
# Relancez le programme
grep "programme" /var/log/syslog | grep apparmor
sudo aa-enforce /chemin/programme
```

### "Une majuscule dans un chemin et tout s'arrête"

AppArmor est **sensible à la casse**. `/Etc/nginx/` et `/etc/nginx/` sont deux chemins différents.
Vérifiez la casse exacte avec `ls`.

---

## Pour aller plus loin

- Combiner AppArmor avec Docker : tout conteneur peut recevoir un profil via `--security-opt apparmor=profil`
- Les *namespaces* AppArmor pour les environnements conteneurisés sans Docker
- L'audit de sécurité avec `lynis` qui vérifie l'état AppArmor du système
- La documentation officielle : `man apparmor.d` et `man aa-status`
