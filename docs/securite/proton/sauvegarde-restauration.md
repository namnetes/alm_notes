# Sauvegarde et restauration d'un secret

Runbook générique pour sauvegarder un secret local (fichier de
configuration, token, clé...) dans Proton Pass sous forme de note
sécurisée, et le restaurer après une réinstallation — sans jamais coller
le secret en clair dans un champ non chiffré.

---

## Principe

| Étape | Outil |
|-------|-------|
| Chiffrer le fichier localement | `gpgtool` |
| Encoder en base64 (format collable dans une note texte) | `base64` |
| Stocker le blob chiffré | Note sécurisée Proton Pass |
| Stocker le mot de passe GPG | Champ caché de la même note, séparé du blob |

Le fichier `.gpg` local peut rester sur le disque après la sauvegarde : il
est déjà chiffré, sans risque.

---

## Convention de nommage

- **Titre de la note** : `<fichier ou usage> — <description courte>`
  (ex. `rclone.conf — Google Drive backup`)
- **Champ caché** : nommé `Mot de passe GPG`, ajouté via
  `+ Ajouter un champ` → type `Caché`

---

## Sauvegarde

```bash
# 1. Chiffrer le fichier avec un mot de passe
gpgtool
# 1 (Chiffrer), chemin : <chemin du fichier secret>

# 2. Encoder en base64 pour pouvoir le coller dans une note texte
base64 -w0 <fichier>.gpg > <fichier>.gpg.b64

# 3. Copier dans le presse-papiers
wl-copy < <fichier>.gpg.b64
# (Xorg/XWayland : xclip -selection clipboard < ...)

# 4. Nettoyer le fichier temporaire une fois collé dans Proton Pass
rm <fichier>.gpg.b64
```

| Commutateur | Rôle |
|--------------|------|
| `base64 -w0` | Désactive le retour à la ligne automatique tous les 76 caractères (comportement par défaut de `base64`). Sans ce commutateur, le blob colle sur plusieurs lignes et devient plus difficile à manipuler dans un champ de note. |
| `wl-copy` (sans option) | Copie l'entrée standard dans le presse-papiers du compositeur Wayland. |
| `xclip -selection clipboard` | Équivalent sous Xorg/XWayland. `-selection clipboard` cible le presse-papiers "standard" (collé avec `Ctrl+V`) — sans ce commutateur, `xclip` cible par défaut la sélection primaire (collée par un clic milieu), inutilisable pour coller dans Proton Pass. |

!!! note "Le base64 n'est pas du chiffrement"
    `base64` ne fait que transformer des octets binaires en texte —
    n'importe qui peut inverser l'opération sans mot de passe
    (`base64 -d`). Ce n'est **pas** ce qui protège le secret. La seule
    protection, c'est le chiffrement GPG fait *avant*, à l'étape 1 :
    coller le base64 d'un fichier non chiffré reviendrait à stocker ce
    fichier en clair, juste écrit différemment.

Créer une nouvelle **note sécurisée** dans Proton Pass (titre selon la
convention ci-dessus) et y répartir le résultat des étapes précédentes
dans deux emplacements **distincts et jamais mélangés** :

| Emplacement dans la note | Contenu à coller |
|---------------------------|-------------------|
| **Corps de la note** (texte principal) | Le contenu du fichier `<fichier>.gpg.b64` — c'est-à-dire le fichier chiffré par GPG à l'étape 1, encodé en base64 à l'étape 2 |
| **Champ caché** `Mot de passe GPG` (`+ Ajouter un champ` → type `Caché`) | Le mot de passe saisi dans `gpgtool` à l'étape 1 pour chiffrer le fichier |

!!! danger "Ne jamais mettre les deux dans le même champ"
    Le blob base64 seul ne permet pas de récupérer le secret. Le mot de passe
    seul ne débloque rien sans le blob. C'est cette séparation en deux
    emplacements qui protège le secret : quelqu'un qui n'accède qu'à l'un
    des deux champs (partage accidentel, capture d'écran, vol partiel...)
    ne peut rien en faire.

---

## Restauration

```bash
# Récupérer le blob base64 depuis la note Proton Pass, puis :
echo "<blob collé depuis Proton Pass>" | base64 -d > <fichier>.gpg

gpgtool
# 2 (Déchiffrer), chemin : <fichier>.gpg
# mot de passe : celui stocké dans le champ caché de la note

# Vérifier que le fichier restauré est bien celui attendu
# (commande spécifique au secret : ex. `rclone listremotes`, test de
# connexion, etc.)
```

| Commutateur | Rôle |
|--------------|------|
| `base64 -d` | Mode décodage. Sans ce commutateur, `base64` encode par défaut — c'est l'opération inverse de l'étape 2 de la sauvegarde. |

!!! tip "Vérification après restauration"
    La dernière étape de vérification dépend du secret restauré (liste
    des remotes, test de connexion, `pass-cli test`...). Documentez-la
    dans la page spécifique à l'outil concerné plutôt qu'ici.

---

## Exemple d'application

Voir [Sauvegarde Google Drive
(rclone.conf)](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md)
pour un exemple concret suivant ce runbook.
