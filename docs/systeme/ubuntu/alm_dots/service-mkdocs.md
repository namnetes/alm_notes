# Service systemd — wiki MkDocs

Le wiki personnel (`alm_notes`) est servi automatiquement au démarrage
de session via un service systemd utilisateur.

Accessible sur **<http://127.0.0.1:8000/>** sans aucune action manuelle.

---

## Commandes courantes

```bash
# Vérifier l'état du service
systemctl --user status mkdocs

# Arrêter le wiki
systemctl --user stop mkdocs

# Redémarrer (après un `git pull` sur alm_notes, par exemple)
systemctl --user restart mkdocs

# Consulter les logs en temps réel
journalctl --user -u mkdocs -f
```

---

## Fichier de service

Versionné dans `alm_dots` et déployé via Stow :

```
alm_dots/.config/systemd/user/mkdocs.service
    → ~/.config/systemd/user/mkdocs.service  (lien symbolique)
```

Contenu du fichier :

```ini
[Unit]
Description=MkDocs serve — wiki personnel alm_notes
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/alm_notes
ExecStart=%h/.local/bin/uv run mkdocs serve --dev-addr 127.0.0.1:8000
Restart=on-failure
RestartSec=5
SuccessExitStatus=143

[Install]
WantedBy=default.target
```

`%h` est remplacé par systemd par le répertoire personnel de l'utilisateur (`/home/galan`).

---

## Installation après une réinstallation

### Prérequis

- `alm_dots` cloné dans `~/alm_dots`
- `alm_notes` cloné dans `~/alm_notes`
- `uv` installé dans `~/.local/bin/uv`
- Stow déployé (voir [Déploiement après installation fraîche](../deploiement-post-installation.md))

### Étapes

```bash
# 1. Stow déploie déjà le fichier .service via le déploiement habituel des dotfiles
cd ~/alm_dots && stow --target="$HOME" .

# 2. Recharger la configuration systemd
systemctl --user daemon-reload

# 3. Activer le service au démarrage de session
systemctl --user enable mkdocs.service

# 4. Le démarrer immédiatement (sans attendre la prochaine connexion)
systemctl --user start mkdocs.service

# 5. Vérifier
systemctl --user status mkdocs
```

Le service démarre ensuite automatiquement à chaque ouverture de session.
