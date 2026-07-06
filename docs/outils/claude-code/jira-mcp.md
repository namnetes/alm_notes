# Jira pas à pas (MCP)

Ce guide connecte Claude Code à **Jira** via le serveur MCP officiel
d'Atlassian, puis met en place le contexte (`CLAUDE.md`) et le réflexe (skill)
pour que vos demandes restent **courtes** : plus besoin de répéter l'URL, ni
l'authentification, à chaque fois.

!!! info "Rappel des trois couches"
    - **Connexion** = serveur MCP (cette page) — la seule brique capable de
      *parler* à Jira.
    - **Contexte** = `CLAUDE.md` (quel projet, quel board) — chargé à chaque
      session.
    - **Réflexe** = [skill](skills.md) auto-déclenché par l'intention.

    Voir aussi [Confluence pas à pas](confluence-mcp.md) : le **même** serveur
    MCP couvre les deux.

!!! warning "Atlassian Cloud uniquement"
    Le serveur MCP officiel ne fonctionne qu'avec **Atlassian Cloud**. Pour un
    Jira **Data Center / Server** auto-hébergé, il faut passer par l'API REST
    (script appelé via l'outil `Bash`) ou un MCP self-hosted — la suite de ce
    guide ne s'applique pas.

---

## Prérequis

- Claude Code installé et authentifié (voir [Installation](installation.md)).
- Un compte **Atlassian Cloud** avec accès au projet Jira visé.
- Un navigateur pour le flux OAuth.

---

## Étape 1 — Connecter le serveur MCP Atlassian

Le serveur est ajouté en transport **HTTP**. Le scope `project` écrit la
configuration dans un fichier `.mcp.json` versionnable — toute l'équipe
partage alors la connexion (chacun s'authentifiant ensuite avec son propre
compte).

```bash
claude mcp add --transport http --scope project \
    atlassian https://mcp.atlassian.com/v1/mcp/authv2  # (1)!
```

1. `atlassian` est le nom local du serveur ; il préfixera les outils
   (`mcp__atlassian__*`). L'endpoint `…/v1/mcp/authv2` couvre Jira **et**
   Confluence.

!!! tip "Scope personnel"
    Pour un usage strictement personnel, retirez `--scope project` : la
    configuration est alors privée (dans `~/.claude.json`), sans fichier
    versionné.

---

## Étape 2 — S'authentifier (OAuth, une seule fois)

Lancez Claude Code, puis dans la session :

```text
/mcp
```

Sélectionnez `atlassian` et suivez la connexion dans le navigateur. Le jeton
est **stocké de façon sécurisée et rafraîchi automatiquement** — vous ne
ressaisirez plus jamais d'identifiants.

!!! danger "Ne mettez jamais de secret dans `CLAUDE.md`"
    L'authentification vit dans la connexion MCP (OAuth), pas dans vos prompts
    ni dans `CLAUDE.md`. Aucun token ne doit apparaître dans un fichier
    versionné.

Vérifiez que le serveur est connecté et expose ses outils :

```bash
claude mcp list
claude mcp get atlassian
```

Dans la session, `/mcp` affiche le nombre d'outils à côté de `atlassian`.

---

## Étape 3 — Le `CLAUDE.md` (à coller dans le projet)

Ce bloc donne à Claude le contexte permanent. Remplacez les valeurs entre
`<…>`, puis collez-le dans le `CLAUDE.md` à la racine du projet.

```markdown
## Jira

- Outils : serveur MCP `atlassian` (déjà connecté, OAuth). Ne jamais demander
  d'identifiants — l'authentification est gérée par MCP.
- Projet Jira par défaut : `<PROJ>` — board : <URL_DU_BOARD>.
- Les URLs de tickets spécifiques se trouvent dans les fichiers du dossier
  `<dossier/contenant/les/urls>`.
- Règle d'écriture : avant toute création ou mise à jour d'un ticket, montrer
  le changement proposé et attendre ma validation explicite.
```

À partir de là, *« quels tickets ouverts sur le board ? »* suffit : Claude
sait quel projet, via quel serveur.

---

## Étape 4 — Le skill (à coller dans le projet)

Le skill encapsule le *comment* et se déclenche **tout seul** dès que vous
parlez d'un ticket. Créez le dossier et le fichier :

```text
<projet>/.claude/skills/jira/SKILL.md
```

```markdown
---
name: jira
description: À utiliser dès que l'utilisateur veut consulter, rechercher,
  créer ou mettre à jour un ticket Jira, y compris quand l'URL ou la clé du
  ticket est dans un fichier du projet.
allowed-tools: mcp__atlassian__*
---

Pour toute demande Jira :

1. Identifie le ticket : clé (`<PROJ>-123`) ou URL trouvée dans le fichier
   mentionné ; sinon utilise le projet/board par défaut du CLAUDE.md.
2. Lecture (statut, description, commentaires) : résume de façon concise.
3. Écriture (création, changement de statut, commentaire) : présente d'abord
   le diff proposé et attends « ok » avant d'appeler l'outil MCP.
4. Ne modifie jamais plus que ce qui est explicitement demandé.
```

C'est la `description` qui déclenche le skill : rédigée autour de
« ticket Jira », elle est sélectionnée sans que vous nommiez le skill.

---

## Étape 5 — (Optionnel) une commande courte

Pour un geste que vous lancez toujours pareil, ajoutez une
[commande personnalisée](commandes.md) :

```text
<projet>/.claude/commands/jira.md
```

```markdown
---
description: Affiche le détail d'un ticket Jira
argument-hint: <CLE-TICKET>
allowed-tools: mcp__atlassian__*
---

Récupère le ticket Jira $ARGUMENTS via le serveur MCP `atlassian` et présente :
statut, assigné, description et les 3 derniers commentaires.
```

Invocation : `/jira <PROJ>-123`.

---

## Étape 6 — Vérifier avec des prompts courts

Une fois les étapes 1 à 4 en place, ces demandes fonctionnent sans rappeler
URL ni auth :

```text
Quels sont les tickets ouverts qui me sont assignés ?
Passe <PROJ>-123 en « En cours » et ajoute un commentaire de suivi.
Crée un bug à partir de l'erreur décrite dans @logs/incident.md.
```

Pour chaque écriture, Claude montre d'abord le changement et attend votre
validation (règle du `CLAUDE.md` + du skill).

---

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `atlassian` en *pending* dans `/mcp` | OAuth non effectué | Relancer `/mcp` et se connecter |
| `401` / `403` | Jeton expiré ou droits insuffisants | `/mcp` → *Clear authentication*, puis se reconnecter |
| Aucun outil exposé | Mauvais endpoint | Vérifier l'URL `…/v1/mcp/authv2` avec `claude mcp get atlassian` |
| Rien ne se passe sur un Jira interne | Instance Data Center | Le MCP cloud ne s'applique pas — voir l'avertissement en tête |
