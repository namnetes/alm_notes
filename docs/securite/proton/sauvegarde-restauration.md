# Sauvegarde et restauration d'un secret

Principe général pour sauvegarder un secret local (fichier de
configuration, token, clé...) dans Proton Pass sous forme de note
sécurisée, et le restaurer après une réinstallation — sans jamais coller
le secret en clair dans un champ non chiffré.

Cette page explique le *pourquoi* de la méthode. Pour une procédure
prête à copier-coller, ne partez pas des commandes ci-dessous : allez
directement à un exemple concret déjà rédigé, comme [Sauvegarde Google
Drive
(rclone.conf)](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md#sauvegarde-et-restauration-de-la-config),
et adaptez les noms de fichiers.

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

## Pourquoi cette méthode est sûre

!!! note "Le base64 n'est pas du chiffrement"
    `base64` ne fait que transformer des octets binaires en texte —
    n'importe qui peut inverser l'opération sans mot de passe
    (`base64 -d`). La seule protection vient du chiffrement GPG fait
    *avant* l'encodage : coller le base64 d'un fichier non chiffré
    reviendrait à stocker ce fichier en clair, juste écrit différemment.

!!! danger "Jamais le blob et le mot de passe dans le même champ"
    Le blob base64 seul ne permet pas de récupérer le secret, et le mot
    de passe seul ne débloque rien sans le blob. C'est cette séparation
    en deux emplacements (corps de la note / champ caché) qui protège le
    secret : quelqu'un qui n'accède qu'à l'un des deux (partage
    accidentel, capture d'écran, vol partiel...) ne peut rien en faire.

---

## Documenter un nouveau secret

Quand un nouveau secret doit être sauvegardé selon cette méthode,
rédiger le runbook concret **dans la page de l'outil concerné** (pas
ici) — avec de vrais chemins et de vraies commandes, sur le modèle de
[Sauvegarde Google Drive
(rclone.conf)](../../systeme/ubuntu/alm_tools/outils/backup-googledrive.md#sauvegarde-et-restauration-de-la-config) :

1. Expliquer le fichier concerné et pourquoi il doit être sauvegardé
2. Sauvegarde : chiffrer (`gpgtool`) → encoder (`base64 -w0`) → copier
   (`wl-copy` / `xclip -selection clipboard`) → coller dans une note
   sécurisée Proton Pass (voir convention de nommage ci-dessus)
3. Restauration : récupérer le blob → décoder (`base64 -d`) →
   déchiffrer (`gpgtool`) → une vérification propre à l'outil restauré
