# Outils et gestion des profils

Cette page couvre le cycle de vie complet d'un profil AppArmor : création, test, affinement,
rechargement et désactivation.

---

## Vue d'ensemble du workflow

```
Étape 1 : Créer le squelette         → aa-genprof
Étape 2 : Tester en mode Complain    → lancer le programme normalement
Étape 3 : Analyser les journaux      → aa-logprof
Étape 4 : Itérer jusqu'à satisfaction
Étape 5 : Passer en mode Enforce     → aa-enforce
Étape 6 : Surveiller                 → journaux
Étape 7 : Ajuster si nécessaire      → aa-logprof + apparmor_parser -r
```

---

## Créer un profil : `aa-genprof`

`aa-genprof` est un assistant interactif qui génère un profil en observant le comportement d'un
programme. Il place automatiquement le programme en mode Complain, vous invite à l'utiliser
normalement, puis analyse les journaux pour vous proposer des règles.

### Utilisation pas à pas

**1. Lancez `aa-genprof` en lui donnant le chemin du programme :**

```bash
sudo aa-genprof /usr/bin/mon-programme
```

La sortie ressemble à :

```
Writing updated profile for /usr/bin/mon-programme.
Setting /usr/bin/mon-programme to complain mode.

Before continuing, you may wish to check if a
profile already exists for the application you
wish to confine. See the following wiki page for
more information:
https://gitlab.com/apparmor/apparmor/wikis/Profiles

[(S)can system log for AppArmor events] / (F)inish
```

**2. Ouvrez un second terminal et utilisez le programme normalement.**
Effectuez toutes les opérations que le programme est censé faire : ouvrir des fichiers, se connecter
au réseau, lire sa configuration, écrire des journaux, etc.

**3. Revenez dans le premier terminal et appuyez sur `S` (Scan).**

`aa-genprof` analyse les journaux et vous pose des questions pour chaque accès détecté :

```
Profile:  /usr/bin/mon-programme
Path:     /etc/mon-programme/config.yaml
Mode:     r
Severity: 2

 [1 - /etc/mon-programme/config.yaml]
  2 - /etc/mon-programme/
  3 - /etc/**
(A)llow / [(D)eny] / (I)gnore / (G)lob / (G)lob with Extension / Audi(t) / Abo(r)t / (F)inish
```

| Touche | Action |
|---|---|
| `A` | Autoriser ce chemin précis |
| `D` | Refuser explicitement |
| `G` | Élargir à un glob (`/etc/mon-programme/*`) |
| `Maj+G` | Glob en conservant l'extension (`/etc/**/*.yaml`) |
| `I` | Ignorer (ne pas ajouter de règle) |
| `F` | Terminer et sauvegarder |

**4. Répétez pour chaque accès détecté, puis appuyez sur `F` pour terminer.**

Le profil est sauvegardé dans `/etc/apparmor.d/` et reste en mode Complain pour que vous puissiez
continuer à l'affiner.

!!! tip "Faites le tour complet des fonctionnalités"
    Lors de l'étape 2, utilisez **toutes** les fonctions du programme : cas normaux, cas d'erreur,
    connexion réseau, lecture de fichiers de configuration optionnels. Plus vous êtes exhaustif,
    moins vous aurez de surprises en mode Enforce.

---

## Affiner un profil existant : `aa-logprof`

`aa-logprof` analyse les journaux AppArmor d'un profil déjà en place (en mode Complain ou Enforce)
et vous propose d'ajouter les règles manquantes. C'est l'outil à utiliser quand un programme déjà
profilé rencontre de nouveaux besoins.

```bash
sudo aa-logprof
```

L'interface est identique à celle de `aa-genprof` : pour chaque accès refusé ou journalisé, vous
choisissez d'autoriser, refuser ou ignorer.

Pour cibler un fichier journal spécifique :

```bash
sudo aa-logprof -f /var/log/syslog
```

---

## Lire les journaux

Comprendre les messages AppArmor est essentiel pour déboguer un profil.

### Emplacement des journaux

| Système | Commande |
|---|---|
| Ubuntu (sans auditd) | `grep apparmor /var/log/syslog` |
| Avec auditd | `grep apparmor /var/log/audit/audit.log` |
| journald (systemd) | `journalctl -k \| grep apparmor` |
| Noyau (dmesg) | `dmesg \| grep apparmor` |

### Anatomie d'un message DENIED

```
audit: type=1400 audit(1714000000.123:456): apparmor="DENIED"
  operation="file_perm"
  profile="/usr/sbin/nginx"
  name="/etc/shadow"
  pid=1234
  comm="nginx"
  requested_mask="r"
  denied_mask="r"
  fsuid=33
  ouid=0
```

| Champ | Signification |
|---|---|
| `apparmor="DENIED"` | L'opération a été bloquée |
| `operation` | Type d'opération : `file_perm`, `exec`, `network`, `capable` |
| `profile` | Le profil qui a appliqué le refus |
| `name` | Le fichier ou la ressource concernée |
| `requested_mask` | La permission demandée (`r`, `w`, `x`…) |
| `denied_mask` | La permission refusée (souvent identique) |
| `comm` | Le nom du processus |
| `fsuid` | UID du processus (33 = www-data ici) |

### Surveiller en temps réel

```bash
# Avec journald
sudo journalctl -kf | grep apparmor

# Avec syslog
sudo tail -f /var/log/syslog | grep apparmor
```

### Cas particulier : les capabilities

Quand un refus porte sur une capability, le champ `operation` est `capable` :

```
apparmor="DENIED" operation="capable" profile="/bin/ping"
capname="net_raw" pid=5678 comm="ping"
```

→ Il faut ajouter `capability net_raw,` dans le profil.

!!! warning "Quand rien ne s'affiche dans les journaux"
    Si votre programme échoue mais que vous ne voyez aucun refus AppArmor, vérifiez que le profil
    est bien chargé avec `sudo aa-status | grep mon-programme`. Si le profil est en mode Enforce
    et que vous n'avez pas de journaux, assurez-vous qu'`auditd` ou `rsyslog` est actif.

---

## Gérer les modes : `aa-enforce` et `aa-complain`

### Passer en mode Enforce

```bash
sudo aa-enforce /etc/apparmor.d/usr.sbin.nginx
# ou directement par chemin du binaire
sudo aa-enforce /usr/sbin/nginx
```

### Passer en mode Complain

```bash
sudo aa-complain /etc/apparmor.d/usr.sbin.nginx
# ou
sudo aa-complain /usr/sbin/nginx
```

### Vérifier l'état d'un profil

```bash
sudo aa-status | grep nginx
```

---

## Recharger un profil : `apparmor_parser`

Après avoir modifié manuellement un fichier de profil, le changement n'est **pas appliqué
automatiquement**. Il faut recharger le profil.

```bash
# Recharger un profil spécifique (le plus courant)
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx

# Recharger tous les profils (plus long)
sudo systemctl reload apparmor
```

!!! tip "Raccourci pratique"
    La combinaison édition → rechargement est si fréquente qu'il est utile de se créer un alias :
    ```bash
    alias aa-reload='sudo apparmor_parser -r'
    ```
    Usage : `aa-reload /etc/apparmor.d/usr.sbin.nginx`

---

## Désactiver un profil : `aa-disable`

`aa-disable` désactive complètement un profil (ni Enforce, ni Complain). Le programme s'exécute
sans aucun confinement.

```bash
sudo aa-disable /etc/apparmor.d/usr.sbin.nginx
```

Cette commande crée un lien symbolique dans `/etc/apparmor.d/disable/` qui empêche le profil
d'être chargé au démarrage.

Pour réactiver :

```bash
sudo rm /etc/apparmor.d/disable/usr.sbin.nginx
sudo apparmor_parser -r /etc/apparmor.d/usr.sbin.nginx
```

!!! warning "aa-disable n'est pas une solution"
    Désactiver un profil pour « faire fonctionner » un programme est une mauvaise pratique.
    Utilisez le mode Complain pour identifier les règles manquantes, puis complétez le profil.
    `aa-disable` ne devrait être qu'une mesure temporaire d'urgence.

---

## Nommer les fichiers de profil

Par convention, les fichiers de profil dans `/etc/apparmor.d/` sont nommés d'après le chemin
du binaire, les `/` étant remplacés par des `.` :

| Binaire | Fichier de profil |
|---|---|
| `/usr/sbin/nginx` | `/etc/apparmor.d/usr.sbin.nginx` |
| `/usr/bin/evince` | `/etc/apparmor.d/usr.bin.evince` |
| `/usr/local/bin/mkdocs` | `/etc/apparmor.d/usr.local.bin.mkdocs` |

Cette convention n'est pas obligatoire mais elle est universellement respectée et attendue par
les outils comme `aa-logprof`.

---

## Résumé des commandes

| Commande | Rôle |
|---|---|
| `sudo aa-status` | État global de tous les profils |
| `sudo aa-genprof /chemin/binaire` | Créer un nouveau profil interactivement |
| `sudo aa-logprof` | Affiner un profil à partir des journaux |
| `sudo aa-enforce /chemin/profil` | Passer en mode Enforce |
| `sudo aa-complain /chemin/profil` | Passer en mode Complain |
| `sudo aa-disable /chemin/profil` | Désactiver un profil |
| `sudo apparmor_parser -r /chemin/profil` | Recharger un profil après modification |
| `sudo systemctl reload apparmor` | Recharger tous les profils |
| `grep apparmor /var/log/syslog` | Voir les refus journalisés |
