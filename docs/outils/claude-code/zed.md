# Intégration Zed

Zed propose **deux intégrations Claude distinctes**. Il est important de
comprendre laquelle correspond à votre besoin avant de configurer.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"background": "#ffffff"}}}%%
flowchart LR
    classDef startStop fill:#e1f5fe,stroke:#01579b,color:#000
    classDef logic     fill:#e8eaf6,stroke:#1a237e,color:#000
    classDef external  fill:#f3e5f5,stroke:#6a1b9a,color:#000

    User([Utilisateur Zed]):::startStop

    subgraph Zed["Éditeur Zed"]
        Panel[Panneau Agent]:::logic
    end

    Native[[Provider Anthropic natif\nclé API uniquement]]:::external
    ACP[[Agent externe Claude Code\nACP — abonnement ou clé API]]:::external
    API[(API Anthropic)]:::external

    User --> Panel
    Panel -->|"option A"| Native --> API
    Panel -->|"option B"| ACP --> API

    subgraph Legend["Légende"]
        direction LR
        L1([Acteur]):::startStop
        L2[Composant Zed]:::logic
        L3[[Service externe]]:::external
    end
```

| Intégration | Authentification | Avantages | Limites |
|-------------|-----------------|-----------|---------|
| **Provider natif** | Clé API uniquement | Réponses rapides, modèles sélectionnables | Pas d'agent autonome, pas d'outils Claude Code |
| **Claude Code via ACP** | Abonnement **ou** clé API | Outils complets (fichiers, bash, MCP) | Démarrage légèrement plus lent |

Le fichier de configuration Zed sur Linux : `~/.config/zed/settings.json`

---

## Option A — Provider Anthropic natif

Pour un usage « LLM dans l'éditeur » sans capacités d'agent.

**Saisir la clé via l'UI** (recommandé — stockée dans le trousseau système) :

1. Ouvrir le panneau Agent : ++ctrl+question++
2. Menu **agent: open settings**
3. Coller la clé Anthropic dans le champ prévu

!!! warning "Ne pas mettre la clé en clair dans `settings.json`"
    Préférer la saisie via l'UI : la clé est stockée dans le trousseau du
    système (keyring), pas en texte brut.

Déclarer les modèles disponibles dans `settings.json` :

```json
{
  "language_models": {
    "anthropic": {
      "available_models": [
        {
          "name": "claude-opus-4-8",
          "display_name": "Claude Opus 4.8",
          "max_tokens": 200000,
          "max_output_tokens": 8192
        },
        {
          "name": "claude-sonnet-4-6",
          "display_name": "Claude Sonnet 4.6",
          "max_tokens": 200000,
          "max_output_tokens": 8192
        },
        {
          "name": "claude-sonnet-4-6",
          "display_name": "Claude Sonnet 4.6 (Thinking)",
          "max_tokens": 200000,
          "max_output_tokens": 8192,
          "mode": {
            "type": "thinking",
            "budget_tokens": 4096
          }
        }
      ]
    }
  }
}
```

---

## Option B — Claude Code comme agent externe (ACP)

Permet d'utiliser l'**abonnement Pro/Max** directement dans Zed, avec accès
aux outils complets de Claude Code (édition de fichiers, exécution bash, MCP).

Dans `~/.config/zed/settings.json` :

```json
{
  "agent_servers": {
    "claude-acp": {
      "type": "registry"
    }
  }
}
```

Au premier démarrage d'un thread Claude Agent, Zed télécharge automatiquement
le paquet [`@zed-industries/claude-agent-acp`](https://github.com/zed-industries/claude-agent-acp).

!!! info "Authentification ACP — totalement séparée du provider natif"
    Se connecter dans le thread lui-même :

    1. Ouvrir un nouveau thread Claude Agent
    2. Taper `/login` dans le thread
    3. Choisir : **Log in with Claude Code** (abonnement OAuth) ou **API key**

### Ouvrir un thread Claude Agent

- ++ctrl+question++ → cliquer sur **+** → choisir **Claude Agent**

Raccourci personnalisé dans `~/.config/zed/keymap.json` :

```json
[
  {
    "bindings": {
      "ctrl-alt-c": [
        "agent::NewExternalAgentThread",
        { "agent": { "custom": { "name": "claude-acp" } } }
      ]
    }
  }
]
```

### Forcer un binaire `claude` particulier

```json
{
  "agent_servers": {
    "claude-acp": {
      "type": "registry",
      "env": {
        "CLAUDE_CODE_EXECUTABLE": "/home/galan/.local/bin/claude"
      }
    }
  }
}
```

Utile si plusieurs versions de Claude Code coexistent (canal `latest` vs `stable`).

---

## Références

- [Zed — agents externes (ACP)](https://zed.dev/docs/ai/external-agents)
- [Zed — fournisseurs de modèles](https://zed.dev/docs/ai/llm-providers)
- [zed-industries/claude-agent-acp](https://github.com/zed-industries/claude-agent-acp)
