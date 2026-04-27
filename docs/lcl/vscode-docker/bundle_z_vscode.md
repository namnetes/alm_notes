
---

# Expression de Besoin : Environnement de Développement Isolé sous Docker

## 1. Contexte du projet
L'objectif est de mettre en place un environnement de développement complet, portable et totalement isolé sur une machine hôte **macOS (architecture Apple Silicon M4)**. Cet environnement doit permettre la génération de projets et le développement sans installer de dépendances directement sur le système d'exploitation macOS.

## 2. Objectifs techniques
* **Isolation stricte :** Toutes les couches logicielles (IDE, runtimes, outils de build) doivent être encapsulées dans une image Docker.
* **Compatibilité ARM64 :** L'image doit être optimisée pour tirer parti des performances de la puce M4.
* **Zéro résidu :** La suppression du conteneur doit entraîner la disparition de tous les outils de développement de la machine hôte.

## 3. Spécifications fonctionnelles

### A. Runtimes et Outils

* **Java :** Installation du dernier JDK LTS (Java 25) requis exclusivement pour le fonctionnement des extensions VS Code Java (Language Support, Debugger). Aucun outil de build (Maven, Gradle) n'est nécessaire.

* **Python :** Installation de la dernière version stable de Python 3.
  > ⚠️ **Version à confirmer** par l'équipe projet avant la construction de l'image.
  * Un fichier de configuration **`ruff.toml`** doit être inclus dans l'image et positionné dans le répertoire de travail par défaut de l'utilisateur (`/home/zdev/`). Ce fichier définit les règles de linting et de formatage utilisées par l'extension Ruff dans VS Code.

* **Node.js et npm :** Installation de la version LTS 24.15.0 pour la gestion des dépendances frontend/backend.

* **NPM Global :** Installation du package Zowe CLI : `npm install -g @zowe/cli@zowe-v3-lts`

* **Plugins Zowe :** Trois plugins doivent être installés après l'installation de Zowe CLI :
  ```
  zowe plugins install @zowe/cics-for-zowe-cli@zowe-v3-lts
  zowe plugins install @zowe/mq-for-zowe-cli@zowe-v3-lts
  zowe plugins install @zowe/zos-ftp-for-zowe-cli@zowe-v3-lts
  ```

### B. Environnement de Développement (IDE)

* **VS Code intégré :** Intégration de `code-server` pour accéder à VS Code via un navigateur web en HTTP (usage local uniquement).

* **Extensions pré-configurées :** L'image doit inclure nativement :
    * Language Support for Java (Red Hat)
    * Debugger for Java (Microsoft)
    * ESLint
    * Even Better TOML
    * JSON Tools
    * Ruff
    * Python Environment Manager (Microsoft)
    * Python Debugger (Microsoft)
    * Python (Microsoft)
    * GitHub Copilot Chat
    * Rainbow CSV
    * YAML (Red Hat)

* **Utilisateur dédié :** Création d'un utilisateur non-root `zdev` avec **zsh** comme shell par défaut, pour garantir la sécurité et la cohérence des droits de fichiers avec macOS.

### C. Gestion Réseau et Proxy

* **Proxy d'entreprise :** L'intégralité de l'environnement (VS Code, NPM, Git, Terminal, GitHub Copilot) doit être configurée pour passer par le proxy d'entreprise.
  * Adresse du proxy : `1111.1111.1111.1111:8080`
  * Ce proxy s'applique également au trafic **GitHub Copilot** dans VS Code (paramètre `http.proxy` dans les settings de code-server).

* **Paramétrage dynamique :** L'adresse du proxy doit pouvoir être surchargée en tant qu'argument au moment de la construction (`--build-arg`) ou de l'exécution (`-e` / `env`), pour faciliter les évolutions futures sans reconstruction complète de l'image.

  > ⚠️ **À confirmer :** Le proxy nécessite-t-il une authentification (login / mot de passe) ? Si oui, le mécanisme de transmission sécurisée des credentials doit être défini (secret Docker, variable d'environnement chiffrée, etc.).

## 4. Gestion des données et déploiement

* **Persistence locale :** Les projets générés à l'intérieur du conteneur doivent être accessibles sur le disque du Mac via des **volumes Docker**.

* **Capacité Remote :** L'environnement doit permettre la connexion à des serveurs distants via SSH pour le déploiement ou l'édition de fichiers "off-host".
  > ⚠️ **À confirmer :** Les clés SSH sont-elles montées depuis le Mac (volume) ou générées dans le conteneur ? Une politique de gestion des clés doit être définie.

* **Profils Zowe :** Les profils de connexion Zowe (z/OS hostname, port, credentials) ne doivent pas être gravés dans l'image. Le mécanisme d'injection (volume monté, variable d'environnement, fichier de configuration externe) est à définir.
  > ⚠️ **À confirmer** par l'équipe projet.

* **Distribution :** L'image est construite par l'équipe support et déployée sur les postes utilisateurs via **SCCM**. Le processus de mise à jour de l'image (versioning, registry interne éventuel) est à définir.

## 5. Contraintes de performance

* Utilisation du moteur de virtualisation natif de macOS (VirtioFS recommandé).
* Optimisation du temps de build via l'utilisation de caches de couches Docker pour les dépendances lourdes (JDK, Node.js).

---

### Résumé des composants clés

| Composant        | Technologie retenue                        |
| :--------------- | :----------------------------------------- |
| **Hôte**         | macOS M4 (ARM64)                           |
| **Conteneur**    | Docker (Image Debian, base ARM64)          |
| **IDE**          | code-server (VS Code navigateur, HTTP)     |
| **Langages**     | JDK 25 LTS · Node.js 24.15.0 LTS · Python 3 (version à confirmer) |
| **CLI Mainframe**| Zowe CLI v3-LTS + plugins CICS, MQ, z/OS FTP |
| **Shell**        | zsh (utilisateur `zdev`)                   |
| **Proxy**        | `1111.1111.1111.1111:8080`                 |
| **Accès**        | Navigateur Web (http://localhost:8443)     |
| **Déploiement**  | Image buildée par support, diffusée via SCCM |

---

### Points ouverts (à confirmer avant construction)

| # | Question                                                                 | Impact                          |
|---|--------------------------------------------------------------------------|---------------------------------|
| 1 | Version Python 3 cible ?                                                 | Contenu de l'image              |
| 2 | Le proxy nécessite-t-il une authentification ?                           | Sécurité / secrets              |
| 3 | Gestion des clés SSH : volume depuis le Mac ou génération dans le conteneur ? | Sécurité / persistance     |
| 4 | Injection des profils Zowe : volume, env var, ou fichier externe ?       | Sécurité / persistance          |
| 5 | Mot de passe d'accès à code-server : variable d'env, fichier fixe ?      | Sécurité / déploiement          |
| 6 | Registry interne pour l'image (Nexus, Harbor, etc.) ou livraison directe ? | Pipeline de distribution      |

---
