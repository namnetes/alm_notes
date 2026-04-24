# uv — Gestionnaire de projets Python

## Un outil pour les gouverner tous

Avant `uv`, gérer un projet Python exigeait de jongler avec plusieurs outils :
`pip` pour les paquets, `venv` pour les environnements virtuels, `pyenv` pour
les versions de Python, `poetry` ou `pip-tools` pour le lock file…

`uv` remplace tout cela avec un seul binaire, écrit en Rust, jusqu'à 100 fois
plus rapide que `pip`, et dont l'interface est volontairement simple.

| Ancienne commande | Équivalent `uv` |
|---|---|
| `pip install requests` | `uv add requests` |
| `python -m venv .venv` | automatique avec `uv` |
| `pip freeze > requirements.txt` | `uv.lock` (généré automatiquement) |
| `pyenv install 3.12` | `uv python install 3.12` |
| `pip install -e .` | `uv tool install .` |

---

## Concepts clés avant de commencer

### Projet vs Outil

`uv` distingue deux usages :

| Concept | Description | Commandes |
|---|---|---|
| **Projet** | Code en cours de développement, avec son propre venv | `uv init`, `uv add`, `uv run` |
| **Outil** | Programme installé globalement, accessible partout | `uv tool install`, `uv tool list` |

Un projet devient un outil quand il est installé avec `uv tool install`.

### L'environnement virtuel automatique

`uv` crée et gère automatiquement un environnement virtuel `.venv` à la racine
de votre projet. **Vous n'avez jamais besoin de l'activer manuellement.**
`uv run` s'en charge.

!!! info "Pourquoi un environnement virtuel ?"
    Sans environnement virtuel, les paquets Python s'installent dans le système.
    Deux projets qui dépendent de versions différentes d'une même bibliothèque
    entrent alors en conflit. Le `.venv` isole chaque projet dans sa propre bulle.

### Le fichier de verrouillage `uv.lock`

Quand vous ajoutez une dépendance, `uv` génère un fichier `uv.lock` qui note
la version exacte de chaque paquet installé (et de leurs propres dépendances).
Ce fichier garantit que votre projet fonctionnera identiquement sur une autre
machine, en CI, ou dans six mois.

!!! tip "Committez toujours `uv.lock`"
    Le fichier `uv.lock` doit être versionné dans git. C'est lui qui assure
    la reproductibilité du projet.

---

## Installation

Le script officiel installe `uv` dans `~/.local/bin/` :

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Rechargez votre shell pour que le `PATH` soit mis à jour :

```bash
source ~/.bashrc
```

Vérifiez l'installation :

```bash
uv --version
```

Attendu : `uv 0.x.x (...)` — si la commande est reconnue, `uv` est opérationnel.

!!! info "Emplacement du binaire"
    `uv` est installé dans `~/.local/bin/uv`. Ce répertoire doit être dans
    votre `PATH`. Vérifiez avec :
    ```bash
    echo $PATH | tr ':' '\n' | grep local
    ```
    Si `~/.local/bin` n'apparaît pas, ajoutez cette ligne à `~/.bashrc` :
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```

### Gérer les versions de Python

`uv` peut installer et gérer les versions de Python indépendamment du système :

```bash
# Voir les versions disponibles
uv python list

# Installer Python 3.12
uv python install 3.12

# Utiliser Python 3.12 dans un projet
uv python pin 3.12
```

!!! note "Python du système vs Python géré par uv"
    `uv` peut utiliser le Python installé sur votre système ou en installer
    un lui-même dans `~/.local/share/uv/python/`. Les deux coexistent sans
    conflit.

### Mise à jour de `uv`

```bash
uv self update
```

---

## Structure de la documentation

| Page | Contenu |
|---|---|
| [Workflow projet](projet.md) | Initialiser, développer, ajouter des dépendances, exécuter |
| [Outils CLI](outils.md) | Créer une commande globale, shims, installation, désinstallation |
| [Référence](reference.md) | Cheat sheet, inventaire des fichiers, erreurs fréquentes |
