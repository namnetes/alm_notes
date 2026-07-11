# Runbooks : connexion et sauvegarde (procédures pas à pas)

Quatre procédures rédigées pour un·e débutant·e : suivez les étapes dans
l'ordre, sans en sauter. Chaque méthode (fichier et phrase de
récupération, 2FA, QR code) doit être configurée **en amont**, avant
d'en avoir besoin, dans **Paramètres → Compte → Récupération** sur
`account.proton.me`.

!!! info "Fichiers essentiels sauvegardés"
    Avant de suivre ces runbooks, assurez-vous d'avoir sauvegardé vos
    méthodes de récupération Proton. Il vous faut au moins une des trois
    méthodes suivantes, déjà configurée et sauvegardée en lieu sûr :

    - **Fichier de récupération** : `proton_recovery.asc`
    - **Phrase de récupération** : `proton-recovery-phrase.pdf`
    - **Codes de récupération 2FA** : `proton_2FA_recovery_codes.txt`

---

## Runbook 1 — Se connecter avec un QR code

**Quand l'utiliser** : vous voulez vous connecter sur un appareil
(nouveau, ou verrouillé car mot de passe oublié) et vous avez un autre
appareil déjà connecté à Proton à portée de main.

**Ce qu'il vous faut :**

- L'appareil sur lequel vous voulez vous connecter — on l'appelle
  **appareil B**
- Un appareil déjà connecté à une app Proton (Mail, Calendar, Drive,
  VPN…) — on l'appelle **appareil A**
- Les deux appareils à portée de main l'un de l'autre

### Étape 1 — Afficher le QR code sur l'appareil B

1. Sur l'appareil B, ouvrez une application Proton (ou allez sur
   `account.proton.me`)
2. Sur l'écran de connexion, cherchez l'option **« Se connecter avec un
   QR code »** (icône QR code, ou dans le menu d'aide)
3. Un QR code s'affiche à l'écran — laissez cet écran ouvert

### Étape 2 — Scanner depuis l'appareil A

4. Sur l'appareil A (déjà connecté), ouvrez l'application Proton
5. Ouvrez les paramètres du compte (icône avatar, ou barre latérale)
6. Sélectionnez **« Se connecter sur un autre appareil »**
   (*Sign in on another device*)
7. Sélectionnez **« Scanner un QR code »**
8. Confirmez votre identité sur l'appareil A (empreinte digitale, visage,
   ou code PIN)
9. Pointez la caméra de l'appareil A vers le QR code affiché sur
   l'appareil B

### Étape 3 — Confirmation

10. Une confirmation s'affiche sur les deux écrans : l'appareil B est
    maintenant connecté

!!! tip "Pas de caméra sur l'appareil A ?"
    Choisissez **« Saisir le code manuellement »** (*Enter code
    manually*) à la place de scanner, et recopiez le code affiché sur
    l'appareil B.

!!! info "Et le mot de passe, dans tout ça ?"
    Une fois connecté via QR code, si vous avez oublié votre mot de
    passe, utilisez la réinitialisation **depuis un appareil déjà
    connecté** (*signed-in reset*, dans Paramètres → Sécurité → Mot de
    passe) pour en définir un nouveau sans avoir besoin de l'ancien.

En savoir plus : [proton.me/support/qr-code-sign-in](https://proton.me/support/qr-code-sign-in)

---

## Runbook 2 — Sauvegarder et restaurer Proton Pass et Proton Authenticator sur un média externe

**Quand l'utiliser** : vous voulez garder une copie de vos mots de passe
(Proton Pass) et de vos codes 2FA (Proton Authenticator) sur une clé USB
ou un disque externe, indépendamment du compte Proton — par exemple
avant une réinstallation complète du poste.

!!! warning "Export mobile non disponible pour Pass"
    L'export de Proton Pass n'est possible que depuis l'extension
    navigateur, l'application web, ou l'application Windows/Linux —
    **pas** depuis l'app mobile.

### 2.1 — Exporter Proton Pass

1. Ouvrez Proton Pass (application web, extension navigateur, ou app de
   bureau)
2. Cliquez sur l'icône d'engrenage ⚙ (paramètres)
3. Allez dans l'onglet **Export**
4. Choisissez le format :

    | Format | Usage |
    |--------|-------|
    | **ZIP contenant un fichier JSON chiffré PGP** | Sauvegarde externe (recommandé) |
    | ZIP non chiffré | Import immédiat ailleurs, jamais pour stocker |
    | CSV | Compatibilité avec un outil tiers uniquement |

5. Si vous choisissez le chiffrement PGP, saisissez une **phrase secrète
   mémorable** et notez-la séparément (par exemple dans une note Proton
   Pass déjà existante — voir [Sauvegarde et restauration d'un
   secret](sauvegarde-restauration.md))
6. Cliquez sur **Export** — le fichier ZIP est téléchargé dans votre
   dossier de téléchargements

!!! danger "Ne jamais copier le ZIP non chiffré tel quel sur une clé USB"
    Un export non chiffré contient tous vos mots de passe **en clair**.
    Utilisez toujours l'option PGP chiffrée pour un stockage externe, ou
    chiffrez le ZIP vous-même (`gpgtool`) avant de le copier.

### 2.2 — Copier la sauvegarde Pass sur le média externe

```bash
cp ~/Téléchargements/Proton_Pass_*.zip /media/<votre-cle-usb>/backups/
```

### 2.3 — Restaurer Proton Pass depuis le média externe

1. Copiez le fichier ZIP depuis le média externe vers le disque local
2. Ouvrez Proton Pass → icône d'engrenage ⚙ → onglet **Import**
3. Sélectionnez **Proton Pass** dans la liste des sources
4. Glissez le fichier ZIP dans la zone prévue (ou **Choisir un fichier**)
5. Si le ZIP est chiffré PGP, entrez la phrase secrète définie à l'export
6. Confirmez — les éléments importés apparaissent dans vos coffres
   (*vaults*)

En savoir plus : [proton.me/support/pass-export](https://proton.me/support/pass-export)

---

### 2.4 — Sauvegarder Proton Authenticator

Proton Authenticator propose une sauvegarde chiffrée automatique (iCloud
sur iOS, compte Proton sur Linux/Windows/Android), et une option d'export
manuel vers un fichier de votre choix.

1. Ouvrez Proton Authenticator
2. Allez dans **⚙ Settings**
3. Section **Security** → activez **Backups** ; sur Android/Linux,
   choisissez l'emplacement et la fréquence
4. Pour un export ponctuel indépendant du cloud : cherchez l'option
   d'export dans **Settings**
5. Un mot de passe peut être proposé pour chiffrer le fichier exporté —
   utilisez-le systématiquement

!!! note "Libellés à vérifier dans votre version"
    La documentation officielle Proton ne détaille pas de façon
    exhaustive le libellé exact du menu d'export manuel sur chaque
    plateforme (vérifié en 2026-07). Si l'intitulé ne correspond pas
    exactement, cherchez dans **Settings** un bouton **Export** ou
    **Backup now** — la fonctionnalité existe, seul le libellé peut
    varier d'une version à l'autre.

### 2.5 — Copier la sauvegarde Authenticator sur le média externe

```bash
cp ~/.config/ProtonAuthenticator/backups/*.json /media/<votre-cle-usb>/backups/
```

### 2.6 — Restaurer Proton Authenticator depuis le média externe

1. Copiez le fichier de sauvegarde depuis le média externe vers le
   disque local
2. Ouvrez Proton Authenticator → **⚙ Settings** → **Import**
3. Utilisez l'icône **Upload** pour charger le fichier depuis l'appareil
   (ou scannez un QR code si le fichier en propose un)
4. Entrez le mot de passe si le fichier est chiffré
5. Vérifiez que les codes restaurés génèrent bien des OTP valides avant
   de supprimer l'ancienne installation

En savoir plus :
[proton.me/support/back-up-2fa-codes](https://proton.me/support/back-up-2fa-codes) ·
[proton.me/support/import-2fa-codes](https://proton.me/support/import-2fa-codes)

---

## Runbook 3 — Se connecter avec la phrase de récupération

**Quand l'utiliser** : vous avez oublié votre mot de passe Proton et vous
avez sauvegardé votre phrase de récupération (12 mots) au préalable.

1. Allez sur l'écran de connexion Proton (`account.proton.me` ou
   n'importe quelle app Proton)
2. Cliquez sur **« Des soucis pour vous connecter ? »** (*Trouble signing
   in?*) — dans certaines apps, cette option est dans le menu d'aide
3. Sélectionnez **« Mot de passe oublié »** (*Forgot password*)
4. Si une autre méthode s'affiche par défaut (email/SMS), cliquez sur
   **« Essayer une autre méthode »** (*Try another way*) pour faire
   apparaître l'option phrase de récupération
5. Saisissez vos **12 mots**, dans l'ordre exact
6. Définissez un **nouveau mot de passe**

!!! success "Le seul cas qui débloque tout en une fois"
    Contrairement à une récupération par email/SMS (qui réinitialise
    seulement le mot de passe et laisse les données chiffrées
    verrouillées), la phrase de récupération sert aussi de clé de
    déchiffrement : après cette étape, vos données (Mail, Drive, Pass…)
    sont **immédiatement accessibles**, sans étape *Unlock data*
    supplémentaire.

!!! danger "Vous n'avez pas la phrase sous la main ?"
    Sans phrase de récupération, la réinitialisation par email/SMS reste
    possible mais **ne débloque pas les données** — il faudra ensuite
    débloquer les données manuellement dans **Recovery → Unlock data**
    (`account.proton.me`), avec un fichier de récupération ou l'ancien
    mot de passe. Détail :
    [proton.me/support/recover-encrypted-messages-files](https://proton.me/support/recover-encrypted-messages-files).

En savoir plus :
[proton.me/support/reset-password](https://proton.me/support/reset-password) ·
[proton.me/support/recovery-phrase](https://proton.me/support/recovery-phrase)

---

## Runbook 4 — Se connecter avec un code de secours (2FA)

**Quand l'utiliser** : vous avez perdu l'accès à votre application
d'authentification (TOTP) **et** à vos clés de sécurité, mais vous avez
sauvegardé les codes de récupération générés lors de l'activation du
2FA.

1. Sur l'écran de connexion, entrez votre email et votre mot de passe
   normalement
2. À l'étape 2FA, sélectionnez **« Je n'ai pas mon appareil 2FA »**
   (*I don't have my 2FA device*)
3. Sélectionnez ensuite **« Je n'ai pas mon code de secours »**
   (*I don't have my back-up code*) — c'est ce lien, malgré son
   intitulé, qui mène à l'écran de saisie des codes de récupération
4. Saisissez l'un de vos **codes de récupération** (usage unique —
   chaque code ne fonctionne qu'une seule fois)
5. Vous êtes reconnecté

!!! danger "À faire immédiatement après reconnexion"
    1. Allez dans **Paramètres → Sécurité → Authentification à deux
       facteurs**
    2. **Désactivez l'appareil 2FA perdu** (application ou clé de
       sécurité) pour empêcher quiconque de s'en servir
    3. Configurez un **nouvel** appareil 2FA (application ou clé) pour
       rester protégé
    4. Régénérez de nouveaux codes de récupération si le lot restant est
       faible

En savoir plus : [proton.me/support/two-factor-authentication-2fa](https://proton.me/support/two-factor-authentication-2fa)
