# proton-drive-cli — CLI, bash et Python (difficulté graduelle)

`proton-drive` est le **CLI officiel de Proton Drive** — voir
[l'annonce officielle](https://proton.me/blog/proton-drive-cli) et
[Sécurité — Proton, proton-drive-cli](../../securite/proton/ecosysteme.md#proton-drive-cli-cli).
Comme pour `pass-cli`, il n'existe aucun SDK Python officiel : la seule
façon de scripter Proton Drive depuis Python est d'appeler le binaire via
`subprocess` et de parser sa sortie `--json`.

Tous les exemples de cette page ont été **exécutés réellement** contre un
compte Proton Drive dont la racine (`/my-files`) contient : `Avatar`,
`Bloc notes`, `Bricolage`, `Bureau`, `Cuisine`, `Google AI Studio`,
`Hardware`, `Licences`, `Taranix QX7`, et un fichier
`Préparation Eau de Javel.pdf`.

!!! danger "Le dossier `Licences` n'apparaît dans aucun exemple exécuté de cette page"
    Il contient des clés de licence logicielles. Il peut apparaître **par
    son nom** dans un listing de la racine (`filesystem list /my-files`
    le montre, comme n'importe quel autre dossier), mais **aucun exemple
    de cette page ne liste son contenu, ne le télécharge, ni ne le cible
    en écriture** — même les scripts d'exclusion ci-dessous l'excluent
    explicitement plutôt que de compter sur le hasard.

!!! info "Prérequis"
    `proton-drive` installé et authentifié (`proton-drive auth login`) —
    voir [Post-installation — groupe cli](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#groupe-cli-etapes-9-a-19)
    pour l'installation, [Sécurité — Proton, proton-drive-cli](../../securite/proton/ecosysteme.md#proton-drive-cli-cli)
    pour l'authentification.

---

## Niveau 1 — CLI direct (lecture seule)

### Authentification : login et logout

```bash
proton-drive auth login
```

```
Sign in in your browser. Keep the terminal open. Waiting for authentication to complete...
Open following URL manually (can be on another device) if browser did not open automatically:
https://account.proton.me/desktop/login?app=drive&pv=3#payload=...
Authentication successful
```

```bash
proton-drive auth logout
```

Ne produit rien sur stdout en cas de succès (code de sortie `0`). Toute
commande lancée après `logout` échoue immédiatement :

```bash
proton-drive filesystem list /my-files
```
```
You need to login first
```

### Explorer l'arborescence

```bash
proton-drive filesystem list /
```

```
/my-files
/devices
/shared-by-me
/shared-with-me
/trash
/albums
/photos
/photos-shared-by-me
/photos-shared-with-me
/photos-trash
```

```bash
proton-drive filesystem list /my-files
```

```
🗂️  👑 keltalan@proton.me Aug 22 2025 18:54 - Avatar
🗂️  👑 keltalan@proton.me Aug 22 2025 18:55 - Bloc notes
🗂️  👑 keltalan@proton.me Aug 22 2025 18:55 - Bricolage
🗂️  👑 keltalan@proton.me Aug 22 2025 18:55 - Bureau
🗂️  👑 keltalan@proton.me Aug 22 2025 18:56 - Cuisine
🗂️  👑 keltalan@proton.me Aug 22 2025 18:56 - Google AI Studio
🗂️  👑 keltalan@proton.me Aug 22 2025 18:56 - Hardware
🗂️  👑 keltalan@proton.me Aug 22 2025 18:56 - Licences
🗂️  👑 keltalan@proton.me Aug 22 2025 18:56 - Taranix QX7
📄  👑 keltalan@proton.me Aug 22 2025 18:57 146763 Préparation Eau de Javel.pdf
```

!!! tip "Quoting shell, pas l'échappement du CLI"
    Les noms contenant des espaces (`Bloc notes`, `Google AI Studio`,
    `Préparation Eau de Javel.pdf`) doivent être entre guillemets **côté
    shell** — c'est une règle bash ordinaire, indépendante de la
    convention propre au CLI qui échappe uniquement les `/` internes à un
    nom (`foo\/bar`).

### Informations détaillées sur un fichier

```bash
proton-drive filesystem info "/my-files/Préparation Eau de Javel.pdf"
```

```
{
  uid: 'WuefI9eisBmyfL4qg_2J5-4P7mavumWpKbwyK1Lvdd6IyK4bch4NiReH4OsNqxkHexCx_XKcnhC5Vxujavj4DQ==~...',
  name: { ok: true, value: 'Préparation Eau de Javel.pdf' },
  type: 'file',
  mediaType: 'application/pdf',
  totalStorageSize: 146822,
  activeRevision: {
    ok: true,
    value: {
      claimedSize: 146763,
      claimedDigests: { sha1: '94fcc31c8dfa84d69107214b89447d647546f426', sha1Verified: false },
      ...
    }
  },
  ...
}
```

### Télécharger un fichier, y compris dans un sous-dossier

```bash
proton-drive filesystem download "/my-files/Cuisine/Cake à la banane.png" ~/Téléchargements/
```

```
Transfer summary:
  Downloaded: 1 items (2.10 MiB)
```

### Limite connue : `/photos` n'est pas navigable (v0.6.0)

```bash
proton-drive filesystem list /photos
```

```
Path type photos is not supported
```

!!! warning "Pas une question de compte vide — une limitation du CLI"
    - `filesystem list /photos` → **`Path type photos is not supported`**,
      même testé sur un compte réel sans photo actuellement présente.
    - `filesystem info /photos` → `Photo not found:` (le chemin est traité
      différemment, il attend un item précis, pas un dossier navigable).
    - Le filtre `-t photo` fonctionne bien comme filtre sur un dossier
      **listable** (`filesystem list /my-files -t photo` → vide,
      cohérent), mais ne rend pas `/photos` lui-même navigable.

    Le CLI est en version `0.6.0` (juillet 2026) : à retester après une
    mise à jour (`check_updates.sh`, voir
    [Post-installation](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#verification-des-mises-a-jour-upstream)).

### La corbeille : cycle complet, testé

Aucune suppression directe d'un fichier actif — la corbeille est un
passage obligé, exactement comme dans l'interface web. Exemple sur un
dossier de test dédié, jamais sur un vrai dossier :

```bash
proton-drive filesystem create-folder /my-files Bac-a-sable-doc
proton-drive filesystem trash /my-files/Bac-a-sable-doc
proton-drive filesystem list /trash
# 🗂️  ... - Bac-a-sable-doc

proton-drive filesystem restore /trash/Bac-a-sable-doc   # annule
# ou, pour purger définitivement :
proton-drive filesystem trash /my-files/Bac-a-sable-doc
proton-drive filesystem empty-trash
```

!!! danger "`delete` refuse un item actif"
    ```bash
    proton-drive filesystem delete /my-files/Bac-a-sable-doc
    ```
    ```
    You can permanently delete items only from trash. Trash your files first.
    ```
    Le cycle est donc toujours `trash` → (`restore` pour annuler, ou
    `delete`/`empty-trash` pour purger).

---

## Niveau 2 — Bash : sauvegarde sélective avec exclusion explicite

Script réel, utilisant les vrais noms de dossiers de la racine, qui
télécharge tout **sauf** `Licences` — l'exclusion est vérifiée dans la
boucle elle-même, pas laissée à l'absence accidentelle du nom dans la
liste :

```bash
#!/usr/bin/env bash
set -euo pipefail

# Sauvegarde sélective de la racine Proton Drive vers un dossier local,
# à l'exclusion explicite de "Licences" (clés de licence — jamais
# synchronisées hors de Proton Drive par ce script).
BACKUP_DIR="$HOME/backups/proton-drive/$(date +%Y-%m-%d)"
EXCLUDE=("Licences")

DOSSIERS=(
    "Avatar" "Bloc notes" "Bricolage" "Bureau" "Cuisine"
    "Google AI Studio" "Hardware" "Taranix QX7"
)

mkdir -p "$BACKUP_DIR"

for dossier in "${DOSSIERS[@]}"; do
    for exclu in "${EXCLUDE[@]}"; do
        [[ "$dossier" == "$exclu" ]] && continue 2
    done
    echo "Sauvegarde : $dossier"
    proton-drive filesystem download \
        --conflict-strategy skip \
        "/my-files/$dossier" "$BACKUP_DIR/"
done

echo "Terminé : $BACKUP_DIR"
```

!!! note "`continue 2` : sortir de la boucle interne ET passer au dossier suivant"
    `continue` seul ne sortirait que de la boucle `for exclu`, provoquant
    une seconde évaluation inutile — `continue 2` saute directement à
    l'itération suivante de la boucle englobante (`for dossier`). Logique
    de boucle vérifiée séparément (sans appel réseau) : même en ajoutant
    `Licences` par erreur à `DOSSIERS`, elle est correctement ignorée.

!!! tip "`--conflict-strategy skip`"
    Sans cette option, `download` **demande une confirmation interactive**
    si un fichier existe déjà localement — bloquant dans un script lancé
    sans terminal attaché (cron, service). `skip` ignore silencieusement
    ce qui existe déjà, `replace` écrase, `keep-both` duplique.

---

## Niveau 3 — Python : inventaire structuré et gestion d'erreurs

### Inventaire de la racine (JSON), exclusion défensive

```python
"""Inventaire de la racine Proton Drive, en excluant Licences par défaut.

Utilise `proton-drive filesystem list <path> --json`. L'option --json doit
être placée APRÈS la sous-commande et ses arguments (`filesystem list
<path> --json`), pas avant `filesystem` — testé : la placer avant produit
`Command not found: --json filesystem`.

Exemple :
    uv run proton_drive_inventory.py
"""

from __future__ import annotations

import json
import subprocess

EXCLUDED_FOLDERS = {"Licences"}


def list_root(path: str = "/my-files") -> list[dict]:
    """Liste le contenu d'un dossier Proton Drive.

    Args:
        path: Chemin distant à lister (syntaxe Posix, voir --help du CLI).

    Returns:
        Une liste de dicts (un par nœud) — voir la structure complète
        renvoyée par `filesystem info` pour le détail des champs.

    Raises:
        subprocess.CalledProcessError: Chemin introuvable ou session
            expirée (`proton-drive auth login` à refaire).
    """
    result = subprocess.run(
        ["proton-drive", "filesystem", "list", path, "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


if __name__ == "__main__":
    for node in list_root():
        name = node["name"]["value"]
        if name in EXCLUDED_FOLDERS:
            print(f"{name} — ignoré (exclusion volontaire)")
            continue
        kind = node["type"]
        size = node.get("totalStorageSize", "-")
        print(f"{kind:6} {name:25} {size}")
```

Sortie réelle (exécutée sur ce compte) :

```
folder Cuisine                   -
folder Taranix QX7               -
folder Avatar                    -
folder Bloc notes                -
folder Bricolage                 -
Licences — ignoré (exclusion volontaire)
folder Google AI Studio          -
file   Préparation Eau de Javel.pdf 146822
folder Hardware                  -
folder Bureau                    -
```

!!! note "`totalStorageSize` absent sur les dossiers"
    Le champ n'existe que sur les fichiers (taille du contenu). Sur un
    dossier, il est simplement absent de l'objet JSON — d'où le
    `.get(..., "-")` plutôt qu'un accès direct qui lèverait `KeyError`.

### Gérer les erreurs : stderr, code de sortie 1, jamais de JSON sur échec

Même comportement que `pass-cli` (voir
[pass-cli en Python](pass-cli-subprocess.md#gerer-les-erreurs-stderr-codes-de-sortie-pas-de-json-sur-echec)) :
`stdout` reste vide en cas d'erreur, le message est sur `stderr`, et
`--json` ne change rien au format de l'erreur — confirmé par test direct.

```python
"""Gestion robuste des erreurs proton-drive : stderr, code 1, pas de JSON
sur échec (confirmé par test direct, y compris avec --json).

Exemple :
    uv run proton_drive_errors.py
"""

from __future__ import annotations

import subprocess


class ProtonDriveError(Exception):
    """Erreur applicative proton-drive (chemin introuvable, session expirée...)."""


def run_proton_drive(*args: str) -> str:
    """Exécute proton-drive et lève une exception typée en cas d'échec.

    Args:
        *args: Arguments passés tels quels au CLI (pas de `shell=True` :
            aucun risque d'injection de commande).

    Returns:
        Le contenu de stdout.

    Raises:
        ProtonDriveError: Code de sortie non nul — message récupéré sur
            stderr, jamais structuré en JSON.
    """
    result = subprocess.run(
        ["proton-drive", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise ProtonDriveError(result.stderr.strip())
    return result.stdout


if __name__ == "__main__":
    try:
        run_proton_drive("filesystem", "info", "/my-files/CeDossierNexistePas")
    except ProtonDriveError as exc:
        print(f"Erreur proton-drive : {exc}")
```

Sortie réelle :

```
Erreur proton-drive : Node not found: CeDossierNexistePas
```

---

## Partage : générer puis révoquer un lien public

`sharing set-url` crée un **lien public réel**, immédiatement actif — à
ne jamais laisser traîner après un test :

```bash
proton-drive sharing set-url --role viewer "/my-files/Bac-a-sable-doc/fichier.txt"
# publicLink.url: https://drive.proton.me/urls/XXXXXXXXXX#XXXXXXXXXXXX

proton-drive sharing status "/my-files/Bac-a-sable-doc/fichier.txt"
# confirme publicLink actif

proton-drive sharing remove-url "/my-files/Bac-a-sable-doc/fichier.txt"
# révoque immédiatement — vérifié : sharing status redevient N/A
```

!!! danger "Un lien public oublié reste accessible à quiconque le possède"
    Testé en conditions réelles : `set-url` génère une URL fonctionnelle
    immédiatement, sans confirmation supplémentaire. Tout script ou
    session interactive qui appelle `set-url` à des fins de test doit
    systématiquement enchaîner sur `remove-url` — ne jamais compter sur
    une expiration automatique si `--expiration` n'a pas été fourni
    explicitement.

---

## Voir aussi

- [Sécurité — Proton, proton-drive-cli](../../securite/proton/ecosysteme.md#proton-drive-cli-cli)
- [Post-installation — module proton-drive-cli](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#groupe-cli-etapes-9-a-19)
- [pass-cli en Python — subprocess et JSON](pass-cli-subprocess.md) — mêmes patterns, autre outil Proton
