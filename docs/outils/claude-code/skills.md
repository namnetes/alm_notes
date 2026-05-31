# Skills (commandes personnalisées)

Les **skills** sont des commandes slash personnalisées (`/ma-commande`) que
Claude Code exécute à la demande. Chaque skill est un fichier Markdown dont
le contenu sert d'instruction à Claude.

---

## Principe

Quand vous tapez `/nom-du-skill` dans Claude Code, il :

1. Trouve le fichier Markdown correspondant
2. Envoie son contenu comme instruction dans le contexte courant
3. Exécute la tâche décrite

Les skills peuvent recevoir des **arguments** via le placeholder `$ARGUMENTS`.

---

## Emplacements

| Répertoire | Portée |
|-----------|--------|
| `~/.claude/commands/` | Global — disponible dans tous les projets |
| `<projet>/.claude/commands/` | Local — disponible uniquement dans ce projet |

Les skills locaux ont la priorité sur les skills globaux si les noms se chevauchent.

---

## Créer un skill

### Structure du fichier

```
~/.claude/commands/<nom>.md
```

Le nom du fichier (sans `.md`) devient la commande slash.

### Format

```markdown
Description courte de ce que fait le skill.

Instructions détaillées pour Claude...

$ARGUMENTS
```

`$ARGUMENTS` est remplacé par ce que l'utilisateur tape après le nom de la
commande. Optionnel si le skill ne prend pas d'arguments.

---

## Tutoriel — skill `git-recap`

Ce skill affiche un récapitulatif de l'état Git du projet courant : branche,
derniers commits, fichiers modifiés. Utile en début de session pour se
remettre dans le contexte.

### Étape 1 — Créer le répertoire

```bash
mkdir -p ~/.claude/commands
```

### Étape 2 — Créer le fichier

```bash
cat > ~/.claude/commands/git-recap.md << 'EOF'
Donne-moi un récapitulatif rapide de l'état Git du projet courant.

Exécute les commandes suivantes et présente les résultats de façon claire :
1. `git branch --show-current` — branche active
2. `git log --oneline -5` — les 5 derniers commits
3. `git status --short` — fichiers modifiés/ajoutés/supprimés

Présente le tout en 3 sections courtes avec des titres. Si le répertoire
courant n'est pas un dépôt Git, dis-le simplement.
EOF
```

### Étape 3 — Tester

Depuis n'importe quel dépôt Git, lancer Claude Code et taper :

```
/git-recap
```

Claude exécute les trois commandes et présente le résumé.

### Résultat attendu

```
## Branche active
main

## Derniers commits
a1b2c3d docs: update alm_tools documentation
e4f5g6h feat: add gnome-settings module
...

## Fichiers modifiés
M  docs/outils/claude-code/skills.md
?? docs/outils/claude-code/index.md
```

---

## Skill avec arguments — `chercher`

Skill qui cherche un terme dans tous les fichiers du projet et présente
les occurrences de façon lisible.

```bash
cat > ~/.claude/commands/chercher.md << 'EOF'
Cherche le terme ou l'expression suivante dans tous les fichiers du projet :

$ARGUMENTS

Utilise grep ou ripgrep pour trouver toutes les occurrences, puis présente
les résultats groupés par fichier avec le numéro de ligne et le contexte
(1 ligne avant et après). Indique le nombre total d'occurrences trouvées.
EOF
```

Utilisation :

```
/chercher SUDO_USER
/chercher "def install_"
```

---

## Skills globaux vs locaux

**Cas d'usage typiques :**

| Type | Exemples |
|------|---------|
| Global (`~/.claude/commands/`) | `git-recap`, `chercher`, `todo` — utiles partout |
| Local (`.claude/commands/`) | `deploy`, `test-integ` — spécifiques au projet |

**Créer un skill local au projet :**

```bash
mkdir -p .claude/commands
cat > .claude/commands/deploy.md << 'EOF'
Lance le déploiement en environnement de staging.
Exécute `make deploy-staging` et vérifie que les health checks passent.
Informe-moi du résultat.
EOF
```

---

## Lister les skills disponibles

```bash
# Skills globaux
ls ~/.claude/commands/

# Skills du projet courant
ls .claude/commands/ 2>/dev/null || echo "Pas de skills locaux"
```

Dans Claude Code, taper `/` puis ++tab++ affiche les commandes disponibles
(skills + commandes natives).
