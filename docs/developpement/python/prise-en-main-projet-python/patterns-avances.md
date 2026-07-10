# 3. Comprendre les patterns avancés

Cette page récapitule les techniques Python qui sortent des bases, en fiche
de référence courte à consulter au besoin plutôt qu'à mémoriser d'un coup.

## 3.1 Décorateurs Typer et sous-applications

pass-tool utilise trois décorateurs Typer (`@app.command()`,
`@vault_app.command(...)`, `@app.callback(invoke_without_command=True)`) et
deux sous-applications (`vault_app`, `entry_app`) pour structurer sa CLI —
déjà rencontrés au chapitre précédent
([2.2](lecture-du-code.md#22-declaration-des-objets-typer),
[2.7](lecture-du-code.md#27-mode-interactif)).

!!! info "Approfondissement dédié"
    Le mécanisme complet — pourquoi c'est `app` qu'on importe et jamais une
    fonction décorée isolément, ce qu'est un callback dans ce contexte, et
    pourquoi ce pattern décorateur + registre se retrouve dans la plupart
    des frameworks Python (Click, Flask, FastAPI, pytest...) — est traité
    en détail, avec le même exemple pass-tool, dans
    [CLI Python — Typer & Click](../cli/index.md) :

    - [L'objet `app`, callbacks et sous-commandes](../cli/typer-app.md)
    - [Le pattern décorateur + registre](../cli/decorateurs-registry.md)

Point pratique à retenir en une phrase : Typer déduit automatiquement les
options de la ligne de commande (`--length`, `--vault`, etc.) à partir des
**paramètres de la fonction** et de leurs annotations de type — pas de
déclaration séparée des arguments comme avec `argparse`.

---

## 3.2 `cast` : une instruction pour mypy, pas pour Python

Déjà vu au chapitre 2 ([2.1](lecture-du-code.md#21-en-tete-imports)), mais à
retenir comme principe général : `cast(T, valeur)` **ne transforme rien à
l'exécution** — il retourne `valeur` telle quelle. Son seul rôle est de dire
à `mypy` (l'outil de vérification statique de types) « traite cette valeur
comme étant de type `T` », dans des cas où mypy ne peut pas le déduire seul
(typiquement après un `json.loads()`, qui retourne toujours `Any`).

!!! tip "Vérifier par l'expérience"
    Si vous supprimez un `cast` pour voir ce qui se passe, le code
    fonctionnera toujours à l'exécution mais `mypy --strict` signalera une
    erreur de typage.

## 3.3 Syntaxe des types : `str | None`

Vous croiserez des annotations comme `vault: str | None = None`. C'est la
syntaxe moderne pour dire « une chaîne de caractères, ou rien » (équivalent
à l'ancien `Optional[str]`).

Cette syntaxe (`X | Y`) n'existe nativement qu'à partir de Python 3.10 : sur
une version antérieure, l'écrire telle quelle provoquerait une erreur à
l'exécution (`str` ne sait pas répondre à `|` avant 3.10). C'est le rôle de
la ligne en tête de `cli.py` :

```python
from __future__ import annotations
```

Elle dit à Python : « ne cherche pas à *exécuter* les annotations de type,
garde-les telles quelles, comme du texte, et ne les regarde que si un outil
(mypy, IDE) le demande explicitement ». Deux conséquences concrètes :

- `str | None` fonctionne dès Python 3.7, sans attendre la 3.10 — utile
  pour la compatibilité.
- Une classe peut référencer son propre nom dans une annotation
  (`def copier(self, autre: Utilisateur) -> None`) sans provoquer de
  `NameError`, puisque Python ne tente plus de résoudre `Utilisateur`
  immédiatement — utile en cas de
  [référence circulaire](../../glossaire.md#reference-circulaire) entre
  classes. pass-tool n'a qu'un seul fichier de fonctions et n'est pas
  concerné par ce cas précis ; la ligne y sert avant tout à la
  compatibilité `str | None`.

!!! note "Un mécanisme en transition"
    Différer l'évaluation des annotations (PEP 563) devait devenir le
    comportement par défaut de Python 3.10, mais ce projet a été abandonné
    en 2021 : trop d'outils (dataclasses, Pydantic…) avaient besoin des
    types réellement évalués à l'exécution. Un remplacement (PEP 649,
    prévu par défaut en Python 3.14) obtient un résultat comparable par un
    autre mécanisme. En attendant, `from __future__ import annotations`
    reste la façon explicite d'obtenir ce comportement.

## 3.4 Récapitulatif : le processus détaché du presse-papier

Déjà détaillé en
[2.5.1](lecture-du-code.md#251-comprendre-_spawn_clipboard_clearer) — on ne
le répète pas ici, mais c'est le pattern le plus subtil du fichier.

!!! warning "Avant de modifier le délai d'effacement"
    Une erreur ici (par exemple ajouter un `communicate()`) bloquerait
    pass-tool plusieurs secondes à chaque copie de mot de passe. Relisez
    impérativement 2.5.1 avant d'intervenir sur cette zone.

---

## Ce qu'il faut retenir de ce chapitre

Aucun de ces patterns n'est propre à pass-tool — ce sont des techniques
Python et Typer qu'on retrouve dans beaucoup de projets CLI modernes. Une
fois compris ici, ils se reconnaîtront ailleurs : c'est tout l'intérêt de
les isoler dans une fiche de référence courte plutôt que de les laisser
dilués dans la lecture du code source.

---

**Suite :** [4. Lire et comprendre les tests](tests.md)
