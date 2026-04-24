# Utilitaires Python et sandbox

---

## Utilitaires Python — `.functions/`

Ces outils sont disponibles sans installation préalable.

### `kvm_admin.py` — Administration KVM

Interface curses interactive pour gérer les VMs via libvirt.

```bash
python3 ~/alm-tools/.functions/kvm_admin.py
```

| Fonction | Description |
|----------|-------------|
| Lister | Affiche les VMs avec état, MAC et IP |
| Démarrer / Arrêter | Contrôle du cycle de vie |
| Supprimer | Suppression propre de la VM |

---

### `csv_checker.py` — Validation CSV

```bash
python3 ~/alm-tools/.functions/csv_checker.py -f fichier.csv
python3 ~/alm-tools/.functions/csv_checker.py -f fichier.csv -d ";"
```

Vérifie la cohérence du nombre de colonnes sur toutes les lignes.

---

### `rename_images.py` — Renommage en lot

```bash
python3 ~/alm-tools/.functions/rename_images.py prefixe
```

Renomme toutes les images du répertoire courant en `prefixe_001.ext`, `prefixe_002.ext`, etc.

---

### `functions_infos.py` — Analyse de fonctions shell

```bash
python3 ~/alm-tools/.functions/functions_infos.py script.sh
```

Extrait et documente les fonctions définies dans les scripts shell.

---

## Sandbox Python/JupyterLab — `python/sandbox.sh`

Crée un environnement de développement Python isolé avec JupyterLab.

!!! info "Prérequis"
    `uv` doit être installé — voir [post-installation](post-installation.md), étape 6.

```bash
bash ~/alm-tools/python/sandbox.sh
```

### Ce que le script crée

Répertoire cible : `~/Workspaces/sandbox/`

| Élément | Description |
|---------|-------------|
| Projet `uv init` | Environnement virtuel géré par `uv` |
| `jupyterlab` | Interface web pour les notebooks |
| `numpy`, `pandas`, `seaborn` | Bibliothèques de data science |
| `requests` | Requêtes HTTP |
| Config WSL | Configuration adaptée si WSL est détecté |
| Noyau JS (optionnel) | `ijavascript` si Node.js est disponible |

### Lancer JupyterLab

```bash
cd ~/Workspaces/sandbox
uv run jupyter lab
```
