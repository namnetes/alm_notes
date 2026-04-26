# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Wikinotes** — personal technical documentation wiki (French), built with MkDocs Material.
All documentation content is written in French.

## Commands

```bash
# Preview the wiki locally (hot reload)
uv run mkdocs serve

# Build the static site to site/
uv run mkdocs build

# Create a new wiki page interactively (registers it in mkdocs.yml nav automatically)
wnp

# First-time setup — installs the wnp shim into ~/.local/bin
bash install.sh
```

`install.sh` requires a `.venv` with PyYAML pre-installed:
```bash
python3 -m venv .venv && .venv/bin/pip install pyyaml
bash install.sh
```

## Architecture

### Content (`docs/`)
Markdown files organized into sections mirroring the MkDocs nav:
- `systeme/` — Ubuntu and Alpine Linux administration
- `developpement/` — Python, uv package manager
- `outils/` — GitHub CLI, ExifTool, yt-dlp
- `lcl/` — z/OS CI/CD pipelines, Kafka architecture, zDevOps governance
- `securite/` — TLS/SSL, AppArmor, certificates, encryption

### Navigation (`mkdocs.yml`)
The `nav:` tree is **manually maintained** and must stay in sync with actual files in `docs/`. Every new page must be added to `nav:` or MkDocs will warn about undocumented pages.

### `new-page.py` — page manager
Interactive CLI that:
1. Prompts for section, title, and optional filename slug
2. Creates the `.md` file from a minimal template
3. Inserts the new entry into the correct place in `mkdocs.yml` nav

Uses a custom YAML loader/dumper to preserve `!!python/name:` tags used by the `pymdownx.superfences` Mermaid fence — do not replace with plain `yaml.safe_load`/`yaml.dump`.

### `migrate.py`
One-shot TiddlyWiki → MkDocs migration script (historical, not for routine use). Hard-coded path to a local HTML export.

## MkDocs Extensions in Use

Key extensions that affect authoring:
- **Mermaid** via `pymdownx.superfences` custom fence — use ` ```mermaid ` blocks (see parent CLAUDE.md for diagram standards)
- **Admonitions** — `!!! note`, `!!! warning`, etc., with `??? details` for collapsible blocks
- **Code annotations** — `# (1)` markers with `content.code.annotate`
- **MathJax** — LaTeX via `$...$` inline and `$$...$$` block (arithmatex extension)
- **Tabs** — `=== "Tab name"` syntax (pymdownx.tabbed)
