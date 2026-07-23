# Pourquoi Python a sa place sur le mainframe

!!! quote "Source"
    Cette page est une adaptation en français, enrichie de recherches complémentaires,
    de l'article [*Why Python belongs on the mainframe*](https://medium.com/@thomas.mcquitty/why-python-belongs-on-the-mainframe-992b77493ebe)
    de Thomas McQuitty (Medium, 2026).

!!! info "Prérequis"
    Cette page suppose une familiarité de base avec l'environnement z/OS (JCL, jeux de
    données, USS) et avec Python. Voir [Mainframe](../index.md) pour le contexte général.

Python ne remplace pas COBOL. Ce n'est pas son rôle. C'est un moyen concret de
moderniser l'automatisation, l'intégration et les flux de travail des développeurs
autour des systèmes qui continuent de faire tourner l'entreprise.

## Un socle solide, un vivier de compétences qui se réduit

Le mainframe reste l'épine dorsale de nombreuses grandes institutions. COBOL, JCL
(*Job Control Language* — le langage de script qui décrit l'exécution des jobs batch
z/OS), Assembleur, CLIST et REXX portent des applications critiques depuis des
décennies. Ces langages sont fiables, profondément intégrés, et toujours très
efficaces pour les tâches auxquelles ils ont été conçus.

Ce qui a changé, c'est le vivier de compétences et l'outillage disponibles autour
de ces systèmes.

La plupart des nouveaux développeurs n'apprennent plus COBOL, JCL, CLIST ou REXX à
l'école. Beaucoup d'organisations forment ces compétences sur le tas, ce qui prend
du temps et repose largement sur des experts mainframe déjà en sous-effectif. Dans
le même temps, les développeurs arrivent avec une expérience Python, des attentes
d'IDE modernes, des habitudes open source, et l'envie de travailler sur plusieurs
plateformes.

C'est là que Python devient intéressant : il ne rend pas le mainframe moderne par
magie, mais il donne aux équipes un langage moderne capable de fonctionner près des
données mainframe, d'automatiser des tâches opérationnelles répétitives, de
s'intégrer aux systèmes distribués, et de rendre certains flux de développement
plus accessibles.

## Les atouts de Python sur z/OS

Python combine plusieurs qualités rares :

- Suffisamment lisible pour le scripting et l'automatisation.
- Supporte à la fois les styles procédural et orienté objet.
- Utilisable en mode interactif pour apprendre ou déboguer — sans commande `TRACE`.
- Un écosystème de paquets immense pour la donnée, les API, les fichiers, le
  reporting, les tests et l'automatisation.
- Largement enseigné et largement utilisé.
- Plus facile à apprendre pour un développeur REXX que d'autres langages comme
  JavaScript.

Cela compte, car la plupart des efforts de modernisation ne visent pas à remplacer
les systèmes cœur. Ils visent à rendre ces systèmes plus faciles à étendre, intégrer,
observer et exploiter.

Python peut soumettre des jobs, accéder à des jeux de données, dialoguer avec des
bases de données, appeler des services, créer des fichiers et des rapports, analyser
des données opérationnelles, et s'intégrer à des outils comme ServiceNow ou des API
internes. Il peut aussi cohabiter avec les actifs mainframe traditionnels au lieu
d'imposer leur réécriture.

En ce sens, Python n'est pas un argument contre le mainframe. C'est un argument pour
maintenir le mainframe utile dans un écosystème technologique plus large.

## La comparaison avec REXX

Une bonne façon de penser Python sur le mainframe est de le comparer à REXX.

REXX a longtemps été précieux car il permet de relier entre elles les fonctions
mainframe. Il est accessible, interprété, et profondément intégré à de nombreux
flux de travail mainframe. Python peut jouer un rôle similaire, mais avec un
écosystème externe bien plus vaste et un vivier de talents bien plus large.

Cela rend Python particulièrement utile pour :

- L'automatisation autrefois écrite en REXX ou CLIST.
- Les tâches utilitaires proches du JCL.
- La manipulation de jeux de données ou de fichiers.
- Le reporting et les scripts opérationnels.
- Les intégrations API.
- Les intégrations ServiceNow ou de ticketing.
- L'accès aux bases de données et la validation de données.
- Le prototypage avant de s'engager dans une implémentation plus large.

L'objectif n'est pas de réécrire immédiatement chaque programme REXX qui fonctionne.
L'objectif est d'identifier les endroits où Python apporte une meilleure
maintenabilité, de meilleures bibliothèques, de meilleurs tests, ou une meilleure
intégration.

## Python comme code de liaison (glue code)

Certains des meilleurs cas d'usage de Python sur mainframe sont du *glue code*
(code de liaison entre composants).

Par exemple, un traitement qui utilise COBOL Sort peut être simplifié en déplaçant
le tri et l'orchestration vers Python, puis en appelant l'application COBOL ensuite.
Ce type de changement peut réduire la complexité du code COBOL, préserver la
logique métier intacte, et déplacer une partie du travail opérationnel vers un
langage que davantage de développeurs peuvent maintenir.

Python est aussi pertinent quand les équipes doivent connecter le mainframe à des
systèmes distribués. Plutôt que d'exporter les données, de les déplacer ailleurs,
de les transformer, puis de renvoyer les résultats, Python peut parfois interroger
ou valider les données directement là où elles se trouvent — ce qui peut être plus
rapide, plus simple, et plus facile à raisonner.

## L'argument des talents

Le vivier de compétences est l'une des raisons les plus concrètes de considérer
Python sur le mainframe.

Python est enseigné largement. Il dispose de ressources d'apprentissage en ligne
solides. Il a une large communauté. Les nouveaux développeurs arrivent souvent
avec une certaine familiarité Python avant même d'avoir la moindre expérience
mainframe.

Cela n'élimine pas le besoin d'expertise mainframe. Au contraire : Python sur le
mainframe fonctionne le mieux quand les développeurs de langages modernes et les
ingénieurs mainframe expérimentés collaborent. Le développeur Python comprend les
API, les paquets et l'automatisation des tests. L'expert mainframe comprend les
jeux de données, le JCL, les modèles de sécurité, les encodages, les sorties de
job et le risque opérationnel.

La combinaison des deux est puissante. Python peut rendre le développement
mainframe plus accessible, mais il ne doit pas servir à contourner la rigueur
mainframe.

## Points de vigilance

Python apporte des bénéfices, mais aussi de nouvelles responsabilités. Les équipes
doivent réfléchir avec soin à :

- La performance pour les traitements *CPU-bound* ou sensibles à la latence.
- L'encodage de caractères, en particulier les frontières entre EBCDIC, ASCII et
  UTF-8 (voir [Exemples pratiques](exemples-pratiques.md#encodage-ebcdic-ascii)).
- Les données binaires et les différences de boutisme (*endianness*) entre
  plateformes (voir [Boutisme (endianness)](../fondamentaux/endianness.md) pour
  l'explication complète, et [Exemples pratiques](exemples-pratiques.md#boutisme-endianness-des-champs-binaires)
  pour le code Python).
- Le bon type numérique COBOL à respecter en lecture/écriture (décimal zoné,
  empaqueté, binaire, flottant — voir [Types numériques sur mainframe](../fondamentaux/types-numeriques.md)).
- La compatibilité des paquets sur z/OS.
- Le risque de chaîne d'approvisionnement (*supply chain*) lié aux dépendances
  open source.
- La gestion des secrets.
- Les modèles d'exécution batch, OMVS, USS et *started task*.
- Les permissions sur les fichiers et les jeux de données.
- La pertinence réelle de Python pour la tâche visée.

Ce ne sont pas des raisons d'éviter Python. Ce sont des raisons de l'introduire de
façon délibérée.

## Où Python est le plus pertinent

Python est un bon candidat quand le travail bénéficie de flexibilité,
d'intégration ou de vélocité de développement :

- Automatisation.
- Reporting.
- Code de liaison (glue logic).
- Validation de données.
- Intégration API.
- Accès aux bases de données.
- Transformation de fichiers.
- Remplacement d'utilitaires JCL.
- Modernisation REXX ou CLIST.
- Outillage opérationnel.

Python est en revanche généralement un mauvais choix pour :

- Réécrire une grosse application COBOL stable pour le seul plaisir de la
  réécrire.
- Les boucles *CPU-bound* serrées.
- Les chemins transactionnels en ligne sensibles à la latence.
- Remplacer des fonctions CICS ou IMS sans raison architecturale forte.
- Tout système déjà correct, rapide et maintenable en l'état.

La modernisation doit créer de la valeur. Elle ne doit pas créer une seconde
implémentation d'un problème déjà résolu.

## Démarrer petit

Le meilleur point de départ n'est généralement pas une grande réécriture
d'application.

Commencez par de l'automatisation isolée. Commencez par un utilitaire REXX ou
CLIST. Commencez par une étape JCL qui fait du déplacement de fichiers, du
parsing, du reporting ou de l'intégration API. Commencez là où l'échec est
contenu et le succès facile à mesurer.

Puis évaluez le résultat :

- Est-ce plus facile à maintenir ?
- Est-ce plus facile à tester ?
- Est-ce plus facile à intégrer ?
- La performance est-elle acceptable ?
- Respecte-t-il les mêmes standards de sécurité et d'exploitation que le
  processus existant ?

Si la réponse est oui, étendez à partir de là.

!!! tip "L'essentiel"
    Python sur le mainframe ne consiste pas à abandonner ce qui fonctionne. Il
    s'agit de donner aux équipes un outil supplémentaire pour le travail qui
    entoure les systèmes métier cœur : automatisation, intégration, reporting,
    validation et modernisation.

    Utilisé à bon escient, Python aide le mainframe à s'intégrer plus
    naturellement dans une architecture d'entreprise moderne. Utilisé sans
    discernement, il peut introduire de nouveaux modes de défaillance dans une
    plateforme qui exige de la rigueur. La différence ne tient pas au langage,
    mais à la façon dont il est adopté.

## Pour aller plus loin — l'écosystème Python sur z/OS

L'article original reste général sur les outils disponibles. Voici les briques
concrètes qui rendent cette approche possible aujourd'hui, avec des exemples dans
la page [Exemples pratiques](exemples-pratiques.md).

| Outil | Rôle | Version référencée |
|---|---|---|
| [IBM Open Enterprise SDK for Python for z/OS](https://www.ibm.com/products/open-enterprise-python-zos) | Interpréteur Python natif sous USS (*Unix System Services* — le sous-système Unix de z/OS) | **3.14** — GA le 2025-11-14, dernières PTF le 2026-02-13 |
| [ZOAU (Z Open Automation Utilities)](https://www.ibm.com/docs/en/zoau) et son module `zoautil_py` | API Python pour manipuler jeux de données, soumettre des jobs, interagir avec JES (*Job Entry Subsystem* — le sous-système qui gère la file des jobs batch) | **1.4.1** — PTF PH68100/UO07004, février 2026 |
| [Zowe CLI et le Zowe Client Python SDK](https://www.zowe.org/) | Automatisation mainframe depuis un poste distant (jobs, jeux de données, provisioning) | Projet Open Mainframe Project / Linux Foundation, versionné indépendamment de z/OS |
| [Ansible Certified Content for IBM Z](https://github.com/ansible-collections/ibm_zos_core) (`ibm.ibm_zos_core`) | Modules Ansible écrits en Python/REXX pour piloter z/OS depuis des playbooks | Collection versionnée indépendamment, voir [notes de version](https://ibm.github.io/z_ansible_collections_doc/ibm_zos_core/docs/source/release_notes.html) |
| [py3270](https://github.com/py3270/py3270) | Automatisation d'écrans 3270 (CICS, ISPF) via `x3270`/`s3270` | Bibliothèque tierce, indépendante des versions z/OS |
| [API REST z/OSMF](https://www.ibm.com/docs/en/zos/2.4.0?topic=guide-using-zosmf-rest-services) | Soumission de jobs et accès aux données via HTTP/JSON, appelable avec `requests` | Composant intégré à z/OS, versionné avec le système d'exploitation |
| [IBM RSE API](https://www.ibm.com/docs/en/explorer-for-zos/3.4?topic=documentation-rse-api) (*Remote System Explorer API*) | API REST alternative à z/OSMF pour jobs, datasets et fichiers USS — utilisée en interne par IDz (*IBM Developer for z/OS*, l'IDE Eclipse) et par le plug-in RSE API pour Zowe CLI | **IBM Explorer for z/OS 3.4.4**, 2026-02-20 (composant hôte RSE qui expose l'API) |

!!! warning "Écart avec l'article original"
    Les points ci-dessus ne figurent pas dans l'article Medium source — ils ont
    été ajoutés lors de l'intégration dans ce wiki, à partir de recherches sur
    l'écosystème IBM Z et Zowe, pour rendre le sujet plus actionnable.

!!! info "Versions vérifiées le 2026-07-23"
    Les numéros de version ci-dessus évoluent vite (PTF mensuelles côté IBM Z).
    Avant toute mise en œuvre, revérifier la version courante sur les pages
    officielles liées plutôt que de se fier à cette page.

## Voir aussi

- [Exemples pratiques](exemples-pratiques.md) — le code Python correspondant
  à chaque outil listé ci-dessus.
- [Types numériques sur mainframe](../fondamentaux/types-numeriques.md) — les
  formats numériques COBOL (décimal zoné, empaqueté, binaire, flottant) et
  leurs cas d'usage recommandés.
- [Boutisme (endianness)](../fondamentaux/endianness.md) — l'ordre des octets
  sur z/Architecture, indépendamment de COBOL.
