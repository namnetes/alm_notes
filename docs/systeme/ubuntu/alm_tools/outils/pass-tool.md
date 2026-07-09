# pass-tool

`pass-tool` est un wrapper ergonomique en Typer/Rich autour de `pass-cli`,
le CLI officiel de Proton Pass — mêmes opérations en plus lisible
(tableaux Rich, génération de mot de passe locale, recherche
cross-vaults), sans jamais réimplémenter ce que `pass-cli` fait déjà.

**Source :** `~/alm_tools/cli/pass-tool`

---

## Prérequis

[`pass-cli`](../../../../securite/proton/ecosysteme.md#pass-cli-cli) installé et
authentifié (`pass-cli login`) — requis par `vault list` et `entry list`,
pas par `gen` (génération 100 % locale, jamais d'appel à `pass-cli`).
Installation automatique via le module postinstall, voir
[Post-installation — groupe cli](../postinstall/post-installation.md#groupe-cli-etapes-9-a-18).

---

## Installation

**Usage normal** — installer depuis le dépôt :

```bash
cd ~/alm_tools
uv tool install ./cli/pass-tool
```

**Mode développement** — les modifications du code source sont actives immédiatement :

```bash
cd ~/alm_tools/cli/pass-tool
uv tool install --editable .
```

!!! warning "Le flag `--force` utilise le cache"
    `uv tool install --force` réutilise un wheel en cache et ne reflète pas les
    dernières modifications du code source. Pour une réinstallation propre :

    ```bash
    uv tool uninstall pass-tool
    uv tool install --no-cache ~/alm_tools/cli/pass-tool
    ```

## Désinstallation

```bash
uv tool uninstall pass-tool
```

Supprime le shim `~/.local/bin/pass-tool` et l'environnement isolé
`~/.local/share/uv/tools/pass-tool/`.

---

## Utilisation

```bash
# Générer un mot de passe (génération locale, jamais pass-cli)
pass-tool gen --length 24 --exclude '{}[]' --clip

# Lister les vaults
pass-tool vault list

# Lister les entrées — recherche cross-vaults (tous les vaults par défaut)
pass-tool entry list --search netflix

# Restreindre le listage à un seul vault
pass-tool entry list --vault Sites

# Mode interactif — menu guidé si aucune sous-commande n'est fournie
pass-tool
```

---

## Options principales

| Commande | Option | Description |
|----------|--------|-------------|
| `gen` | `--length` / `-l` | Longueur du mot de passe généré (4-64, défaut 20) |
| `gen` | `--exclude` | Caractères à bannir de la génération |
| `gen` | `--clip` | Copie dans le presse-papier, effacement automatique après 15s |
| `entry list` | `--vault` | Restreint le listage à ce seul vault (défaut : tous) |
| `entry list` | `--search` | Filtre les entrées sur ce terme, insensible à la casse (titre uniquement) |
| — | `--version` / `-V` | Afficher la version et quitter |

---

## Robustesse et sécurité

- **Génération de mot de passe 100 % locale**, exclusivement via le module
  `secrets` de Python — jamais de réseau, jamais d'appel à `pass-cli` pour
  `gen`.
- **Presse-papier (`--clip`)** : effacement automatique après 15s via un
  process détaché ; protection anti-écrasement testée en conditions
  réelles — l'effacement n'a lieu que si le presse-papier contient encore
  exactement le mot de passe copié (si l'utilisateur a copié autre chose
  entre-temps, rien n'est effacé).
- **`vault list` et `entry list` n'affichent jamais de secret** —
  uniquement des métadonnées (nom, type, état...), absentes de la sortie
  `pass-cli` tant que `--show-secrets` n'est pas demandé ; `pass-tool` ne
  passe jamais cette option.
- **Erreurs `pass-cli` gérées proprement** (session expirée, vault
  inconnu...) : message Rich clair, jamais de trace Python brute, avec
  indication actionnable (`pass-cli login`) si l'erreur ressemble à un
  problème d'authentification.
- `pass-cli` lui-même expose deux commandes qui révèlent des secrets sans
  confirmation (`item view` sans `--field`, `item list --show-secrets`) —
  `pass-tool` ne les appelle jamais. Voir
  [Sécurité — Proton, pass-cli](../../../../securite/proton/ecosysteme.md#pass-cli-cli)
  pour le détail de ces commandes natives à risque.

---

Documentation complète : [cli/pass-tool/README.md](https://github.com/namnetes/alm_tools/blob/main/cli/pass-tool/README.md)
