# Plugin zDevOps IDz

Plugin Eclipse RCP intégré dans **IDz (IBM Developer for z/OS)** qui automatise les opérations DevOps mainframe LCL : gestion des évolutions GitLab, build, déploiement et audit via Jenkins FabCI.

---

## Architecture du plugin

### Type et build

| Attribut | Valeur |
|---|---|
| Type | Plugin OSGi / Eclipse RCP |
| IDE cible | IBM Developer for z/OS (IDz) |
| Langage | Java 17 |
| Build | Maven + Tycho 4.0.8 |
| Version | 2.0.1-SNAPSHOT |
| Plugin ID | `fr.lcl.zdevops.idz.plugin` |

```bash
# Build complet (avec miroirs internes)
mvn clean package -s settings.xml -U \
  -Dmaven.wagon.http.ssl.insecure=true \
  -Dmaven.wagon.http.ssl.allowall=true
```

Le JAR produit : `plugin/target/zdevops.idz-plugin*.jar`

### Structure des modules Maven

| Module | Rôle |
|---|---|
| `plugin/` | Plugin principal — toute la logique métier et l'UI |
| `feature/` | Packaging Eclipse feature |
| `fragment/` | Fragment Windows x86\_64 |
| `site/` | Site de mise à jour p2 pour la distribution |

### Organisation du code

```
plugin/src/fr/lcl/zdevops/idz/plugin/
├── Activator.java           # Point d'entrée OSGi
├── config/                  # ConfigLoader — lit zdevops.ini
├── services/                # Couche métier
│   ├── IGitLabService.java
│   ├── IGitService.java
│   ├── impl/GitLabService.java
│   ├── impl/GitService.java
│   └── JenkinsJobService.java
├── ui/
│   ├── handlers/            # 13 handlers (un par commande)
│   ├── dialogs/             # Boîtes de dialogue SWT/JFace
│   ├── views/               # JenkinsBrowserView, arbres
│   ├── monitors/            # Jobs de progression (clone, push…)
│   └── models/              # Modèles de données (ManifestModel…)
├── utils/                   # 7 classes utilitaires
└── exceptions/              # Hiérarchie d'exceptions métier
```

### Concepts clés

!!! abstract "Évolution"
    Unité de travail représentée par une branche Git `feature_<nom>` dans GitLab. Toute modification de code source doit se faire dans une évolution.

!!! abstract "Manifest (`.mf.json`)"
    Fichier JSON dans `META-INF/` qui décrit l'évolution : code application, type (BATCH/TP), liste des fichiers à builder, dépendances vers d'autres évolutions.

!!! abstract "Code application"
    Identifiant de 4 caractères du dépôt GitLab (`daXX` pour BATCH, `dyXX` pour TP).

!!! abstract "Toolchain"
    Environnement cible sélectionné dans `zdevops.ini` : `dev`, `rec`, `frm` ou `prd`. Détermine les URLs GitLab et Jenkins utilisées.

!!! abstract "FabCI"
    Infrastructure Jenkins interne LCL (Fabrique CI/CD). Toute la compilation, le déploiement et l'audit sont délégués à ses pipelines — le plugin ne contient aucune logique de compilation.

---

## Fonctions du plugin

### Gestion des évolutions

| # | Fonction | Raccourci | Description |
|---|---|---|---|
| 1 | [Démarrer une évolution](fonctions-evolutions.md#demarrer-une-evolution) | `Ctrl+1` | Crée une branche `feature_XXX` dans GitLab et clone le dépôt dans IDz |
| 2 | [Participer à une évolution](fonctions-evolutions.md#participer-a-une-evolution) | `Ctrl+2` | Rejoint une évolution existante (clone ou bascule de branche) |
| 3 | [Évolution depuis une évolution](fonctions-evolutions.md#evolution-depuis-une-evolution) | `Ctrl+8` | Crée une nouvelle branche depuis une `feature_` existante |
| 4 | [Consulter les sources](fonctions-evolutions.md#consulter-les-sources) | `Ctrl+9` | Clone un dépôt sur `master` en lecture seule |

### Gestion du manifest

| # | Fonction | Raccourci | Description |
|---|---|---|---|
| 5 | [Mettre à jour les copybooks](fonctions-manifest.md#mettre-a-jour-les-copybooks) | `Ctrl+4` | Télécharge les copybooks externes dans `dex_read_only/` |
| 6 | [Gérer les composants](fonctions-manifest.md#gerer-les-composants-du-manifest) | `Ctrl+5` | Sélectionne les fichiers sources à inclure dans le manifest |
| 7 | [Gérer les dépendances](fonctions-manifest.md#gerer-les-dependances-du-manifest) | `Ctrl+7` | Déclare les dépendances vers d'autres évolutions |

### Pipelines CI/CD

| # | Fonction | Raccourci | Pipeline Jenkins |
|---|---|---|---|
| 8 | [Builder](fonctions-cicd.md#builder) | `Ctrl+0` | `BuildAndPush` |
| 9 | [Déployer](fonctions-cicd.md#deployer) | `Ctrl+B` | `ProxyCD` |
| 10 | [Audit](fonctions-cicd.md#audit) | `Ctrl+6` | `auditEtQualite` |

### Déploiement unitaire

| # | Fonction | Accès | Pipeline Jenkins |
|---|---|---|---|
| 11 | [Promote Unitaire](fonctions-unitaire.md#promote-unitaire) | Clic droit sur un fichier | `PromoteUnitaire` |
| 12 | [Clean Unitaire](fonctions-unitaire.md#clean-unitaire) | Clic droit sur un fichier | `CleanUnitaire` |

### Configuration

| # | Fonction | Raccourci | Description |
|---|---|---|---|
| 13 | [GitLab Token](configuration.md#gitlab-token) | `Ctrl+E` | Stockage sécurisé du token GitLab personnel |
| 14 | [Jenkins Token](configuration.md#jenkins-token) | `Ctrl+K` | Stockage sécurisé du token Jenkins (par toolchain) |

---

## Pages

| Page | Description |
|---|---|
| [Gestion des évolutions](fonctions-evolutions.md) | Fonctions 1 à 4 : démarrer, participer, bifurquer, consulter |
| [Gestion du manifest](fonctions-manifest.md) | Fonctions 5 à 7 : copybooks, composants, dépendances |
| [Pipelines CI/CD](fonctions-cicd.md) | Fonctions 8 à 10 : build, déploiement, audit qualité |
| [Déploiement unitaire](fonctions-unitaire.md) | Fonctions 11 et 12 : promote et clean sur un seul composant |
| [Configuration](configuration.md) | Fonctions 13 et 14 : tokens GitLab et Jenkins |
| [Infrastructure Jenkins](infrastructure-jenkins.md) | FabCI, pipelines, protocole d'appel REST, paramètres |
