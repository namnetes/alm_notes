# Les threads — parallélisme avec les bibliothèques sync

Les threads sont la **troisième approche** de la concurrence en Python.
Ils permettent d'exécuter plusieurs tâches en parallèle **sans changer
de bibliothèque**, ce qui en fait souvent la solution de transition idéale
entre le code synchrone pur et l'async.

---

## Qu'est-ce qu'un thread ?

Un **thread** (fil d'exécution) est un mini-programme qui tourne *à l'intérieur*
de votre programme principal. Vous pouvez en démarrer plusieurs, et Python les
fait alterner très rapidement, donnant l'impression qu'ils s'exécutent en même
temps.

**Analogie — le restaurant :**

Imaginez un restaurant. Votre programme est le restaurant. Chaque **thread**
est un serveur. Ils partagent tous la même cuisine (la mémoire).

- Un seul serveur (sync) : il prend la commande de la table 1, attend que
  le plat soit prêt, le livre, puis s'occupe de la table 2. La table 2 attend
  pendant tout ce temps.
- Plusieurs serveurs (threads) : le serveur 1 prend la commande de la table 1
  et va en cuisine. Pendant que le plat se prépare, le serveur 2 s'occupe de
  la table 2. Les deux tables sont servies en même temps.

Le problème ? Si deux serveurs veulent mettre à jour le même cahier de réservation
en même temps, ils risquent de s'écraser mutuellement. C'est la **race condition**
(condition de course) — on y reviendra.

---

## Le GIL — la règle qui change tout

Le **GIL** (Global Interpreter Lock) est un mécanisme interne de Python qui
interdit à deux threads d'exécuter du code Python **pur** *en même temps*.
C'est comme s'il n'y avait qu'une seule clé pour démarrer le moteur — un seul
thread peut l'avoir à la fois.

**Mais il y a une exception cruciale :** pendant une **attente I/O**
(requête réseau, lecture de fichier, `time.sleep`), Python dit au thread :
*"Tu n'as pas besoin de la clé pendant que tu attends — pose-la."* Le GIL est
alors libéré, et un autre thread peut en profiter.

```
Tâches I/O (réseau, fichier, sleep) :

Thread 1 → [Python] ──[ATTENTE 1s — GIL libéré]──────────── [Python]
Thread 2 →           [Python] ──[ATTENTE 1s — GIL libéré]────────── [Python]
           ──────────────────────────────────────────────────────────────────▶
                                                              ≈ 1s au total ✅

Tâches CPU pures (calculs) :

Thread 1 → [calcul — GIL ⚷][calcul — GIL ⚷][calcul — GIL ⚷]
Thread 2 →                  [attend...     ][calcul — GIL ⚷][calcul — GIL ⚷]
           ──────────────────────────────────────────────────────────────────▶
                                                              ≈ 2s au total ❌
```

**Résumé :** les threads aident pour les I/O, pas pour les calculs CPU.

---

## Exemple 1 — Threads sur des tâches I/O (ils aident)

```python
"""Threads sur des tâches I/O — démonstration du gain de temps.

Le GIL est libéré pendant time.sleep(), ce qui permet à tous les threads
de "dormir" en parallèle.

Exécution :
    uv run test_threads_io.py
"""

import concurrent.futures
import time


def fetch_data(nom: str, duree: float) -> str:
    """Simule une requête réseau d'une durée variable.

    Le GIL est libéré pendant time.sleep() — les autres threads
    peuvent s'exécuter pendant cette attente.

    Args:
        nom: Identifiant de la ressource.
        duree: Durée simulée en secondes.

    Returns:
        Message de résultat.
    """
    print(f"  → [{nom}] Début  (durée : {duree}s)")
    time.sleep(duree)   # ← GIL libéré ici — les autres threads avancent
    print(f"  ✓ [{nom}] Terminé")
    return f"Résultat de {nom}"


def main() -> None:
    taches = [
        ("Utilisateurs", 1.0),
        ("Produits",     0.8),
        ("Commandes",    1.2),
        ("Stocks",       0.5),
        ("Factures",     0.9),
    ]

    debut = time.perf_counter()

    # max_workers = nombre de tâches → un thread par tâche
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(taches)) as ex:
        # submit() soumet chaque tâche au pool et retourne un "futur"
        futurs = [ex.submit(fetch_data, nom, duree) for nom, duree in taches]
        # result() attend la fin de chaque tâche et récupère son résultat
        resultats = [f.result() for f in futurs]

    fin = time.perf_counter()
    duree_max = max(d for _, d in taches)
    print(f"\n[THREADS] Temps réel      : {fin - debut:.2f}s")
    print(f"[THREADS] Temps théorique : {duree_max}s  (durée de la plus longue tâche)")
    print(f"[THREADS] Résultats       : {len(resultats)} tâches terminées")


if __name__ == "__main__":
    main()
```

**Résultat attendu :**

```
  → [Utilisateurs] Début  (durée : 1.0s)
  → [Produits] Début  (durée : 0.8s)
  → [Commandes] Début  (durée : 1.2s)
  → [Stocks] Début  (durée : 0.5s)
  → [Factures] Début  (durée : 0.9s)
  ✓ [Stocks] Terminé
  ✓ [Produits] Terminé
  ✓ [Factures] Terminé
  ✓ [Utilisateurs] Terminé
  ✓ [Commandes] Terminé

[THREADS] Temps réel      : 1.20s
[THREADS] Temps théorique : 1.2s  (durée de la plus longue tâche)
[THREADS] Résultats       : 5 tâches terminées
```

**1.2s au lieu de 4.4s** — même résultat qu'avec l'async, sans changer
de bibliothèque.

---

## Exemple 2 — Threads sur des tâches CPU (ils n'aident pas)

```python
"""Threads sur des tâches CPU — démonstration de l'absence de gain.

Le GIL n'est PAS libéré pendant les calculs Python purs. Les threads
s'alternent (time-slicing) mais ne tournent jamais vraiment en parallèle.

Exécution :
    uv run test_threads_cpu.py
"""

import concurrent.futures
import time


def calcul_intensif(n: int) -> int:
    """Calcule la somme des carrés de 0 à n-1 — tâche purement CPU.

    Pendant ce calcul, le GIL reste verrouillé : aucun autre thread
    ne peut avancer en même temps.

    Args:
        n: Limite supérieure du calcul.

    Returns:
        Somme des carrés.
    """
    return sum(i * i for i in range(n))


N = 8_000_000  # 8 millions d'itérations


def main() -> None:
    # Version synchrone — séquentielle
    debut = time.perf_counter()
    for _ in range(4):
        calcul_intensif(N)
    temps_sync = time.perf_counter() - debut

    # Version avec threads
    debut = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        list(ex.map(calcul_intensif, [N] * 4))
    temps_threads = time.perf_counter() - debut

    print(f"[SYNC]    4 calculs : {temps_sync:.2f}s")
    print(f"[THREADS] 4 calculs : {temps_threads:.2f}s")
    print()
    print("→ Les temps sont quasi-identiques.")
    print("  Le GIL empêche les threads de calculer en parallèle.")
    print("  Pour du CPU, utilisez multiprocessing.")


if __name__ == "__main__":
    main()
```

**Résultat attendu :**

```
[SYNC]    4 calculs : 2.40s
[THREADS] 4 calculs : 2.50s
→ Les temps sont quasi-identiques.
  Le GIL empêche les threads de calculer en parallèle.
  Pour du CPU, utilisez multiprocessing.
```

!!! info "Les threads peuvent même être légèrement plus lents sur CPU"
    Créer et gérer des threads a un coût (overhead). Sur des calculs purs,
    vous pouvez observer que les threads sont marginalement **plus lents**
    que le code sync — c'est parfaitement normal.

---

## Le danger caché : les race conditions

Quand plusieurs threads partagent et modifient les **mêmes données**,
des bugs aléatoires peuvent apparaître. Ces bugs sont parmi les plus
difficiles à reproduire car ils dépendent de l'ordre d'exécution exact
des threads — ordre qui change à chaque lancement.

### Comprendre le problème

L'opération `counter += 1` semble simple, mais Python la décompose
en **trois étapes** :

```
1. Lire counter   (valeur = 5)
2. Calculer +1    (résultat = 6)
3. Écrire counter (counter = 6)
```

Si un autre thread s'intercale entre l'étape 1 et l'étape 3, il lit
la même valeur initiale (`5`), calcule `6`, et écrit `6` lui aussi.
**Les deux threads ont incrémenté, mais counter ne vaut que 6 au lieu
de 7.** Une mise à jour a été perdue.

### Démonstration — race condition garantie

Ce script utilise `time.sleep()` pour forcer l'intercalement des threads
et rendre le bug systématique (plutôt qu'aléatoire).

```python
"""Démonstration d'une race condition avec des threads.

Le sleep() entre la lecture et l'écriture garantit que les deux threads
lisent la même valeur avant que l'un d'eux n'écrive — bug reproductible.

Exécution :
    uv run test_race_condition.py
"""

import threading
import time

# Variable partagée entre les deux threads
counter = 0


def incrementer_sans_verrou(nom_thread: str) -> None:
    """Incrémente counter 4 fois de façon non-sécurisée.

    Le sleep() simule un traitement entre la lecture et l'écriture,
    ce qui garantit que les deux threads lisent la même valeur.

    Args:
        nom_thread: Nom du thread pour l'affichage.
    """
    global counter
    for _ in range(4):
        valeur_lue = counter        # Étape 1 : je lis la valeur actuelle
        time.sleep(0.05)            # Étape 2 : je "traite" — l'autre thread peut lire aussi !
        counter = valeur_lue + 1    # Étape 3 : j'écris, mais l'autre a peut-être déjà écrit
        print(f"  [{nom_thread}] a lu {valeur_lue} → écrit {counter}")


def main() -> None:
    global counter
    counter = 0

    t1 = threading.Thread(target=incrementer_sans_verrou, args=("Thread-1",))
    t2 = threading.Thread(target=incrementer_sans_verrou, args=("Thread-2",))

    t1.start()
    t2.start()
    t1.join()   # Attend que Thread-1 se termine
    t2.join()   # Attend que Thread-2 se termine

    print(f"\nValeur finale  : {counter}")
    print(f"Valeur attendue : 8  (2 threads × 4 incréments)")
    if counter < 8:
        print(f"→ BUG ! {8 - counter} incréments perdus à cause de la race condition.")


if __name__ == "__main__":
    main()
```

**Résultat attendu :**

```
  [Thread-1] a lu 0 → écrit 1
  [Thread-2] a lu 0 → écrit 1   ← les deux ont lu 0 en même temps !
  [Thread-1] a lu 1 → écrit 2
  [Thread-2] a lu 1 → écrit 2   ← encore !
  [Thread-1] a lu 2 → écrit 3
  [Thread-2] a lu 2 → écrit 3
  [Thread-1] a lu 3 → écrit 4
  [Thread-2] a lu 3 → écrit 4

Valeur finale  : 4
Valeur attendue : 8  (2 threads × 4 incréments)
→ BUG ! 4 incréments perdus à cause de la race condition.
```

La valeur finale est `4` au lieu de `8`. La moitié des incréments ont été perdus.

!!! info "Pourquoi async n'a pas ce problème"
    En mode async, il n'y a **qu'un seul thread**. L'event loop exécute
    une seule coroutine à la fois, et ne passe à la suivante qu'au moment
    d'un `await`. Entre deux `await`, votre code s'exécute de façon atomique —
    personne ne peut vous interrompre.

---

## La solution : le verrou (`Lock`)

Un `Lock` (verrou) est un mécanisme qui garantit qu'**un seul thread à la
fois** peut exécuter un bloc de code. Les autres threads attendent que le
verrou soit libéré avant de continuer.

```python
"""Race condition corrigée avec un verrou threading.Lock.

Exécution :
    uv run test_lock.py
"""

import threading
import time

counter = 0
verrou = threading.Lock()   # Le verrou partagé entre les threads


def incrementer_avec_verrou(nom_thread: str) -> None:
    """Incrémente counter 4 fois de façon sécurisée avec un verrou.

    Le bloc `with verrou:` garantit qu'un seul thread exécute les 3 étapes
    (lire / traiter / écrire) sans interruption.

    Args:
        nom_thread: Nom du thread pour l'affichage.
    """
    global counter
    for _ in range(4):
        with verrou:                    # Acquiert le verrou (les autres attendent)
            valeur_lue = counter
            time.sleep(0.05)
            counter = valeur_lue + 1
            print(f"  [{nom_thread}] a lu {valeur_lue} → écrit {counter}")
        # ← Verrou libéré ici — l'autre thread peut maintenant l'acquérir


def main() -> None:
    global counter
    counter = 0

    t1 = threading.Thread(target=incrementer_avec_verrou, args=("Thread-1",))
    t2 = threading.Thread(target=incrementer_avec_verrou, args=("Thread-2",))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print(f"\nValeur finale  : {counter}")
    print(f"Valeur attendue : 8")
    print("→ Correct — le verrou protège les 3 étapes.")


if __name__ == "__main__":
    main()
```

**Résultat attendu :**

```
  [Thread-1] a lu 0 → écrit 1
  [Thread-2] a lu 1 → écrit 2   ← Thread-2 a attendu que Thread-1 finisse
  [Thread-1] a lu 2 → écrit 3
  [Thread-2] a lu 3 → écrit 4
  ...

Valeur finale  : 8
Valeur attendue : 8
→ Correct — le verrou protège les 3 étapes.
```

!!! warning "Le verrou ralentit le code"
    Avec un verrou, les threads ne peuvent plus vraiment se chevaucher pour
    les sections protégées — ils s'attendent. Le gain de performance ne vient
    que des sections *sans* verrou (notamment les attentes I/O).
    Sur des calculs purs entièrement sous verrou, les threads n'apportent
    aucun avantage.

---

## `ThreadPoolExecutor` — la façon moderne

Créer des threads manuellement (`threading.Thread`) demande de gérer
le démarrage, l'attente et la récupération des résultats à la main.
`ThreadPoolExecutor` simplifie tout ça :

```python
"""Exemple complet avec ThreadPoolExecutor.

Exécution :
    uv run test_executor.py
"""

import concurrent.futures
import time


def traiter_fichier(chemin: str) -> dict:
    """Simule le traitement d'un fichier (lecture + analyse).

    Args:
        chemin: Chemin fictif du fichier à traiter.

    Returns:
        Dictionnaire avec le chemin et le nombre de lignes simulé.
    """
    time.sleep(0.5)  # Simule la lecture du fichier
    return {"fichier": chemin, "lignes": 100}


def main() -> None:
    fichiers = [
        "/data/rapport_2024_01.csv",
        "/data/rapport_2024_02.csv",
        "/data/rapport_2024_03.csv",
        "/data/rapport_2024_04.csv",
    ]

    debut = time.perf_counter()

    # Approche 1 : map() — même interface qu'un for, mais en parallèle
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        resultats = list(ex.map(traiter_fichier, fichiers))

    print("Résultats (map) :")
    for r in resultats:
        print(f"  {r}")

    # Approche 2 : submit() — plus flexible, permet de récupérer au fur et à mesure
    debut2 = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        futurs = {ex.submit(traiter_fichier, f): f for f in fichiers}

        # as_completed() retourne les futurs dans l'ordre où ils se terminent
        for futur in concurrent.futures.as_completed(futurs):
            chemin = futurs[futur]
            resultat = futur.result()   # Lève l'exception si la tâche a échoué
            print(f"  Terminé : {chemin} ({resultat['lignes']} lignes)")

    fin = time.perf_counter()
    print(f"\nTemps total : {fin - debut:.2f}s (4 fichiers × 0.5s en parallèle)")


if __name__ == "__main__":
    main()
```

| Méthode | Usage | Ordre des résultats |
|---------|-------|---------------------|
| `executor.map(fn, items)` | Simple, comme `map()` | Même ordre que l'entrée |
| `executor.submit(fn, *args)` | Flexible, gestion d'erreur par futur | Dépend de `as_completed()` |

---

## Avantages des threads

| Avantage | Détail |
|----------|--------|
| **Compatibilité totale** | Fonctionne avec **toutes** les bibliothèques, même celles sans async |
| **Migration facile** | On ajoute `ThreadPoolExecutor` autour du code existant |
| **Efficace sur I/O** | Même performance qu'async pour les attentes réseau/fichier |
| **FastAPI l'utilise** | Les endpoints `def` (sans `async`) sont automatiquement dans un thread pool |

## Inconvénients des threads

| Inconvénient | Détail |
|--------------|--------|
| **Race conditions** | Les données partagées doivent être protégées par des verrous |
| **GIL sur CPU** | N'accélère pas les calculs purs — utiliser `multiprocessing` |
| **Débogage difficile** | Les bugs de concurrence sont aléatoires et durs à reproduire |
| **Overhead** | Créer et gérer des threads a un coût (mémoire, temps de démarrage) |
| **Moins efficace qu'async** | À très haute concurrence (milliers de connexions), async est meilleur |

## Quand utiliser les threads

- Code utilisant des bibliothèques **sans alternative async** (`requests`, `psycopg2`, `PIL`)
- **Migration progressive** : paralléliser du code sync existant sans tout réécrire
- FastAPI avec bibliothèques sync : utilisez `def` (FastAPI gère le thread pool)
- **Tâches en arrière-plan** dans une application sync (envoi d'email, log asynchrone)

---

*Voir aussi : [Python synchrone](sync.md) · [Python asynchrone](async.md) · [Async vs Sync — guide de décision](async-vs-sync.md)*
