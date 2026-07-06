/* Dropdown sur les onglets de navigation qui ont des sous-sections */
document$.subscribe(function () {

  // Supprimer les dropdowns existants (rechargement SPA)
  document.querySelectorAll('.md-tabs__dropdown').forEach(el => el.remove());
  document.querySelectorAll('.md-tabs__item--has-dropdown').forEach(el => {
    el.classList.remove('md-tabs__item--has-dropdown');
  });

  const tabItems = document.querySelectorAll('.md-tabs__item');

  tabItems.forEach(tabItem => {
    const tabLink = tabItem.querySelector('.md-tabs__link');
    if (!tabLink) return;
    const tabText = tabLink.textContent.trim();

    // Chercher la section correspondante dans la nav primaire
    const navSections = document.querySelectorAll(
      '.md-nav--primary > .md-nav__list > .md-nav__item--nested'
    );

    navSections.forEach(section => {
      const ellipsis = section.querySelector(':scope > label > .md-ellipsis');
      if (!ellipsis || ellipsis.textContent.trim() !== tabText) return;

      // Récupérer les enfants directs (sous-sections ou pages)
      const children = section.querySelectorAll(
        ':scope > nav > ul > li.md-nav__item'
      );
      if (!children.length) return;

      // N'ajouter un dropdown que si des sous-sections existent
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
