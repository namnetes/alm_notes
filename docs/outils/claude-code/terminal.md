# Assistant terminal (Warp-like)

Cette page documente l'intégration de Claude AI directement dans le terminal,
inspirée des terminaux comme **Warp** (Rust, IA native). Deux niveaux
d'intégration sont disponibles :

- **Fonctions shell** (`ai`, `explain`, `fix`) — dans n'importe quel terminal
- **Kitten Kitty** (`kitty_mod+a/x/s`) — intégration native avec capture du terminal

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Terminal Kitty                                         │
│                                                         │
│  ┌──────────────────┐    ┌──────────────────────────┐   │
│  │  Fonctions shell │    │  Kitten claude_ask.sh    │   │
│  │  ai / explain    │    │  kitty_mod+a/x/s         │   │
│  │  fix             │    │  capture écran/sélection │   │
│  └────────┬─────────┘    └────────────┬─────────────┘   │
│           │                           │                 │
└───────────┼───────────────────────────┼─────────────────┘
            │                           │
            ▼                           ▼
     API Anthropic Haiku (claude-haiku-4-5-20251001)
     Réponse en < 3 secondes · ~0.001€ par requête
```

**Pourquoi Haiku et non Sonnet ?**
L'autocomplétion et l'explication terminal nécessitent de la vitesse, pas de la
profondeur. Haiku répond en 1-3s contre 5-15s pour Sonnet, pour un coût 10x
inférieur. Le contexte terminal est court — Haiku suffit largement.

---

## Fonctions shell

Disponibles dans tout terminal après rechargement : `source ~/.bash_functions`

### `ai` — Langage naturel → commande bash

```bash
ai <description en langage naturel>
```

Claude génère la commande, l'affiche, l'ajoute à l'historique bash, et propose
de l'exécuter (avec possibilité de modifier avant).

**Cas d'usage :**

```bash
# Trouver les 10 fichiers les plus gros dans /var
ai "les 10 fichiers les plus volumineux dans /var"
→ find /var -type f -exec du -h {} + | sort -rh | head -10
Exécuter ? [Entrée=oui, modifiez si besoin, Ctrl+C=annuler]

# Compresser un dossier en excluant .git
ai "compresser le dossier courant en tar.gz en excluant .git"
→ tar --exclude='.git' -czf ../$(basename "$PWD").tar.gz .

# Trouver tous les processus qui écoutent sur le port 8080
ai "processus qui écoutent sur le port 8080"
→ ss -tlnp | grep :8080

# Inverser l'ordre des lignes d'un fichier
ai "inverser l'ordre des lignes de monfile.txt"
→ tac monfile.txt

# Extraire les emails uniques d'un fichier log
ai "extraire les adresses email uniques du fichier access.log"
→ grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' access.log | sort -u

# Surveiller les modifications d'un fichier en temps réel
ai "afficher les nouvelles lignes de app.log en temps réel avec coloration"
→ tail -f app.log | grep --color=always -E 'ERROR|WARN|$'
```

!!! tip "L'historique bash"
    La commande suggérée est ajoutée à l'historique bash (`history -s`).
    Même si vous annulez avec Ctrl+C, la commande reste accessible avec `↑`.

---

### `explain` — Explication d'une commande

```bash
explain <commande>    # explique la commande donnée
explain               # explique la dernière commande de l'historique
```

**Cas d'usage :**

```bash
# Expliquer une commande complexe
explain "find . -name '*.py' -mtime -7 -exec grep -l 'TODO' {} \;"
→ find . : cherche dans le répertoire courant
→ -name '*.py' : uniquement les fichiers Python
→ -mtime -7 : modifiés dans les 7 derniers jours
→ -exec grep -l 'TODO' {} \; : liste ceux contenant "TODO"

# Expliquer la dernière commande après l'avoir exécutée
sudo systemctl --user daemon-reload
explain
→ sudo : exécute avec les droits root
→ systemctl --user : gère les services de l'utilisateur courant
→ daemon-reload : recharge les fichiers de configuration systemd

# Comprendre une commande vue dans un tutoriel
explain "awk 'NR==FNR{a[$0];next} $0 in a' file1 file2"
→ NR==FNR : vrai uniquement lors de la lecture du premier fichier
→ a[$0] : stocke chaque ligne dans le tableau a
→ next : passe à la ligne suivante sans continuer
→ $0 in a : affiche les lignes du file2 présentes dans file1
```

---

### `fix` — Diagnostic d'erreur

```bash
fix "message d'erreur"    # analyse l'erreur fournie
fix                        # demande de coller l'erreur (Ctrl+D pour envoyer)
```

**Cas d'usage :**

```bash
# Corriger une erreur de permission
fix "Permission denied: '/var/log/app.log'"
→ Cause : votre utilisateur n'a pas accès en lecture à ce fichier.
→ Solution : sudo chmod 644 /var/log/app.log
→           ou : sudo usermod -aG adm $USER && newgrp adm

# Diagnostiquer une erreur Python
fix "ModuleNotFoundError: No module named 'pandas'"
→ Le module pandas n'est pas installé dans l'environnement actif.
→ Solution : uv add pandas  (si projet uv)
→           ou : pip install pandas

# Analyser une erreur de compilation
fix "error: linker 'cc' not found"
→ Le compilateur C (gcc/cc) est absent.
→ Solution : sudo apt install build-essential

# Erreur Docker
fix "Cannot connect to the Docker daemon at unix:///var/run/docker.sock"
→ Le service Docker n'est pas démarré.
→ Solution : sudo systemctl start docker
→ Si persistant : sudo usermod -aG docker $USER && newgrp docker

# Coller une erreur multi-lignes
fix
Dernière commande : make all
Collez l'erreur (Ctrl+D pour envoyer) :
# → coller le bloc d'erreur complet, puis Ctrl+D
```

---

## Kitten Kitty — intégration native

Le kitten capture automatiquement le contenu visible du terminal (ou la
sélection) et l'analyse dans une fenêtre dédiée.

### Raccourcis

| Raccourci     | Mode        | Action                                             |
| ------------- | ----------- | -------------------------------------------------- |
| `kitty_mod+a` | `explain`   | Explique la sélection ou l'écran courant           |
| `kitty_mod+x` | `fix`       | Donne la commande corrective pour l'erreur visible |
| `kitty_mod+s` | `summarize` | Résume la session terminal en 3-5 lignes           |

### Différence avec les fonctions shell

|                  | Fonctions shell      | Kitten Kitty                                   |
| ---------------- | -------------------- | ---------------------------------------------- |
| Contexte         | Fourni manuellement  | Capturé automatiquement depuis l'écran         |
| Sélection        | Non                  | Oui — sélectionnez du texte avant le raccourci |
| Nouvelle fenêtre | Non — réponse inline | Oui — fenêtre dédiée                           |
| Cas d'usage      | Requêtes ponctuelles | Analyse d'un output visible                    |

### Workflow typique avec le kitten

```
1. Une commande produit une erreur dans le terminal

   $ docker build .
   ERROR [2/4] RUN apt-get install -y libssl-dev
   ...
   error: failed to solve: ...

2. Sélectionner le bloc d'erreur à la souris (copy_on_select l'ajoute au
   presse-papiers automatiquement)

3. kitty_mod+x  → nouvelle fenêtre s'ouvre

   ✦ Claude — Correction
   13:42:07 · claude-haiku-4-5

   docker build . --no-cache

4. Entrée pour fermer
```

### Fonctionnement interne

```
kitty_mod+a
    │
    ▼
launch --type=window bash -c "claude_ask.sh explain"
    │
    ├─ kitty @ --to $KITTY_LISTEN_ON get-text --extent selection
    │  (récupère la sélection si présente)
    │
    ├─ kitty @ --to $KITTY_LISTEN_ON get-text --extent screen
    │  (récupère l'écran si pas de sélection)
    │
    ├─ wl-paste / xclip
    │  (fallback presse-papiers)
    │
    └─ API Anthropic Haiku
           │
           ▼
       Réponse affichée dans la fenêtre
```

Le socket `unix:/tmp/kitty-{kitty_pid}` permet au script lancé dans la nouvelle
fenêtre de communiquer avec l'instance Kitty parente via `kitty @`.

---

## Fichiers déployés

Tous les fichiers sont dans `alm_dots` et déployés via `stow .` :

| Fichier                                        | Destination (stow)                      | Rôle                             |
| ---------------------------------------------- | --------------------------------------- | -------------------------------- |
| `alm_dots/.bash_functions`                     | `~/.bash_functions`                     | Fonctions `ai`, `explain`, `fix` |
| `alm_dots/.config/kitty/kittens/claude_ask.sh` | `~/.config/kitty/kittens/claude_ask.sh` | Kitten Kitty                     |
| `alm_dots/.config/kitty/kitty.conf`            | `~/.config/kitty/kitty.conf`            | Raccourcis `kitty_mod+a/x/s`     |

---

## Réinstallation automatique

Après une réinstallation Ubuntu, tout est rétabli par :

```bash
# 1. Déployer alm_dots (fonctions + kitten + kitty.conf)
cd ~/alm_dots && stow .

# 2. Vérifier l'intégration via postinstall
cd ~/alm_tools/postinstall
sudo make claude-terminal
```

Le module `claude-terminal` vérifie :

- `python3` et `curl` disponibles
- `ANTHROPIC_API_KEY` présente dans `~/.bashrc`
- `claude_ask.sh` présent et exécutable
- `~/.claude/commands/` créé

---

## Comparaison avec Warp

| Fonctionnalité                  | Warp              | Cette intégration                     |
| ------------------------------- | ----------------- | ------------------------------------- |
| Langage naturel → commande      | ✅                | ✅ `ai`                               |
| Explication de commande         | ✅                | ✅ `explain`                          |
| Diagnostic d'erreur             | ✅                | ✅ `fix` + `kitty_mod+x`              |
| Capture automatique du terminal | ✅                | ✅ kitten via `kitty @`               |
| Fenêtre dédiée IA               | ✅                | ✅ `--type=window`                    |
| Modèle configurable             | ❌ (propriétaire) | ✅ Haiku / Sonnet / Opus              |
| Fonctionne hors Warp            | ❌                | ✅ fonctions shell portables          |
| Open source                     | ❌                | ✅ tout est dans alm_dots             |
| Prix                            | ~15$/mois         | ~0$/mois (abonnement Claude existant) |
