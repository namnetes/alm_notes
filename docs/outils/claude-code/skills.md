# Skills (Agent Skills)

Un **skill** (*Agent Skill*) est une compétence décrite dans un fichier
`SKILL.md`. Par défaut, elle est **doublement invocable** : Claude peut la
déclencher lui-même en lisant sa `description` quand votre demande
correspond, **et** vous pouvez la lancer à la main avec `/nom-du-skill`.

!!! warning "Depuis 2026 : commandes personnalisées et skills sont le même mécanisme"
    Anthropic a fusionné les deux systèmes. Un fichier
    `.claude/commands/x.md` et un skill `.claude/skills/x/SKILL.md`
    créent **tous les deux** la commande `/x` et se comportent pareil :
    invocables à la main **et** automatiquement par Claude, sauf
    frontmatter contraire (voir [Contrôler qui invoque le
    skill](#controler-qui-invoque-le-skill) plus bas). Le dossier
    `.claude/commands/` reste pris en charge — c'est le format historique,
    sans dossier de ressources associées — mais `.claude/skills/` est
    recommandé pour tout nouveau contenu : il ajoute la [divulgation
    progressive](#divulgation-progressive-joindre-des-ressources), le
    contrôle fin de qui peut invoquer le skill, et l'exécution en subagent
    isolé (`context: fork`). En cas de conflit de nom entre les deux,
    **le skill l'emporte**. Voir aussi [Commandes
    personnalisées](commandes.md).

| | `.claude/commands/x.md` | `.claude/skills/x/SKILL.md` |
|---|---|---|
| Invocation manuelle (`/x`) | Oui | Oui |
| Invocation automatique par Claude | Oui (sauf `disable-model-invocation: true`) | Oui (sauf `disable-model-invocation: true`) |
| Dossier de ressources associées | Non | Oui (scripts, gabarits, docs de référence…) |
| Recommandé pour | Prompts courts, sans ressource | Tout le reste |

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

Tous les champs sont **facultatifs** ; seul `description` est recommandé.
Liste non exhaustive (une quinzaine de champs existent au total, voir la
[documentation officielle](https://code.claude.com/docs/en/skills#frontmatter-reference)) :

| Clé | Rôle |
|---|---|
| `name` | Nom affiché dans les listings — ne change **pas** ce que vous tapez après `/` (c'est le nom du dossier qui le détermine) |
| `description` | **Le critère de déclenchement automatique** : décrit *ce que fait* le skill et *quand* l'utiliser |
| `allowed-tools` | Pré-autorise des outils (sans prompt de confirmation) tant que le skill est actif |
| `disable-model-invocation` | `true` = seul **vous** pouvez invoquer le skill, Claude ne le déclenche jamais seul |
| `user-invocable` | `false` = seul **Claude** peut l'invoquer ; masqué du menu `/` |
| `context: fork` | Exécute le skill dans un **subagent isolé** (voir `agent:` pour choisir lequel) |
| `model`, `effort` | Force un modèle ou un niveau d'effort pour la durée du skill |

!!! tip "La `description` est la partie la plus importante"
    C'est le texte que Claude lit pour décider d'activer le skill tout seul.
    Soyez explicite sur les **déclencheurs** : « À utiliser quand… ». Une
    description vague (« aide pour les tableaux ») sera rarement sélectionnée
    au bon moment.

---

## Contrôler qui invoque le skill

Par défaut, **vous et Claude** pouvez tous les deux invoquer un skill.

!!! example "`disable-model-invocation: true` — invocation manuelle uniquement"
    Pour un skill à effet de bord (déploiement, envoi de message…), on ne
    veut **pas** que Claude le déclenche seul :

    ```markdown
    ---
    name: deploy
    description: Déploie l'application en production
    disable-model-invocation: true
    ---

    Déploie $ARGUMENTS en production :
    1. Lance la suite de tests
    2. Construit l'application
    3. Pousse vers la cible de déploiement
    ```

    Seul `/deploy` déclenche ce skill — jamais une décision autonome de Claude.

!!! example "`user-invocable: false` — invocation automatique uniquement"
    Pour une connaissance de fond que Claude doit connaître mais qui n'est
    pas une action à lancer à la main (ex. « comment fonctionne cet ancien
    système ») : `user-invocable: false` masque le skill du menu `/`, mais
    Claude continue de le charger automatiquement quand c'est pertinent.

Le passage d'arguments (`$ARGUMENTS`, `$1`, `$2`…) fonctionne à l'identique
pour les commandes et les skills — voir [Passer des
arguments](commandes.md#passer-des-arguments).

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
