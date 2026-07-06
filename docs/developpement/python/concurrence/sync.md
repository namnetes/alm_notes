# Python synchrone — le mode par défaut

Avant de parler d'`async`, il faut comprendre ce que fait Python *normalement* :
une exécution **synchrone**, ligne par ligne, dans un seul fil d'exécution.

## Qu'est-ce que l'exécution synchrone ?

Python exécute votre programme comme vous lisez un livre : **une instruction à la
fois, de haut en bas**. Chaque instruction doit se terminer avant que la suivante
commence.

```python
print("Étape 1")  # S'exécute en premier
print("Étape 2")  # Attend que l'étape 1 soit terminée
print("Étape 3")  # Attend que l'étape 2 soit terminée
```

C'est simple, prévisible, et facile à déboguer. C'est aussi le comportement
**par défaut** de Python — pas besoin de configuration spéciale.

## Le problème : les opérations I/O bloquantes

"I/O" (Input/Output) désigne toute opération où Python *attend* une réponse
extérieure : lecture de fichier, requête HTTP, accès à une base de données, etc.

Pendant cette attente, Python est **bloqué** : il ne peut rien faire d'autre.

```
Temps →  0s         1s         2s         3s
────────────────────────────────────────────────────
Requête 1 [═════ attente réseau (1s) ═════][traitement]
Requête 2                                   [═════ attente (1s) ═════][traitement]
Requête 3                                                              [═════ attente (1s) ═════]
                                                                                    ↑ Total : 3s
```

Trois requêtes d'une seconde chacune = **3 secondes** au total en mode synchrone.

---

## Exemple 1 — Chronométrer le blocage I/O

Copiez ce code dans un fichier `test_sync.py` et exécutez-le avec `uv run test_sync.py`.

```python
"""Démonstration du comportement synchrone de Python.

Ce script simule trois appels réseau d'une seconde chacun et mesure
le temps total écoulé. Il montre que les appels se font les uns après
les autres, sans chevauchement possible.

Exécution :
    uv run test_sync.py
"""

import time


def fetch_data(url: str) -> str:
    """Simule un appel réseau d'une seconde.

    Args:
        url: L'URL fictive à "télécharger".

    Returns:
        Le contenu simulé de la réponse.
    """
    print(f"  → Début : {url}")
    time.sleep(1)  # Simule 1 seconde d'attente réseau — bloque tout
    print(f"  ✓ Terminé : {url}")
    return f"Contenu de {url}"


def main() -> None:
    urls = [
        "https://api.exemple.com/utilisateurs",
        "https://api.exemple.com/produits",
        "https://api.exemple.com/commandes",
    ]

    debut = time.perf_counter()

    resultats = [fetch_data(url) for url in urls]

    fin = time.perf_counter()
    print(f"\nTemps total : {fin - debut:.2f}s")
    print(f"Attendu : {len(urls)}s  (3 requêtes × 1s — séquentiel)")
    print(f"Résultats : {resultats}")


if __name__ == "__main__":
    main()
```

**Résultat attendu :**

```
  → Début : https://api.exemple.com/utilisateurs
  ✓ Terminé : https://api.exemple.com/utilisateurs
  → Début : https://api.exemple.com/produits
  ✓ Terminé : https://api.exemple.com/produits
  → Début : https://api.exemple.com/commandes
  ✓ Terminé : https://api.exemple.com/commandes

Temps total : 3.00s
Attendu : 3s  (3 requêtes × 1s — séquentiel)
```

Observez bien : la deuxième URL ne démarre qu'une fois la première **entièrement
terminée**. Les URLs s'attendent mutuellement.

---

## Contourner le blocage : les threads

Python propose les **threads** pour paralléliser du code synchrone. Plusieurs
threads s'exécutent "en même temps" — en réalité, Python les alterne très
rapidement (le GIL libère son verrou pendant les I/O, voir encadré ci-dessous).

### Exemple 2 — Même code avec `ThreadPoolExecutor`

```python
"""Parallélisation du code synchrone avec les threads.

Ce script reprend le même scénario (3 appels × 1s) mais les lance
en parallèle grâce à ThreadPoolExecutor.

Exécution :
    uv run test_threads.py
"""

import concurrent.futures
import time


def fetch_data(url: str) -> str:
    """Simule un appel réseau d'une seconde.

    Args:
        url: L'URL fictive à "télécharger".

    Returns:
        Le contenu simulé de la réponse.
    """
    print(f"  → Début : {url}")
    time.sleep(1)
    print(f"  ✓ Terminé : {url}")
    return f"Contenu de {url}"


def main() -> None:
    urls = [
        "https://api.exemple.com/utilisateurs",
        "https://api.exemple.com/produits",
        "https://api.exemple.com/commandes",
    ]

    debut = time.perf_counter()

    # ThreadPoolExecutor lance les trois appels dans des threads séparés
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        resultats = list(executor.map(fetch_data, urls))

    fin = time.perf_counter()
    print(f"\nTemps total : {fin - debut:.2f}s")
    print("Attendu : ~1s  (3 threads en parallèle)")


if __name__ == "__main__":
    main()
```

**Résultat attendu :**

```
  → Début : https://api.exemple.com/utilisateurs
  → Début : https://api.exemple.com/produits
  → Début : https://api.exemple.com/commandes
  ✓ Terminé : https://api.exemple.com/utilisateurs
  ✓ Terminé : https://api.exemple.com/produits
  ✓ Terminé : https://api.exemple.com/commandes

Temps total : 1.00s
Attendu : ~1s  (3 threads en parallèle)
```

Les trois URLs démarrent **simultanément**. Chacune attend 1 seconde dans son
propre thread — au bout d'une seconde, toutes se terminent en même temps.

!!! info "Le GIL — Global Interpreter Lock"
    Python interdit à deux threads d'exécuter du code Python **pur** simultanément
    (c'est le rôle du GIL). Mais pendant une **attente I/O** (`time.sleep`,
    lecture réseau, accès disque), le GIL est libéré — d'autres threads peuvent
    s'exécuter. C'est pourquoi les threads accélèrent les tâches I/O mais
    **n'accélèrent pas les calculs CPU** (le GIL reste verrouillé pendant
    les calculs purs).

---

## Avantages du mode synchrone

| Avantage | Détail |
|----------|--------|
| **Simplicité** | Code facile à lire, à écrire, à déboguer |
| **Compatibilité universelle** | Toutes les bibliothèques Python fonctionnent |
| **Débogage aisé** | Les erreurs apparaissent à la ligne exacte du problème |
| **Comportement prévisible** | L'ordre d'exécution est toujours le même |

## Inconvénients

| Inconvénient | Détail |
|--------------|--------|
| **Blocage I/O** | Une seule opération à la fois — les autres attendent |
| **Peu adapté aux serveurs** | 100 requêtes simultanées → 99 attendent en file |
| **Threads = complexité** | `ThreadPoolExecutor` fonctionne mais ajoute de la complexité et des risques (race conditions) |

## Quand le mode synchrone suffit

- **Scripts ponctuels** : migration de données, scripts de déploiement
- **Tâches CPU-intensives** : calculs scientifiques, traitement d'images (PIL, numpy)
- **Bibliothèques sans alternative async** : `requests`, `psycopg2`, `PIL`
- **Projets simples** sans besoin de haute concurrence
- **Apprentissage** : maîtrisez le sync avant d'aborder l'async

---

*Voir aussi : [Python asynchrone](async.md) · [Les threads](threads.md) · [Async vs Sync vs Threads — guide de décision](async-vs-sync.md)*
