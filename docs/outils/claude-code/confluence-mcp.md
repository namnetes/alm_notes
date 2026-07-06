# Confluence pas à pas (MCP)

Ce guide connecte Claude Code à **Confluence** via le serveur MCP officiel
d'Atlassian, puis met en place le contexte (`CLAUDE.md`) et le réflexe (skill)
pour des demandes **courtes** — sans répéter l'URL ni l'authentification.

!!! info "Le même serveur MCP couvre Jira et Confluence"
    Si vous avez déjà suivi [Jira pas à pas](jira-mcp.md), le serveur
    `atlassian` est **déjà connecté** : passez directement à l'étape 2.

!!! warning "Atlassian Cloud uniquement"
    Le serveur MCP officiel ne fonctionne qu'avec **Atlassian Cloud**. Pour un
    Confluence **Data Center / Server** auto-hébergé, il faut passer par l'API
    REST (script appelé via l'outil `Bash`) ou un MCP self-hosted.

---

## Prérequis

- Claude Code installé et authentifié (voir [Installation](installation.md)).
- Un compte **Atlassian Cloud** avec accès à l'espace Confluence visé.

---

## Étape 1 — Connecter le serveur MCP Atlassian

!!! note "Déjà fait pour Jira ?"
    Si le serveur `atlassian` apparaît dans `claude mcp list`, sautez cette
    étape — il dessert aussi Confluence.

```bash
claude mcp add --transport http --scope project \
    atlassian https://mcp.atlassian.com/v1/mcp/authv2
```

Le détail (scopes, choix personnel vs équipe) est documenté à l'étape 1 de
[Jira pas à pas](jira-mcp.md#etape-1-connecter-le-serveur-mcp-atlassian).

---

## Étape 2 — S'authentifier (OAuth, une seule fois)

Dans la session Claude Code :

```text
/mcp
```

Sélectionnez `atlassian`, connectez-vous dans le navigateur. Le jeton est
stocké et rafraîchi automatiquement.

!!! danger "Aucun secret dans `CLAUDE.md`"
    L'authentification vit dans la connexion MCP, jamais dans un fichier
    versionné.

---

## Étape 3 — Le `CLAUDE.md` (à coller dans le projet)

Remplacez les valeurs entre `<…>` puis collez ce bloc dans le `CLAUDE.md` à
la racine du projet.

```markdown
## Confluence

- Outils : serveur MCP `atlassian` (déjà connecté, OAuth). Ne jamais demander
  d'identifiants.
- Espace Confluence par défaut : `<CLE_ESPACE>` — page racine : <URL_RACINE>.
- Les URLs de pages spécifiques se trouvent dans les fichiers du dossier
  `<dossier/contenant/les/urls>`.
- Règle d'écriture : avant de créer ou modifier une page, montrer le contenu
  proposé (titre + corps) et attendre ma validation explicite.
- Style : reprendre le ton et la structure des pages existantes de l'espace.
```

Désormais, *« publie cette synthèse dans l'espace habituel »* suffit.

---

## Étape 4 — Le skill (à coller dans le projet)

```text
<projet>/.claude/skills/confluence/SKILL.md
```

```markdown
---
name: confluence
description: À utiliser dès que l'utilisateur veut consulter, résumer, créer
  ou mettre à jour une page Confluence, y compris quand l'URL est dans un
  fichier du projet.
allowed-tools: mcp__atlassian__*
---

Pour toute demande Confluence :

1. Identifie la page : URL trouvée dans le fichier mentionné ; sinon utilise
   l'espace par défaut du CLAUDE.md.
2. Lecture : résume ou extrais l'information demandée de façon concise.
3. Écriture (création, mise à jour) : propose d'abord le titre et le corps en
   Markdown, attends « ok », puis appelle l'outil MCP.
4. Respecte la structure et le ton des pages existantes de l'espace.
```

---

## Étape 5 — (Optionnel) une commande courte

```text
<projet>/.claude/commands/confluence-publie.md
```

```markdown
---
description: Prépare une page Confluence à partir d'un fichier du projet
argument-hint: <chemin/fichier.md>
allowed-tools: mcp__atlassian__*
---

À partir du contenu de @$ARGUMENTS, propose une page Confluence (titre +
corps) pour l'espace par défaut. Montre le rendu proposé et attends ma
validation avant de la créer via le serveur MCP `atlassian`.
```

Invocation : `/confluence-publie docs/analyse.md`.

---

## Étape 6 — Vérifier avec des prompts courts

```text
Résume la page Confluence liée dans @docs/specs.md.
Crée une page « Compte rendu — sprint 12 » à partir de @notes/sprint12.md.
Mets à jour la page d'architecture avec la section que je viens d'écrire.
```

Chaque écriture passe par une proposition validée avant publication.

---

## Dépannage

| Symptôme | Cause probable | Action |
|---|---|---|
| `atlassian` en *pending* dans `/mcp` | OAuth non effectué | Relancer `/mcp` et se connecter |
| `401` / `403` | Jeton expiré ou droits insuffisants | `/mcp` → *Clear authentication*, puis se reconnecter |
| Page créée au mauvais endroit | Espace par défaut absent du `CLAUDE.md` | Préciser `<CLE_ESPACE>` dans le `CLAUDE.md` |
| Rien ne se passe sur un Confluence interne | Instance Data Center | Le MCP cloud ne s'applique pas — voir l'avertissement en tête |
