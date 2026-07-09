# pass-cli en Python — subprocess et JSON

Il n'existe pas de SDK Python officiel pour Proton Pass (confirmé :
aucune bibliothèque `protonpass`/`pass-sdk` publiée par Proton). La seule
façon de scripter Proton Pass depuis Python est d'appeler le binaire
`pass-cli` via `subprocess` et de parser sa sortie `--output json`. Cette
page couvre le strict nécessaire pour le faire sans jamais exposer un
secret par accident.

!!! info "Prérequis"
    `pass-cli` installé et authentifié (`pass-cli login`) — voir
    [Sécurité — Proton, pass-cli](../../securite/proton/ecosysteme.md#pass-cli-cli).
    Tous les exemples supposent un `PATH` où `pass-cli` est résolu.

---

## Lister les vaults et les items (lecture seule)

`pass-cli item list --output json`, **sans** `--show-secrets`, ne
contient tout simplement pas les champs sensibles dans sa structure — ce
ne sont pas des valeurs vides ou masquées, elles sont absentes. Rien à
filtrer côté Python pour rester sûr : c'est déjà le cas côté CLI.

```python
"""Liste les vaults et les items actifs d'un vault Proton Pass.

Utilise `pass-cli vault list --output json` et
`pass-cli item list <vault> --output json` (sans --show-secrets) : les
champs sensibles sont absents de la structure retournée par le CLI,
pas seulement masqués à l'affichage.

Exemple :
    uv run pass_cli_list.py
"""

from __future__ import annotations

import json
import subprocess


def list_vaults() -> list[dict]:
    """Liste les vaults disponibles.

    Returns:
        Une liste de dicts avec les clés `name`, `vault_id`, `share_id`.

    Raises:
        subprocess.CalledProcessError: Si pass-cli échoue (session
            expirée, non authentifié...).
    """
    result = subprocess.run(
        ["pass-cli", "vault", "list", "--output", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)["vaults"]


def list_items(vault_name: str) -> list[dict]:
    """Liste les items actifs d'un vault — métadonnées uniquement.

    Args:
        vault_name: Nom du vault à lister.

    Returns:
        Une liste de dicts (`id`, `title`, `item_type`, `state`...) —
        jamais de mot de passe ni de champ sensible.
    """
    result = subprocess.run(
        [
            "pass-cli", "item", "list", vault_name,
            "--filter-state", "active",
            "--output", "json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)["items"]


if __name__ == "__main__":
    for vault in list_vaults():
        print(f"{vault['name']}")
        for item in list_items(vault["name"]):
            print(f"  - {item['title']} [{item['item_type']}]")
```

!!! warning "`--search` n'existe pas"
    `item list` ne propose aucune option de recherche textuelle — testé
    directement, l'ajouter provoque une erreur (`unexpected argument
    '--search'`). Seuls `--filter-type`/`--filter-state`/`--sort-by`
    existent côté CLI. Pour chercher par titre, filtrer côté Python après
    coup :

    ```python
    def find_item_by_title(vault_name: str, title: str) -> dict | None:
        """Cherche un item par titre exact (filtrage côté client)."""
        return next(
            (item for item in list_items(vault_name) if item["title"] == title),
            None,
        )
    ```

---

## Récupérer un champ précis, jamais l'item complet

`pass-cli item view` révèle l'**intégralité** de l'item par défaut, mot
de passe inclus, sans confirmation. La seule façon sûre de l'appeler
depuis un script est de toujours préciser `--field` :

```python
"""Récupère UN champ précis d'un item Proton Pass, sans exposer le reste.

`pass-cli item view` révèle l'intégralité de l'item par défaut (mot de
passe inclus), sans confirmation. Ne jamais l'appeler sans --field dans
un script.

Exemple :
    uv run pass_cli_get_field.py "Sites" "Netflix" username
"""

from __future__ import annotations

import subprocess
import sys


def get_item_field(vault_name: str, item_title: str, field: str) -> str:
    """Récupère un seul champ d'un item, sans exposer les autres.

    Args:
        vault_name: Nom du vault contenant l'item.
        item_title: Titre exact de l'item.
        field: Nom du champ à récupérer (ex. "username", "password").

    Returns:
        La valeur brute du champ — `--field` produit une sortie stdout
        contenant uniquement la valeur, sans texte décoratif.

    Raises:
        subprocess.CalledProcessError: Vault/item introuvable, ou champ
            absent de cet item.
    """
    result = subprocess.run(
        [
            "pass-cli", "item", "view",
            "--vault-name", vault_name,
            "--item-title", item_title,
            "--field", field,
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.rstrip("\n")


if __name__ == "__main__":
    vault, title, field = sys.argv[1], sys.argv[2], sys.argv[3]
    value = get_item_field(vault, title, field)
    # Ne JAMAIS faire `print(value)` ici si field == "password" — voir
    # la section "Ce qu'il ne faut jamais faire" plus bas.
    print(f"Champ '{field}' récupéré ({len(value)} caractères).")
```

---

## Gérer les erreurs : stderr, codes de sortie, pas de JSON sur échec

Deux familles d'erreurs distinctes, avec des codes de sortie différents,
**jamais structurées en JSON même avec `--output json`** :

- **Code `2`** — erreur de syntaxe CLI (argument/sous-commande invalide) :
  presque toujours un bug du script Python appelant, pas un problème de
  données.
- **Code `1`** — erreur applicative (vault/item introuvable, session
  invalide...) : message texte sur `stderr`, jamais en JSON.
- **`stdout` reste vide dans tous les cas d'erreur** — signal fiable pour
  distinguer succès/échec avant même de regarder le code de sortie.

```python
"""Gestion robuste des erreurs pass-cli : stderr, codes 1/2, pas de JSON
sur échec (confirmé par test direct, y compris avec --output json).

Exemple :
    uv run pass_cli_errors.py
"""

from __future__ import annotations

import subprocess


class PassCliError(Exception):
    """Erreur applicative pass-cli (code de sortie 1)."""


class PassCliUsageError(Exception):
    """Erreur d'appel du CLI par le script lui-même (code de sortie 2).

    Signale presque toujours un bug côté appelant (arguments mal
    construits) plutôt qu'un problème de données.
    """


def run_pass_cli(*args: str) -> str:
    """Exécute pass-cli et lève une exception typée selon le code retour.

    Args:
        *args: Arguments passés tels quels à pass-cli (pas de
            `shell=True` : aucun risque d'injection de commande).

    Returns:
        Le contenu de stdout, débarrassé du retour à la ligne final.

    Raises:
        PassCliUsageError: Code de sortie 2 (erreur de syntaxe CLI).
        PassCliError: Code de sortie 1 (erreur applicative).
    """
    result = subprocess.run(
        ["pass-cli", *args],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return result.stdout.rstrip("\n")

    # stdout est toujours vide en cas d'erreur — le message utile est sur
    # stderr, jamais en JSON même si --output json était demandé.
    message = result.stderr.strip()

    if result.returncode == 2:
        raise PassCliUsageError(message)
    raise PassCliError(message)


if __name__ == "__main__":
    try:
        run_pass_cli("item", "list", "VaultQuiNExistePas")
    except PassCliUsageError as exc:
        print(f"Bug d'appel du script — arguments invalides : {exc}")
    except PassCliError as exc:
        print(f"Erreur applicative (vault/item...) : {exc}")
```

---

## Ce qu'il ne faut jamais faire

!!! danger "Anti-pattern : afficher un secret sans confirmation explicite"
    ```python
    def afficher_item_sans_confirmation(vault_name: str, item_title: str) -> None:
        """❌ NE PAS REPRODUIRE — exemple pédagogique d'anti-pattern.

        `pass-cli item view` sans `--field` révèle TOUT l'item en clair,
        mot de passe inclus, sans confirmation. Appeler cette fonction
        puis afficher stdout expose un secret réel dans n'importe quel
        terminal, log applicatif ou capture d'écran — sans qu'aucune
        action explicite de l'utilisateur ne l'ait demandé.
        """
        result = subprocess.run(
            ["pass-cli", "item", "view",
             "--vault-name", vault_name, "--item-title", item_title],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout)  # ❌ Le mot de passe apparaît en clair ici.
    ```

    Même danger, à plus grande échelle : `pass-cli item list
    --show-secrets --output json` dump le contenu complet (tous les mots
    de passe inclus) de **tous les items d'un vault en un seul appel** —
    jamais dans un script sans garde explicite.

!!! tip "Bonne pratique : révélation avec confirmation explicite"
    ```python
    def reveler_avec_confirmation(vault_name: str, item_title: str) -> str | None:
        """Révèle un mot de passe uniquement après confirmation explicite.

        Args:
            vault_name: Nom du vault contenant l'item.
            item_title: Titre exact de l'item.

        Returns:
            Le mot de passe si l'utilisateur confirme explicitement,
            sinon None.
        """
        reponse = input(
            f"Révéler le mot de passe de « {item_title} » à l'écran ? "
            "Tapez EXACTEMENT 'oui je confirme' : "
        )
        if reponse != "oui je confirme":
            print("Annulé — rien n'a été affiché.")
            return None

        result = subprocess.run(
            [
                "pass-cli", "item", "view",
                "--vault-name", vault_name,
                "--item-title", item_title,
                "--field", "password",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.rstrip("\n")
    ```

---

## Voir aussi

- [Sécurité — Proton, pass-cli](../../securite/proton/ecosysteme.md#pass-cli-cli)
- [Post-installation — module pass-cli](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#groupe-cli-etapes-9-a-18)
