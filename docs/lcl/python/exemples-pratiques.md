# Exemples pratiques — Python et mainframe

Cette page rassemble des exemples de code illustrant les cas d'usage décrits dans
[Pourquoi Python a sa place sur le mainframe](pourquoi-python-mainframe.md). Ce
sont des points de départ à adapter, pas du code prêt pour la production : la
gestion des identifiants, des erreurs réseau et des accès concurrents dépendra de
votre environnement.

!!! info "Prérequis"
    Ces exemples supposent une familiarité avec les jeux de données z/OS (fichiers
    séquentiels ou partitionnés) et avec JCL. Voir
    [Pourquoi Python a sa place sur le mainframe](pourquoi-python-mainframe.md) pour
    le contexte.

## Soumettre et suivre un job JCL

L'approche dépend de l'endroit où s'exécute le script Python : directement sous
USS (*Unix System Services*, le sous-système Unix de z/OS) avec ZOAU, ou depuis un
poste distant avec le SDK Python de Zowe.

=== "ZOAU (zoautil_py) — depuis USS"

    [ZOAU](https://www.ibm.com/docs/en/zoau) expose une API Python native pour
    piloter JES (*Job Entry Subsystem*), le sous-système qui gère la file des
    jobs batch.

    ```python
    """Soumet un job JCL et attend son statut final."""

    import time

    from zoautil_py import datasets, exceptions, jobs

    TIMEOUT_SECONDS = 70
    POLL_INTERVAL_SECONDS = 3


    def run_job(jcl_dataset: str) -> dict[str, str] | None:
        """Soumet un job JCL et attend sa fin.

        Args:
            jcl_dataset: Nom du jeu de données contenant le JCL, au format
                `HLQ.NOM(MEMBRE)`.

        Returns:
            Dictionnaire avec les clés NAME, OWNER, STATUS et RC, ou None si le
            jeu de données est introuvable ou si la soumission échoue.

        Raises:
            exceptions.ZOAUException: Si ZOAU rencontre une erreur interne non
                liée à un jeu de données manquant.
        """
        if not datasets.exists(jcl_dataset):
            print(f"Jeu de données introuvable : {jcl_dataset}")
            return None

        job = jobs.submit(jcl_dataset, timeout=TIMEOUT_SECONDS)  # (1)!

        while job.status == "ACTIVE":
            time.sleep(POLL_INTERVAL_SECONDS)
            job.refresh()  # (2)!

        return {
            "NAME": job.name,
            "OWNER": job.owner,
            "STATUS": job.status,
            "RC": job.return_code,
        }
    ```

    1. `timeout` borne l'attente de la soumission elle-même (acceptation par
       JES), pas l'exécution complète du job.
    2. `refresh()` interroge à nouveau JES pour mettre à jour le statut — sans
       cet appel, `job.status` resterait figé à sa valeur initiale.

=== "Zowe Client Python SDK — depuis un poste distant"

    Le [SDK Python de Zowe](https://medium.com/zowe/zowe-client-python-sdk-getting-started-6b15848ca25c)
    pilote le mainframe via z/OSMF, sans nécessiter d'exécution native sous USS —
    utile pour de l'automatisation lancée depuis un poste de développement ou un
    pipeline CI/CD.

    ```python
    """Liste les jobs actifs d'un propriétaire donné via le SDK Zowe."""

    from zowe.zos_jobs_for_zowe_sdk import Jobs
    from zowe.core_for_zowe_sdk import ProfileManager


    def list_active_jobs(owner: str) -> list[dict[str, str]]:
        """Récupère les jobs actifs appartenant à `owner`.

        Args:
            owner: Identifiant du propriétaire des jobs (souvent l'ID TSO).

        Returns:
            Liste de dictionnaires décrivant chaque job (nom, id, statut).
        """
        profile = ProfileManager().load(profile_type="zosmf")
        jobs_client = Jobs(profile)
        return jobs_client.list_jobs(owner=owner)
    ```

## Encodage EBCDIC ↔ ASCII

Les jeux de données z/OS sont encodés en EBCDIC (*Extended Binary Coded Decimal
Interchange Code*), tandis que les fichiers USS et les échanges avec le monde
distribué sont généralement en ASCII ou UTF-8. Un même caractère `A` vaut
`x'C1'` en EBCDIC (code page `cp037`, US/Canada) contre `x'41'` en ASCII.

!!! warning "Piège fréquent"
    Lire un jeu de données EBCDIC comme si c'était de l'ASCII produit des
    caractères corrompus silencieusement — sans erreur Python. Toujours
    vérifier l'encodage source avant de traiter un fichier mainframe.

```python
"""Convertit un enregistrement EBCDIC (cp037) vers UTF-8."""

EBCDIC_CODE_PAGE = "cp037"


def ebcdic_to_utf8(raw_record: bytes) -> str:
    """Décode un enregistrement EBCDIC en texte UTF-8.

    Args:
        raw_record: Octets bruts lus depuis un jeu de données z/OS.

    Returns:
        Le contenu décodé en texte UTF-8.
    """
    return raw_record.decode(EBCDIC_CODE_PAGE)


def utf8_to_ebcdic(text: str) -> bytes:
    """Encode du texte UTF-8 en EBCDIC (cp037) avant écriture sur z/OS.

    Args:
        text: Texte à encoder.

    Returns:
        Les octets encodés en EBCDIC, prêts à écrire sur un jeu de données.
    """
    return text.encode(EBCDIC_CODE_PAGE)
```

Python supporte nativement plusieurs code pages EBCDIC (`cp037`, `cp500`,
`cp1047`…) — voir la [documentation Python des codecs](https://docs.python.org/3/library/codecs.html#standard-encodings)
pour la liste complète. Le bon code page dépend de la configuration régionale du
système z/OS cible, pas d'un choix arbitraire côté client.

## Boutisme (endianness) des champs binaires

Au-delà du texte, les champs binaires COBOL (`COMP`, `COMP-4`/`BINARY`) posent un
second piège : l'ordre dans lequel les octets d'un nombre sont rangés en mémoire
diffère entre le mainframe et un poste x86/x64.

!!! note "Parenthèse vérifiée — COMP, COMP-4, COMP-5 et BINARY : lequel choisir ?"
    Ces quatre clauses `USAGE` sont souvent confondues. En Enterprise COBOL
    for z/OS 6.x :

    - **`COMP`** et **`COMP-4`** sont strictement synonymes : un entier binaire
      en complément à deux, occupant un *halfword* (2 octets, 1 à 4 chiffres
      déclarés), un *fullword* (4 octets, 5 à 9 chiffres) ou un *doubleword*
      (8 octets, 10 à 18 chiffres) selon le nombre de chiffres de la clause
      `PICTURE`.
    - **`BINARY`** utilise le même stockage physique que `COMP`/`COMP-4`, mais
      son comportement à l'exécution dépend de l'option de compilation
      `TRUNC` : avec `TRUNC(STD)`, toute valeur qui dépasse le nombre de
      chiffres déclarés dans la `PICTURE` est tronquée à ce nombre de
      chiffres (comportement portable, mais qui coûte des instructions
      machine supplémentaires à chaque affectation) ; avec `TRUNC(OPT)`, le
      compilateur suppose que les données respectent toujours la `PICTURE`
      (le plus rapide, mais risqué si l'hypothèse est fausse) ; avec
      `TRUNC(BIN)`, tous les champs binaires du programme se comportent comme
      des `COMP-5` (troncature sur la taille binaire réelle, pas sur la
      `PICTURE`).
    - **`COMP-5`** est la clause « binaire natif » : la valeur exploite toute
      la capacité du champ binaire (2/4/8 octets), sans jamais être tronquée
      au nombre de chiffres de la `PICTURE` — quelle que soit l'option
      `TRUNC` du programme. C'est le choix recommandé pour les champs
      échangés avec du code non-COBOL (C, PL/I, IMS, Db2...) qui peut y
      écrire des valeurs binaires en dehors des bornes décimales déclarées.

    [D'après la documentation IBM sur l'option TRUNC](https://www.ibm.com/docs/en/cobol-zos/6.4.0?topic=options-trunc) :
    plutôt que d'activer `TRUNC(BIN)` pour tout le programme (ce qui pénalise
    aussi les champs qui n'en ont pas besoin), la pratique recommandée est de
    déclarer `COMP-5` uniquement sur les champs concernés, et de garder
    `TRUNC(OPT)` pour le reste — c'est l'option la plus performante en
    général, à condition de valider que les données respectent bien la
    `PICTURE`.

    **Ce qui ne change pas : l'endianness.** `COMP`, `COMP-4`, `COMP-5` et
    `BINARY` partagent tous le même stockage physique big-endian sur z/OS. La
    conversion Python montrée plus bas s'applique donc identiquement aux
    quatre, indépendamment de l'option `TRUNC` — celle-ci ne change que les
    règles de troncature côté COBOL, jamais l'ordre des octets en mémoire.

### Big-endian vs little-endian, octet par octet

- **Big-endian** (« gros-boutiste ») : l'octet de **poids fort** est stocké en
  premier (à l'adresse la plus basse). C'est l'ordre utilisé par le
  *z/Architecture* de z/OS pour les champs `COMP`/`COMP-4`/`BINARY`.
- **Little-endian** (« petit-boutiste ») : l'octet de **poids faible** est
  stocké en premier. C'est l'ordre natif des processeurs x86/x64 (donc de la
  plupart des postes Linux et Windows).

Prenons la valeur entière `4660` (soit `0x1234` en hexadécimal), stockée sur 4
octets (`0x00001234`). Voici comment ces 4 octets sont rangés selon l'ordre :

| Adresse | Big-endian (z/OS, `COMP-4`) | Little-endian (x86/x64) |
|---|---|---|
| Octet 1 | `0x00` (poids fort) | `0x34` (poids faible) |
| Octet 2 | `0x00` | `0x12` |
| Octet 3 | `0x12` | `0x00` |
| Octet 4 | `0x34` (poids faible) | `0x00` (poids fort) |

Les deux lignes contiennent **exactement les mêmes octets, dans l'ordre
inverse** (`00 00 12 34` contre `34 12 00 00`). C'est pour cela que lire un
champ binaire mainframe avec le mauvais ordre ne provoque aucune erreur Python :
les 4 octets existent bien, ils sont juste réinterprétés dans le mauvais sens,
et la valeur obtenue est un nombre différent (potentiellement énorme ou
négatif) plutôt qu'un plantage.

!!! note "Parenthèse vérifiée — l'inversion s'applique à toute longueur"
    L'exemple ci-dessus porte sur 4 octets, mais l'inversion byte-par-byte
    n'est pas une particularité des champs 4 octets : elle s'applique **à
    n'importe quelle longueur**. Le *z/Architecture* définit ses unités de
    stockage en big-endian de façon uniforme : le *halfword* (16 bits, 2
    octets), le *fullword* (32 bits, 4 octets), le *doubleword* (64 bits, 8
    octets), et même le *quadword* (128 bits, 16 octets) suivent tous la même
    règle — l'octet de poids fort en premier. Convertir vers/depuis le
    little-endian x86/x64 revient donc toujours à la même opération, quelle
    que soit la taille du champ : inverser la totalité de la séquence
    d'octets. C'est exactement ce que font `int.from_bytes()`/`to_bytes()` et
    `struct` avec un format `>` : ils s'adaptent nativement à 2, 4, 8 octets
    ou plus, sans logique différente selon la longueur.

!!! danger "Piège fréquent"
    `struct` et `int.from_bytes()` utilisent par défaut l'ordre **natif** de la
    machine qui exécute le script — little-endian sur la quasi-totalité des
    postes de développement. Un script qui fonctionne en test sur des données
    factices (générées localement) peut donc produire des valeurs fausses en
    production face à de vraies données mainframe, sans qu'aucune exception ne
    le signale.

### Méthode 1 — `struct`, pour un décodage typé (entier, flottant)

Le module standard `struct` accepte un caractère d'ordre explicite en tête du
format : `>` pour big-endian, `<` pour little-endian. Ne jamais utiliser `@`
(ordre natif, valeur par défaut si omis) ni `=` pour des données mainframe.

```python
"""Décode/encode un entier binaire COBOL (COMP-4) en respectant le boutisme z/OS."""

import struct

MAINFRAME_BYTE_ORDER = ">"  # (1)!


def read_cobol_comp4(raw_field: bytes) -> int:
    """Décode un champ COBOL COMP-4 (binaire 4 octets, signé) en entier Python.

    Args:
        raw_field: 4 octets bruts lus depuis un enregistrement z/OS.

    Returns:
        La valeur entière signée correspondante.

    Raises:
        struct.error: Si `raw_field` ne fait pas exactement 4 octets.
    """
    return struct.unpack(f"{MAINFRAME_BYTE_ORDER}i", raw_field)[0]


def write_cobol_comp4(value: int) -> bytes:
    """Encode un entier Python en champ COBOL COMP-4 (binaire 4 octets, signé).

    Args:
        value: Valeur entière signée à encoder, dans les bornes d'un `int32`.

    Returns:
        4 octets au format attendu par un programme COBOL sur z/OS.
    """
    return struct.pack(f"{MAINFRAME_BYTE_ORDER}i", value)
```

1. `">"` force l'ordre big-endian quel que soit le processeur qui exécute le
   script Python — sans ce préfixe, `struct` utilise par défaut le boutisme
   natif de la machine locale (little-endian sur x86/x64), ce qui donnerait
   une valeur incorrecte pour un champ produit par COBOL sur z/OS.

### Méthode 2 — `int.from_bytes()` / `int.to_bytes()`, sans import

Pour un entier simple, `int.from_bytes()` et `int.to_bytes()` (natifs au type
`int`, aucun import requis) sont plus lisibles que `struct` et acceptent des
tailles de champ arbitraires (2, 4, 8 octets, ou toute autre taille COBOL) :

```python
"""Alternative sans struct pour décoder/encoder un entier binaire mainframe."""


def read_cobol_binary(raw_field: bytes) -> int:
    """Décode un champ binaire COBOL (`COMP`/`BINARY`) de taille quelconque.

    Args:
        raw_field: Octets bruts lus depuis un enregistrement z/OS, quelle
            que soit leur longueur (2, 4, 8 octets...).

    Returns:
        La valeur entière signée correspondante.
    """
    return int.from_bytes(raw_field, byteorder="big", signed=True)


def write_cobol_binary(value: int, length: int) -> bytes:
    """Encode un entier Python en champ binaire COBOL sur `length` octets.

    Args:
        value: Valeur entière signée à encoder.
        length: Nombre d'octets du champ cible (2, 4, 8...).

    Returns:
        Les octets au format attendu par un programme COBOL sur z/OS.

    Raises:
        OverflowError: Si `value` ne tient pas sur `length` octets signés.
    """
    return value.to_bytes(length, byteorder="big", signed=True)
```

!!! tip "Retenir la règle"
    Peu importe la méthode choisie (`struct` ou `int.from_bytes`) : la seule
    règle qui compte est de **toujours préciser `big`/`">"` explicitement**
    pour des données issues de z/OS, et de ne jamais s'appuyer sur l'ordre par
    défaut de la bibliothèque, qui suit le processeur local.

## Format PACKED (décimal empaqueté, COMP-3)

Le décimal empaqueté (`COMP-3` en COBOL) est un format **propre au monde
mainframe** — il n'a pas d'équivalent dans les types numériques standards de
Python, C ou Java. Il stocke deux chiffres décimaux par octet (un par
*nibble*, c'est-à-dire un demi-octet de 4 bits), plus un nibble final réservé
au signe. C'est un format compact et rapide à traiter pour COBOL, mais il faut
le désempaqueter explicitement pour l'utiliser en Python.

### Structure bit à bit

Un **nibble** (ou *quartet*) est un demi-octet : 4 bits, donc exactement un
chiffre hexadécimal (`0`–`F`). Un octet contient toujours 2 nibbles : le
nibble de poids fort (les 4 bits de gauche) et le nibble de poids faible (les
4 bits de droite).

Prenons le nombre `-123` stocké dans un champ `PIC S9(3) COMP-3` (3 chiffres
signés). Sur 3 chiffres + 1 nibble de signe = 4 nibbles, soit exactement 2
octets pleins. Voici les bits réels de ces 2 octets :

```text
Octet 1                  Octet 2
┌───────────┬───────────┐┌───────────┬───────────┐
│  0 0 0 1  │  0 0 1 0  ││  0 0 1 1  │  1 1 0 1  │  ← bits
│  nibble 1 │  nibble 2 ││  nibble 3 │  nibble 4 │
│     1     │     2     ││     3     │     D     │  ← valeur (hex)
│  chiffre  │  chiffre  ││  chiffre  │   signe   │  ← rôle
└───────────┴───────────┘└───────────┴───────────┘
     = 0x12                   = 0x3D
```

Chaque groupe de 4 bits (un nibble) se lit comme un chiffre hexadécimal
indépendant :

- `0001` (binaire) = `1` (hexa) → 1er chiffre du nombre
- `0010` (binaire) = `2` (hexa) → 2e chiffre du nombre
- `0011` (binaire) = `3` (hexa) → 3e chiffre du nombre
- `1101` (binaire) = `D` (hexa) → nibble de **signe**, pas un chiffre

En assemblant les 2 nibbles de chaque octet, `0001 0010` donne l'octet `0x12`
et `0011 1101` donne l'octet `0x3D` — soit la séquence d'octets `0x12 0x3D`
telle qu'elle est réellement écrite dans le jeu de données. Les 3 premiers
nibbles donnent les chiffres `1`, `2`, `3` → `123` ; le dernier nibble (`D`)
indique que le nombre est négatif → `-123`.

Le dernier nibble n'est donc jamais un chiffre : c'est un code de signe. Les
codes de signe standards définis par IBM sont :

| Nibble de signe | Signification |
|---|---|
| `C` ou `A` ou `E` | Positif |
| `D` ou `B` | Négatif |
| `F` | Non signé (traité comme positif) |

!!! note "Parenthèse vérifiée — pourquoi préférer un nombre de chiffres impair"
    Le nombre de chiffres choisi dans la clause `PICTURE` n'est pas neutre pour
    le stockage. Le nombre total de nibbles d'un champ `COMP-3` est toujours
    *chiffres + 1* (le nibble de signe), et un champ occupe toujours un nombre
    **entier** d'octets, donc un nombre **pair** de nibbles.

    - Avec un nombre de chiffres **impair** (ex. `PIC S9(5) COMP-3` → 5 + 1 =
      6 nibbles), le total tombe déjà juste sur un nombre pair : le champ
      occupe exactement 3 octets, sans aucun nibble perdu.
    - Avec un nombre de chiffres **pair** (ex. `PIC S9(4) COMP-3` → 4 + 1 =
      5 nibbles), le total est impair : COBOL doit compléter avec un nibble de
      bourrage à zéro pour atteindre un octet plein, soit 3 octets occupés
      pour seulement 4 chiffres utiles — un nibble est gaspillé (comme dans
      l'exemple `pack_comp3` plus bas, qui insère ce nibble de bourrage).

    C'est bien la recommandation documentée dans le guide de performance
    d'Enterprise COBOL for z/OS ([IBM Docs — PACKED-DECIMAL (COMP-3)](https://www.ibm.com/docs/en/SS6SG3_6.3.0/perf/packed_decimal.html),
    guide de performance Enterprise COBOL 6.x) : coder un nombre impair de chiffres
    pour que le champ remplisse exactement un nombre entier d'octets. En
    pratique, cela signifie qu'un champ initialement pensé en `PIC S9(4)` doit
    être **arrondi au nombre impair supérieur**, soit `PIC S9(5)` — ce qui ne
    coûte rien en octets (3 octets dans les deux cas) tout en gagnant un
    chiffre de capacité utile au lieu de le perdre dans un nibble de
    bourrage.

Un même champ `COMP-3` peut aussi porter un nombre de décimales implicite,
défini par la clause COBOL `PICTURE` (ex. `PIC S9(5)V99 COMP-3` : 7 chiffres
dont 2 décimales implicites, aucun point décimal stocké physiquement).

### Décoder et encoder en Python avec `Decimal`

Le type `decimal.Decimal` de la bibliothèque standard convient particulièrement
bien ici : les montants mainframe sont typiquement financiers, et `Decimal`
évite les erreurs d'arrondi binaire qu'un `float` introduirait.

```python
"""Décode/encode un champ décimal empaqueté (COMP-3) avec decimal.Decimal."""

from decimal import Decimal

NEGATIVE_SIGN_NIBBLES = frozenset({0x0B, 0x0D})  # Codes IBM "B" et "D" — voir le tableau des signes ci-dessus.


def unpack_comp3(raw_field: bytes, scale: int = 0) -> Decimal:
    """Décode un champ COBOL COMP-3 (décimal empaqueté) en Decimal.

    Args:
        raw_field: Octets bruts du champ empaqueté, signe inclus.
        scale: Nombre de décimales implicites définies par la clause
            PICTURE COBOL (ex. 2 pour `PIC S9(5)V99 COMP-3`).

    Returns:
        La valeur décimale correspondante, décimales implicites replacées.
    """
    nibbles = []
    for byte in raw_field:
        nibbles.append(byte >> 4)
        nibbles.append(byte & 0x0F)

    sign_nibble = nibbles[-1]
    digits = "".join(str(nibble) for nibble in nibbles[:-1])
    sign = "-" if sign_nibble in NEGATIVE_SIGN_NIBBLES else ""

    value = Decimal(sign + digits)
    return value.scaleb(-scale) if scale else value


def pack_comp3(value: Decimal, num_digits: int, scale: int = 0) -> bytes:
    """Encode un Decimal en champ COBOL COMP-3 (décimal empaqueté).

    Args:
        value: Valeur décimale à encoder.
        num_digits: Nombre total de chiffres du champ COBOL (sans le signe),
            ex. 5 pour `PIC S9(5)V99 COMP-3` (le compte n'inclut pas les 2
            décimales, qui font partie des `num_digits` au total physique).
        scale: Nombre de décimales implicites (ex. 2 pour `V99`).

    Returns:
        Les octets empaquetés, signe inclus, au format attendu par COBOL.

    Raises:
        ValueError: Si `value` compte plus de chiffres que `num_digits`.
    """
    sign_nibble = 0x0D if value < 0 else 0x0C
    scaled_value = int(abs(value) * (10**scale))
    digit_string = str(scaled_value).zfill(num_digits)

    if len(digit_string) > num_digits:
        raise ValueError(f"{value} dépasse {num_digits} chiffres")

    nibbles = [int(digit) for digit in digit_string] + [sign_nibble]
    if len(nibbles) % 2:
        nibbles.insert(0, 0)  # Nibble de bourrage pour aligner sur un octet plein. # (1)!

    raw = bytearray()
    for high, low in zip(nibbles[0::2], nibbles[1::2]):
        raw.append((high << 4) | low)
    return bytes(raw)
```

1. Le nombre total de nibbles est `num_digits + 1` (le signe). Si `num_digits`
   est pair, ce total est impair et ne tient pas sur un nombre entier
   d'octets — un nibble `0` est ajouté en tête pour compléter le dernier
   octet, exactement comme le ferait un compilateur COBOL.

### Comment fonctionne l'algorithme

**Décodage (`unpack_comp3`)** — reproduit à la main ce que fait un
compilateur COBOL en sens inverse :

1. Chaque octet est séparé en ses 2 nibbles avec des opérateurs bit à bit :
   `byte >> 4` décale les bits de 4 rangs vers la droite, ne laissant que le
   nibble haut ; `byte & 0x0F` masque tout sauf les 4 bits de poids faible,
   isolant le nibble bas. Ce sont les deux moitiés d'octet vues dans le
   schéma bit à bit plus haut.
2. Tous les nibbles sauf le dernier sont concaténés en une chaîne de
   chiffres (`1`, `2`, `3` → `"123"`).
3. Le dernier nibble est comparé à `NEGATIVE_SIGN_NIBBLES` : s'il y figure, un
   `-` est préfixé à la chaîne de chiffres.
4. La chaîne signée est convertie directement en `Decimal`.
5. Si `scale` est non nul, `Decimal.scaleb(-scale)` déplace la virgule
   virtuelle vers la gauche sans toucher aux chiffres eux-mêmes (`123` avec
   `scale=2` devient `1.23`) — c'est la traduction du `V99` implicite du COBOL.

**Encodage (`pack_comp3`)** — l'opération inverse, étape par étape :

1. Le nibble de signe est choisi selon `value < 0` (`0x0C` positif, `0x0D`
   négatif — le couple C/D est la convention de signe *préférée* d'IBM,
   utilisée par les compilateurs COBOL modernes).
2. Multiplier par `10**scale` puis convertir en entier « retire »
   virtuellement la virgule : c'est l'inverse exact de l'étape 5 du décodage.
3. `zfill(num_digits)` complète la chaîne de zéros à gauche pour atteindre
   exactement le nombre de chiffres physiques du champ COBOL cible.
4. Chaque caractère de la chaîne devient un nibble entier, et le nibble de
   signe est ajouté en dernière position — l'inverse de l'étape 2 du
   décodage.
5. Si le total de nibbles est impair, un nibble `0` est inséré en tête (le
   nibble de bourrage expliqué plus haut).
6. Les nibbles sont regroupés deux par deux (`nibbles[0::2]` avec
   `nibbles[1::2]`) et recombinés en octets avec `(high << 4) | low` — l'exact
   opérateur miroir de l'étape 1 du décodage.

```pycon
>>> unpack_comp3(bytes([0x12, 0x3D]))
Decimal('-123')
>>> unpack_comp3(bytes([0x00, 0x12, 0x3C]), scale=2)
Decimal('1.23')
>>> pack_comp3(Decimal("-123"), num_digits=3)
b'\x12='
```

!!! warning "Ne pas confondre avec l'endianness"
    Le décimal empaqueté n'est **pas** une question d'ordre d'octets : ses
    nibbles se lisent toujours de gauche à droite, chiffre le plus significatif
    en premier. Le problème est celui du désempaquetage (extraire les
    chiffres des nibbles), pas du boutisme — les deux pièges sont
    indépendants et peuvent se cumuler sur un même enregistrement COBOL qui
    mélangerait champs `COMP-3` et champs `COMP-4`.

!!! info "Alternative : bibliothèques tierces"
    Pour traiter des copybooks COBOL complets (mélange de champs texte,
    `COMP`, `COMP-3`, tableaux, `REDEFINES`...) plutôt que des champs isolés,
    des bibliothèques comme [`copybook`](https://pypi.org/project/copybook/)
    ou des outils dédiés (voir le pattern AWS
    [Convert and unpack EBCDIC data to ASCII](https://docs.aws.amazon.com/prescriptive-guidance/latest/patterns/convert-and-unpack-ebcdic-data-to-ascii-on-aws-by-using-python.html))
    évitent de réécrire ce parsing à la main pour chaque structure de données.

## Automatiser un écran 3270 (CICS, ISPF)

Quand une transaction n'expose ni API ni accès direct aux données, [py3270](https://github.com/py3270/py3270)
pilote un émulateur `x3270`/`s3270` pour automatiser l'écran — utile pour des
tests de non-régression ou des tâches répétitives sur une transaction CICS
existante, sans toucher à son code.

```python
"""Se connecte à une transaction CICS et lit un champ écran."""

from py3270 import Emulator


def read_cics_field(host: str, transaction_id: str) -> str:
    """Lance une transaction CICS et lit le contenu d'un champ écran.

    Args:
        host: Adresse du gestionnaire de terminal (ex. `mainframe.example.com:23`).
        transaction_id: Code à quatre caractères de la transaction CICS.

    Returns:
        Le texte trouvé à l'écran, ligne 5 colonne 10, sur 20 caractères.
    """
    emulator = Emulator(visible=False)  # (1)!
    emulator.connect(host)
    emulator.send_string(transaction_id)
    emulator.send_enter()
    emulator.wait_for_field()  # (2)!

    field_value = emulator.string_get(5, 10, 20)
    emulator.terminate()
    return field_value
```

1. `visible=False` lance `s3270` (sans interface graphique) plutôt que
   `x3270` — adapté à un script d'automatisation sans supervision humaine.
2. Attend que l'hôte ait fini de rafraîchir l'écran avant de lire un champ —
   sans cette attente, la lecture peut se produire avant l'affichage des
   nouvelles données.

!!! danger "Solution de contournement, pas une architecture cible"
    Le screen scraping 3270 automatise une interface conçue pour un humain. À
    utiliser en solution transitoire (tests, migration progressive), pas comme
    fondation durable d'une intégration — préférer une API REST ou un appel
    programmatique dès que possible.

## Piloter le mainframe via l'API REST z/OSMF

[z/OSMF](https://www.ibm.com/docs/en/zos/2.4.0?topic=guide-using-zosmf-rest-services)
(*z/OS Management Facility*) expose des services REST pour soumettre des jobs et
accéder aux données — l'approche la plus indépendante de la plateforme cliente,
puisqu'elle ne nécessite qu'une bibliothèque HTTP standard.

```python
"""Soumet un job JCL via l'API REST z/OSMF."""

import requests

ZOSMF_BASE_URL = "https://mainframe.example.com:443/zosmf/restjobs/jobs"


def submit_job_via_zosmf(
    jcl_text: str, user: str, password: str
) -> dict[str, str]:
    """Soumet du JCL en texte brut via z/OSMF.

    Args:
        jcl_text: Contenu JCL complet à soumettre.
        user: Identifiant TSO/RACF.
        password: Mot de passe ou phrase de passe associé.

    Returns:
        Le document JSON du job renvoyé par z/OSMF (id, statut...).

    Raises:
        requests.HTTPError: Si z/OSMF rejette la requête (JCL invalide,
            authentification refusée...).
    """
    response = requests.put(
        ZOSMF_BASE_URL,
        data=jcl_text,
        auth=(user, password),
        headers={"Content-Type": "text/plain", "X-CSRF-ZOSMF-HEADER": "true"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
```

!!! tip "Secrets"
    Ne jamais coder en dur les identifiants comme dans l'exemple ci-dessus : les
    lire depuis un gestionnaire de secrets ou des variables d'environnement (voir
    le point de vigilance « gestion des secrets » dans
    [Pourquoi Python a sa place sur le mainframe](pourquoi-python-mainframe.md#points-de-vigilance)).

## Piloter le mainframe via l'API RSE API (IDz)

[RSE API](https://www.ibm.com/docs/en/explorer-for-zos/3.4?topic=documentation-rse-api)
(*Remote System Explorer API*) est une alternative à z/OSMF pour dialoguer avec
z/OS en REST — jeux de données, jobs JES, fichiers USS. C'est l'API que IDz (*IBM
Developer for z/OS*, l'IDE Eclipse) utilise en interne, et celle que pilote aussi
le plug-in RSE API pour Zowe CLI. Elle est intéressante quand RSE API est déjà
déployé pour l'IDE et qu'on veut réutiliser la même porte d'entrée pour de
l'automatisation, plutôt que d'ouvrir z/OSMF en plus.

!!! info "Prérequis côté serveur"
    Le started task `RSEAPI` doit tourner sur le LPAR cible (port par défaut
    `6800`). La documentation Swagger interactive de l'instance est disponible à
    `http(s)://<host>:6800/rseapi/api-docs/` — la référence à consulter pour
    valider le schéma exact des réponses sur votre version.

```python
"""Liste des jeux de données et soumission d'un job via RSE API."""

import requests

RSE_API_BASE_URL = "https://mainframe.example.com:6800/rseapi/api/v1"


def list_datasets(
    filter_pattern: str, user: str, password: str
) -> list[dict[str, str]]:
    """Liste les jeux de données correspondant à un filtre.

    Args:
        filter_pattern: Filtre de nom, ex. `HLQ.TOOLS.*`.
        user: Identifiant TSO/RACF.
        password: Mot de passe ou phrase de passe associé.

    Returns:
        Liste des jeux de données trouvés, tels que renvoyés par RSE API.
    """
    response = requests.get(
        f"{RSE_API_BASE_URL}/datasets/{filter_pattern}/list",
        auth=(user, password),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def submit_jcl(jcl_text: str, user: str, password: str) -> dict[str, str]:
    """Soumet du JCL en texte brut via RSE API.

    Args:
        jcl_text: Contenu JCL complet à soumettre.
        user: Identifiant TSO/RACF.
        password: Mot de passe ou phrase de passe associé.

    Returns:
        Le document JSON du job créé (nom, propriétaire, jobid, statut...).

    Raises:
        requests.HTTPError: Si RSE API rejette la requête (JCL invalide,
            authentification refusée...).
    """
    response = requests.post(
        f"{RSE_API_BASE_URL}/jobs/string/",  # (1)!
        json={"jcl": jcl_text},
        auth=(user, password),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_job_status(
    job_name: str, job_id: str, user: str, password: str
) -> dict[str, str]:
    """Récupère le statut d'un job déjà soumis.

    Args:
        job_name: Nom du job (ex. `MYJOB1`).
        job_id: Identifiant JES du job (ex. `JOB12345`), renvoyé par
            `submit_jcl`.
        user: Identifiant TSO/RACF.
        password: Mot de passe ou phrase de passe associé.

    Returns:
        Le document JSON décrivant le statut courant du job.
    """
    response = requests.get(
        f"{RSE_API_BASE_URL}/jobs/{job_name}/{job_id}",
        auth=(user, password),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
```

1. Le point final (`/jobs/string/`) indique à RSE API que le JCL est fourni en
   ligne dans le corps de la requête, par opposition à une soumission depuis
   un jeu de données déjà existant.

!!! warning "Choisir entre z/OSMF et RSE API"
    Les deux exposent des fonctionnalités qui se recoupent largement (jobs,
    datasets, fichiers USS). z/OSMF est un composant standard livré avec z/OS ;
    RSE API dépend de l'installation d'IBM Explorer for z/OS (IDz) côté serveur.
    Si IDz est déjà déployé pour les développeurs, réutiliser RSE API évite
    d'ouvrir un second point d'entrée REST. Sinon, z/OSMF suffit et évite une
    dépendance produit supplémentaire.

## Automatisation déclarative avec Ansible

Pour une automatisation orientée playbook plutôt que script, la collection
[`ibm.ibm_zos_core`](https://github.com/ansible-collections/ibm_zos_core) fournit
des modules Ansible — eux-mêmes écrits en Python — comme `zos_job_submit`.

```yaml
- name: Soumettre un job JCL et attendre sa fin
  ibm.ibm_zos_core.zos_job_submit:
    src: "HLQ.TOOLS.JCL(MONJOB)"
    location: data_set
    wait_time_s: 30
  register: job_result

- name: Afficher le code retour
  debug:
    var: job_result.jobs[0].ret_code
```

Cette approche convient bien si l'équipe est déjà outillée Ansible côté
distribué et veut orchestrer mainframe et systèmes ouverts dans les mêmes
playbooks.
