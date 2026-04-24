# Syntaxe des profils AppArmor

Un profil AppArmor est un fichier texte placé dans `/etc/apparmor.d/`. Il décrit précisément ce
qu'un programme est autorisé à faire. Cette page explique comment le lire et l'écrire.

---

## Anatomie d'un profil

```
#include <tunables/global>                       ← (1) Variables globales

profile mon-programme /usr/bin/mon-programme {  ← (2) Déclaration du profil

    #include <abstractions/base>                 ← (3) Inclusions

    # Fichiers accessibles
    /etc/mon-programme/   r,                     ← (4) Règles de fichiers
    /etc/mon-programme/** r,
    /var/log/mon-programme/ rw,
    /var/log/mon-programme/*.log rw,

    # Capacités système
    capability net_bind_service,                 ← (5) Capabilities

    # Réseau
    network inet tcp,                            ← (6) Règles réseau

    # Refus explicites
    deny /etc/shadow r,                          ← (7) Refus

}
```

| Numéro | Rôle |
|---|---|
| (1) | Charge les variables globales comme `@{HOME}` et `@{PROC}` |
| (2) | Nom du profil et chemin du binaire qu'il cible |
| (3) | Inclut des ensembles de règles prédéfinies (abstractions) |
| (4) | Règles d'accès aux fichiers et répertoires |
| (5) | Capacités Linux nécessaires au programme |
| (6) | Accès réseau autorisé |
| (7) | Interdictions explicites (prioritaires sur les autorisations) |

!!! note "Nom du profil vs chemin du binaire"
    Le nom du profil (avant le chemin) est libre. Le chemin après est le binaire réellement ciblé.
    Dans la pratique, le nom reprend souvent le chemin : `profile /usr/sbin/nginx /usr/sbin/nginx { ... }`.
    La forme courte `profile /usr/sbin/nginx { ... }` (sans nom explicite) est également valide.

---

## Les permissions de fichiers

Chaque règle de fichier se termine par une virgule. Les permissions sont des lettres accolées.

| Lettre | Signification | Exemple d'usage |
|---|---|---|
| `r` | Lecture | Lire un fichier de configuration |
| `w` | Écriture | Créer, modifier, supprimer un fichier |
| `a` | Ajout (*append*) | Écrire dans un journal sans pouvoir le lire |
| `x` | Exécution | Lancer un programme (nécessite un qualificateur) |
| `l` | Lien dur (*link*) | Créer un lien hard vers un fichier |
| `k` | Verrouillage (*lock*) | `flock()` sur un fichier |
| `m` | Mappage mémoire exécutable | `mmap()` avec `PROT_EXEC` (bibliothèques partagées) |

```
/etc/passwd          r,    # lecture seule
/var/log/app/*.log   rw,   # lecture + écriture
/var/log/app/*.log   a,    # ajout uniquement (sans lecture)
/usr/lib/**          mr,   # mmap + lecture (bibliothèques)
```

!!! warning "w inclut la suppression"
    La permission `w` autorise non seulement l'écriture dans un fichier, mais aussi sa suppression
    (`unlink`) et son renommage. Utilisez `a` (append) si vous souhaitez autoriser l'écriture de
    journaux sans permettre leur effacement.

---

## Les jokers (*wildcards*)

Les jokers permettent de viser plusieurs fichiers avec une seule règle.

| Joker | Portée | Exemple |
|---|---|---|
| `*` | Correspond à **tout** sauf `/` — un seul niveau | `/etc/nginx/*.conf` |
| `**` | Correspond à **tout** y compris `/` — tous niveaux | `/var/www/**` |
| `?` | Correspond à **un seul caractère** quelconque | `/tmp/php?????` |

```
/etc/nginx/          r,       # le répertoire lui-même
/etc/nginx/*.conf    r,       # tous les .conf dans /etc/nginx/ (pas de sous-dossiers)
/etc/nginx/**        r,       # tout dans /etc/nginx/ et ses sous-dossiers
/tmp/tmp.???????     rw,      # fichiers temporaires de 7 caractères
```

!!! warning "Répertoire vs contenu du répertoire"
    `/etc/nginx/` (avec le slash final) donne accès au répertoire en tant qu'objet (lister son
    contenu). `/etc/nginx/*` donne accès aux fichiers qu'il contient. Les deux sont souvent
    nécessaires ensemble.

---

## Les qualificateurs d'exécution

La lettre `x` seule n'est pas valide pour les fichiers exécutables : elle doit être accompagnée
d'un qualificateur qui précise ce que devient le processus fils.

| Qualificateur | Comportement | Quand l'utiliser |
|---|---|---|
| `ix` | Le fils **hérite** du profil du parent (*inherit*) | Helpers internes, scripts appelés par le programme |
| `px` | Le fils charge **son propre profil** AppArmor (*profile*) | Programmes qui ont leur propre profil défini |
| `Px` | Comme `px` mais nettoie les variables d'environnement | Idem, avec isolation renforcée |
| `cx` | Le fils charge un **sous-profil local** défini dans le même fichier | Programmes avec des phases distinctes |
| `Cx` | Comme `cx` avec nettoyage des variables | Idem, renforcé |
| `ux` | Le fils s'exécute **sans confinement** | À éviter sauf nécessité absolue |
| `Ux` | Sans confinement, variables nettoyées | Légèrement moins risqué que `ux` |

```
/bin/bash             ix,   # bash hérite du profil (usage interne)
/usr/bin/python3      ix,   # python hérite du profil
/usr/sbin/sendmail    px,   # sendmail charge son propre profil
/usr/bin/gpg          Px,   # gpg avec isolation de l'environnement
```

!!! danger "`ux` est une porte ouverte"
    Utiliser `ux` revient à dire « ce programme peut lancer n'importe quoi sans restriction ».
    C'est souvent une faille dans un profil. Préférez `ix` (hériter) ou `px` (profil dédié)
    dans tous les cas possibles.

---

## Les capabilities Linux

Les capabilities sont des droits système privilégiés, indépendants des fichiers. Elles
correspondent aux droits spéciaux que `root` possède, découpés en unités fines.

| Capability | Signification |
|---|---|
| `net_raw` | Sockets réseau bruts — nécessaire pour `ping`, `tcpdump` |
| `net_bind_service` | Écouter sur un port inférieur à 1024 (HTTP, SSH, etc.) |
| `setuid` | Changer d'identité utilisateur |
| `setgid` | Changer de groupe |
| `dac_override` | Contourner les permissions de fichiers |
| `dac_read_search` | Lire n'importe quel fichier indépendamment des permissions |
| `sys_ptrace` | Inspecter un processus (`strace`, `gdb`) |
| `sys_admin` | Opérations d'administration système (à éviter — trop large) |
| `kill` | Envoyer des signaux à des processus arbitraires |
| `chown` | Changer le propriétaire d'un fichier |

```
capability net_bind_service,   # Nginx sur le port 80
capability setuid,             # Nginx change d'utilisateur après démarrage
capability net_raw,            # ping a besoin de sockets ICMP bruts
```

!!! tip "Comment trouver la capability manquante ?"
    Quand un programme échoue silencieusement, cherchez dans les journaux une ligne `DENIED`
    avec `operation="capable"`. Le champ `capname` vous indique exactement laquelle ajouter.
    Voir la page [Outils et gestion](outils.md) pour lire les journaux.

---

## Les règles réseau

Les règles réseau contrôlent les types de connexions qu'un programme peut établir.

```
network,                 # Autorise TOUT le réseau (à éviter)
network tcp,             # TCP uniquement (IPv4 + IPv6)
network udp,             # UDP uniquement
network inet,            # IPv4 uniquement (tous protocoles)
network inet6,           # IPv6 uniquement
network inet tcp,        # IPv4 + TCP
network inet6 tcp,       # IPv6 + TCP
network inet stream,     # Équivalent à inet tcp
network inet dgram,      # Équivalent à inet udp
network unix stream,     # Socket Unix de type stream (IPC local)
```

!!! info "Réseau et capabilities"
    Certaines opérations réseau nécessitent à la fois une règle réseau **et** une capability.
    Par exemple, `ping` a besoin de `network inet raw,` (socket brut) **et** de
    `capability net_raw,`. L'un sans l'autre ne suffit pas.

---

## Les variables

Les variables évitent de dupliquer des chemins et rendent les profils portables.

```
#include <tunables/global>

# Utilisation des variables prédéfinies
@{HOME}/**              r,     # tous les répertoires personnels
@{PROC}/[0-9]*/status   r,     # /proc/<pid>/status pour n'importe quel PID
@{sys}/class/net/       r,     # /sys/class/net/
```

| Variable | Valeur |
|---|---|
| `@{HOME}` | `/root /home/*` |
| `@{PROC}` | `/proc` |
| `@{sys}` | `/sys` |
| `@{run}` | `/run /var/run` |
| `@{pid}` | `[0-9]*` (n'importe quel PID) |
| `@{multiarch}` | Fragment d'architecture (ex. `x86_64-linux-gnu`) |

Vous pouvez aussi définir vos propres variables dans un profil :

```
@{DOC_DIR} = /home/galan/workspaces/wikinotes

profile mkdocs /usr/local/bin/mkdocs {
    @{DOC_DIR}/docs/** r,
    @{DOC_DIR}/mkdocs.yml r,
    @{DOC_DIR}/site/ rw,
    @{DOC_DIR}/site/** rw,
}
```

---

## Les abstractions

Les abstractions sont des fichiers d'inclusion prêts à l'emploi, situés dans
`/etc/apparmor.d/abstractions/`. Elles regroupent les règles communes à une catégorie de programmes.

```
#include <abstractions/base>          # Accès minimal indispensable à tout programme (libc, /dev/null…)
#include <abstractions/nameservice>   # DNS, NSS (/etc/hosts, /etc/resolv.conf…)
#include <abstractions/python>        # Interpréteur Python et bibliothèques standard
#include <abstractions/ssl_certs>     # Certificats SSL (/etc/ssl/, /usr/share/ca-certificates/)
#include <abstractions/fonts>         # Polices de caractères
#include <abstractions/user-tmp>      # /tmp et /var/tmp
```

!!! tip "Listez les abstractions disponibles"
    ```bash
    ls /etc/apparmor.d/abstractions/
    ```
    Il en existe une cinquantaine. Consultez leur contenu pour comprendre ce qu'elles autorisent.

---

## Les profils locaux

Les profils locaux permettent d'**ajouter des règles à un profil existant** (fourni par un paquet)
sans modifier le fichier original. Ils survivent aux mises à jour du système.

Les fichiers locaux se trouvent dans `/etc/apparmor.d/local/`.

**Exemple :** autoriser Nginx à lire un répertoire supplémentaire.

Contenu de `/etc/apparmor.d/local/usr.sbin.nginx` :

```
# Autorisation supplémentaire pour mon site statique
/data/sites/mon-site/** r,
```

Cette règle est automatiquement incluse dans le profil Nginx principal grâce à la ligne :

```
include if exists <local/usr.sbin.nginx>
```

que tous les profils officiels contiennent.

!!! warning "Vérifiez que la ligne d'inclusion existe"
    Tous les profils n'ont pas forcément cette ligne d'inclusion. Vérifiez avec :
    ```bash
    grep "local/" /etc/apparmor.d/usr.sbin.nginx
    ```

---

## Les règles de refus

Un refus (`deny`) est prioritaire sur toute règle d'autorisation. Il sert à exclure explicitement
un sous-ensemble d'une règle large.

```
# Autoriser tout le répertoire personnel...
@{HOME}/** r,

# ...sauf les clés SSH et le trousseau GPG
deny @{HOME}/.ssh/**    r,
deny @{HOME}/.gnupg/**  r,
```

!!! info "deny vs absence de règle"
    Ne pas avoir de règle et avoir une règle `deny` ont le même effet pratique en mode Enforce :
    l'accès est refusé. La différence est que `deny` **supprime aussi la journalisation** de
    l'opération refusée. Utilisez `deny` pour masquer le bruit dans les journaux lorsque vous
    savez qu'un refus est normal et attendu.

---

## Récapitulatif : un profil minimal commenté

```
#include <tunables/global>

profile mon-app /usr/bin/mon-app {

    # --- Abstractions ---
    # Base indispensable à tout programme (libc, /dev/null, /proc/self/)
    #include <abstractions/base>

    # --- Binaire ---
    # Le programme lui-même doit pouvoir être lu et mappé en mémoire
    /usr/bin/mon-app mr,

    # --- Configuration ---
    /etc/mon-app/       r,
    /etc/mon-app/**     r,

    # --- Données ---
    /var/lib/mon-app/   rw,
    /var/lib/mon-app/** rw,

    # --- Journaux (ajout uniquement) ---
    /var/log/mon-app/   rw,
    /var/log/mon-app/** a,

    # --- Capabilities ---
    capability net_bind_service,

    # --- Réseau ---
    network inet tcp,

    # --- Refus explicites ---
    deny /etc/shadow    r,
    deny @{HOME}/.ssh/  r,

}
```
