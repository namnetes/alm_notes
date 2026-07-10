# Prise en main d'un projet Python pour y contribuer

Une méthode pour se repérer rapidement dans un petit projet Python inconnu,
jusqu'à pouvoir y apporter une modification en confiance. Les six chapitres
suivants suivent une progression volontairement réutilisable : vue
d'ensemble → mise en route → lecture du code → patterns → tests → workflow.

!!! info "Méthode générique, illustrée par un cas réel"
    Chaque étape est démontrée sur un projet réel du dépôt, **pass-tool**
    (`~/alm_tools/cli/pass-tool`) — un petit CLI Python d'une dizaine de
    fichiers. pass-tool sert de fil rouge concret du début à la fin, mais
    la démarche se transpose telle quelle à n'importe quel autre petit
    projet Python : les questions à se poser sont les mêmes, seules les
    réponses changent d'un projet à l'autre.

---

## Objectif

Ce guide s'adresse à un développeur qui connaît les bases de Python
(syntaxe, fonctions, structures de données) mais découvre **un projet
précis**. Il ne couvre pas Python en général, ni Git, ni l'usage courant de
pass-tool en tant qu'utilisateur final (voir
[pass-tool — documentation utilisateur](../../../systeme/ubuntu/alm_tools/outils/pass-tool.md)
pour ça).

À la fin de ce guide, vous devriez être capable de :

- comprendre l'organisation du code d'un projet inconnu et vous y repérer
  seul,
- lancer ses tests et ses outils de qualité
  ([lint](../../glossaire.md#lint-linting),
  [typage](../../glossaire.md#typage-statique)) en local,
- identifier où intervenir pour apporter une modification donnée,
- suivre un [workflow](../../glossaire.md#workflow) de contribution
  structuré, même sans [CI](../../glossaire.md#integration-continue-ci)
  en place.

---

## Vue d'ensemble en 30 secondes (le projet utilisé comme fil rouge)

pass-tool est un petit outil en ligne de commande (CLI) qui encapsule le
binaire `pass-cli` (Proton Pass) pour simplifier des opérations courantes :
génération de mots de passe, listage de coffres et d'entrées, copie
sécurisée dans le presse-papier avec effacement automatique.

Quelques repères de taille et de structure :

- **~850 lignes de code Python** au total, dont l'essentiel dans un seul
  fichier (`src/pass_tool/cli.py`) qui concentre toute la logique métier.
- Pas d'[architecture en couches](../../glossaire.md#architecture-en-couches),
  pas de classes complexes : essentiellement des fonctions, organisées par
  thème (génération de mot de passe, coffres, entrées, presse-papier).
- **~300 lignes de tests**, un fichier par thématique, qui simulent
  (« [mockent](../../glossaire.md#mock-mocker) ») les appels au binaire
  `pass-cli` plutôt que de l'exécuter réellement.
- Outillage : `uv` (environnement + dépendances), Typer + Rich (CLI),
  pytest (tests), ruff (lint/format), mypy `--strict` (typage).

Le point important à retenir, et qui vaut pour beaucoup de petits projets :
**il n'y a pas forcément d'architecture à apprendre**. Ici, la difficulté
n'est pas dans la structure du projet (simple) mais dans quelques
techniques Python un peu avancées utilisées à l'intérieur d'un seul
fichier. On les détaille au chapitre 3.

---

## Les six chapitres

<div class="grid cards" markdown>

-   :material-rocket-launch: **[1. Mise en route technique](mise-en-route.md)**

    Installer, lancer les tests, vérifier le style et le typage — avant
    même d'ouvrir le code.

-   :material-file-code-outline: **[2. Lire le code section par section](lecture-du-code.md)**

    Découper un fichier par zone fonctionnelle plutôt que de le lire dans
    l'ordre d'écriture.

-   :material-decagram-outline: **[3. Comprendre les patterns avancés](patterns-avances.md)**

    Les techniques Python qui sortent des bases, en fiche de référence
    courte. Voir aussi la définition de
    [pattern](../../glossaire.md#pattern-design-pattern) dans le glossaire.

-   :material-flask-outline: **[4. Lire et comprendre les tests](tests.md)**

    Le mécanisme de mock, `runner.invoke`, et comment lancer un test isolé.

-   :material-source-branch-check: **[5. Le workflow de contribution](workflow-et-exercice.md)**

    Makefile, pre-commit, cycle recommandé, convention de commit — et un
    exercice pratique.

-   :material-map-marker-path: **[6. Où trouver quoi](reference.md)**

    Index rapide : fichiers du projet, documentation existante, pièges
    connus.

</div>

---

## Voir aussi

- [CLI Python — Typer & Click](../cli/index.md) — approfondissement des
  patterns Typer (décorateurs, callbacks, sous-apps) évoqués au chapitre 3,
  avec le même exemple pass-tool.
- [pass-cli en Python — subprocess et JSON](../pass-cli-subprocess.md) —
  patterns génériques de communication avec `pass-cli` via `subprocess`.
