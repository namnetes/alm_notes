# AppArmor

## Une armure pour les applications

Imaginez qu'un programme sur votre système soit un employé. Par défaut, cet employé a accès à l'ensemble
du bâtiment : il peut ouvrir toutes les portes, lire tous les dossiers, brancher n'importe quel câble.
Si cet employé est malveillant — ou simplement compromis par un attaquant — les dégâts peuvent être
considérables.

**AppArmor**, c'est le badge d'accès. Il définit précisément quelles portes cet employé est autorisé
à ouvrir, quels dossiers il peut lire, et quelles actions lui sont interdites. Même si l'employé est
piraté, l'attaquant se retrouve dans la même cage.

---

## Deux systèmes de sécurité qui coexistent

Linux dispose déjà d'un système de permissions classique : les droits `rwx` sur les fichiers, les
utilisateurs, les groupes. C'est ce qu'on appelle le contrôle d'accès discrétionnaire (**DAC** —
*Discretionary Access Control*). Ce système repose sur **qui vous êtes** (votre identité utilisateur).

AppArmor ajoute une deuxième couche : le contrôle d'accès obligatoire (**MAC** — *Mandatory Access
Control*). Ce système repose sur **ce que vous êtes** (le programme que vous exécutez), indépendamment
de l'utilisateur qui l'a lancé.

!!! info "Exemple concret"
    Le serveur web Nginx tourne souvent sous l'utilisateur `www-data`. Avec les permissions DAC
    classiques, `www-data` peut accéder à tout ce que cet utilisateur est autorisé à lire.
    Avec AppArmor, même si Nginx est compromis, le profil l'empêche de lire `/etc/shadow`,
    `/root/.ssh/`, ou tout autre fichier hors de son périmètre légitime.

---

## Comment AppArmor fonctionne

AppArmor est intégré directement dans le **noyau Linux** (via le framework LSM — *Linux Security
Modules*). À chaque appel système effectué par un programme (ouvrir un fichier, créer une connexion
réseau, lancer un processus fils), le noyau interroge AppArmor :

1. Ce programme a-t-il un profil actif ?
2. L'opération demandée est-elle autorisée dans ce profil ?
3. Si oui → l'opération est exécutée. Si non → elle est bloquée (ou journalisée selon le mode).

Un **profil AppArmor** est un fichier texte qui décrit les droits d'un programme : quels fichiers
il peut lire, écrire, exécuter, quelles connexions réseau il peut ouvrir, quelles capacités système
il peut utiliser.

---

## Les deux modes

AppArmor peut opérer dans deux modes pour chaque profil :

| Mode | Comportement |
|---|---|
| **Enforce** | Les règles sont appliquées. Les opérations non autorisées sont **bloquées** et journalisées. |
| **Complain** | Les règles sont ignorées. Les opérations non autorisées sont **journalisées uniquement**. |

!!! tip "Utiliser Complain pour apprendre"
    Le mode Complain est votre meilleur allié lors de la création d'un profil. Lancez le programme
    en mode Complain, utilisez-le normalement, puis lisez les journaux pour découvrir exactement
    ce dont il a besoin. Vous pouvez ensuite construire un profil précis avant de passer en Enforce.

---

## Installation

Sur Ubuntu et Debian, AppArmor est installé et actif par défaut depuis plusieurs années.
Vérifiez qu'il est bien présent :

```bash
sudo systemctl status apparmor
```

Si le service est absent :

```bash
sudo apt update
sudo apt install apparmor apparmor-utils apparmor-profiles apparmor-profiles-extra
```

| Paquet | Contenu |
|---|---|
| `apparmor` | Le module noyau et le service de base |
| `apparmor-utils` | Les outils en ligne de commande (`aa-status`, `aa-genprof`, etc.) |
| `apparmor-profiles` | Profils prêts à l'emploi pour de nombreuses applications |
| `apparmor-profiles-extra` | Profils supplémentaires de la communauté |

---

## Premier contact : `aa-status`

La commande `aa-status` donne une vue d'ensemble de l'état d'AppArmor sur le système :

```bash
sudo aa-status
```

Exemple de sortie :

```
apparmor module is loaded.
56 profiles are loaded.
47 profiles are in enforce mode.
   /usr/bin/evince
   /usr/sbin/cups-browsed
   /usr/sbin/cupsd
   ...
9 profiles are in complain mode.
   /usr/bin/chromium
   ...
3 processes have profiles defined.
3 processes are in enforce mode.
   /usr/sbin/cupsd (1234)
0 processes are in complain mode.
```

!!! note "Lire la sortie"
    - **profiles are loaded** : nombre total de profils connus d'AppArmor
    - **enforce mode** : profils actifs qui bloquent réellement
    - **complain mode** : profils en observation seulement
    - **processes** : programmes actuellement en cours d'exécution avec un profil actif

---

## AppArmor vs SELinux

SELinux (Red Hat, Fedora, CentOS) et AppArmor (Ubuntu, Debian, SUSE) remplissent le même rôle :
renforcer le contrôle d'accès au niveau du noyau. SELinux est plus puissant mais nettement plus
complexe à administrer. AppArmor est plus accessible, basé sur des chemins de fichiers lisibles,
et reste le choix par défaut sur les distributions Debian-based.

!!! info
    Cette documentation couvre uniquement AppArmor. Les concepts de MAC et de confinement sont
    transposables à SELinux, mais la syntaxe et les outils sont différents.

---

## Structure de la documentation

| Page | Contenu |
|---|---|
| [Syntaxe des profils](syntaxe.md) | Écrire et lire un profil AppArmor |
| [Outils et gestion](outils.md) | Créer, modifier, recharger, déboguer des profils |
| [Exemples et exercices](exemples.md) | Cas pratiques commentés, exercices guidés |
