#!/usr/bin/env python3
"""Script interactif pour gérer les pages du wiki MkDocs."""

import os
import re
import sys
import unicodedata
from pathlib import Path

import yaml

DOCS_DIR = Path(__file__).parent / "docs"
MKDOCS_YML = Path(__file__).parent / "mkdocs.yml"

PAGE_TEMPLATE = """# {title}

"""


# ---------------------------------------------------------------------------
# YAML — loader/dumper qui préserve les tags !!python/name:
# ---------------------------------------------------------------------------

class _PythonTag:
    def __init__(self, tag: str, value: str) -> None:
        self.tag = tag
        self.value = value


def _build_loader() -> type:
    loader = yaml.SafeLoader

    def constructor(ldr, tag_suffix, node):
        return _PythonTag(f"tag:yaml.org,2002:python/name:{tag_suffix}", node.value)

    yaml.add_multi_constructor("tag:yaml.org,2002:python/name:", constructor, Loader=loader)
    return loader


def _build_dumper() -> type:
    dumper = yaml.Dumper

    def representer(dmp, data: _PythonTag):
        return dmp.represent_scalar(data.tag, data.value)

    dumper.add_representer(_PythonTag, representer)
    return dumper


_LOADER = _build_loader()
_DUMPER = _build_dumper()


def load_mkdocs() -> dict:
    with open(MKDOCS_YML, encoding="utf-8") as f:
        return yaml.load(f, Loader=_LOADER)


def save_mkdocs(data: dict) -> None:
    with open(MKDOCS_YML, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=_DUMPER, allow_unicode=True, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# Utilitaires — nav
# ---------------------------------------------------------------------------

def collect_sections(nav: list, prefix: str = "") -> list[tuple[str, list]]:
    """Retourne [(label_complet, liste_nav)] pour toutes les sections."""
    sections = []
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    label = f"{prefix}{key}" if prefix else key
                    sections.append((label, value))
                    sections.extend(collect_sections(value, prefix=f"{label} > "))
    return sections


def collect_pages(nav: list) -> list[tuple[str, str]]:
    """Retourne [(titre, chemin_relatif)] pour toutes les pages dans nav."""
    pages = []
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str):
                    pages.append((key or value, value))
                elif isinstance(value, list):
                    pages.extend(collect_pages(value))
        elif isinstance(item, str):
            pages.append((item, item))
    return pages


def infer_section_dir(section_nav: list) -> str | None:
    for item in section_nav:
        if isinstance(item, dict):
            for value in item.values():
                if isinstance(value, str) and "/" in value:
                    return str(Path(value).parent)
        elif isinstance(item, str) and "/" in item:
            return str(Path(item).parent)
    return None


def nav_add_to_section(nav: list, target_label: str, entry: dict, prefix: str = "") -> bool:
    for item in nav:
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    label = f"{prefix}{key}" if prefix else key
                    if label == target_label:
                        value.append(entry)
                        return True
                    if nav_add_to_section(value, target_label, entry, prefix=f"{label} > "):
                        return True
    return False


def nav_remove_page(nav: list, target_rel: str) -> bool:
    """Supprime dans nav l'entrée pointant vers target_rel."""
    for i, item in enumerate(nav):
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, str) and value == target_rel:
                    nav.pop(i)
                    return True
                if isinstance(value, list) and nav_remove_page(value, target_rel):
                    return True
        elif isinstance(item, str) and item == target_rel:
            nav.pop(i)
            return True
    return False


def nav_remove_section(nav: list, target_label: str, prefix: str = "") -> bool:
    """Supprime dans nav la section identifiée par son label complet."""
    for i, item in enumerate(nav):
        if isinstance(item, dict):
            for key, value in item.items():
                if isinstance(value, list):
                    label = f"{prefix}{key}" if prefix else key
                    if label == target_label:
                        nav.pop(i)
                        return True
                    if nav_remove_section(value, target_label, prefix=f"{label} > "):
                        return True
    return False


# ---------------------------------------------------------------------------
# Utilitaires — analyse d'impact
# ---------------------------------------------------------------------------

_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)#\s]+)\)")


def find_references(target_rel: str, exclude_rels: set[str] | None = None) -> list[tuple[Path, int, str]]:
    """
    Cherche dans tous les fichiers .md de docs/ les liens pointant vers target_rel.
    exclude_rels : chemins relatifs à ignorer (ex. pages de la même section).
    """
    target_path = Path(target_rel)
    filename = target_path.name

    hits: list[tuple[Path, int, str]] = []
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        rel_file = md_file.relative_to(DOCS_DIR)
        if str(rel_file) == target_rel:
            continue
        if exclude_rels and str(rel_file) in exclude_rels:
            continue

        lines = md_file.read_text(encoding="utf-8").splitlines()
        for lineno, line in enumerate(lines, 1):
            for match in _LINK_RE.finditer(line):
                href = match.group(2)
                href_norm = Path(href).name
                if href_norm == filename or target_rel in href:
                    hits.append((md_file, lineno, line.strip()))
                    break  # une seule occurrence par ligne suffit
    return hits


def print_refs(refs: list[tuple[Path, int, str]]) -> None:
    for md_file, lineno, line in refs:
        rel = md_file.relative_to(DOCS_DIR)
        print(f"   docs/{rel}:{lineno}")
        print(f"      {line}")


# ---------------------------------------------------------------------------
# Utilitaires — I/O
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def prompt(message: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{message}{suffix}: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nAnnulé.")
        sys.exit(0)
    return answer if answer else default


def choose_from_list(items: list[str], label: str) -> int:
    print(f"\n{label}")
    for i, item in enumerate(items, 1):
        print(f"  {i:2}. {item}")
    while True:
        raw = prompt("Votre choix (numéro)")
        if raw.isdigit() and 1 <= int(raw) <= len(items):
            return int(raw) - 1
        print(f"  Entrez un nombre entre 1 et {len(items)}.")


# ---------------------------------------------------------------------------
# Commandes
# ---------------------------------------------------------------------------

def cmd_create_section(config: dict) -> None:
    nav: list = config.get("nav", [])
    sections = collect_sections(nav)

    section_name = prompt("\nNom de la nouvelle section")
    if not section_name:
        print("Nom vide, abandon.")
        return

    section_dir = prompt("Repertoire (sous docs/)", default=slugify(section_name))

    # Section parente optionnelle
    parent_labels = ["[ Racine ]"] + [label for label, _ in sections]
    parent_idx = choose_from_list(parent_labels, "Ou placer cette section ?")

    new_section_nav: list = []
    nav_entry = {section_name: new_section_nav}

    if parent_idx == 0:
        nav.append(nav_entry)
    else:
        parent_label = parent_labels[parent_idx]
        nav_add_to_section(nav, parent_label, nav_entry)

    # Index optionnel
    want_index = prompt("Creer un fichier index.md ? (o/n)", default="o")
    if want_index.lower() in ("o", "oui", "y", "yes"):
        index_path = DOCS_DIR / section_dir / "index.md"
        index_path.parent.mkdir(parents=True, exist_ok=True)
        index_path.write_text(PAGE_TEMPLATE.format(title=section_name), encoding="utf-8")
        new_section_nav.append(f"{section_dir}/index.md")
        print(f"Index cree  : docs/{section_dir}/index.md")
    else:
        (DOCS_DIR / section_dir).mkdir(parents=True, exist_ok=True)

    config["nav"] = nav
    save_mkdocs(config)
    print(f"Section '{section_name}' ajoutee dans mkdocs.yml")


def cmd_add_page(config: dict) -> None:
    nav: list = config.get("nav", [])

    sections = collect_sections(nav)
    if not sections:
        print("Aucune section existante. Creez d'abord une section.")
        return

    idx = choose_from_list([label for label, _ in sections], "Dans quelle section ajouter la page ?")
    target_label, target_nav_list = sections[idx]
    section_dir = infer_section_dir(target_nav_list) or slugify(target_label.split(" > ")[-1])

    page_title = prompt("\nTitre de la page")
    if not page_title:
        print("Titre vide, abandon.")
        return

    file_slug = prompt("Nom du fichier (sans .md)", default=slugify(page_title))
    rel_path = f"{section_dir}/{file_slug}.md"
    abs_path = DOCS_DIR / rel_path

    print(f"\nRecapitulatif :")
    print(f"  Titre   : {page_title}")
    print(f"  Fichier : docs/{rel_path}")
    print(f"  Section : {target_label}")
    if prompt("Confirmer ? (o/n)", default="o").lower() not in ("o", "oui", "y", "yes"):
        print("Annule.")
        return

    abs_path.parent.mkdir(parents=True, exist_ok=True)
    if abs_path.exists():
        print(f"\nATTENTION : docs/{rel_path} existe deja.")
        if prompt("Ecraser ? (o/n)", default="n").lower() not in ("o", "oui", "y", "yes"):
            print("Annule.")
            return

    abs_path.write_text(PAGE_TEMPLATE.format(title=page_title), encoding="utf-8")

    nav_add_to_section(nav, target_label, {page_title: rel_path})

    config["nav"] = nav
    save_mkdocs(config)

    editor = config.get("editor") or os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"
    print(f"\nPage creee  : docs/{rel_path}")
    print("nav mis a jour dans mkdocs.yml\n")
    print("Pour editer la page :")
    print(f"\n    {editor} docs/{rel_path}\n")


def cmd_delete_page(config: dict) -> None:
    nav: list = config.get("nav", [])
    pages = collect_pages(nav)

    if not pages:
        print("Aucune page dans la navigation.")
        return

    labels = [f"{title}  (docs/{rel})" for title, rel in pages]
    idx = choose_from_list(labels, "Quelle page supprimer ?")
    title, rel_path = pages[idx]
    abs_path = DOCS_DIR / rel_path

    print(f"\nPage      : {title}")
    print(f"Fichier   : docs/{rel_path}")

    print("\nAnalyse des references en cours...")
    refs = find_references(rel_path)

    if refs:
        print(f"\n[!] {len(refs)} reference(s) vers cette page :\n")
        print_refs(refs)
        print()
    else:
        print("  Aucune reference trouvee dans les autres pages.\n")

    if prompt("Supprimer definitivement ? (o/n)", default="n").lower() not in ("o", "oui", "y", "yes"):
        print("Annule.")
        return

    if abs_path.exists():
        abs_path.unlink()
        print(f"Fichier supprime : docs/{rel_path}")
    else:
        print(f"Fichier introuvable (deja supprime ?) : docs/{rel_path}")

    nav_remove_page(nav, rel_path)
    config["nav"] = nav
    save_mkdocs(config)
    print("Navigation mise a jour dans mkdocs.yml")


def cmd_delete_section(config: dict) -> None:
    nav: list = config.get("nav", [])
    sections = collect_sections(nav)

    if not sections:
        print("Aucune section dans la navigation.")
        return

    idx = choose_from_list([label for label, _ in sections], "Quelle section supprimer ?")
    target_label, section_nav = sections[idx]
    pages_in_section = collect_pages(section_nav)
    section_rels = {rel for _, rel in pages_in_section}

    print(f"\nSection : {target_label}")
    print(f"Pages concernees ({len(pages_in_section)}) :")
    for title, rel in pages_in_section:
        print(f"  - {title}  (docs/{rel})")

    print("\nAnalyse des references externes en cours...")
    impact: dict[str, tuple[str, list]] = {}
    for title, rel in pages_in_section:
        refs = find_references(rel, exclude_rels=section_rels)
        if refs:
            impact[rel] = (title, refs)

    if impact:
        total = sum(len(r) for _, r in impact.values())
        print(f"\n[!] {total} reference(s) externe(s) vers des pages de cette section :\n")
        for rel, (title, refs) in impact.items():
            print(f"  [{title}]  docs/{rel}")
            print_refs(refs)
            print()
    else:
        print("  Aucune reference externe trouvee.\n")

    if prompt("Supprimer la section et tous ses fichiers ? (o/n)", default="n").lower() not in ("o", "oui", "y", "yes"):
        print("Annule.")
        return

    deleted = 0
    dirs_to_check: set[Path] = set()
    for _, rel in pages_in_section:
        abs_path = DOCS_DIR / rel
        dirs_to_check.add(abs_path.parent)
        if abs_path.exists():
            abs_path.unlink()
            deleted += 1

    for d in sorted(dirs_to_check, reverse=True):
        if d.exists() and d != DOCS_DIR and not any(d.iterdir()):
            d.rmdir()

    print(f"{deleted} fichier(s) supprime(s).")

    nav_remove_section(nav, target_label)
    config["nav"] = nav
    save_mkdocs(config)
    print("Navigation mise a jour dans mkdocs.yml")


# ---------------------------------------------------------------------------
# Point d'entrée
# ---------------------------------------------------------------------------

def main() -> None:
    print("=" * 50)
    print("  Wikinotes — Gestionnaire de pages")
    print("=" * 50)

    config = load_mkdocs()

    actions = [
        "Creer une section",
        "Ajouter une page",
        "Supprimer une page",
        "Supprimer une section",
        "Quitter",
    ]
    idx = choose_from_list(actions, "Que souhaitez-vous faire ?")

    if idx == 0:
        cmd_create_section(config)
    elif idx == 1:
        cmd_add_page(config)
    elif idx == 2:
        cmd_delete_page(config)
    elif idx == 3:
        cmd_delete_section(config)
    else:
        print("Au revoir.")


if __name__ == "__main__":
    main()
