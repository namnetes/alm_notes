# Dépannage

## `uv: command not found`

```bash
# Recharger le PATH
source "$HOME/.local/bin/env"

# Ou ajouter manuellement
export PATH="$HOME/.local/bin:$PATH"

# Vérifier que uv est installé
ls ~/.local/bin/uv
```

---

## `mkdocs: command not found` après `uv sync`

Ne pas appeler `mkdocs` directement — toujours passer par `uv run` :

```bash
uv run mkdocs --version    # ✓ correct
mkdocs --version           # ✗ peut ne pas fonctionner
```

---

## `docs_dir 'docs' does not exist`

MkDocs cherche `docs/` par défaut. Si vos fichiers Markdown sont ailleurs,
déclarez-le dans `mkdocs.yml` :

```yaml
docs_dir: doc    # ← indiquez le bon chemin
```

---

## Page non trouvée dans la navigation

Si une page apparaît dans `nav` mais n'existe pas sur le disque :

```
WARNING - Config value 'nav': The file 'api/reference.md' does not exist.
```

Créez le fichier manquant ou corrigez le chemin dans `nav`.

---

## Liens brisés en mode `--strict`

```
ERROR - Doc file 'guide.md' contains a link to 'autre.md#section-inexistante'
        which is not found in the documentation files.
```

Vérifiez que :

1. Le fichier cible existe bien dans `docs_dir`.
2. L'ancre correspond exactement au titre (`## Mon titre` → ancre `#mon-titre`).
3. Le chemin est relatif au fichier source, pas à la racine du projet.

---

## Mermaid ne s'affiche pas

Vérifiez que `pymdownx.superfences` est activé **avec** la configuration
`custom_fences` pour Mermaid dans `mkdocs.yml` :

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

Le support Mermaid est intégré au thème Material, pas au thème MkDocs par
défaut — `theme.name: material` est obligatoire.

---

## Le port 8000 est déjà utilisé

```bash
# Trouver et tuer le processus qui utilise le port
lsof -ti:8000 | xargs kill -9

# Ou lancer sur un autre port
uv run mkdocs serve --dev-addr 127.0.0.1:8001
```

!!! tip "Détection automatique de port"
    Le Makefile standard du projet utilise `lsof` pour trouver
    automatiquement un port libre entre 8000 et 8050.
    Voir la page [Commandes](commandes.md) pour le snippet complet.
