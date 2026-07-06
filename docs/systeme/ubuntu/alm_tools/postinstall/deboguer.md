# Déboguer

Quand une cible échoue ou produit un résultat inattendu, voici les outils
et techniques disponibles.

---

## Lire les logs

Chaque invocation de `sudo make` crée un fichier de log horodaté :

```
/var/log/postinstall_2026-05-28_14-30-00.log
```

### Trouver le fichier le plus récent

```bash
ls -lt /var/log/postinstall_*.log | head -5
```

### Suivre la progression en direct (depuis un second terminal)

```bash
tail -f $(ls -t /var/log/postinstall_*.log | head -1)
```

### Filtrer les messages importants

```bash
LOG=$(ls -t /var/log/postinstall_*.log | head -1)

# Voir uniquement les erreurs bloquantes
grep -E '\[ERROR\]|\[FATAL\]' "$LOG"

# Voir erreurs, fatals et avertissements
grep -E '\[ERROR\]|\[FATAL\]|\[WARNING\]' "$LOG"

# Voir uniquement les succès
grep '\[SUCCESS\]' "$LOG"

# Résumé rapide : étapes et leur statut
grep -E '▶  |✓  .*done|\[ERROR\]|\[FATAL\]' "$LOG"

# Contexte autour d'une erreur (5 lignes avant/après)
grep -A 5 -B 5 '\[ERROR\]' "$LOG"

# Chercher une étape précise
grep -i 'uv' "$LOG"
```

### Niveaux de log

Tous les messages suivent le format `[YYYY-MM-DD HH:MM:SS] [NIVEAU] message`.

| Niveau | Couleur | Signification |
|--------|---------|---------------|
| `[DEBUG]` | Bleu clair | Détails d'exécution (masqués par défaut) |
| `[INFO]` | Bleu | Progression normale |
| `[SUCCESS]` | Vert | Étape terminée avec succès |
| `[WARNING]` | Jaune | Anomalie non bloquante |
| `[ERROR]` | Rouge | Échec d'une opération, le script peut continuer |
| `[FATAL]` | Rouge | Erreur critique — arrêt immédiat |

!!! note "`WARNING` et `ERROR` vont vers stderr"
    Dans le fichier de log, les deux flux stdout et stderr sont capturés ensemble
    grâce à la redirection `2>&1` dans la macro `RUN` du Makefile.

---

## Exécuter un module directement

C'est la méthode principale pour tester ou déboguer une étape sans passer
par le Makefile. La sortie s'affiche dans le terminal — **sans écriture dans
le fichier de log**.

```bash
cd ~/alm_tools/postinstall

# Syntaxe générale
sudo bash modules/<groupe>/<script>.sh

# Exemples
sudo bash modules/cli/install_uv.sh
sudo bash modules/apps/install_brave.sh
sudo bash modules/desktop/install_fonts.sh
sudo bash modules/devtools/install_devinit.sh
sudo bash modules/system/update_system.sh
```

C'est intentionnel : en mode débogage direct, on veut voir la sortie brute
sans la passer dans `tee`.

---

## Mode DEBUG verbose

La variable `DEBUG=true` active les messages de niveau `[DEBUG]`, masqués
par défaut. Elle révèle les détails internes : détection du HOME utilisateur,
résolution des chemins, état des fichiers de lock, vérifications intermédiaires.

```bash
# sudo -E est requis pour transmettre les variables d'environnement à root
sudo -E DEBUG=true bash modules/cli/install_uv.sh
sudo -E DEBUG=true bash modules/apps/install_zed.sh
```

Sans `-E`, `sudo` filtre les variables d'environnement et `DEBUG` n'est pas
transmis au script.

---

## Vérification syntaxique sans exécution

`bash -n` parse un script et signale les erreurs de syntaxe **sans exécuter
aucune commande**. Utile avant de modifier un module.

```bash
# Vérifier un module spécifique
bash -n modules/cli/install_uv.sh

# Vérifier tous les modules d'un groupe
for f in modules/cli/*.sh; do
    bash -n "$f" && echo "OK: $f" || echo "ERREUR: $f"
done

# Vérifier l'ensemble des modules
find modules/ -name '*.sh' -exec bash -n {} \; -print
```

---

## Erreurs fréquentes

### `sudo: make: command not found`

`make` n'est pas installé. L'installer manuellement :

```bash
sudo apt-get install -y make
```

### `uv requis [...] Installez uv en premier`

Le module `devinit` ou `pioinit` a été lancé avant `uv`.
Installer uv d'abord :

```bash
sudo make uv
sudo make devinit
```

### `Impossible de déterminer le HOME de <user>`

Le script est lancé avec `sudo` mais `$SUDO_USER` est vide. Cela arrive
si `sudo` est utilisé en chaîne (`sudo su` puis `make`). Toujours lancer
directement depuis votre compte :

```bash
sudo make uv        # correct
sudo su -c "make uv"  # incorrect — SUDO_USER sera vide
```

### `[WARNING] First revision timestamp is older than last revision timestamp`

Message du plugin `git-revision-date-localized` dans le wiki, sans rapport
avec `postinstall`. Il apparaît après un renommage de fichier dans git et
disparaît au prochain commit.
