# Raccourcis clavier — macOS

Cette page recense les raccourcis clavier du **mode interactif** de Claude
Code (celui qui s'ouvre en tapant `claude` dans un terminal, par opposition
au mode non-interactif `claude -p "..."` utilisé dans les scripts), pour les
utilisateurs **macOS**.

!!! info "Vous êtes sur Windows ou Linux ?"
    Cette page est spécifique à macOS (touche `Option`, `Cmd`, configuration
    du terminal). Consultez la page dédiée :
    [Raccourcis clavier — Windows / Linux](raccourcis-windows-linux.md).

!!! info "Convention de notation"
    Les raccourcis sont notés avec `+` entre les touches : ++cmd+c++
    signifie « maintenir Cmd et appuyer sur C ». Une séquence comme
    ++ctrl+x++ ++ctrl+k++ signifie « appuyer sur Ctrl+X, relâcher, puis
    appuyer sur Ctrl+K » — ce n'est **pas** une combinaison à trois touches
    simultanées.

Source vérifiée : [documentation officielle — mode interactif](https://code.claude.com/docs/en/interactive-mode).

---

## Prérequis — configurer Option comme touche Meta

Sur macOS, la touche `Option` n'envoie pas par défaut le signal « Meta »
attendu par certains raccourcis hérités des shells Unix (`readline`). Sans
cette configuration, `Option+B` ou `Option+F` insèrent un caractère
accentué (`∫`, `ƒ`…) au lieu d'agir comme raccourci.

D'après la documentation officielle, les raccourcis suivants **nécessitent**
cette configuration : ++option+b++, ++option+f++, ++option+y++,
++option+m++ et ++option+p++.

!!! warning "Comment configurer Option comme Meta"
    - **iTerm2** : Settings → Profiles → Keys → General → régler « Left/Right
      Option key » sur **Esc+**
    - **Apple Terminal** : Settings → Profiles → Keyboard → cocher **« Use
      Option as Meta Key »**
    - **VS Code** (terminal intégré) : ajouter
      `"terminal.integrated.macOptionIsMeta": true` dans les settings

!!! tip "Option+T ne nécessite plus cette configuration"
    Depuis la version 2.1.132 de Claude Code, ++option+t++ (réflexion
    étendue) fonctionne nativement sur macOS, sans configuration Meta.

---

## Contrôles généraux

| Raccourci | Effet |
|---|---|
| ++ctrl+c++ | Interrompre / effacer la saisie. Si rien n'est en cours d'exécution : **1ʳᵉ pression** efface le texte en cours de frappe, **2ᵉ pression** quitte Claude Code |
| ++escape++ | Interrompre Claude en cours de réponse (arrête la génération/l'outil en cours, le travail déjà fait est conservé) |
| ++escape++ ++escape++ | Si la saisie contient du texte : l'efface et enregistre le brouillon dans l'historique (rappelable avec ++up++). Si la saisie est vide : ouvre le menu de *rewind* (retour à un point antérieur de la conversation) |
| ++ctrl+d++ | Quitter la session (signal EOF) |
| ++ctrl+x++ ++ctrl+k++ | Stopper tous les subagents en arrière-plan (appuyer deux fois en moins de 3 secondes pour confirmer) |
| ++ctrl+b++ | Mettre les tâches Bash/agents en cours en arrière-plan (sous `tmux` : appuyer deux fois, à cause de la touche de préfixe `tmux`) |
| ++ctrl+t++ | Afficher/masquer la [liste des tâches](#liste-des-taches) dans la zone de statut du terminal |
| ++ctrl+g++ ou ++ctrl+x++ ++ctrl+e++ | Ouvrir le prompt (ou la dernière réponse de Claude, si activé dans `/config`) dans l'éditeur de texte par défaut (`$EDITOR`) |
| ++ctrl+l++ | Redessiner l'écran (conserve la saisie et l'historique — utile si l'affichage se corrompt) |
| ++ctrl+o++ | Afficher/masquer le [visualiseur de transcript](#visualiseur-de-transcript-ctrlo) |
| ++ctrl+r++ | [Recherche inversée](#recherche-inversee-dans-lhistorique) dans l'historique des commandes |
| ++ctrl+v++ ou ++cmd+v++ (iTerm2) | Coller une image du presse-papiers — insère une puce `[Image #N]` réutilisable dans le prompt |
| ++left++ / ++right++ | Naviguer entre les onglets d'une boîte de dialogue (permissions, menus) |
| ++up++ / ++down++ ou ++ctrl+p++ / ++ctrl+n++ | Déplacer le curseur dans une saisie multiligne ; une fois sur la première/dernière ligne visuelle, navigue dans l'historique des commandes |
| ++shift+tab++ ou ++option+m++ | Faire défiler les **modes de permission** : `default`, `acceptEdits`, `plan`, et tout mode personnalisé activé (`auto`, `bypassPermissions`…). *Nécessite Option comme Meta* |
| ++option+p++ | Changer de modèle, sans effacer le prompt en cours. *Nécessite Option comme Meta* |
| ++option+t++ | Activer/désactiver la réflexion étendue (*extended thinking*) — sans effet sur Fable 5, qui l'utilise toujours |
| ++option+o++ | Activer/désactiver le mode rapide (*fast mode*) |

---

## Édition de texte (ligne de saisie)

Ces raccourcis fonctionnent dans le champ de saisie, comme dans un shell
Bash (héritage de la bibliothèque `readline`).

| Raccourci | Effet |
|---|---|
| ++ctrl+a++ | Aller au début de la ligne logique courante (utile en saisie multiligne) |
| ++ctrl+e++ | Aller à la fin de la ligne logique courante |
| ++ctrl+k++ | Supprimer jusqu'à la fin de la ligne (le texte supprimé reste récupérable) |
| ++ctrl+u++ | Supprimer du curseur jusqu'au début de la ligne (répéter pour effacer plusieurs lignes en saisie multiligne). Sur iTerm2 et Terminal.app, `Cmd+Retour arrière` fait aussi l'affaire |
| ++ctrl+w++ | Supprimer le mot précédent |
| ++ctrl+y++ | Recoller le dernier texte supprimé par ++ctrl+k++, ++ctrl+u++ ou ++ctrl+w++ |
| ++option+y++ (juste après ++ctrl+y++) | Faire défiler l'historique des suppressions pour recoller un extrait plus ancien. *Nécessite Option comme Meta* |
| ++option+b++ | Reculer d'un mot. *Nécessite Option comme Meta* |
| ++option+f++ | Avancer d'un mot. *Nécessite Option comme Meta* |

---

## Thème et affichage

| Raccourci | Effet |
|---|---|
| ++ctrl+t++ | Activer/désactiver la coloration syntaxique des blocs de code — **uniquement** à l'intérieur du sélecteur `/theme` (ne pas confondre avec le `Ctrl+T` de la liste des tâches, contextuel à l'écran affiché) |

---

## Saisie multiligne

Par défaut, ++enter++ envoie immédiatement le message. Pour insérer un
retour à la ligne **sans envoyer** :

| Méthode | Raccourci | Compatibilité |
|---|---|---|
| Échappement rapide | ++backslash++ puis ++enter++ | Fonctionne dans **tous** les terminaux |
| Séquence de contrôle | ++ctrl+j++ | Fonctionne dans n'importe quel terminal, sans configuration |
| Shift+Entrée | ++shift+enter++ | Natif dans iTerm2, WezTerm, Ghostty, Kitty, Warp, Apple Terminal |
| Touche Option | ++option+enter++ | Après avoir configuré Option comme Meta (voir plus haut) |
| Collage direct | — | Coller un bloc de code ou des logs multilignes fonctionne toujours |

!!! tip "Shift+Entrée ne fonctionne pas dans votre terminal ?"
    Pour VS Code, Cursor, Devin Desktop, Alacritty ou Zed, lancez
    `/terminal-setup` dans Claude Code pour installer le raccourci.

---

## Commandes rapides (préfixes)

| Préfixe | Effet |
|---|---|
| `/` en début de ligne | Ouvre une commande ou un [skill](skills.md) |
| `!` en début de ligne | Bascule en [mode shell](#mode-shell) |
| `@` | Mentionne un chemin de fichier avec autocomplétion |

---

## Recherche inversée dans l'historique

++ctrl+r++ ouvre une recherche interactive dans l'historique des prompts
(les 100 plus récents, dédupliqués, sur le périmètre sélectionné) :

| Étape | Touche |
|---|---|
| Démarrer la recherche | ++ctrl+r++ |
| Taper la requête | (le terme recherché est surligné dans les résultats) |
| Parcourir les correspondances plus anciennes | ++ctrl+r++ à nouveau |
| Changer de périmètre (session → projet → tous les projets) | ++ctrl+s++ |
| Valider sans envoyer | ++tab++ ou ++escape++ |
| Valider et envoyer immédiatement | ++enter++ |
| Annuler et restaurer la saisie d'origine | ++ctrl+c++ |
| Annuler (recherche vide) | ++backspace++ |

---

## Mode shell (`!`)

Taper `!` en début de ligne exécute la commande directement, sans passer
par Claude, tout en ajoutant sa sortie au contexte de la conversation.

| Raccourci | Effet |
|---|---|
| ++tab++ | Autocomplétion depuis l'historique des commandes `!` du projet courant |
| `/`  (dans un chemin) | Déclenche une autocomplétion de chemin de fichier en direct |
| ++escape++, ++backspace++ ou ++ctrl+u++ (sur une saisie vide) | Sortir du mode shell |
| ++ctrl+b++ | Mettre la commande en arrière-plan si elle est longue |

---

## Visualiseur de transcript (`Ctrl+O`)

++ctrl+o++ affiche l'historique complet de la conversation, y compris les
détails normalement repliés (résultats d'outils, appels MCP…).

| Raccourci | Effet |
|---|---|
| ++question++ | Afficher le panneau d'aide des raccourcis (nécessite le rendu plein écran) |
| ++open-bracket++ / ++close-bracket++ | Aller au prompt utilisateur précédent / suivant (nécessite le rendu plein écran) |
| ++ctrl+e++ | Afficher/masquer tout le contenu replié (rebindable via `transcript:toggleShowAll`) |
| ++open-bracket++ | Écrire la conversation complète dans le scrollback natif du terminal, consultable ensuite via ++cmd+f++ (nécessite le rendu plein écran) |
| ++v++ | Ouvrir la conversation dans `$VISUAL` ou `$EDITOR` (nécessite le rendu plein écran) |
| ++q++, ++ctrl+c++ ou ++escape++ | Quitter le visualiseur (rebindable via `transcript:exit`) |

---

## Suggestions de prompt

Une suggestion grisée peut apparaître dans le champ de saisie (tirée de
l'historique Git du projet ou de la conversation en cours).

| Raccourci | Effet |
|---|---|
| ++tab++ ou ++right++ | Placer la suggestion dans le champ de saisie |
| ++enter++ | Envoyer la suggestion placée |
| Toute frappe | Ignorer la suggestion |

---

## Questions annexes (`/btw`)

`/btw <question>` pose une question rapide sans polluer l'historique de la
conversation. Une fois la réponse affichée :

| Touche | Effet |
|---|---|
| ++space++, ++enter++ ou ++escape++ | Fermer la réponse et revenir au prompt |
| ++up++ / ++down++ | Faire défiler la réponse |
| ++left++ / ++right++ | Naviguer entre cette réponse et les précédentes questions `/btw` de la session |
| ++c++ | Copier la réponse en Markdown brut dans le presse-papiers |
| ++f++ | Créer une nouvelle session (*fork*) reprenant la conversation + cette question/réponse comme échange réel |
| ++x++ | Effacer la liste des questions `/btw` précédentes affichées au-dessus |

---

## Liste des tâches

| Raccourci | Effet |
|---|---|
| ++ctrl+t++ | Afficher/masquer la liste des tâches en cours (jusqu'à 5 affichées) |

---

## Statut des pull requests

Quand une branche a une pull request ouverte, un lien cliquable apparaît
dans le pied de page du terminal (ex. « PR #446 »).

| Raccourci | Effet |
|---|---|
| `Cmd+clic` sur le lien | Ouvrir la pull request dans le navigateur |

!!! info "Nécessite `gh` authentifié"
    Le statut de PR nécessite que le CLI `gh` soit installé et connecté
    (`gh auth login`).

---

## Saisie vocale

| Raccourci | Effet |
|---|---|
| Maintenir ou taper ++space++ | Dictée vocale (si activée) — maintenir pour enregistrer, ou lancer `/voice tap` pour basculer en mode « appui pour activer/désactiver » |

---

## Mode Vim

Claude Code propose un mode d'édition inspiré de Vim, à activer via
`/config` → *Editor mode*. Si vous n'êtes pas familier de Vim, le mode par
défaut (proche d'un champ de texte classique) convient très bien — ignorez
cette section. Les touches Vim ci-dessous n'utilisent que des lettres
(pas de Meta) : elles fonctionnent nativement, sans configuration
particulière.

!!! info "Rappel express : la logique des modes Vim"
    En mode **INSERT**, taper au clavier insère du texte normalement. En
    mode **NORMAL**, chaque touche est une *commande* — aucune lettre ne
    s'insère directement. ++escape++ ramène toujours au mode NORMAL depuis
    INSERT ou VISUAL.

### Passer d'un mode à l'autre

| Touche | Effet | Depuis |
|---|---|---|
| ++escape++ | Passer en NORMAL | INSERT, VISUAL |
| ++i++ | INSERT, juste avant le curseur | NORMAL |
| ++shift+i++ | INSERT, au début de la ligne | NORMAL |
| ++a++ | INSERT, juste après le curseur | NORMAL |
| ++shift+a++ | INSERT, à la fin de la ligne | NORMAL |
| ++o++ | Ouvrir une ligne en dessous, passer en INSERT | NORMAL |
| ++shift+o++ | Ouvrir une ligne au-dessus, passer en INSERT | NORMAL |
| ++v++ | Sélection visuelle caractère par caractère | NORMAL |
| ++shift+v++ | Sélection visuelle ligne par ligne | NORMAL |

### Navigation (mode NORMAL)

| Touche | Effet |
|---|---|
| ++h++ / ++j++ / ++k++ / ++l++ | Gauche / bas / haut / droite |
| ++space++ | Droite (alternative à `l`) |
| ++w++ | Mot suivant |
| ++e++ | Fin du mot courant |
| ++b++ | Mot précédent |
| ++0++ | Début de ligne |
| `$` | Fin de ligne |
| `^` | Premier caractère non-blanc de la ligne |
| ++g++ ++g++ | Début de toute la saisie |
| ++shift+g++ | Fin de toute la saisie |
| `f`{car} / `F`{car} | Aller au prochain / précédent caractère indiqué |
| `t`{car} / `T`{car} | Aller juste avant / juste après le caractère indiqué |
| ++semicolon++ | Répéter la dernière recherche `f`/`F`/`t`/`T` |
| ++comma++ | Répéter la dernière recherche `f`/`F`/`t`/`T`, en sens inverse |
| ++slash++ | Recherche inversée dans l'historique (équivalent de ++ctrl+r++) |

!!! note "En bout de saisie, `j`/`k` naviguent l'historique"
    Si le curseur est au tout début ou à la toute fin de la saisie et ne
    peut plus avancer, `j`/`k` et les flèches naviguent alors dans
    l'historique des commandes, comme en mode normal (hors Vim).

### Édition (mode NORMAL)

| Touche | Effet |
|---|---|
| ++x++ | Supprimer un caractère |
| ++d++ ++d++ | Supprimer la ligne entière |
| ++shift+d++ | Supprimer jusqu'à la fin de la ligne |
| `dw` / `de` / `db` | Supprimer : jusqu'au mot suivant / fin du mot / mot précédent |
| ++c++ ++c++ | Changer la ligne (supprime, passe en INSERT) |
| ++shift+c++ | Changer jusqu'à la fin de la ligne |
| `cw` / `ce` / `cb` | Changer : jusqu'au mot suivant / fin du mot / mot précédent |
| ++y++ ++y++ ou ++shift+y++ | Copier la ligne (*yank*) |
| `yw` / `ye` / `yb` | Copier : jusqu'au mot suivant / fin du mot / mot précédent |
| ++p++ / ++shift+p++ | Coller après / avant le curseur |
| `>>` / `<<` | Indenter / désindenter la ligne |
| ++shift+j++ | Joindre la ligne suivante à la ligne courante |
| ++u++ | Annuler |
| ++period++ | Répéter le dernier changement |

### Objets texte

Combinables avec ++d++ (supprimer), ++c++ (changer) ou ++y++ (copier) — par
exemple `di"` supprime le contenu entre guillemets sous le curseur.

| Objet | Signification |
|---|---|
| `iw` / `aw` | Mot **i**ntérieur (sans les espaces autour) / **a**vec les espaces autour |
| `iW` / `aW` | Idem pour un "MOT" délimité par des espaces (inclut la ponctuation collée) |
| `i"` / `a"` | Contenu entre guillemets doubles, avec ou sans les guillemets |
| `i'` / `a'` | Contenu entre guillemets simples |
| `i(` / `a(` | Contenu entre parenthèses |
| `i[` / `a[` | Contenu entre crochets |
| `i{` / `a{` | Contenu entre accolades |

### Mode visuel (sélection)

++v++ pour une sélection caractère par caractère, ++shift+v++ pour une
sélection ligne par ligne. Les mouvements étendent la sélection, les
opérateurs agissent dessus directement.

| Touche | Effet |
|---|---|
| ++d++ / ++x++ | Supprimer la sélection |
| ++y++ | Copier la sélection |
| ++c++ / ++s++ | Changer la sélection |
| ++p++ | Remplacer la sélection par le contenu du registre |
| `r`{car} | Remplacer chaque caractère sélectionné |
| ++tilde++ / ++u++ / ++shift+u++ | Basculer la casse / tout en minuscules / tout en majuscules |
| `>` / `<` | Indenter / désindenter les lignes sélectionnées |
| ++shift+j++ | Joindre les lignes sélectionnées |
| ++o++ | Échanger curseur et ancre de sélection |
| ++v++ / ++shift+v++ | Basculer entre sélection caractère/ligne, ou quitter |

!!! warning "Sélection par blocs non supportée"
    Le mode visuel « par blocs » (`Ctrl+V` dans Vim classique) n'est **pas**
    supporté par Claude Code.

---

## Personnaliser les raccourcis

Les combinaisons de touches peuvent être redéfinies via
`~/.claude/keybindings.json`.

!!! tip "Bloqué sur un raccourci qui ne répond pas ?"
    Utilisez le skill `keybindings-help` de ce wiki (invocable directement
    dans Claude Code) pour rebinder une touche, ajouter un raccourci en
    plusieurs frappes (*chord*), ou déboguer un conflit de configuration.

---

## Références

- [Documentation officielle — mode interactif](https://code.claude.com/docs/en/interactive-mode)
