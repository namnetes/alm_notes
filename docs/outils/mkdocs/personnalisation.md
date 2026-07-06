# Personnalisations de ce wiki

Cette page documente toutes les modifications apportées au-delà d'une
installation MkDocs Material standard. Elle sert de référence pour reproduire
ou faire évoluer la configuration.

---

## Vue d'ensemble

| Fichier | Rôle |
|---|---|
| `docs/stylesheets/extra.css` | Mise en page 100% largeur, dimensions sidebars, dropdown CSS |
| `docs/javascripts/nav-dropdown.js` | Menu déroulant interactif sur les onglets de navigation |
| `docs/javascripts/mathjax.js` | Initialisation de MathJax 3 pour le rendu LaTeX |
| `mkdocs.yml` | Désactivation des polices Google, langue FR, plugins, features |
| `Makefile` | Détection de port dynamique, gestion du serveur en arrière-plan |

---

## CSS — `docs/stylesheets/extra.css`

### 1. Mise en page 100 % largeur

Par défaut, Material for MkDocs centre le contenu dans une colonne d'environ
1200 px avec des marges blanches de chaque côté. Ces règles suppriment cette
contrainte pour utiliser toute la largeur de l'écran.

```css
.md-grid {
  max-width: 100%;
  margin: 0;
}

.md-content {
  max-width: 100%;
}

.md-main__inner {
  padding-left: 0;
  padding-right: 0;
}

.md-content__inner {
  max-width: 100%;
}
```

**Pourquoi ?** Les tableaux larges (comparatifs, références techniques) et les
blocs de code dépassent souvent 1200 px. Avec la largeur complète, rien n'est
tronqué ni scrollable horizontalement.

### 2. Dimensions des sidebars

Material impose des largeurs fixes qui ne correspondent pas toujours au contenu.
Ces règles les ajustent :

```css
:root {
  --md-sidebar-width: 13.068rem;
}

/* Sidebar gauche (navigation) */
.md-sidebar {
  width: 13.068rem !important;
}

/* Sidebar droite (table des matières) */
.md-sidebar--secondary {
  width: 20.7537rem !important;
}
```

**Pourquoi ces valeurs précises ?** Elles ont été calibrées à la main pour que
la sidebar gauche affiche les titres de section sans troncature, et que la
sidebar droite (TOC) soit assez large pour les ancres longues générées depuis
les titres français.

### 3. Fix du padding interne des sidebars (webkit)

Material calcule le padding droit des sidebars avec un `calc(100% - 11.5rem)`
qui bloque le contenu à 11.5 rem quelle que soit la largeur déclarée. Cette
règle écrase ce calcul pour webkit (Chrome, Edge, Brave) :

```css
@supports selector(::-webkit-scrollbar) {
  [dir=ltr] .md-sidebar__inner {
    padding-right: 0.4rem !important;
  }
}

.md-sidebar__inner {
  padding-right: 0.4rem !important;
}
```

**Pourquoi `@supports selector(::-webkit-scrollbar)` ?** Ce sélecteur CSS est
reconnu uniquement par les navigateurs webkit, ce qui permet de cibler la règle
spécifique de Material sans affecter Firefox.

### 4. Ellipsis sur les titres longs dans la sidebar

Material 9.7 ne tronque pas les titres longs dans la nav — ils wrappent sur
plusieurs lignes et décalent le chevron de pliage hors alignement :

```css
.md-nav__link .md-ellipsis {
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

**Résultat** : les titres longs sont tronqués avec `…` sur une seule ligne. Le
titre complet reste accessible en survolant le lien (tooltip natif du navigateur
via l'attribut `title`).

### 5. Dropdown CSS sur les onglets de navigation

Les onglets de la barre supérieure affichent un menu déroulant au survol
quand la section correspondante contient des sous-sections :

```css
.md-tabs__item--has-dropdown {
  position: relative;
}

.md-tabs__dropdown {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  list-style: none;
  margin: 0;
  padding: 0.3rem 0;
  background-color: var(--md-primary-fg-color--dark);
  min-width: 11rem;
  border-radius: 0 0 0.2rem 0.2rem;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.md-tabs__item--has-dropdown:hover .md-tabs__dropdown {
  display: block;
}

.md-tabs__dropdown li a {
  display: block;
  padding: 0.45rem 1rem;
  color: var(--md-primary-bg-color);
  font-size: 0.7rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  text-decoration: none;
  white-space: nowrap;
  opacity: 0.85;
  transition: opacity 0.15s, background-color 0.15s;
}

.md-tabs__dropdown li a:hover {
  opacity: 1;
  background-color: rgba(0, 0, 0, 0.15);
}
```

La classe `md-tabs__item--has-dropdown` est injectée dynamiquement par
`nav-dropdown.js` (voir ci-dessous).

---

## JavaScript — `docs/javascripts/nav-dropdown.js`

Ce script construit et injecte les menus déroulants sur les onglets de
navigation qui ont des sous-sections.

```js
document$.subscribe(function () {

  // Nettoyage des dropdowns existants (navigation SPA sans rechargement)
  document.querySelectorAll('.md-tabs__dropdown').forEach(el => el.remove());
  document.querySelectorAll('.md-tabs__item--has-dropdown').forEach(el => {
    el.classList.remove('md-tabs__item--has-dropdown');
  });

  const tabItems = document.querySelectorAll('.md-tabs__item');

  tabItems.forEach(tabItem => {
    const tabLink = tabItem.querySelector('.md-tabs__link');
    if (!tabLink) return;
    const tabText = tabLink.textContent.trim();

    const navSections = document.querySelectorAll(
      '.md-nav--primary > .md-nav__list > .md-nav__item--nested'
    );

    navSections.forEach(section => {
      const ellipsis = section.querySelector(':scope > label > .md-ellipsis');
      if (!ellipsis || ellipsis.textContent.trim() !== tabText) return;

      const children = section.querySelectorAll(
        ':scope > nav > ul > li.md-nav__item'
      );
      if (!children.length) return;

      // Ne créer un dropdown que si la section a des sous-sections
      const hasSubSections = [...children].some(c =>
        c.classList.contains('md-nav__item--nested')
      );
      if (!hasSubSections) return;

      const dropdown = document.createElement('ul');
      dropdown.className = 'md-tabs__dropdown';

      children.forEach(child => {
        const isNested = child.classList.contains('md-nav__item--nested');
        const a = document.createElement('a');

        if (isNested) {
          const label = child.querySelector(':scope > label > .md-ellipsis');
          const firstLink = child.querySelector('a.md-nav__link');
          if (!label || !firstLink) return;
          a.textContent = label.textContent.trim();
          a.href = firstLink.href;
        } else {
          const link = child.querySelector(':scope > a.md-nav__link');
          if (!link) return;
          a.textContent = link.textContent.trim();
          a.href = link.href;
        }

        if (a.textContent) {
          const li = document.createElement('li');
          li.appendChild(a);
          dropdown.appendChild(li);
        }
      });

      if (dropdown.children.length) {
        tabItem.classList.add('md-tabs__item--has-dropdown');
        tabItem.appendChild(dropdown);
      }
    });
  });
});
```

**Points clés :**

- `document$.subscribe(…)` — observable fourni par Material pour les
  navigations SPA (sans rechargement complet de la page). Le script se
  réexécute à chaque changement de page, ce qui évite les dropdowns obsolètes.
- Le script ne crée un dropdown que si la section contient des
  **sous-sections** (`md-nav__item--nested`). Les sections plates (onglet
  avec pages directes) gardent un comportement standard.
- Pour les sous-sections imbriquées, le lien pointe vers la **première page**
  de la sous-section (`firstLink`), pas vers une ancre de section qui
  n'existerait pas.

---

## JavaScript — `docs/javascripts/mathjax.js`

Initialise MathJax 3 pour le rendu des formules LaTeX dans les pages.
Fonctionne conjointement avec l'extension `pymdownx.arithmatex` de MkDocs.

```js
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex"
  }
};

document$.subscribe(() => {
  MathJax.typesetPromise()
})
```

**Fonctionnement :**

- `pymdownx.arithmatex` entoure les formules LaTeX d'une balise
  `<div class="arithmatex">` ou `<span class="arithmatex">`.
- `processHtmlClass: "arithmatex"` dit à MathJax de ne traiter que ces
  balises — le reste du HTML est ignoré, ce qui évite des rendus parasites.
- `document$.subscribe(() => MathJax.typesetPromise())` relance le rendu
  MathJax après chaque navigation SPA, sinon les formules restent en texte
  brut sur les pages visitées sans rechargement.

**Écrire du LaTeX dans une page :**

```markdown
Formule inline : \( E = mc^2 \)

Formule en bloc :

\[
  \int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
\]
```

Le CDN MathJax est déclaré dans `mkdocs.yml` :

```yaml
extra_javascript:
  - javascripts/mathjax.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js
```

!!! warning "Ordre de chargement"
    `mathjax.js` doit être déclaré **avant** le CDN MathJax dans
    `extra_javascript`. MathJax lit `window.MathJax` au démarrage — si le CDN
    se charge en premier, la configuration est ignorée.

---

## `mkdocs.yml` — paramètres personnalisés

### Polices Google désactivées

```yaml
theme:
  font: false
```

Material charge par défaut deux polices depuis Google Fonts (Roboto et Roboto
Mono), ce qui implique une requête réseau externe à chaque chargement de page.
`font: false` utilise les polices système du navigateur — plus rapide, aucune
dépendance externe, fonctionne hors ligne.

### Interface en français

```yaml
theme:
  language: fr
```

Traduit tous les labels de l'interface générés par Material : boutons de
recherche, libellés de navigation, texte du sélecteur de mode clair/sombre.

### Features de navigation activées

```yaml
theme:
  features:
    - navigation.tabs          # barre d'onglets horizontale en haut
    - navigation.sections      # sections visibles dans la sidebar
    - navigation.indexes       # index.md devient la page de la section
    - navigation.expand        # déploie automatiquement la section active
    - navigation.top           # bouton "retour en haut" en bas de page
    - search.highlight         # surligne le terme cherché dans la page
    - search.suggest           # complétion automatique dans la recherche
    - content.code.copy        # bouton copier sur chaque bloc de code
    - content.code.annotate    # annotations numérotées dans les blocs de code
```

### Extension LaTeX

```yaml
markdown_extensions:
  - pymdownx.arithmatex:
      generic: true
```

L'option `generic: true` produit un HTML générique (balises `arithmatex`)
compatible avec n'importe quel moteur de rendu LaTeX côté client, pas
seulement MathJax. Sans cette option, l'output est spécifique à MathJax 2.

### Plugins activés

```yaml
plugins:
  - search:
      lang: fr                     # index de recherche en français (stemming)
  - minify:
      minify_html: true            # compresse le HTML généré
  - git-revision-date-localized:
      enable_creation_date: true   # "Créé le" + "Modifié le" en pied de page
  - awesome-pages                  # ordre des pages via fichiers .pages
  - include-markdown               # inclure un .md dans un autre
  - macros                         # variables Jinja2 dans les pages
```

---

## Makefile — automatisation du serveur

### Détection de port dynamique

```makefile
PORT := $(shell \
    for p in $$(seq 8000 8050); do \
        lsof -ti:$$p >/dev/null 2>&1 || { echo $$p; break; }; \
    done)
HOST := 127.0.0.1
```

Sonde les ports 8000 à 8050 et choisit le premier libre. Indispensable quand
plusieurs projets docs tournent en parallèle sur la même machine.

### Serveur en arrière-plan (`docs-start` / `docs-stop`)

```makefile
PID_FILE := .mkdocs.pid
LOG_FILE := .mkdocs.log

docs-start:
    @if [ -f $(PID_FILE) ] && kill -0 $$(cat $(PID_FILE)) 2>/dev/null; then \
        printf "MkDocs tourne déjà (PID $$(cat $(PID_FILE))).\n"; \
    else \
        rm -f $(PID_FILE); \
        uv run mkdocs serve --dev-addr $(HOST):$(PORT) > $(LOG_FILE) 2>&1 & \
        echo $$! > $(PID_FILE); \
    fi

docs-stop:
    @PID=$$(cat $(PID_FILE)); \
    if kill -0 $$PID 2>/dev/null; then \
        kill $$PID; \
    fi; \
    rm -f $(PID_FILE)
```

- `.mkdocs.pid` enregistre le PID du processus pour pouvoir l'arrêter.
- `.mkdocs.log` capture stdout et stderr du serveur — consultable avec
  `cat .mkdocs.log` si le serveur plante au démarrage.
- `kill -0 $$PID` teste si le processus est vivant **sans** l'arrêter (signal
  zéro = test d'existence seulement). Évite les erreurs si le serveur a été
  tué manuellement entre `docs-start` et `docs-stop`.

### Variable d'environnement

```makefile
export DISABLE_MKDOCS_2_WARNING := true
```

Supprime le bandeau d'avertissement affiché par MkDocs 2.x lors de
l'utilisation de certaines fonctionnalités dépréciées dans la config.
