# Python asynchrone — l'event loop et les coroutines

L'asynchronisme permet à Python de **gérer plusieurs opérations en attente
simultanément** sans utiliser plusieurs threads. C'est particulièrement efficace
pour les serveurs qui traitent des centaines de requêtes en parallèle.

## Le concept central : l'event loop

Imaginez un **serveur de restaurant** efficace. Au lieu de rester devant la
table A à attendre que la cuisine prépare le plat (1 minute), il prend la
commande de la table B, apporte l'addition à la table C, puis revient chercher
le plat de la table A quand il est prêt.

L'**event loop** (boucle d'événements) fait exactement ça pour votre programme :

```
Event loop
│
├── Coroutine A : attend une réponse réseau  →  mise en pause
├── Coroutine B : attend une lecture de fichier  →  mise en pause
├── Coroutine C : calcule un résultat  →  s'exécute
│
│   La réponse réseau de A arrive...
├── Coroutine A : reprend et traite la réponse
│
│   Le fichier de B est lu...
└── Coroutine B : reprend et traite le fichier
```

Personne n'attend inutilement. Dès qu'une tâche est bloquée, une autre avance.

---

## Les mots-clés : `async def` et `await`

### `async def` — définir une coroutine

```python
# Fonction normale — s'exécute immédiatement quand appelée
def fonction_normale() -> str:
    return "Résultat"

# Coroutine — ne s'exécute PAS immédiatement quand appelée
async def coroutine() -> str:
    return "Résultat"
```

!!! warning "Une coroutine n'est pas une fonction ordinaire"
    Appeler `coroutine()` **ne retourne pas** `"Résultat"`. Cela retourne un
    **objet coroutine** qui doit être exécuté par l'event loop.

    ```python
    resultat = coroutine()        # ← Ne fait rien ! Crée juste un objet.
    resultat = await coroutine()  # ← Exécute réellement la coroutine.
    ```

### `await` — suspendre et déléguer

`await` dit à l'event loop : *"Je vais attendre ce résultat. Pendant ce temps,
tu peux exécuter d'autres tâches."*

```python
import asyncio


async def fetch_data(url: str) -> str:
    """Simule une requête réseau asynchrone.

    Args:
        url: L'URL fictive à "télécharger".

    Returns:
        Le contenu simulé.
    """
    print(f"  → Début : {url}")
    await asyncio.sleep(1)  # Suspend CETTE coroutine pendant 1s.
                             # L'event loop peut avancer les autres.
    print(f"  ✓ Terminé : {url}")
    return f"Contenu de {url}"


async def main() -> None:
    # Appel séquentiel — attend chaque résultat avant de continuer
    resultat = await fetch_data("https://api.exemple.com/utilisateurs")
    print(resultat)


asyncio.run(main())  # Lance l'event loop
```

!!! info "`await` ne peut s'utiliser que dans une fonction `async def`"
    C'est pourquoi `main()` est aussi une `async def`. L'event loop exige que
    toute la "chaîne d'appels" soit asynchrone jusqu'au point d'entrée
    `asyncio.run()`. Cette propagation est parfois appelée **contamination async**.

---

## Exemple 1 — Premier script async

```python
"""Premier contact avec asyncio.

Exécution :
    uv run hello_async.py
"""

import asyncio


async def dire_bonjour(nom: str, delai: float) -> str:
    """Attend un délai puis retourne un message de salutation.

    Args:
        nom: Le prénom à saluer.
        delai: Temps d'attente simulé en secondes.

    Returns:
        Le message de salutation.
    """
    print(f"  [{nom}] Je commence à attendre {delai}s...")
    await asyncio.sleep(delai)
    message = f"Bonjour {nom} !"
    print(f"  [{nom}] {message}")
    return message


async def main() -> None:
    # Appel séquentiel — l'un après l'autre
    await dire_bonjour("Alice", 1.0)
    await dire_bonjour("Bob", 0.5)


asyncio.run(main())
```

**Résultat :** 1.5s au total — même en async, les appels séquentiels s'attendent.
La magie vient dans l'exemple suivant.

---

## Exemple 2 — Lancer des tâches en parallèle avec `gather()`

La vraie puissance d'`asyncio` vient de `gather()`, qui lance plusieurs
coroutines **simultanément** :

```python
"""Exécution parallèle de coroutines avec asyncio.gather().

Ce script lance 3 téléchargements simultanés et mesure le temps total.

Exécution :
    uv run test_async.py
"""

import asyncio
import time


async def fetch_data(url: str) -> str:
    """Simule un appel réseau d'une seconde.

    Args:
        url: L'URL fictive à "télécharger".

    Returns:
        Le contenu simulé de la réponse.
    """
    print(f"  → Début : {url}")
    await asyncio.sleep(1)  # Suspend cette coroutine — les autres avancent
    print(f"  ✓ Terminé : {url}")
    return f"Contenu de {url}"


async def main() -> None:
    urls = [
        "https://api.exemple.com/utilisateurs",
        "https://api.exemple.com/produits",
        "https://api.exemple.com/commandes",
    ]

    debut = time.perf_counter()

    # gather() lance TOUTES les coroutines en même temps
    # et attend que toutes soient terminées
    resultats = await asyncio.gather(*[fetch_data(url) for url in urls])

    fin = time.perf_counter()
    print(f"\nTemps total : {fin - debut:.2f}s")
    print("Attendu : ~1s  (3 coroutines en parallèle)")
    print(f"Résultats : {resultats}")


asyncio.run(main())
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
Attendu : ~1s  (3 coroutines en parallèle)
```

Les trois URLs démarrent **immédiatement**. Chacune se "suspend" pendant 1
seconde. Au bout d'une seconde, toutes se terminent. Temps total : 1s au lieu
de 3s.

---

## Utiliser de vraies bibliothèques async

Pour bénéficier de l'async en production, il faut des bibliothèques
*async-natives*. Une bibliothèque sync ordinaire **bloquerait l'event loop**.

| Besoin | Bibliothèque sync ❌ | Bibliothèque async ✅ |
|--------|---------------------|----------------------|
| Requêtes HTTP | `requests` | `httpx`, `aiohttp` |
| PostgreSQL | `psycopg2` | `asyncpg`, `psycopg` (v3) |
| MySQL / MariaDB | `mysql-connector-python` | `aiomysql` |
| Lecture de fichiers | `open()` | `aiofiles` |
| Redis | `redis` (sync) | `redis.asyncio` |
| SQLAlchemy | `Session` | `AsyncSession` |

### Exemple 3 — Requêtes HTTP réelles avec `httpx`

```python
"""Téléchargement concurrent de vraies URLs avec httpx.

Prérequis :
    uv add httpx

Exécution :
    uv run test_httpx.py
"""

import asyncio
import time

import httpx


async def fetch_url(client: httpx.AsyncClient, url: str) -> tuple[str, int]:
    """Télécharge une URL et retourne son URL et la taille de la réponse.

    Args:
        client: Client HTTP async partagé (économise les connexions).
        url: URL à télécharger.

    Returns:
        Tuple (url, nombre de caractères dans la réponse).
    """
    response = await client.get(url, timeout=10.0)
    return url, len(response.text)


async def main() -> None:
    # httpbin.org/delay/1 répond après exactement 1 seconde
    urls = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
        "https://httpbin.org/delay/1",
    ]

    debut = time.perf_counter()

    # AsyncClient est partagé entre toutes les coroutines (connexions réutilisées)
    async with httpx.AsyncClient() as client:
        resultats = await asyncio.gather(
            *[fetch_url(client, url) for url in urls]
        )

    fin = time.perf_counter()
    print(f"Temps : {fin - debut:.2f}s pour {len(urls)} requêtes")
    for url, taille in resultats:
        print(f"  {url} → {taille} caractères")


asyncio.run(main())
```

---

## L'erreur à ne jamais commettre

Utiliser une bibliothèque **synchrone** dans une fonction `async def` sans
`await` bloque l'event loop entier — toutes les coroutines s'arrêtent.

```python
import asyncio
import time     # ← bibliothèque SYNCHRONE
import requests # ← bibliothèque SYNCHRONE


# ❌ Mauvais — time.sleep() bloque l'event loop entier
async def mauvais_sleep() -> None:
    time.sleep(2)  # Aucune autre coroutine ne peut avancer pendant 2s

# ✅ Bon — asyncio.sleep() suspend cette coroutine seulement
async def bon_sleep() -> None:
    await asyncio.sleep(2)  # Les autres coroutines continuent


# ❌ Mauvais — requests bloque l'event loop
async def mauvais_fetch(url: str) -> dict:
    response = requests.get(url)  # Bloque l'event loop entier
    return response.json()

# ✅ Bon — httpx est async-native
async def bon_fetch(url: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

---

## Avantages du mode asynchrone

| Avantage | Détail |
|----------|--------|
| **Haute concurrence** | Des milliers de connexions simultanées avec un seul thread |
| **Efficace sur les I/O** | Temps total ≈ durée de la plus longue opération |
| **Pas de race conditions** | Un seul thread → pas de conflits de données entre coroutines |
| **Standard FastAPI** | `async def` utilise directement l'event loop de FastAPI |

## Inconvénients

| Inconvénient | Détail |
|--------------|--------|
| **Courbe d'apprentissage** | Les concepts (coroutine, event loop, `await`) demandent du temps |
| **Contamination** | Une fonction async oblige ses appelants à être async aussi |
| **Bibliothèques async requises** | Mixer sync et async sans précaution bloque tout |
| **Débogage plus difficile** | Les traces de pile sont moins lisibles |
| **Pas utile sur CPU** | N'accélère pas les calculs purs (pour ça, voir `multiprocessing`) |

## Quand utiliser l'async

- **Serveurs web** traitant de nombreuses requêtes simultanées (FastAPI, Starlette)
- **Clients qui appellent plusieurs APIs** en parallèle
- **Bots** (Discord, Telegram) qui attendent des événements en permanence
- **Scrapers** téléchargeant de nombreuses pages web simultanément

---

*Voir aussi : [Python synchrone](sync.md) · [Les threads](threads.md) · [Async vs Sync vs Threads — guide de décision](async-vs-sync.md)*
