#!/usr/bin/env python3
"""
Migration TiddlyWiki → MkDocs/Material
Extrait les tiddlers de grimoire_moderne.html et génère les fichiers Markdown.
"""

import re
import json
import base64
import os
from pathlib import Path
from collections import defaultdict

SRC = Path("/home/galan/alm-technook/grimoire_moderne.html")
DOCS = Path("/home/galan/workspaces/wikinotes/docs")
IMGS = DOCS / "assets" / "images"
MKDOCS_YML = Path("/home/galan/workspaces/wikinotes/mkdocs.yml")

# ─── Mapping tiddler → fichier destination ────────────────────────────────────
# Valeur = chemin relatif à docs/
# None = ignorer

FILE_MAP = {
    # SYSTEME / UBUNTU
    "Post-Installation Ubuntu 24.04":                            "systeme/ubuntu/post-installation.md",
    "01. Mettre à jour le système":                              "systeme/ubuntu/post-installation.md",
    "02. Créer une clé SSH pour accéder à des dépôts GitHub":    "systeme/ubuntu/post-installation.md",
    "03. Cloner divers projets Github personnels":               "systeme/ubuntu/post-installation.md",
    "04. Starship Cross-Shell Prompt":                           "systeme/ubuntu/post-installation.md",
    "05. Installer la police Firacode":                          "systeme/ubuntu/post-installation.md",
    "06. Configurez Gnome Terminal":                             "systeme/ubuntu/post-installation.md",
    "07. Configurer Nautilus":                                   "systeme/ubuntu/post-installation.md",
    "08. Installer firefox depuis les dépôts PPA de Mozilla":    "systeme/ubuntu/post-installation.md",
    "09. Exporter/Importer les Exceptions de coockies Firefox":  "systeme/ubuntu/post-installation.md",
    "10. Installez Ubuntu Restricetd Packages":                  "systeme/ubuntu/post-installation.md",
    "11. Paramétrage Gnome":                                     "systeme/ubuntu/post-installation.md",
    "12. Définir kitty comment terminal par défaut":             "systeme/ubuntu/post-installation.md",
    "Mes extensions":                                            "systeme/ubuntu/gnome.md",
    "GNU Stow et la gestion des dotfiles":                       "systeme/ubuntu/dotfiles.md",

    # SYSTEME / ALPINE
    "Alpine Linux":                                              "systeme/alpine/index.md",
    "Post-Installation Alpine Linux":                            "systeme/alpine/post-installation.md",
    "Changer le nom d\u2019hôte":                                "systeme/alpine/post-installation.md",
    "Installer les définitions de terminaux":                    "systeme/alpine/post-installation.md",
    "Création d'un partage de répertoire(s)":                    "systeme/alpine/partage.md",
    "Créer une machine virtuelle Alpine Linux avec KVM":         "systeme/alpine/vm-kvm.md",
    "Installation Alpine Linux 3.19.2 sur une VM KVM":           "systeme/alpine/installation-kvm.md",
    "Installer docker sur la VM Alpine Linux":                   "systeme/alpine/docker.md",
    "Lazydocker":                                                "systeme/alpine/lazydocker.md",

    # VIRTUALISATION
    "Virtualisation":                                            "virtualisation/index.md",
    "Introduction à KVM et QEMU":                                "virtualisation/introduction.md",
    "Installer KVM, QEMU et Libvirt":                            "virtualisation/installation.md",
    "Libvirt et KVM":                                            "virtualisation/libvirt.md",
    "Réseaux et KVM":                                            "virtualisation/reseau.md",
    "KVM virtio et un réseau NAT":                               "virtualisation/reseau.md",
    "Réseau par défaut":                                         "virtualisation/reseau.md",
    "Réseau par défaut depuis virt-manager":                     "virtualisation/reseau.md",
    "Automatiser l'accès SSH à une machine virtuelle KVM":       "virtualisation/ssh.md",
    "Autoriser le port forwarding":                              "virtualisation/port-forwarding.md",

    # CONTENEURS
    "0. Introduction à Docker":                                  "conteneurs/index.md",
    "1. Installer et Utiliser Docker sur Ubuntu 24.04":          "conteneurs/installation.md",
    "2. Installer cosign":                                       "conteneurs/cosign.md",
    "3. Installer Docker Compose":                               "conteneurs/compose.md",
    "4. Version docker-compose dans docker-compose.yml":         "conteneurs/compose.md",
    "5. Les capacités réseau de Docker":                         "conteneurs/reseau.md",

    # DEVELOPPEMENT / PYTHON
    "Développement Python":                                      "developpement/python/index.md",
    "Python dans Ubuntu 24.04":                                  "developpement/python/environnement.md",
    "Définir l'ordre de priorité Python":                        "developpement/python/environnement.md",
    "Reproduire un environnement virtuel de développement":      "developpement/python/environnement.md",
    "Création du projet sandbox en utilsant uv":                 "developpement/python/uv.md",
    "Exemples d'utilisation de deque":                           "developpement/python/deque.md",
    "Requête GET simple":                                        "developpement/python/urllib3.md",
    "Requête envoi de données":                                  "developpement/python/urllib3.md",
    "Télécharger un fichier":                                    "developpement/python/urllib3.md",
    "Authentificaiton par token":                                "developpement/python/urllib3.md",
    "Parser un fichier html avec beautifulsoup":                 "developpement/python/beautifulsoup.md",

    # DEVELOPPEMENT / WEB
    "Html":                                                      "developpement/web/html.md",
    "Les URL":                                                   "developpement/web/html.md",
    "Les caractères spéciaux HTML":                              "developpement/web/html.md",

    # DEVELOPPEMENT DIVERS
    "Traitement de Données et Tableaux":                         "developpement/bash.md",
    "mapfile":                                                   "developpement/bash.md",
    "rust":                                                      "developpement/rust.md",
    "Installer Appache Groovy":                                  "developpement/groovy.md",
    "Installer Lua":                                             "developpement/lua.md",
    "Installer les JDK/JRE Java":                                "developpement/java.md",
    "Installer Node.JS":                                         "developpement/nodejs.md",
    "1. Installer fnm (Fast Node Manager)":                      "developpement/nodejs.md",
    "2. Ecrire un prorgamme de test":                            "developpement/nodejs.md",

    # IA
    "IA":                                                        "ia/index.md",
    "IA Locale avec Ollama & VS Code":                           "ia/ollama-vscode.md",
    "Configurer ollama & qwen3-coder:30b":                       "ia/qwen3-coder.md",
    "Claude Code (Terminal Edition) 2026":                       "ia/claude-code.md",
    "Installer Gemini CLI":                                      "ia/gemini-cli.md",
    "Interactions de base":                                      "ia/gemini-cli.md",

    # OUTILS
    "Installer Microsoft Visual Studio Code":                    "outils/vscode.md",
    "Extensions utiles":                                         "outils/vscode.md",
    "Générateur d'extension Microsoft VS Code":                  "outils/vscode.md",
    "Client GitHub CLI":                                         "outils/github-cli.md",
    "1. Générez un jeton d'authentification":                    "outils/github-cli.md",
    "2. Connexion aux services GitHub":                          "outils/github-cli.md",
    "4. Lister tous les dépôts et gist":                         "outils/github-cli.md",
    "5. Cloner un dépôt":                                        "outils/github-cli.md",
    "ExifTool : L'utilitaire ultime pour la manipulation des métadonnées": "outils/exiftool.md",
    "yt-dlp Téléchargement de vidéo Youtube":                    "outils/yt-dlp.md",
    "Dashy : Une alternative moderne à Homer":                   "outils/dashy.md",
    "Installer Microsoft Edge":                                  "outils/microsoft-edge.md",
    "Ansible":                                                   "outils/ansible.md",

    # RESEAU
    "Réseau":                                                    "reseau/index.md",
    "Comprendre l\u2019attribution de l\u2019adresse IP avec DHCP": "reseau/dhcp.md",
    "Qu\u2019est-ce que mDNS ?":                                 "reseau/mdns.md",
    "Serveur SFTP":                                              "reseau/sftp.md",
    "Installer un serveur SFTP léger sur Ubuntu 24.04":          "reseau/sftp.md",
    "Partage de fichiers et répertoires":                        "reseau/partage-fichiers.md",

    # SECURITE
    "Sécurité":                                                  "securite/index.md",
    "Certificats":                                               "securite/certificats.md",
    "Format des certificats":                                    "securite/certificats.md",
    "Chiffrer et déchiffrer des fichiers et des répertoires avec openssl": "securite/openssl.md",
    "ecryptfs":                                                  "securite/ecryptfs.md",
    "1. Créer un répertoire sécurisé":                           "securite/ecryptfs.md",
    "2. Récupérer les données avec System Rescue CD":            "securite/ecryptfs.md",
    "3. Suppression du dossier sécurisé":                        "securite/ecryptfs.md",
    "4. Sauvegarde du dossier sécurisé":                         "securite/ecryptfs.md",
    "Mise en oeuvre manuelle de la sauvegarde":                  "securite/ecryptfs.md",
    "Sauvegarde automatisée":                                    "securite/ecryptfs.md",
    "5. Restaurer la sauvegarde du dossier sécurisé":            "securite/ecryptfs.md",
    "6. Désactiver le montage automatique":                      "securite/ecryptfs.md",
    "Proton":                                                    "securite/proton.md",
    "Installation Proton VPN":                                   "securite/proton.md",
    "Installer Proton Mail":                                     "securite/proton.md",
    "Installer Proton Pass":                                     "securite/proton.md",

    # PROJETS
    "Web Hello World":                                           "projets/web-hello-world.md",
    "1. Préparation de l'environnement":                         "projets/web-hello-world.md",
    "2. Configurer un environnement Python & Bootstrap":         "projets/web-hello-world.md",
    "3. Développement de l\u2019application":                     "projets/web-hello-world.md",
    "4. Exécution et test de l\u2019application":                "projets/web-hello-world.md",
    "5. Déploiement de l'application":                           "projets/web-hello-world.md",
    "5. Appliquer un thème Bootstrap prêt à l'emploi":           "projets/web-hello-world.md",
    "Conversion de page html en pdf":                            "projets/web2pdf.md",
    "1. Spécifications fonctionnelles":                          "projets/web2pdf.md",
    "2. Développement de la solution":                           "projets/web2pdf.md",
    "3. La première version du projet":                          "projets/web2pdf.md",
    "4. La deuxième version du projet":                          "projets/web2pdf.md",
    "5. La troisème version du projet":                          "projets/web2pdf.md",

    # ELECTRONIQUE
    "Electronique":                                              "electronique/index.md",
    "Lois Physiques de l'électricités":                          "electronique/lois-physiques.md",
    "Loi d'Ohm":                                                 "electronique/lois-physiques.md",
}

# Ordre explicite des tiddlers dans chaque fichier fusionné.
# Tuple (titre, niveau_section) :
#   niveau_section = 0 → premier tiddler (titre du fichier, heading_offset=1)
#   niveau_section = 2 → ## section (heading_offset=2)
#   niveau_section = 3 → ### sous-section (heading_offset=3)
FILE_ORDER: dict[str, list[tuple[str, int]]] = {
    "systeme/ubuntu/post-installation.md": [
        ("Post-Installation Ubuntu 24.04", 0),
        ("01. Mettre à jour le système", 2),
        ("02. Créer une clé SSH pour accéder à des dépôts GitHub", 2),
        ("03. Cloner divers projets Github personnels", 2),
        ("04. Starship Cross-Shell Prompt", 2),
        ("05. Installer la police Firacode", 2),
        ("06. Configurez Gnome Terminal", 2),
        ("07. Configurer Nautilus", 2),
        ("08. Installer firefox depuis les dépôts PPA de Mozilla", 2),
        ("09. Exporter/Importer les Exceptions de coockies Firefox", 2),
        ("10. Installez Ubuntu Restricetd Packages", 2),
        ("11. Paramétrage Gnome", 2),
        ("12. Définir kitty comment terminal par défaut", 2),
    ],
    "systeme/alpine/post-installation.md": [
        ("Post-Installation Alpine Linux", 0),
        ("Changer le nom d\u2019hôte", 2),
        ("Installer les définitions de terminaux", 2),
    ],
    "virtualisation/reseau.md": [
        ("Réseaux et KVM", 0),
        ("Réseau par défaut", 2),
        ("Réseau par défaut depuis virt-manager", 2),
        ("KVM virtio et un réseau NAT", 2),
    ],
    "conteneurs/compose.md": [
        ("3. Installer Docker Compose", 0),
        ("4. Version docker-compose dans docker-compose.yml", 2),
    ],
    "developpement/python/environnement.md": [
        ("Python dans Ubuntu 24.04", 0),
        ("Définir l'ordre de priorité Python", 2),
        ("Reproduire un environnement virtuel de développement", 2),
    ],
    "developpement/python/urllib3.md": [
        ("Requête GET simple", 0),
        ("Requête envoi de données", 2),
        ("Télécharger un fichier", 2),
        ("Authentificaiton par token", 2),
    ],
    "developpement/web/html.md": [
        ("Html", 0),
        ("Les URL", 2),
        ("Les caractères spéciaux HTML", 2),
    ],
    "developpement/nodejs.md": [
        ("Installer Node.JS", 0),
        ("1. Installer fnm (Fast Node Manager)", 2),
        ("2. Ecrire un prorgamme de test", 2),
    ],
    "developpement/bash.md": [
        ("Traitement de Données et Tableaux", 0),
        ("mapfile", 2),
    ],
    "ia/gemini-cli.md": [
        ("Installer Gemini CLI", 0),
        ("Interactions de base", 2),
    ],
    "outils/vscode.md": [
        ("Installer Microsoft Visual Studio Code", 0),
        ("Extensions utiles", 2),
        ("Générateur d'extension Microsoft VS Code", 2),
    ],
    "outils/github-cli.md": [
        ("Client GitHub CLI", 0),
        ("1. Générez un jeton d'authentification", 2),
        ("2. Connexion aux services GitHub", 2),
        ("4. Lister tous les dépôts et gist", 2),
        ("5. Cloner un dépôt", 2),
    ],
    "reseau/sftp.md": [
        ("Serveur SFTP", 0),
        ("Installer un serveur SFTP léger sur Ubuntu 24.04", 2),
    ],
    "securite/certificats.md": [
        ("Certificats", 0),
        ("Format des certificats", 2),
    ],
    "securite/ecryptfs.md": [
        ("ecryptfs", 0),
        ("1. Créer un répertoire sécurisé", 2),
        ("2. Récupérer les données avec System Rescue CD", 2),
        ("3. Suppression du dossier sécurisé", 2),
        ("4. Sauvegarde du dossier sécurisé", 2),
        ("Mise en oeuvre manuelle de la sauvegarde", 3),
        ("Sauvegarde automatisée", 3),
        ("5. Restaurer la sauvegarde du dossier sécurisé", 2),
        ("6. Désactiver le montage automatique", 2),
    ],
    "securite/proton.md": [
        ("Proton", 0),
        ("Installation Proton VPN", 2),
        ("Installer Proton Mail", 2),
        ("Installer Proton Pass", 2),
    ],
    "projets/web-hello-world.md": [
        ("Web Hello World", 0),
        ("1. Préparation de l'environnement", 2),
        ("2. Configurer un environnement Python & Bootstrap", 2),
        ("3. Développement de l\u2019application", 2),
        ("4. Exécution et test de l\u2019application", 2),
        ("5. Déploiement de l'application", 2),
        ("5. Appliquer un thème Bootstrap prêt à l'emploi", 2),
    ],
    "projets/web2pdf.md": [
        ("Conversion de page html en pdf", 0),
        ("1. Spécifications fonctionnelles", 2),
        ("2. Développement de la solution", 2),
        ("3. La première version du projet", 2),
        ("4. La deuxième version du projet", 2),
        ("5. La troisème version du projet", 2),
    ],
    "electronique/lois-physiques.md": [
        ("Lois Physiques de l'électricités", 0),
        ("Loi d'Ohm", 2),
    ],
}

# ─── Navigation mkdocs.yml ────────────────────────────────────────────────────

NAV = """
nav:
  - Accueil: index.md
  - Système:
    - Ubuntu:
      - Post-Installation: systeme/ubuntu/post-installation.md
      - Gnome & Extensions: systeme/ubuntu/gnome.md
      - Dotfiles (GNU Stow): systeme/ubuntu/dotfiles.md
    - Alpine Linux:
      - systeme/alpine/index.md
      - Installation sur KVM: systeme/alpine/installation-kvm.md
      - Post-Installation: systeme/alpine/post-installation.md
      - Créer une VM KVM: systeme/alpine/vm-kvm.md
      - Partage de répertoires: systeme/alpine/partage.md
      - Docker sur Alpine: systeme/alpine/docker.md
      - Lazydocker: systeme/alpine/lazydocker.md
  - Virtualisation:
    - virtualisation/index.md
    - Introduction à KVM/QEMU: virtualisation/introduction.md
    - Installation: virtualisation/installation.md
    - Libvirt: virtualisation/libvirt.md
    - Réseau: virtualisation/reseau.md
    - SSH automatisé: virtualisation/ssh.md
    - Port Forwarding: virtualisation/port-forwarding.md
  - Conteneurs:
    - conteneurs/index.md
    - Installation Docker: conteneurs/installation.md
    - Cosign: conteneurs/cosign.md
    - Docker Compose: conteneurs/compose.md
    - Réseau Docker: conteneurs/reseau.md
  - Développement:
    - Python:
      - developpement/python/index.md
      - Environnement & venv: developpement/python/environnement.md
      - Gestion avec uv: developpement/python/uv.md
      - Collections (deque): developpement/python/deque.md
      - urllib3: developpement/python/urllib3.md
      - BeautifulSoup: developpement/python/beautifulsoup.md
    - Web:
      - HTML: developpement/web/html.md
    - Bash: developpement/bash.md
    - Node.js: developpement/nodejs.md
    - Java: developpement/java.md
    - Rust: developpement/rust.md
    - Groovy: developpement/groovy.md
    - Lua: developpement/lua.md
  - Intelligence Artificielle:
    - ia/index.md
    - Ollama & VS Code: ia/ollama-vscode.md
    - qwen3-coder:30b: ia/qwen3-coder.md
    - Claude Code: ia/claude-code.md
    - Gemini CLI: ia/gemini-cli.md
  - Outils:
    - VS Code: outils/vscode.md
    - GitHub CLI: outils/github-cli.md
    - ExifTool: outils/exiftool.md
    - yt-dlp: outils/yt-dlp.md
    - Dashy: outils/dashy.md
    - Microsoft Edge: outils/microsoft-edge.md
    - Ansible: outils/ansible.md
  - Réseau:
    - reseau/index.md
    - DHCP: reseau/dhcp.md
    - mDNS: reseau/mdns.md
    - Serveur SFTP: reseau/sftp.md
    - Partage de fichiers: reseau/partage-fichiers.md
  - Sécurité:
    - securite/index.md
    - Certificats: securite/certificats.md
    - OpenSSL: securite/openssl.md
    - ecryptfs: securite/ecryptfs.md
    - Proton: securite/proton.md
  - Projets:
    - Web Hello World: projets/web-hello-world.md
    - Web2PDF: projets/web2pdf.md
  - Électronique:
    - electronique/index.md
    - Lois Physiques: electronique/lois-physiques.md
"""

# ─── Conversion WikiText → Markdown ──────────────────────────────────────────

def img_rel(dest_file: str) -> str:
    """Chemin relatif de dest_file vers assets/images/"""
    depth = len(Path(dest_file).parent.parts)
    return ("../" * depth) + "assets/images"

def resolve_link(target: str, link_text: str, tiddler_to_file: dict, current_file: str) -> str:
    """Résout un lien interne TiddlyWiki vers un chemin Markdown relatif."""
    if target in tiddler_to_file:
        dest = tiddler_to_file[target]
        rel = os.path.relpath(dest, str(Path(current_file).parent))
        return f"[{link_text}]({rel})"
    return f"**{link_text}**"

def convert_tables(text: str) -> str:
    """Convertit les tableaux TiddlyWiki en tableaux Markdown."""
    lines = text.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^\|.*\|$', line):
            # Collecter toutes les lignes de la table
            table_lines = []
            while i < len(lines) and re.match(r'^\|.*\|$', lines[i]):
                table_lines.append(lines[i])
                i += 1

            if not table_lines:
                continue

            # Déterminer si la première ligne est un header (contient !)
            first_cells = [c.strip() for c in table_lines[0][1:-1].split('|')]
            has_header = any(c.startswith('!') for c in first_cells)

            md_rows = []
            for idx, tl in enumerate(table_lines):
                cells = [c.strip().lstrip('!').strip() for c in tl[1:-1].split('|')]
                row = '| ' + ' | '.join(cells) + ' |'
                md_rows.append(row)
                if idx == 0:
                    sep = '| ' + ' | '.join(['---'] * len(cells)) + ' |'
                    md_rows.append(sep)

            result.extend(md_rows)
        else:
            result.append(line)
            i += 1
    return '\n'.join(result)

def convert_wikitext(text: str, tiddler_to_file: dict, current_file: str,
                     heading_offset: int = 1) -> str:
    """Convertit du WikiText TiddlyWiki en Markdown."""
    if not text or not text.strip():
        return ""

    # 1. Protéger les blocs de code fencés
    code_blocks: dict[str, str] = {}
    counter = [0]

    def save_code(m: re.Match) -> str:
        key = f"\x00CODE{counter[0]}\x00"
        code_blocks[key] = m.group(0)
        counter[0] += 1
        return key

    text = re.sub(r'```(?:[^\n]*)\n.*?```', save_code, text, flags=re.DOTALL)

    # 2. Supprimer les widgets et macros TiddlyWiki
    text = re.sub(r'\\define\b.*?(?=\\define|\Z)', '', text, flags=re.DOTALL)
    text = re.sub(r'<<toc[^>]*>>', '', text)
    text = re.sub(r'<<list-links[^>]*>>', '', text)
    text = re.sub(r'<<tabs[^>]*>>', '', text)
    text = re.sub(r'<<[\w-]+(?:\s[^>]*)?>>', '', text)
    text = re.sub(r'<\$(?:list|reveal|button|transclude|checkbox|select)[^>]*/>',  '', text)
    text = re.sub(r'<\$(?:list|reveal|button|transclude|checkbox|select)[^>]*>.*?</\$(?:list|reveal|button|transclude|checkbox|select)>', '', text, flags=re.DOTALL)

    # Convertir <$link to="X">text</$link>
    def convert_link_widget(m: re.Match) -> str:
        target = m.group(1)
        ltext = m.group(2).strip()
        return resolve_link(target, ltext or target, tiddler_to_file, current_file)
    text = re.sub(r'<\$link to="([^"]+)">(.*?)</\$link>', convert_link_widget, text, flags=re.DOTALL)

    # Supprimer les widgets restants
    text = re.sub(r'<\$[^/][^>]*/>', '', text)
    text = re.sub(r'<\$[^>]+>', '', text)
    text = re.sub(r'</\$\w+>', '', text)

    # Supprimer les divs TiddlyWiki
    text = re.sub(r'<div[^>]*class="tc-[^"]*"[^>]*>', '', text)
    text = re.sub(r'</div>', '', text)

    # 3. Entités HTML courantes → Unicode
    entities = {
        '&laquo;': '«', '&raquo;': '»', '&amp;': '&', '&lt;': '<', '&gt;': '>',
        '&nbsp;': ' ', '&mdash;': '—', '&ndash;': '–', '&hellip;': '…',
        '&copy;': '©', '&reg;': '®', '&trade;': '™', '&euro;': '€',
        '&deg;': '°', '&times;': '×', '&divide;': '÷', '&Omega;': 'Ω',
    }
    for ent, char in entities.items():
        text = text.replace(ent, char)

    # 4. Images : [img [name.png]] ou [img width=N [name.png]]
    img_dir = img_rel(current_file)
    def convert_image(m: re.Match) -> str:
        name = m.group(1).strip()
        return f"![{name}]({img_dir}/{name})"
    text = re.sub(r'\[img(?:[^\[]*)\[\s*([^\]]+?)\s*\]\]', convert_image, text)

    # 5. Liens [[text|url]] ou [[url]] ou [[text|TiddlerName]] ou [[TiddlerName]]
    def convert_tw_link(m: re.Match) -> str:
        inner = m.group(1)
        if '|' in inner:
            ltext, target = inner.split('|', 1)
            if target.startswith('http'):
                return f"[{ltext}]({target})"
            return resolve_link(target, ltext, tiddler_to_file, current_file)
        else:
            target = inner
            if target.startswith('http'):
                return f"<{target}>"
            return resolve_link(target, target, tiddler_to_file, current_file)
    text = re.sub(r'\[\[([^\]]+)\]\]', convert_tw_link, text)

    # 6. Annotations @@ (classes CSS TiddlyWiki) → supprimer la classe, garder le texte
    text = re.sub(r'@@\.[\w-]+\s*(.*?)@@', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'@@(.*?)@@', r'\1', text, flags=re.DOTALL)

    # 7. Titres + listes (traitement ligne par ligne)
    lines = text.split('\n')
    new_lines = []
    for line in lines:
        # Titre TW : ! texte (un ou plusieurs !)
        m = re.match(r'^(!+)\s+(.*)', line)
        if m:
            level = min(len(m.group(1)) + heading_offset, 6)
            new_lines.append('#' * level + ' ' + m.group(2))
            continue
        # Liste ordonnée TW : # texte
        m = re.match(r'^(#+) (.+)', line)
        if m:
            depth = len(m.group(1))
            new_lines.append('    ' * (depth - 1) + '1. ' + m.group(2))
            continue
        # Liste non ordonnée TW : * texte
        m = re.match(r'^(\*+) (.+)', line)
        if m:
            depth = len(m.group(1))
            new_lines.append('    ' * (depth - 1) + '* ' + m.group(2))
            continue
        new_lines.append(line)
    text = '\n'.join(new_lines)

    # 8. Mise en forme du texte (hors blocs de code)
    text = re.sub(r"''(.+?)''", r'**\1**', text)
    text = re.sub(r'//(.+?)//', r'*\1*', text)
    text = re.sub(r'__(.+?)__', r'<u>\1</u>', text)
    text = re.sub(r'~~(.+?)~~', r'~~\1~~', text)
    text = re.sub(r'\^\^(.+?)\^\^', r'<sup>\1</sup>', text)
    text = re.sub(r',,(.+?),,', r'<sub>\1</sub>', text)

    # 9. Tableaux TiddlyWiki → Markdown
    text = convert_tables(text)

    # 10. Restaurer les blocs de code
    for key, block in code_blocks.items():
        text = text.replace(key, block)

    # 11. Nettoyage des lignes vides excessives
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

# ─── Extraction des images ────────────────────────────────────────────────────

def extract_images(tiddlers: dict) -> None:
    IMGS.mkdir(parents=True, exist_ok=True)
    image_types = {'image/png': '.png', 'image/jpeg': '.jpg', 'image/gif': '.gif',
                   'image/svg+xml': '.svg', 'image/webp': '.webp'}
    count = 0
    for title, t in tiddlers.items():
        mime = t.get('type', '')
        if mime in image_types:
            raw = t.get('text', '')
            if not raw:
                continue
            ext = image_types[mime]
            fname = title if title.endswith(ext) else title + ext
            out = IMGS / fname
            try:
                data = base64.b64decode(raw)
                out.write_bytes(data)
                count += 1
            except Exception as e:
                print(f"  [WARN] image {title}: {e}")
    print(f"  {count} images extraites dans assets/images/")

# ─── Migration principale ────────────────────────────────────────────────────

def build_tiddler_to_file(tiddlers: dict) -> dict[str, str]:
    """Construit un dict {titre_tiddler → chemin_fichier} pour la résolution des liens."""
    result = {}
    for title in tiddlers:
        if title in FILE_MAP and FILE_MAP[title] is not None:
            result[title] = FILE_MAP[title]
    return result

def get_file_plan(tiddlers: dict) -> dict[str, list[tuple[str, int]]]:
    """
    Retourne pour chaque fichier de destination la liste ordonnée de
    (titre_tiddler, niveau_section).
    """
    # Partir des ordres explicites
    plan: dict[str, list[tuple[str, int]]] = {}
    for dest_file, order in FILE_ORDER.items():
        plan[dest_file] = [(t, lvl) for t, lvl in order if t in tiddlers]

    # Pour les tiddlers sans ordre explicite, un seul tiddler par fichier
    seen = set()
    for order_list in FILE_ORDER.values():
        for title, _ in order_list:
            seen.add(title)

    for title, dest in FILE_MAP.items():
        if dest is None or title in seen:
            continue
        if title not in tiddlers:
            continue
        if dest not in plan:
            plan[dest] = [(title, 0)]
        # Si le fichier est déjà dans le plan mais ce tiddler n'y est pas encore,
        # on l'ajoute (cas des sous-tiddlers non listés explicitement)

    return plan

def migrate() -> None:
    # Charger les tiddlers
    html = SRC.read_text(encoding='utf-8')
    scripts = re.findall(
        r'<script[^>]+class="tiddlywiki-tiddler-store"[^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    all_tiddlers = {t['title']: t for t in json.loads(scripts[0])}
    print(f"Tiddlers chargés : {len(all_tiddlers)}")

    # Extraire les images
    print("Extraction des images...")
    extract_images(all_tiddlers)

    # Construire le plan de migration
    tiddler_to_file = build_tiddler_to_file(all_tiddlers)
    plan = get_file_plan(all_tiddlers)

    # Générer les fichiers Markdown
    print(f"Génération de {len(plan)} fichiers Markdown...")
    generated = 0
    skipped = 0

    for dest_file, tiddler_list in sorted(plan.items()):
        if not tiddler_list:
            skipped += 1
            continue

        out_path = DOCS / dest_file
        out_path.parent.mkdir(parents=True, exist_ok=True)

        parts = []

        for idx, (title, section_level) in enumerate(tiddler_list):
            t = all_tiddlers.get(title)
            if not t:
                print(f"  [WARN] tiddler introuvable : {title!r}")
                continue

            raw = t.get('text', '')
            heading_offset = section_level if section_level > 0 else 1
            md = convert_wikitext(raw, tiddler_to_file, dest_file, heading_offset)

            if section_level == 0:
                # Premier tiddler → titre du fichier
                parts.append(f"# {title}\n\n{md}" if md else f"# {title}")
            else:
                # Section ou sous-section dans le fichier fusionné
                prefix = '#' * section_level
                if md:
                    parts.append(f"{prefix} {title}\n\n{md}")
                else:
                    parts.append(f"{prefix} {title}")

        if not parts:
            skipped += 1
            continue

        content = "\n\n---\n\n".join(parts)
        content = re.sub(r'\n{3,}', '\n\n', content).strip() + "\n"
        out_path.write_text(content, encoding='utf-8')
        generated += 1

    # Créer l'index principal s'il n'existe pas déjà avec du contenu
    index_path = DOCS / "index.md"
    if not index_path.exists() or index_path.read_text().strip() == "# TechNook — Mon Grimoire Moderne\n\nDocumentation technique personnelle.":
        index_path.write_text(
            "# TechNook — Mon Grimoire Moderne\n\n"
            "Documentation technique personnelle d'Alan Marchand.\n\n"
            "Utilisez la navigation pour explorer les sections.\n",
            encoding='utf-8'
        )

    print(f"  {generated} fichiers générés, {skipped} ignorés.")

    # Mettre à jour mkdocs.yml avec la navigation
    update_mkdocs_nav()
    print("mkdocs.yml mis à jour.")

def update_mkdocs_nav() -> None:
    """Injecte le bloc nav: dans mkdocs.yml."""
    yml = MKDOCS_YML.read_text(encoding='utf-8')
    # Supprimer un éventuel bloc nav existant
    yml = re.sub(r'\nnav:.*', '', yml, flags=re.DOTALL)
    yml = yml.rstrip() + "\n" + NAV.lstrip('\n')
    MKDOCS_YML.write_text(yml, encoding='utf-8')

if __name__ == "__main__":
    migrate()
