# Concurrence en Python — Sync, Threads & Async

Python propose **trois modèles** pour gérer plusieurs tâches simultanément.
Comprendre lequel choisir est indispensable dès que votre code attend des
données extérieures : réseau, disque, base de données.

## Pages

<div class="grid cards" markdown>

-   :material-arrow-down-thin: **[Python synchrone](sync.md)**

    Le mode par défaut — exécution ligne par ligne et blocage I/O.

-   :material-sync: **[Python asynchrone](async.md)**

    L'event loop, les coroutines `async/await` et `asyncio`.

-   :material-source-branch: **[Les threads](threads.md)**

    Parallélisme avec les bibliothèques sync — GIL, race conditions, verrous.

-   :material-scale-balance: **[Async vs Sync vs Threads](async-vs-sync.md)**

    Comparaison avec exemples mesurables et guide de décision.

</div>

## À retenir avant de commencer

- **Synchrone** = Python exécute une instruction à la fois ; pendant une
  attente réseau, **tout s'arrête**.
- **Threads** = plusieurs fils d'exécution OS ; chacun peut progresser
  pendant que les autres attendent ; attention aux **race conditions** sur les
  données partagées.
- **Asynchrone** = un seul fil d'exécution géré par une boucle d'événements ;
  pendant qu'une tâche attend, **les autres avancent** — sans risque de race
  condition.
- Le bon choix dépend de **ce que fait votre code**, pas de vos préférences.

```mermaid
flowchart LR
    subgraph SYNC["Synchrone — total : 3s"]
        direction TB
        S1["Tâche A : 1s"] --> S2["Tâche B : 1s"] --> S3["Tâche C : 1s"]
    end

    subgraph THREADS["Threads — total : ~1s"]
        direction TB
        T1["Tâche A : 1s"]
        T2["Tâche B : 1s"]
        T3["Tâche C : 1s"]
    end

    subgraph ASYNC["Asynchrone — total : ~1s"]
        direction TB
        A1["Tâche A : 1s"]
        A2["Tâche B : 1s"]
        A3["Tâche C : 1s"]
    end

    SYNC  --> NS["1 fil — séquentiel\nChaque tâche attend la précédente"]
    THREADS --> NT["N fils OS — parallèle\nGIL libéré sur les attentes I/O"]
    ASYNC --> NA["1 fil — coopératif\nL'event loop alterne les tâches"]

    style SYNC fill:#fff3e0,stroke:#e65100
    style THREADS fill:#fce4ec,stroke:#c62828
    style ASYNC fill:#e8f5e9,stroke:#2e7d32
```
