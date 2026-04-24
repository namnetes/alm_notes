# Outils CLI

Un **outil** est un programme installé globalement sur votre système, accessible
depuis n'importe quel répertoire, comme `git`, `curl` ou `ruff`. Cette page
explique comment transformer un projet `uv` en outil de ce type.

---

## Projet vs Outil global

| | Projet (`uv run`) | Outil global (`uv tool install`) |
|---|---|---|
| Portée | Le répertoire du projet uniquement | Tout le système |
| Usage | Développement, tests | Utilisation quotidienne |
| Activation | `uv run commande` | `commande` directement |
| Environnement | `.venv/` dans le projet | `~/.local/share/uv/tools/nom/` |

!!! info "Quand choisir quoi ?"
    Pendant le développement, utilisez `uv run`. Une fois l'outil terminé et
    prêt à l'emploi, installez-le globalement avec `uv tool install .`. Les
    deux coexistent : vous pouvez continuer à développer avec `uv run` tout
    en ayant la version installée accessible globalement.

---

## Étape 1 — Déclarer un point d'entrée

Un **point d'entrée** (entry point) est le lien entre un nom de commande shell
et une fonction Python. Il se déclare dans `pyproject.toml` sous
`[project.scripts]`.

### Syntaxe

```toml
[project.scripts]
nom-commande = "nom_module.fichier:fonction"
```

| Partie | Signification |
|---|---|
| `nom-commande` | Ce que vous taperez dans le terminal |
| `nom_module` | Le nom du package Python (avec underscores) |
| `fichier` | Le nom du fichier Python (sans `.py`) |
| `fonction` | La fonction à appeler (souvent `main`) |

### Exemple complet

Pour un projet `mon-hello` dont le code est dans `src/mon_hello/main.py` :

```toml
[project]
name = "mon-hello"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
mon-hello = "mon_hello.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Et dans `src/mon_hello/main.py` :

```python
def main() -> None:
    print("Bonjour depuis mon-hello !")
```

!!! warning "La fonction doit exister et être importable"
    Si `uv tool install` réussit mais que la commande échoue avec
    `ImportError`, vérifiez que :
    - La fonction `main` est bien définie dans le fichier indiqué
    - Le module est importable (pas de faute de frappe dans le chemin)
    - Le `__init__.py` est présent dans le dossier du package

---

## Étape 2 — Tester le point d'entrée avant l'installation

Avant d'installer globalement, testez le point d'entrée dans le contexte
du projet :

```bash
uv run mon-hello
```

Si la commande fonctionne, le point d'entrée est correctement configuré.
Si elle échoue, corrigez le problème avant de passer à l'installation globale.

---

## Étape 3 — Installer l'outil globalement

```bash
uv tool install .
```

Le point `.` signifie « le projet dans le répertoire courant ».

Sortie attendue :

```
Resolved 1 package in 10ms
Installed mon-hello v0.1.0
Installed 1 executable: mon-hello
```

`uv` crée deux choses :
1. Un **environnement isolé** dans `~/.local/share/uv/tools/mon-hello/`
2. Un **shim** dans `~/.local/bin/mon-hello`

### Ce qu'est un shim

Un shim est un petit script exécutable qui fait le lien entre votre terminal
et le vrai programme dans son environnement isolé :

```
Vous tapez : mon-hello
      ↓
~/.local/bin/mon-hello   ← le shim (quelques lignes)
      ↓
~/.local/share/uv/tools/mon-hello/bin/mon-hello   ← le vrai programme
      ↓
Résultat affiché
```

!!! info "Pourquoi passer par un shim ?"
    Le shim permet à votre commande de fonctionner depuis n'importe quel
    répertoire, sans que vous ayez à connaître ni activer l'environnement
    isolé dans lequel le programme vit.

---

## Étape 4 — Vérifier l'installation

```bash
# Vérifier que le shim est bien en place
which mon-hello

# Lancer depuis n'importe quel répertoire
cd /tmp
mon-hello
```

```
Bonjour depuis mon-hello !
```

---

## Gérer les outils installés

### Lister les outils installés

```bash
uv tool list
```

Exemple de sortie :

```
devinit v0.1.0
 - devinit
mon-hello v0.1.0
 - mon-hello
```

### Mettre à jour un outil après modification

Pendant le développement, après avoir modifié le code :

```bash
uv tool install . --force
```

Le `--force` réinstalle même si le numéro de version n'a pas changé.

!!! tip "Alias pratique"
    Si vous mettez souvent à jour un outil en cours de développement,
    ajoutez un alias dans votre `.bash_aliases` :
    ```bash
    alias reinstall='uv tool install . --force'
    ```

### Désinstaller un outil

```bash
uv tool uninstall mon-hello
```

Cette commande supprime :
- L'environnement isolé dans `~/.local/share/uv/tools/mon-hello/`
- Le shim dans `~/.local/bin/mon-hello`

Vérifiez que la commande a bien disparu :

```bash
which mon-hello   # ne doit plus rien retourner
mon-hello         # doit afficher "command not found"
```

### Nettoyer le cache

`uv` maintient un cache des paquets téléchargés pour accélérer les
prochaines installations. Pour libérer de l'espace disque :

```bash
uv cache clean
```

---

## Plusieurs commandes dans un même projet

Un projet peut exposer plusieurs commandes. Déclarez-les toutes dans
`[project.scripts]` :

```toml
[project.scripts]
meteo       = "meteo_cli.main:main"
meteo-hist  = "meteo_cli.historique:main"
meteo-carte = "meteo_cli.carte:main"
```

Chaque commande génère son propre shim dans `~/.local/bin/`.

---

## Exercice guidé — de zéro à la commande globale

Cet exercice crée un outil `bonjour` qui affiche un message personnalisé.

**Étape 1 : Créer et initialiser le projet**

```bash
mkdir ~/projets/bonjour && cd ~/projets/bonjour
uv init --app bonjour
```

**Étape 2 : Ajouter une dépendance**

```bash
uv add typer
```

**Étape 3 : Écrire le code**

Remplacez le contenu de `src/bonjour/main.py` :

```python
import typer

app = typer.Typer()


@app.command()
def main(
    nom: str = typer.Argument(default="Monde"),
    majuscules: bool = typer.Option(False, "--maj", help="Mettre en majuscules"),
) -> None:
    """Affiche un message de bienvenue."""
    message = f"Bonjour, {nom} !"
    if majuscules:
        message = message.upper()
    print(message)
```

**Étape 4 : Déclarer le point d'entrée**

Ajoutez dans `pyproject.toml` :

```toml
[project.scripts]
bonjour = "bonjour.main:app"
```

**Étape 5 : Tester dans le projet**

```bash
uv run bonjour
uv run bonjour Alice
uv run bonjour Alice --maj
```

Résultats attendus :

```
Bonjour, Monde !
Bonjour, Alice !
BONJOUR, ALICE !
```

**Étape 6 : Installer globalement**

```bash
uv tool install .
```

**Étape 7 : Tester depuis n'importe où**

```bash
cd ~
bonjour
bonjour "Alan" --maj
```

**Étape 8 : Vérifier dans l'inventaire**

```bash
uv tool list
which bonjour
```

**Étape 9 : Désinstaller**

```bash
uv tool uninstall bonjour
bonjour   # doit afficher "command not found"
```

!!! tip "Aide automatique avec typer"
    `typer` génère automatiquement une aide en ligne de commande.
    Testez : `bonjour --help`
