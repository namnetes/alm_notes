# Commandes personnalisées

Une **commande personnalisée** (*custom slash command*) est un fichier Markdown
qui devient une commande `/ma-commande` dans Claude Code. Son contenu sert de
prompt : quand vous l'invoquez, Claude reçoit ces instructions dans le contexte
courant et les exécute.

!!! info "Commandes ≠ Skills"
    Une **commande** se déclenche **manuellement** (vous tapez `/x`). Un
    [skill](skills.md) est au contraire activé **automatiquement** par Claude
    selon sa description. Deux mécanismes distincts, deux dossiers différents
    (`commands/` vs `skills/`).

---

## Où placer une commande

Le nom du fichier (sans `.md`) devient le nom de la commande.

| Emplacement | Portée | Invocation |
|---|---|---|
| `~/.claude/commands/<nom>.md` | Personnel — tous les projets | `/<nom>` |
| `<projet>/.claude/commands/<nom>.md` | Projet — versionné avec le dépôt | `/<nom>` |

!!! tip "Sous-dossiers = espaces de noms"
    Un fichier `~/.claude/commands/git/recap.md` est invoqué par `/git:recap`.
    Pratique pour regrouper des commandes liées.

---

## Anatomie d'un fichier de commande

Un fichier de commande se compose de deux parties : un **frontmatter** YAML
optionnel (entre `---`) et le **corps** Markdown (le prompt).

```markdown
---
description: Explique une commande shell en français
argument-hint: <commande shell>
allowed-tools: Bash(uname:*)
model: claude-haiku-4-5-20251001
---

Le corps du fichier est le prompt envoyé à Claude.
```

### Clés du frontmatter

| Clé | Rôle |
|---|---|
| `description` | Texte affiché dans la liste des commandes (`/`) |
| `argument-hint` | Indice d'arguments montré pendant l'autocomplétion |
| `allowed-tools` | Outils autorisés sans confirmation (ex. `Bash(git status:*)`) |
| `model` | Force un modèle précis pour cette commande (sinon : modèle courant) |

Toutes ces clés sont **facultatives** : un fichier sans frontmatter fonctionne.

---

## Passer des arguments

| Placeholder | Remplacé par |
|---|---|
| `$ARGUMENTS` | Tout ce qui suit le nom de la commande |
| `$1`, `$2`, … | Les arguments positionnels, un par un |

```markdown
# Tout l'argument d'un bloc
Corrige la faute dans : $ARGUMENTS

# Arguments séparés
Compare le fichier $1 avec le fichier $2 et résume les différences.
```

---

## Injecter du contexte dynamique

Deux préfixes enrichissent le prompt **avant** son envoi à Claude :

- **`!`commande`` ** exécute une commande shell et insère sa sortie
  (nécessite l'outil `Bash` dans `allowed-tools`).
- **`@chemin/fichier`** insère le contenu d'un fichier du projet.

```markdown
Voici l'état du dépôt : !`git status --short`
Analyse aussi la configuration : @pyproject.toml
```

---

## Exemple simple et testable — `/explique`

Une commande sans dépendance ni état : elle explique une commande shell donnée
en argument.

### Étape 1 — Créer le fichier

```bash
mkdir -p ~/.claude/commands
cat > ~/.claude/commands/explique.md << 'EOF'
---
description: Explique une commande shell en français, étape par étape
argument-hint: <commande shell>
---

Explique en français, de façon concise, ce que fait la commande shell
suivante. Détaille chaque option et signale tout effet destructif.

Commande : $ARGUMENTS
EOF
```

### Étape 2 — Tester

Lancez Claude Code dans n'importe quel répertoire et tapez :

```text
/explique tar -xzf archive.tar.gz -C /tmp
```

### Résultat attendu

Claude explique la commande option par option, par exemple :

```text
`tar` archive ou extrait des fichiers.
- `-x` : extraire le contenu de l'archive
- `-z` : décompresser le flux gzip (.tar.gz)
- `-f archive.tar.gz` : nom du fichier archive en entrée
- `-C /tmp` : extraire dans le répertoire /tmp

Aucun effet destructif : les fichiers existants de même nom seraient
toutefois écrasés sans confirmation.
```

---

## Exemple avec injection shell — `/contexte`

Cette commande montre l'injection `!` et `allowed-tools`. Elle résume l'état
machine sans que vous ayez à confirmer chaque commande.

```bash
cat > ~/.claude/commands/contexte.md << 'EOF'
---
description: Résume l'état système courant
allowed-tools: Bash(uname:*), Bash(df:*)
---

Voici l'état de la machine :

- Noyau : !`uname -sr`
- Espace disque racine : !`df -h / | tail -1`

Résume ces informations en une phrase et préviens si le disque dépasse 90 %
d'occupation.
EOF
```

Test :

```text
/contexte
```

Claude reçoit la sortie réelle de `uname` et `df`, déjà injectée dans le
prompt, et la résume.

---

## Lister les commandes disponibles

```bash
# Commandes personnelles
ls ~/.claude/commands/

# Commandes du projet courant
ls .claude/commands/ 2>/dev/null || echo "Aucune commande locale"
```

Dans Claude Code, tapez `/` puis ++tab++ pour afficher toutes les commandes
disponibles (personnalisées + natives) avec leur `description`.
