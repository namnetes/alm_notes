# runbg

`runbg.sh` lance n'importe quel script Bash en arrière-plan avec journalisation
automatique via `nohup`. Utile pour des tâches longues qu'on veut détacher
du terminal courant.

**Source :** `~/alm_tools/jobs/runbg.sh`

---

## Utilisation

```bash
~/alm_tools/jobs/runbg.sh [options] <script.sh>
```

### Exemples

```bash
# Lancement simple
~/alm_tools/jobs/runbg.sh mon_script.sh

# Avec un nom de log personnalisé
~/alm_tools/jobs/runbg.sh --name export-data mon_script.sh

# Avec notification bureau à la fin (si notify-send est disponible)
~/alm_tools/jobs/runbg.sh --name export-data --notify mon_script.sh

# Avec un fichier de variables d'environnement
~/alm_tools/jobs/runbg.sh --name export-data --env /chemin/vars.env mon_script.sh
```

---

## Options

| Option | Description |
|--------|-------------|
| `--name NAME` | Nom utilisé dans le fichier de log (défaut : nom du script sans extension) |
| `--notify` | Envoie une notification bureau à la fin via `notify-send` |
| `--env FILE` | Source un fichier de variables d'environnement avant l'exécution |
| `--help` | Affiche l'aide |

---

## Journaux

Les logs sont écrits dans `~/.nohups/` avec le format :

```
~/.nohups/<nom>_YYYY-MM-DD_HH-MM-SS.out
```

Consulter le log d'un job en cours :

```bash
tail -f ~/.nohups/export-data_2026-05-28_14-30-00.out

# Dernier log créé
tail -f $(ls -t ~/.nohups/*.out | head -1)
```

---

## Comportement

- Si le script n'est pas exécutable, `runbg.sh` ajoute automatiquement les droits `+x`
- Le PID du processus lancé est affiché dans le terminal
- `nohup` détache le processus du terminal — il continue même si le terminal est fermé
- `lock_guard` (via `lib/common.sh`) n'est **pas** utilisé ici — plusieurs instances peuvent tourner en parallèle
