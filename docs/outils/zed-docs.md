# Documentation Zed (locale)

Procédure de remise en place de la documentation officielle de Zed Editor,
servie localement via **mdBook**, après une réinstallation du système.

Le projet `~/alm_docs/zed` contient :

- les sources Markdown (`src/`) copiées depuis le dépôt officiel Zed
- la configuration mdBook (`book.toml`)
- le script de mise à jour (`zed-docs-update`)
- le script d'installation (`install.sh`)

---

## Prérequis

- `git` et `curl` installés
- `~/.local/bin` dans le `$PATH` (géré par `~/.local/bin/env`, sourcé depuis `~/.bashrc`)

---

## Installation from scratch

### 1. Cloner le dépôt alm_docs

```bash
git clone git@github.com:keltalan/alm_docs.git ~/alm_docs
```

### 2. Lancer le script d'installation

```bash
~/alm_docs/zed/install.sh
```

Ce script effectue automatiquement :

- le téléchargement de `mdbook` dans `~/.local/bin/` (si absent)
- la création d'un lien symbolique `~/.local/bin/zed-docs-update` → `~/alm_docs/zed/zed-docs-update`

### 3. Premier build

```bash
zed-docs-update
```

Lors du premier lancement, si le clone du dépôt Zed est absent de `~/workspaces/zed/`,
le script le crée automatiquement en **sparse checkout** (docs uniquement, très léger).

Il synchronise ensuite les sources et génère le site dans `~/alm_docs/zed/book/`.

---

## Utilisation courante

### Mettre à jour la documentation

```bash
zed-docs-update
```

Le script récupère la dernière version de `main`, synchronise les fichiers modifiés,
et reconstruit le site.

### Consulter la documentation dans le navigateur

```bash
mdbook serve ~/alm_docs/zed
```

Puis ouvrir : [http://localhost:3000](http://localhost:3000)

---

## Structure du projet

```
~/alm_docs/zed/
├── book.toml           # Configuration mdBook
├── install.sh          # Script d'installation (lien + mdbook)
├── zed-docs-update     # Script de mise à jour (commande principale)
├── src/                # Sources Markdown (172 fichiers)
│   ├── SUMMARY.md      # Navigation complète
│   ├── getting-started.md
│   ├── ai/
│   ├── languages/
│   └── ...
└── book/               # Site généré (ignoré par git)
```

---

## Dépôts concernés

| Rôle | Chemin local | Dépôt distant |
|------|-------------|---------------|
| Ce projet (docs Zed) | `~/alm_docs/zed` | `git@github.com:keltalan/alm_docs.git` |
| Sources Zed (sparse) | `~/workspaces/zed` | `https://github.com/zed-industries/zed` |
