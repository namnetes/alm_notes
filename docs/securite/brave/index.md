# Brave — Confidentialité et durcissement

Brave est un navigateur basé sur Chromium qui bloque nativement
publicités et traqueurs, sans extension tierce. Cette page documente
la configuration retenue sur ce poste et le raisonnement derrière les
choix qui vont au-delà des réglages par défaut, pour renforcer la
sécurité et l'anonymat.

!!! info "Prérequis"
    Aucune connaissance préalable requise. Tous les réglages cités sont
    accessibles via `brave://settings`.

## Tutoriels

<div class="grid cards" markdown>

-   :material-backup-restore: **[Réinstallation du poste](reinstallation.md)**

    Runbook complet pour reconfigurer Brave de zéro après une
    réinstallation : réglages de base, durcissement sécurité/anonymat,
    extensions.

</div>

---

## État de référence (audit du 2026-07-07)

| Élément | Valeur |
|---|---|
| Version | 150.1.92.134 |
| Profil | `Default`, non connecté à un compte Google/Brave |
| Télémétrie (P3A/UMA) | Désactivée |
| Politique d'entreprise (MDM) | Aucune — poste personnel non managé |
| Mots de passe stockés dans Brave | 0 (délégué à [Proton Pass](../proton/ecosysteme.md)) |
| Brave Sync | Non connecté |
| Permissions caméra / micro / géoloc / notifications | Aucune accordée à aucun site |

## Extensions installées

| Extension | ID | Rôle |
|---|---|---|
| Proton Pass | `ghmbeldphafepmbegfdlkpapadhbakde` | Gestionnaire de mots de passe (remplace celui de Brave) |
| New Tab Redirect | `icpgjfneehieebagbmdbhnlpiopdcmna` | Redirige le nouvel onglet vers `localhost:8080` (dashboard Homer) |

!!! note "Pourquoi pas le gestionnaire de mots de passe de Brave ?"
    Proton Pass centralise les identifiants entre tous les appareils
    (pas seulement ce navigateur) et gère aussi les codes 2FA. Le
    gestionnaire intégré à Brave reste désactivé pour éviter la
    confusion entre deux coffres.

## Philosophie de durcissement

Deux axes distincts, parfois en tension :

- **Sécurité** : se protéger d'attaques actives (phishing, malware,
  interception réseau).
- **Anonymat** : réduire ce qui permet d'identifier ou de suivre
  l'utilisateur (fingerprinting, fuites d'IP, télémétrie).

Un réglage intuitivement "plus privé" peut en réalité nuire à
l'anonymat (ex. Do Not Track rend le profil plus unique). Le runbook
de réinstallation documente ces cas sous "Non recommandé malgré
l'intuition".

---

## Références

- [Documentation Brave — Confidentialité](https://support.brave.com/hc/en-us/categories/360001059151-Privacy)
- [Brave Search](https://search.brave.com/)
