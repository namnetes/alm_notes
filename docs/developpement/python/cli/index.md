# CLI Python — Typer & Click

Comment sont construites les interfaces en ligne de commande (CLI) modernes
en Python — l'objet applicatif central, les callbacks, et le pattern de
décorateurs qui les enregistre. Ce chapitre part d'un exemple réel du dépôt
(`pass-tool`) pour expliquer des mécanismes qui déroutent souvent un
débutant : pourquoi on importe `app` et jamais la fonction qu'on vient
d'écrire, ce qu'est un « callback » dans ce contexte, et pourquoi ce pattern
revient partout en Python.

---

## Pourquoi un framework CLI plutôt que `sys.argv` à la main ?

Une CLI doit gérer bien plus que "lire les mots après le nom du programme" :

- parser les options (`--length 20`, `-l 20`), leurs types (`int`, `bool`,
  `str | None`), leurs valeurs par défaut
- gérer les sous-commandes (`pass-tool vault list` vs `pass-tool entry list`)
- générer automatiquement `--help`
- produire des messages d'erreur cohérents et des codes de sortie corrects
- gérer l'autocomplétion shell

Réimplémenter tout ça à la main avec `sys.argv` est possible mais fastidieux
et fragile. D'où l'usage systématique d'un framework dédié.

## argparse, Click, Typer — panorama rapide

| Framework | Style | Boilerplate | Basé sur les type hints |
|---|---|---|---|
| `argparse` (stdlib) | Impératif — on construit un `ArgumentParser` à la main | Élevé | Non |
| `Click` | Décoratif — `@click.command()`, `@click.option()` | Moyen | Non (types déclarés via `type=`) |
| `Typer` | Décoratif — construit **au-dessus de Click** | Faible | Oui — la signature de la fonction *est* la spec CLI |

`pass-tool` utilise **Typer** : chaque paramètre de fonction avec son type
hint (`length: int`, `clip: bool`) devient automatiquement une option de
ligne de commande, sans déclaration séparée.

!!! info "Typer et Click ne sont pas concurrents"
    Typer est un générateur qui construit un objet Click en coulisses. Tout
    ce que Click sait faire (groupes de commandes, aide auto-générée,
    gestion des erreurs) est hérité par Typer — Typer ajoute la couche
    "type hints → CLI" par-dessus.

---

## Dans ce chapitre

<div class="grid cards" markdown>

-   :material-application-cog-outline: **[L'objet `app`, callbacks et sous-commandes](typer-app.md)**

    Pourquoi `app` (et pas une fonction) est le vrai point d'entrée, ce
    qu'est un callback dans ce contexte, comment les sous-commandes
    s'assemblent.

-   :material-decagram-outline: **[Le pattern décorateur + registre](decorateurs-registry.md)**

    Généralisation : le même mécanisme se retrouve dans Click, Flask,
    FastAPI, pytest, Django admin — pourquoi ce pattern est si répandu en
    Python.

</div>

---

## Exemple de référence utilisé dans ce chapitre

Tous les extraits de code viennent du projet réel `pass-tool` du dépôt
`alm_tools` :

**Source :** `~/alm_tools/cli/pass-tool/src/pass_tool/cli.py`

Documentation utilisateur de cet outil :
[pass-tool](../../../systeme/ubuntu/alm_tools/outils/pass-tool.md).
