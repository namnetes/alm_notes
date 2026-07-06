# Wikinotes

Wiki de documentation technique personnelle propulsé par **MkDocs Material**.

## Lancement

```bash
uv sync               # installer les dépendances
make docs             # serveur de développement (port auto 8000–8050)
make docs-start       # serveur en arrière-plan
make docs-stop        # arrêter le serveur de fond
make docs-build       # compiler vers site/
```

## Gestion des pages

```bash
uv run python new-page.py   # ajouter / supprimer sections et pages
```

## Structure

```
docs/         # contenu Markdown (systeme, developpement, lcl, securite, outils…)
drafts/       # brouillons en attente d'intégration dans docs/
mkdocs.yml    # configuration MkDocs et navigation explicite
new-page.py   # gestionnaire interactif de pages
```
