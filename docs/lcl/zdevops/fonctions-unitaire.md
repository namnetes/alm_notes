# Déploiement unitaire

Promote Unitaire et Clean Unitaire agissent sur un **seul composant sélectionné** dans l'explorateur IDz, contrairement au Builder qui traite l'intégralité du manifest.

---

## Vue d'ensemble

| Fonction | Pipeline | Effet sur l'environnement TU |
|---|---|---|
| Promote Unitaire | `PromoteUnitaire` | Ajoute / met à jour le composant |
| Clean Unitaire | `CleanUnitaire` | Retire le composant |

!!! abstract "Environnement cible fixe"
    Ces deux fonctions ciblent toujours l'environnement **TU** (Test Unitaire), quelle que soit la toolchain configurée. C'est une valeur fixe dans le code.

---

## Prérequis

- Un **fichier** (pas un dossier) sélectionné dans l'explorateur IDz
- Ce fichier doit être dans l'un des répertoires autorisés (voir ci-dessous), en tant que répertoire de **premier niveau** du projet
- Le projet doit contenir un manifest unique dans `META-INF/`
- Le [token Jenkins](configuration.md#jenkins-token) configuré

### Répertoires autorisés

```
asm  ast  cli  mps  msk  par  poe  skl  spn  src  srp  srt  srx
```

Un fichier dans `META-INF/`, `dex_read_only/`, `cpy/` ou tout autre répertoire est refusé.

---

## Promote Unitaire

**Accès :** Clic droit sur un fichier > Promote Unitaire

Promeut un seul composant vers l'environnement TU, sans builder l'intégralité du manifest.

### Construction du paramètre `commande`

Le plugin construit un objet JSON envoyé à Jenkins :

```json
{
  "appName": "da01",
  "version": "20250401-001",
  "site": "DEV",
  "couloir": "STDA",
  "environment": "TU",
  "componentType": ["LOD", "BGB", "DBR"],
  "component": "MONPROG"
}
```

| Champ | Source |
|---|---|
| `appName` | `application_code` dans le manifest |
| `version` | `manifest_number` dans le manifest |
| `site` | Propriété `deploy.site.name` du toolchain |
| `couloir` | Déduit de `application_type` : `STD`→`STDA`, `CRF`→`CRFA`, sinon valeur brute |
| `environment` | Toujours `TU` (valeur fixe) |
| `componentType` | Voir tableau ci-dessous |
| `component` | Nom du fichier **sans extension**, en **majuscules** |

### Correspondance répertoire → `componentType`

| Répertoire du fichier | `componentType` envoyé |
|---|---|
| `src` | `["LOD", "BGB", "DBR"]` |
| `srt` | `["LOT", "BGT", "DBR"]` |
| Tout autre répertoire | `["<REPERTOIRE_EN_MAJUSCULES>"]` |

**Exemples :**
- Fichier dans `asm/` → `["ASM"]`
- Fichier dans `skl/` → `["SKL"]`
- Fichier dans `src/` → `["LOD", "BGB", "DBR"]`

### Appel Jenkins

| Attribut | Valeur |
|---|---|
| Pipeline | `PromoteUnitaire` |
| Paramètre | `commande` = JSON ci-dessus (encodé URL) |
| HTTP | `POST <jenkins>/job/PromoteUnitaire/buildWithParameters?commande=<json>` |

---

## Clean Unitaire

**Accès :** Clic droit sur un fichier > Clean Unitaire

Retire un composant de l'environnement TU. Utile pour annuler un Promote Unitaire ou nettoyer entre deux séries de tests.

!!! info "Identique au Promote Unitaire, pipeline différent"
    Clean Unitaire utilise **exactement le même code** que Promote Unitaire (même handler `DeployHandler`, même validation, même JSON). La seule différence est le pipeline déclenché : `CleanUnitaire` au lieu de `PromoteUnitaire`.

| Attribut | Valeur |
|---|---|
| Pipeline | `CleanUnitaire` |
| Paramètre | `commande` = même JSON que Promote Unitaire |
| HTTP | `POST <jenkins>/job/CleanUnitaire/buildWithParameters?commande=<json>` |

---

## Erreurs communes

| Situation | Message |
|---|---|
| Fichier dans un répertoire non autorisé | "Le fichier XXX ne peut être candidat à un Promote/Clean Unitaire" |
| Répertoire non au premier niveau du projet | Même message |
| Aucun manifest ou manifests multiples | Avertissement ou erreur |
| Token Jenkins absent | Boîte de saisie automatique |
