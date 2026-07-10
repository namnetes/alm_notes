# Glossaire du développement

Définitions courtes des termes de développeur employés tels quels dans les
guides de ce wiki — vocabulaire courant chez un développeur expérimenté,
mais pas toujours évident pour qui découvre un projet. Les pages du wiki
continuent d'utiliser ces mots normalement ; elles renvoient ici pour qui
en a besoin.

---

## Architecture en couches

Une façon d'organiser le code en niveaux (couches) qui ne communiquent
qu'avec leurs voisins directs — typiquement présentation → logique
métier → accès aux données. Chaque couche a une seule responsabilité et
ignore les détails d'implémentation des autres.

C'est utile pour les projets qui grossissent, mais ce n'est pas
systématique : un petit script ou un petit CLI peut très bien se
contenter de fonctions organisées par thème, sans couches du tout.

## Intégration continue (CI)

Un système qui exécute automatiquement les tests (et parfois le lint, le
typage…) à chaque `push` ou pull request, avant que le code ne soit
intégré à la branche principale. « CI » est l'abréviation de
*Continuous Integration*.

En l'absence de CI sur un projet, ces vérifications restent à la charge
du contributeur, généralement via un `Makefile` local (`make check`).

## Lint / linting

L'analyse automatique du code source pour détecter des erreurs de style,
du code mort ou des erreurs probables, **sans exécuter le programme**.
Dans l'écosystème Python de ce wiki, l'outil utilisé est `ruff`
(`uv run ruff check .`).

## Mock / mocker

Remplacer, le temps d'un test, un élément réel (un appel réseau, un
binaire externe, une écriture disque…) par un objet factice qui simule
son comportement attendu. Ça permet de tester une fonction sans dépendre
d'une ressource externe lente, indisponible ou risquée à exécuter
réellement.

```python
from unittest.mock import patch

with patch("pass_tool.cli.subprocess.run") as mock_run:
    mock_run.return_value.stdout = '{"result": "ok"}'
    # Le code testé « croit » avoir appelé pass-cli, sans l'avoir fait.
```

## Pattern (design pattern)

Une solution reconnue et nommée à un problème de conception qui revient
régulièrement — pas une bibliothèque à installer, mais une façon de
structurer du code que d'autres développeurs reconnaîtront
immédiatement (ex. Policy Pattern, Ports & Adapters, décorateur +
registre). Voir [Design Patterns](python/patterns/index.md) pour des
exemples détaillés.

## Référence circulaire

Une situation où le code fait référence à un nom (une classe, le plus
souvent) qui n'est pas encore complètement défini au moment où Python lit
la ligne — par exemple une méthode qui accepte en paramètre une instance
de sa propre classe. Sans précaution, ça provoque une `NameError`, car
Python évalue les annotations de type immédiatement, dans l'ordre du
fichier.

```python
class Utilisateur:
    def est_le_meme_que(self, autre: Utilisateur) -> bool:  # NameError
        return self.id == autre.id
```

Différer l'évaluation des annotations (`from __future__ import
annotations`) contourne le problème — voir
[3.3 Syntaxe des types](python/prise-en-main-projet-python/patterns-avances.md#33-syntaxe-des-types-str-none)
pour le détail.

## Typage statique

L'ajout d'annotations de type sur les paramètres et valeurs de retour
des fonctions (`def f(x: int) -> str:`), vérifiées par un outil dédié —
ici `mypy --strict` — **avant** l'exécution du programme. Ça permet
d'attraper des erreurs de type (passer un `str` là où un `int` est
attendu) sans avoir à lancer le code ni les tests.

## Workflow

L'enchaînement d'étapes suivi pour faire évoluer un projet : par
exemple créer une branche, coder, lancer les tests et le lint,
committer avec un message conventionnel, ouvrir une pull request. Un
« workflow de contribution » est donc la procédure à suivre pour
proposer une modification à un projet donné.
