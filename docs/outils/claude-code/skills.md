# Skills (Agent Skills)

Un **skill** (*Agent Skill*) est une compétence que vous décrivez à Claude
Code et qu'il décide d'utiliser **lui-même**, automatiquement, quand la tâche
en cours correspond. Contrairement à une commande, vous ne le déclenchez pas à
la main : c'est le modèle qui le sélectionne en lisant sa `description`.

!!! info "Ne pas confondre avec les commandes personnalisées"
    Les deux mécanismes sont distincts — voir le tableau ci-dessous et la page
    [Commandes personnalisées](commandes.md).

| | Commande personnalisée | Skill |
|---|---|---|
| Fichier | `.claude/commands/x.md` | `.claude/skills/x/SKILL.md` (un dossier) |
| Invocation | **Manuelle** — vous tapez `/x` | **Automatique** — Claude décide selon la `description` |
| Rôle | Raccourci de prompt déclenché par vous | Capacité activée par Claude au bon moment |
| Contenu | Un prompt | Instructions + scripts/ressources éventuels |

---

## Où placer un skill

Un skill est un **dossier** contenant au minimum un fichier `SKILL.md`.

| Emplacement | Portée |
|---|---|
| `~/.claude/skills/<nom>/SKILL.md` | Personnel — tous les projets |
| `<projet>/.claude/skills/<nom>/SKILL.md` | Projet — versionné avec le dépôt |

---

## Anatomie d'un `SKILL.md`

```markdown
---
name: tableau-markdown
description: À utiliser quand l'utilisateur demande de convertir des données
  (liste, CSV, texte collé) en tableau Markdown aligné et lisible.
---

Convertis les données fournies en un tableau Markdown propre :

- Déduis les colonnes depuis la première ligne ou la structure des données.
- Aligne les séparateurs pour que le tableau soit lisible en texte brut.
- Si une valeur manque, mets une cellule vide plutôt que d'inventer.
```

### Clés du frontmatter

| Clé | Obligatoire | Rôle |
|---|---|---|
| `name` | Oui | Identifiant en minuscules-tirets, unique |
| `description` | Oui | **Le critère de déclenchement** : décrit *ce que fait* le skill et *quand* l'utiliser |
| `allowed-tools` | Non | Restreint les outils disponibles quand le skill est actif |

!!! tip "La `description` est la partie la plus importante"
    C'est le seul texte que Claude lit pour décider d'activer le skill. Soyez
    explicite sur les **déclencheurs** : « À utiliser quand… ». Une description
    vague (« aide pour les tableaux ») sera rarement sélectionnée au bon moment.

---

## Divulgation progressive — joindre des ressources

Un skill peut embarquer des fichiers dans son dossier (scripts, gabarits,
références). Claude ne les lit **que s'il en a besoin** — c'est la *divulgation
progressive*, qui garde le contexte léger.

```text
~/.claude/skills/rapport-csv/
├── SKILL.md            # instructions + quand l'utiliser
├── modele.md           # gabarit de rapport
└── analyser.py         # script appelé par Claude si nécessaire
```

Dans `SKILL.md`, il suffit de mentionner ces fichiers : « Utilise le gabarit
`modele.md` » ou « Lance `analyser.py` sur le fichier fourni ».

---

## Exemple simple et testable — `tableau-markdown`

### Étape 1 — Créer le skill

```bash
mkdir -p ~/.claude/skills/tableau-markdown
cat > ~/.claude/skills/tableau-markdown/SKILL.md << 'EOF'
---
name: tableau-markdown
description: À utiliser quand l'utilisateur demande de convertir des données
  (liste, CSV, texte collé) en tableau Markdown aligné et lisible.
---

Convertis les données fournies en un tableau Markdown propre :

- Déduis les colonnes depuis la première ligne ou la structure des données.
- Aligne les séparateurs pour que le tableau soit lisible en texte brut.
- Si une valeur manque, laisse la cellule vide plutôt que d'inventer.
EOF
```

### Étape 2 — Déclencher (sans le nommer)

Lancez Claude Code et formulez une demande qui **correspond à la
description** — sans jamais taper de commande :

```text
Convertis ces données en tableau :
nom;age;ville
Alice;30;Lyon
Bob;25;Paris
```

### Résultat attendu

Claude reconnaît que la demande correspond au skill, l'active seul, et répond :

```text
| nom   | age | ville |
|-------|-----|-------|
| Alice | 30  | Lyon  |
| Bob   | 25  | Paris |
```

!!! note "Comment vérifier que le skill a bien servi"
    Si vous supprimez le dossier du skill puis reposez la même question, Claude
    produira quand même un tableau — mais sans suivre vos règles précises
    (cellule vide plutôt qu'invention, alignement…). C'est la différence
    qu'apporte le skill.

---

## Autres exemples concrets

### `commit-conventionnel` — message de commit normalisé

Déclenché quand vous demandez de rédiger un commit. Il impose le format
[Conventional Commits](https://www.conventionalcommits.org/).

```markdown
---
name: commit-conventionnel
description: À utiliser quand l'utilisateur demande de rédiger ou proposer un
  message de commit Git.
allowed-tools: Bash(git diff:*), Bash(git status:*)
---

Rédige un message de commit au format Conventional Commits.

1. Inspecte les changements indexés (`git diff --staged`).
2. Choisis le type : `feat`, `fix`, `docs`, `refactor`, `test`, `chore`.
3. Rédige un sujet impératif de 50 caractères maximum, en anglais.
4. Ajoute un corps seulement si le « pourquoi » n'est pas évident.
```

Déclencheur : *« rédige le message de commit »* — sans taper de commande.

### `revue-bash` — relecture de script shell

```markdown
---
name: revue-bash
description: À utiliser quand l'utilisateur demande de relire, auditer ou
  améliorer un script Bash.
---

Relis le script Bash fourni et signale, par ordre de gravité :

- absence de `set -euo pipefail` ;
- variables non protégées par des guillemets (`"$var"`) ;
- usage de `[ ]` là où `[[ ]]` serait plus sûr ;
- commandes destructives sans garde-fou.

Propose une version corrigée à la fin.
```

Déclencheur : *« relis ce script »* en collant un `.sh`.

### `rapport-csv` — skill avec script embarqué

Illustre la divulgation progressive : le skill délègue le calcul à un script
Python livré dans son dossier.

```text
~/.claude/skills/rapport-csv/
├── SKILL.md
└── analyser.py     # uv run analyser.py <fichier.csv>
```

```markdown
---
name: rapport-csv
description: À utiliser quand l'utilisateur demande des statistiques ou un
  rapport sur un fichier CSV.
allowed-tools: Bash(uv run:*)
---

Pour analyser un fichier CSV :

1. Lance `uv run ~/.claude/skills/rapport-csv/analyser.py <fichier>`.
2. Présente la sortie sous forme de tableau Markdown.
3. Signale toute colonne au taux de valeurs manquantes supérieur à 10 %.
```

Déclencheur : *« fais-moi un rapport sur ventes.csv »*. Claude lit `SKILL.md`,
puis exécute `analyser.py` seulement à ce moment-là.

---

## Lister les skills disponibles

```bash
# Skills personnels
ls ~/.claude/skills/

# Skills du projet courant
ls .claude/skills/ 2>/dev/null || echo "Aucun skill local"
```
