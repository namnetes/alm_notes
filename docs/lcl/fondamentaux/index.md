# Fondamentaux mainframe

Concepts de bas niveau communs à tous les sujets mainframe (COBOL, Kafka,
Python...) : comment les nombres sont réellement stockés en mémoire sur
z/OS, et pourquoi l'ordre des octets diffère d'un poste x86/x64.

<div class="grid cards" markdown>

-   :material-numeric: **[Types numériques sur mainframe](types-numeriques.md)**

    Décimal zoné (`DISPLAY`), décimal empaqueté (`COMP-3`), binaire fixe
    (`COMP`/`COMP-4`/`COMP-5`), virgule flottante (HFP, BFP, DFP) : structure,
    différences, et cas d'usage recommandés d'après IBM.

-   :material-swap-horizontal: **[Boutisme (endianness)](endianness.md)**

    Big-endian vs little-endian, pourquoi z/Architecture est big-endian de
    bout en bout, et comment convertir en Python (`struct`, `int.from_bytes`,
    `numpy`).

</div>
