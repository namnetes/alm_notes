# Boutisme (endianness) sur mainframe

!!! info "Prérequis"
    Cette page suppose une familiarité de base avec la notion d'octet et de
    bit. Voir [Types numériques sur mainframe](types-numeriques.md) pour le
    contexte plus large des formats de données COBOL.

Le **boutisme** (*endianness*) est l'ordre dans lequel les octets d'une
valeur occupant plusieurs octets sont rangés en mémoire ou dans un flux de
données. Ce n'est pas une particularité mainframe — c'est une question qui se
pose partout où une valeur numérique dépasse la taille d'un seul octet — mais
c'est un piège fréquent dès qu'on fait dialoguer un mainframe z/OS (big-endian)
avec un poste Linux/Windows x86 (little-endian).

## Le concept, indépendamment de tout mainframe

Un octet (8 bits) ne pose jamais de problème d'ordre : il n'y a qu'une seule
façon de le lire. Le problème apparaît dès qu'une valeur occupe **plusieurs**
octets consécutifs — un entier sur 4 octets, par exemple. Deux conventions
existent alors pour ranger ces octets :

- **Big-endian** (« gros-boutiste ») : l'octet de poids **fort** (le plus
  significatif) est stocké en premier, à l'adresse mémoire la plus basse.
- **Little-endian** (« petit-boutiste ») : l'octet de poids **faible** (le
  moins significatif) est stocké en premier.

Le terme vient d'un jeu de mots dans *Les Voyages de Gulliver* (Jonathan
Swift), où deux camps s'opposent sur la bonne façon de casser un œuf à la
coque — par le gros bout ou par le petit bout. Danny Cohen a repris cette
image en 1980 dans une note célèbre sur les architectures réseau pour
désigner ce débat, purement conventionnel, sur l'ordre des octets.

## z/Architecture : big-endian de bout en bout

Le processeur des mainframes IBM Z (*z/Architecture*, héritier direct du
System/360 des années 1960) fonctionne en **big-endian**, et ce de façon
uniforme quelle que soit la taille de l'unité de stockage :

| Unité z/Architecture | Taille | Ordre |
|---|---|---|
| Byte | 8 bits (1 octet) | — (pas d'ambiguïté possible) |
| Halfword | 16 bits (2 octets) | Big-endian |
| Fullword | 32 bits (4 octets) | Big-endian |
| Doubleword | 64 bits (8 octets) | Big-endian |
| Quadword | 128 bits (16 octets) | Big-endian |

C'est cette uniformité qui permet une règle simple : **convertir un champ
binaire mainframe vers x86/x64 (ou inversement) revient toujours à inverser
l'intégralité de la séquence d'octets**, quelle que soit sa longueur — 2, 4,
8 ou 16 octets. Il n'y a pas de cas particulier à connaître selon la taille du
champ.

## x86/x64 : little-endian

Les processeurs x86 et x64 qui équipent la quasi-totalité des postes de
développement Linux et Windows sont **little-endian**. C'est le sens inverse
de z/Architecture — d'où la nécessité de convertir explicitement tout champ
binaire échangé entre les deux mondes.

!!! note "Parenthèse — le boutisme réseau (network byte order)"
    Ce n'est pas qu'une affaire de mainframe : les protocoles réseau
    (TCP/IP) définissent depuis les années 1980 un *network byte order*
    standard, qui est... big-endian. C'est pour cette raison que les API
    socket historiques (`htonl`, `ntohl`, `htons`, `ntohs` en C) existent :
    elles convertissent entre l'ordre natif de la machine locale (souvent
    little-endian) et l'ordre big-endian imposé par le protocole réseau. Le
    choix du big-endian pour z/Architecture n'est donc pas isolé : c'est
    aussi la convention historique du monde réseau, indépendamment de tout
    lien avec IBM.

## Exemple bit à bit

Prenons la valeur entière `4660` (soit `0x1234` en hexadécimal), stockée sur
4 octets (`0x00001234`). Voici comment ces 4 octets sont rangés selon
l'ordre :

| Adresse | Big-endian (z/Architecture) | Little-endian (x86/x64) |
|---|---|---|
| Octet 1 | `0x00` (poids fort) | `0x34` (poids faible) |
| Octet 2 | `0x00` | `0x12` |
| Octet 3 | `0x12` | `0x00` |
| Octet 4 | `0x34` (poids faible) | `0x00` (poids fort) |

Les deux lignes contiennent **exactement les mêmes octets, dans l'ordre
inverse** (`00 00 12 34` contre `34 12 00 00`). C'est la raison pour laquelle
un mauvais ordre ne provoque jamais d'erreur de lecture : les octets existent
tous, ils sont seulement réinterprétés dans le mauvais sens, produisant une
valeur numérique différente (souvent un très grand nombre, ou une valeur
négative inattendue) plutôt qu'un plantage.

## Comment détecter un problème d'endianness dans des données réelles

Sans documentation fiable sur le format source, quelques signaux doivent
alerter :

- Une valeur qui devrait être un petit entier (ex. un compteur, un code
  produit) apparaît comme un nombre énorme (des milliards) ou négatif.
- Une valeur binaire décodée avec l'ordre natif de la machine locale
  (little-endian) « fonctionne » sur un poste x86 mais produit des résultats
  faux une fois le script déployé ailleurs, ou face à de vraies données
  mainframe après des tests sur des données factices générées localement.
- Inverser manuellement l'ordre des octets (`raw_field[::-1]` en Python) fait
  soudain apparaître une valeur plausible.

Dans le doute, toujours confirmer le format exact (COBOL `COMP`/`COMP-4` vs
autre chose) avec le copybook source plutôt que de deviner à partir des
données.

## Conversion en Python

### `struct` — format typé, ordre explicite

```python
"""Décode un entier binaire (COMP-4) en respectant l'ordre big-endian z/OS."""

import struct

value = struct.unpack(">i", raw_field)[0]  # (1)!
```

1. Le préfixe `>` force le big-endian. `<` forcerait le little-endian, `@`
   (valeur par défaut si omis) utilise l'ordre **natif** de la machine
   locale — à ne jamais utiliser pour des données mainframe.

### `int.from_bytes()` / `int.to_bytes()` — sans import, taille arbitraire

```python
"""Alternative sans struct, pour un champ binaire de longueur quelconque."""

value = int.from_bytes(raw_field, byteorder="big", signed=True)
raw_field_again = value.to_bytes(len(raw_field), byteorder="big", signed=True)
```

Ces deux méthodes acceptent nativement n'importe quelle longueur de champ (2,
4, 8, 16 octets...) sans logique différente selon la taille — cohérent avec
le fait que z/Architecture applique le même ordre big-endian à toutes ses
unités de stockage.

### Données en volume : `numpy`

Pour convertir un tableau entier de valeurs binaires en une seule opération
plutôt que champ par champ, le caractère d'ordre des octets se place dans le
descripteur de type (`dtype`) :

```python
"""Décode un tableau de valeurs binaires big-endian avec numpy."""

import numpy as np

values = np.frombuffer(raw_buffer, dtype=">i4")  # (1)!
```

1. `">i4"` signifie « entier signé 4 octets, big-endian ». `"<i4"` donnerait
   le little-endian. Comme pour `struct`, omettre le préfixe utilise l'ordre
   natif de la machine — à éviter pour des données mainframe.

## Ce qui n'est PAS concerné par l'endianness

Deux formats mainframe fréquemment rencontrés aux côtés des champs binaires
ne sont **pas** soumis à l'endianness — les confondre est une source d'erreur
classique :

- **Le texte encodé caractère par caractère** (EBCDIC, ASCII, UTF-8) : chaque
  octet porte un caractère complet et autonome, pas un fragment d'un nombre
  plus grand. Voir
  [encodage EBCDIC](../python/exemples-pratiques.md#encodage-ebcdic-ascii).
- **Le décimal empaqueté** (`COMP-3`) : chaque nibble porte un chiffre
  décimal à une position fixe, lue de gauche à droite — c'est un format
  sériel comparable à une chaîne de caractères, pas un entier en base 256
  réparti sur plusieurs octets. Voir
  [Format PACKED](../python/exemples-pratiques.md#format-packed-decimal-empaquete-comp-3).

La règle générale : l'endianness ne concerne que les valeurs représentées
comme un **entier positionnel en base 256** réparti sur plusieurs octets
(`BINARY`/`COMP`/`COMP-4`/`COMP-5`, et les flottants HFP/BFP). Dès qu'un
format lit ses octets ou ses nibbles de façon strictement séquentielle sans
notion de poids binaire global, l'endianness ne s'applique pas.

## Sources

- [z/Architecture Principles of Operation (SA22-7832)](https://www.ibm.com/docs/en/module_1678991624569/pdf/SA22-7832-14.pdf) — définition des unités byte/halfword/fullword/doubleword/quadword et de leur ordre big-endian.
- [Wikipedia — Endianness](https://en.wikipedia.org/wiki/Endianness) — historique du terme et du network byte order.
- [Documentation Python — module `struct`](https://docs.python.org/3/library/struct.html) — caractères de format d'ordre des octets.
