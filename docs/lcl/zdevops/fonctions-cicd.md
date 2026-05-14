# Pipelines CI/CD

Les fonctions Builder, Déployer et Audit déclenchent des pipelines Jenkins **FabCI** en passant le nom du manifest comme paramètre. Le plugin ne contient aucune logique de compilation ou de déploiement — tout est délégué à Jenkins.

!!! tip "Infrastructure Jenkins"
    Voir [Infrastructure Jenkins](infrastructure-jenkins.md) pour le détail complet des URLs FabCI, du protocole REST et de la mécanique de polling.

---

## Prérequis communs

- Un projet sélectionné dans l'explorateur IDz (ou fichier ouvert dans l'éditeur)
- Un manifest unique dans `META-INF/`
- Le [token Jenkins](configuration.md#jenkins-token) configuré — si absent, la boîte de saisie s'ouvre automatiquement

---

## Builder

**Raccourci :** `Ctrl+0` — Menu : zDevOps > Builder

Déclenche la **compilation** de tous les composants listés dans le manifest de l'évolution courante.

| Attribut | Valeur |
|---|---|
| Pipeline Jenkins | `BuildAndPush` |
| Paramètre | `NomManifest` = nom du manifest sans `.mf.json` |
| Appel HTTP | `POST <jenkins>/job/BuildAndPush/buildWithParameters?NomManifest=<nom>` |

### Séquence

```
1. Vérification du token Jenkins (saisie si absent)
2. Lecture du manifest dans META-INF/ → nom sans extension
3. POST vers Jenkins → HTTP 201 + URL de file d'attente
4. Polling file d'attente → URL du build
5. Ouverture vue Blue Ocean dans IDz
6. Polling du build toutes les 2s jusqu'à building=false
```

---

## Déployer

**Raccourci :** `Ctrl+B` — Menu : zDevOps > Déployer

Installe les composants compilés dans l'**environnement cible** (recette, production…). Déclenche le pipeline de Continuous Deployment.

| Attribut | Valeur |
|---|---|
| Pipeline Jenkins | `ProxyCD` |
| Paramètre | `NomManifest` = nom du manifest sans `.mf.json` |
| Appel HTTP | `POST <jenkins>/job/ProxyCD/buildWithParameters?NomManifest=<nom>` |

!!! note "Vue maximisée"
    Quand le pipeline déclenché est `ProxyCD`, la vue Jenkins Blue Ocean est affichée automatiquement en **mode maximisé** dans IDz pour une meilleure lisibilité des logs de déploiement.

!!! warning "Prérequis non vérifié"
    Le plugin ne vérifie pas qu'un build réussi a été effectué avant le déploiement. C'est à la charge du développeur.

---

## Audit

**Raccourci :** `Ctrl+6` — Menu : zDevOps > Audit

Déclenche une **analyse qualité** du code source de l'évolution. Produit un rapport Jenkins.

| Attribut | Valeur |
|---|---|
| Pipeline Jenkins | `auditEtQualite` |
| Paramètre | `NomManifest` = nom du manifest sans `.mf.json` |
| Appel HTTP | `POST <jenkins>/job/auditEtQualite/buildWithParameters?NomManifest=<nom>` |

---

## Tableau récapitulatif

| Fonction | Pipeline | Paramètre | Raccourci |
|---|---|---|---|
| Builder | `BuildAndPush` | `NomManifest` | `Ctrl+0` |
| Déployer | `ProxyCD` | `NomManifest` | `Ctrl+B` |
| Audit | `auditEtQualite` | `NomManifest` | `Ctrl+6` |

---

## Erreurs communes

| Situation | Message |
|---|---|
| Aucun projet sélectionné | "Veuillez sélectionner un projet dans l'explorateur" |
| Token Jenkins absent (et non saisi) | "Merci de générer et renseigner votre token Jenkins" |
| Job Jenkins introuvable | "Aucun job Jenkins trouvé avec le nom : BuildAndPush" |
| Échec HTTP lors du déclenchement | "Échec du lancement du job Jenkins : …" |
| Build non démarré après 60s | "Le build n'a pas démarré après 60 secondes" |
