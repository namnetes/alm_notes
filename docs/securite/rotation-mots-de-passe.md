# Rotation des mots de passe (Proton Pass)

Procédure de rotation manuelle des mots de passe avec **Proton Pass**, sans
jamais taper un mot de passe au clavier. La rotation n'est pas automatique
(aucun gestionnaire grand public ne change le mot de passe *sur le site* à
votre place) : Proton Pass s'occupe de la génération, du remplissage et du
stockage ; le déclenchement reste manuel.

---

## Principe

| Étape | Qui s'en charge |
|-------|-----------------|
| Décider qu'il est temps de roter | Vous (cadence ci-dessous) |
| Générer un nouveau mot de passe ≥ 24 caractères | Proton Pass (générateur) |
| Remplir les champs "mot de passe actuel" / "nouveau mot de passe" sur le site | Extension navigateur / autofill mobile (copier-coller, jamais saisi) |
| Valider le changement sur le site | Vous (clic) |
| Sauvegarder la nouvelle valeur dans le coffre | Proton Pass |

---

## Générer un mot de passe ≥ 24 caractères

Dans Proton Pass (application ou extension), lors de la création/modification
d'une entrée :

1. Champ **Mot de passe** → icône générateur (dé/refresh).
2. Régler le curseur de longueur sur **24** (ou plus) et activer chiffres +
   caractères spéciaux.
3. Cliquer **Régénérer** jusqu'à obtenir un résultat satisfaisant, puis
   **Utiliser ce mot de passe**.

!!! tip "Longueur par défaut"
    Le curseur ne mémorise pas toujours 24 comme valeur par défaut d'une
    entrée à l'autre. Vérifiez-le à chaque génération plutôt que de vous fier
    à la valeur affichée.

---

## Ne jamais taper le mot de passe

=== "Ordinateur (extension navigateur)"
    1. Sur la page de connexion ou de changement de mot de passe, cliquer
       dans le champ concerné.
    2. L'icône Proton Pass apparaît dans le champ → cliquer dessus →
       sélectionner l'entrée.
    3. Le champ est rempli automatiquement (autofill), rien n'est tapé au
       clavier.
    4. Si le champ n'est pas détecté : ouvrir l'extension, cliquer sur l'œil
       "afficher", puis **Copier** et coller (`Ctrl+V`) dans le champ.

=== "Mobile (Android/iOS)"
    1. Activer Proton Pass comme service d'autofill du système
       (Paramètres → Mots de passe → service d'autofill).
    2. Sur l'écran de connexion, taper dans le champ mot de passe → une
       suggestion Proton Pass apparaît au-dessus du clavier → tap dessus.

---

## Workflow de rotation, étape par étape

1. **Ouvrir l'entrée** concernée dans Proton Pass.
2. **Modifier** → générer un nouveau mot de passe (24+ caractères, voir
   ci-dessus) mais **ne pas encore enregistrer**.
3. Aller sur le site, section *changer le mot de passe* (pas la page de
   connexion classique).
4. Remplir **mot de passe actuel** via autofill/copier-coller depuis
   l'ancienne valeur encore visible dans Proton Pass.
5. Remplir **nouveau mot de passe** (et sa confirmation) via
   copier-coller depuis le mot de passe généré à l'étape 2.
6. Valider le changement **sur le site**.
7. Une fois la confirmation du site obtenue, **enregistrer** la modification
   dans Proton Pass.

!!! warning "Ordre important"
    Ne sauvegardez le nouveau mot de passe dans Proton Pass qu'**après**
    confirmation du site. Si le changement échoue côté site et que vous avez
    déjà écrasé l'ancienne valeur, vous perdez l'accès au compte tant que
    vous n'avez pas retrouvé l'ancien mot de passe.

??? info "Historique des modifications"
    Selon le plan, Proton Pass conserve un historique des versions
    précédentes d'une entrée (accessible depuis la fiche de l'entrée). Cela
    permet de retrouver un ancien mot de passe en cas d'erreur de
    manipulation — vérifiez la disponibilité de cette fonction sur votre
    plan avant de vous y fier entièrement.

---

## Cadence de rotation recommandée

Proton Pass n'a pas de champ "expiration" avec rappel intégré. La rotation
reste pilotée par vous — un rappel calendrier récurrent (Proton Calendar,
par exemple) par catégorie de comptes est le plus simple.

| Catégorie | Exemples | Fréquence indicative |
|-----------|----------|----------------------|
| Critique | Compte Proton lui-même, banque, e-mail principal | Tous les 6 mois |
| Sensible | Cloud, GitHub, comptes pro | Tous les 12 mois |
| Standard | Services divers, forums, abonnements | Rotation opportuniste (à la demande) |
| Immédiat | Tout mot de passe signalé par le moniteur de fuites Proton Pass Plus | Dès l'alerte |

!!! danger "Priorité absolue"
    Un mot de passe signalé par le **moniteur de fuites** (Pass Plus) ou
    réutilisé sur plusieurs comptes doit être roté immédiatement, avant
    toute autre considération de planning.

---

## Bonnes pratiques associées

- Toujours activer la **2FA** en complément (voir [Proton →
  Authentification à deux facteurs](proton/ecosysteme.md#authentification-a-deux-facteurs-2fa))
  quand le service le permet.
- Ne jamais réutiliser un mot de passe entre deux comptes, même après
  rotation.
- Pour les comptes les plus critiques, envisager une clé de sécurité
  physique en plus du mot de passe (voir [YubiKey](yubikey/index.md)).
