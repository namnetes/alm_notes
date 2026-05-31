# Installation

## Dépendances système

Ces paquets sont nécessaires avant d'installer quoi que ce soit avec Python.
La commande est idempotente (sans effet si le paquet est déjà installé) :

```bash
sudo apt update && sudo apt install -y \
    python3 \
    python3-venv \
    curl \
    git
```

| Paquet | Rôle |
|---|---|
| `python3` | Interpréteur Python (MkDocs est écrit en Python) |
| `python3-venv` | Crée des environnements Python isolés |
| `curl` | Télécharge l'installateur de `uv` |
| `git` | Versionner le code source et la documentation |

!!! warning "Ne pas utiliser `apt install python3-mkdocs`"
    Ubuntu 24.04 propose un paquet `python3-mkdocs` dans ses dépôts officiels,
    mais il installe une version ancienne et partagée entre tous les projets.
    **Préférez toujours une installation par projet avec `uv`** : chaque
    projet garde sa propre version de MkDocs, sans conflit.

---

## Installer `uv`

`uv` est un gestionnaire de paquets Python ultra-rapide écrit en Rust.
Il remplace `pip`, `virtualenv` et `pip-tools` en un seul outil.

```bash
# Télécharger et exécuter l'installateur officiel
curl -LsSf https://astral.sh/uv/install.sh | sh

# Recharger le PATH pour que la commande uv soit disponible
source "$HOME/.local/bin/env"

# Vérifier l'installation
uv --version
# → uv 0.x.x (...)
```

!!! tip "Rendre `uv` disponible dans tous les terminaux"
    L'installateur ajoute automatiquement `uv` à votre `~/.bashrc`.
    Si la commande n'est pas trouvée dans un nouveau terminal :

    ```bash
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    ```

---

## Ajouter MkDocs à un projet Python existant

### Initialiser un projet avec `uv` (si nécessaire)

```bash
mkdir mon-projet && cd mon-projet
uv init
```

`uv init` crée la structure minimale :

```
mon-projet/
├── pyproject.toml
├── README.md
└── hello.py
```

### Ajouter MkDocs et le thème Material

La version minimale (deux paquets seulement) :

```bash
uv add --dev mkdocs mkdocs-material
```

### Stack complet recommandé

Pour un site de documentation professionnel avec toutes les fonctionnalités
(rechargement automatique à la date de modification, inclusions de fichiers,
macros, pages automatiques, minification) :

```bash
uv add --dev \
    mkdocs \
    mkdocs-material \
    mkdocs-minify-plugin \
    mkdocs-git-revision-date-localized-plugin \
    mkdocs-awesome-pages-plugin \
    mkdocs-include-markdown-plugin \
    mkdocs-macros-plugin
```

| Plugin | Rôle |
|---|---|
| `mkdocs-material` | Thème Material Design — navigation, recherche, mode sombre |
| `mkdocs-minify-plugin` | Compresse le HTML généré (site plus léger) |
| `mkdocs-git-revision-date-localized-plugin` | Affiche "Dernière modification : …" sur chaque page |
| `mkdocs-awesome-pages-plugin` | Contrôle l'ordre des pages via des fichiers `.pages` |
| `mkdocs-include-markdown-plugin` | Inclure un fichier Markdown dans un autre |
| `mkdocs-macros-plugin` | Variables et macros Jinja2 dans les pages Markdown |

Votre `pyproject.toml` contiendra :

```toml
[dependency-groups]
dev = [
    "mkdocs>=1.6.1",
    "mkdocs-material>=9.7.6",
    "mkdocs-minify-plugin>=0.8.0",
    "mkdocs-git-revision-date-localized-plugin>=1.2.0",
    "mkdocs-awesome-pages-plugin>=2.9.0",
    "mkdocs-include-markdown-plugin>=6.0.0",
    "mkdocs-macros-plugin>=1.0.0",
]
```

!!! info "Pourquoi `--dev` ?"
    MkDocs sert à générer de la documentation — il ne fait pas partie du
    code applicatif livré. Le placer dans les dépendances `dev` évite qu'il
    soit installé dans les environnements de production.

### Installer les dépendances

```bash
uv sync
```

Cette commande lit `pyproject.toml`, crée `.venv/` et installe tous les
paquets. À répéter après chaque ajout de dépendance.

### Vérifier l'installation

```bash
uv run mkdocs --version
# → INFO    -  MkDocs version : 1.6.x
```

!!! note "Toujours préfixer avec `uv run`"
    `uv run mkdocs` garantit que c'est le MkDocs installé dans **ce projet**
    qui est utilisé, pas un autre potentiellement présent sur le système.

---

## Installer une version spécifique de Python (optionnel)

Si votre projet requiert une version plus récente que celle d'Ubuntu :

```bash
uv python install 3.14

# Vérifier les versions disponibles
uv python list
```

Cela télécharge un binaire Python autonome dans `~/.local/share/uv/python/`.
Aucun impact sur le Python système d'Ubuntu.
