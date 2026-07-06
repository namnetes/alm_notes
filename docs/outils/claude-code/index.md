# Claude Code

**Claude Code** est l'assistant IA en ligne de commande d'Anthropic. Il s'intègre
directement dans le terminal et dans Zed pour lire, écrire et exécuter du code
dans le contexte d'un projet entier.

---

## Démarrage rapide

```bash
# Installation
curl -fsSL https://claude.ai/install.sh | bash

# Premier lancement (ouvre le navigateur pour l'authentification)
claude

# Vérifier l'installation
claude --version
claude doctor
```

---

## Pages

<div class="grid cards" markdown>

-   :material-download-box-outline: **[Installation & Authentification](installation.md)**

    Abonnement vs API, installation, connexion, script de bascule.

-   :material-cog-outline: **[Configuration](configuration.md)**

    Hiérarchie CLAUDE.md, settings.local.json, déploiement Stow.

-   :material-slash-forward-box: **[Commandes personnalisées](commandes.md)**

    Commandes slash `/x` : frontmatter, arguments, injection `!`/`@`, exemple
    testable.

-   :material-microsoft-windows: :material-linux: **[Raccourcis clavier — Windows / Linux](raccourcis-windows-linux.md)**

    Contrôles généraux, édition de ligne, saisie multiligne, transcript
    viewer, mode Vim complet.

-   :material-apple: **[Raccourcis clavier — macOS](raccourcis-macos.md)**

    Idem, avec les variantes `Option`/`Cmd` et la configuration Meta requise
    par certains raccourcis.

-   :material-puzzle-outline: **[Skills](skills.md)**

    Agent Skills auto-invoqués par Claude : `SKILL.md`, divulgation
    progressive, exemple testable.

-   :material-jira: **[Jira (MCP)](jira-mcp.md)**

    Pas à pas : connecter Jira via MCP Atlassian, `CLAUDE.md` et skill prêts
    à coller.

-   :material-confluence: **[Confluence (MCP)](confluence-mcp.md)**

    Pas à pas : connecter Confluence via MCP Atlassian, `CLAUDE.md` et skill
    prêts à coller.

-   :material-console: **[Assistant terminal](terminal.md)**

    `ai`, `explain`, `fix` + kitten Kitty — intégration Warp-like.

-   :material-microsoft-visual-studio-code: **[Intégration Zed](zed.md)**

    Provider natif Anthropic et agent ACP dans Zed.

</div>

---

## Références

- [Tarification Claude](https://claude.com/pricing)
- [Documentation officielle — installation](https://code.claude.com/docs/en/setup)
- [Documentation officielle — authentification](https://code.claude.com/docs/en/authentication)
- [Console Anthropic (clés API)](https://console.anthropic.com)
