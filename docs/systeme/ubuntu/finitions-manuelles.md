# Finitions manuelles après le provisionnement

Cette page recense les réglages qui restent **à faire à la main** après
avoir exécuté `sudo make all` depuis `~/alm_tools/postinstall` : choix
interactifs, comptes en ligne, préférences graphiques — tout ce qu'un
script ne peut pas (ou ne doit pas) automatiser.

Elle complète le tutoriel
[Déploiement après installation fraîche](deploiement-post-installation.md),
dont elle détaille l'étape « Finitions ».

!!! info "Ce qu'`alm_tools/postinstall` prend en charge automatiquement"
    - Mise à jour APT + codecs et polices Microsoft (`restricted`)
    - Paramètres GNOME : dock, batterie, hot corners, accent bleu (`gnome-settings`)
    - Polices FiraCode, JetBrains Mono, Cascadia Code (`fonts`)
    - Starship prompt (`starship`)
    - Extensions Nautilus : wipe, admin, image-converter (`pkg-install`)
    - Modèles Nautilus dans `~/Modèles` (`nautilus-templates`)
    - Ouvrir Kitty depuis Nautilus (`nautilus-terminal`)
    - Suppression définitive de Firefox — APT + Snap + résidus (`remove-firefox`)

    → Voir [alm_tools — Post-installation](alm_tools/postinstall/post-installation.md)

---

## 1. Ubuntu Pro (optionnel)

Ubuntu Pro est gratuit pour usage personnel (jusqu'à 5 machines).
Il donne accès aux mises à jour de sécurité étendues (ESM).

1. Connectez-vous sur [ubuntu.com/pro](https://ubuntu.com/pro)
2. Copiez la commande `pro attach <token>` depuis le tableau de bord
3. Exécutez-la dans le terminal
4. Relancez la mise à jour : `sudo apt update && sudo apt upgrade -y`

---

## 2. Terminal

### Kitty comme terminal par défaut

`alm_tools` installe Kitty via l'installeur upstream (`make kitty` →
`~/.local/kitty.app`, voir
[Kitty — installation](../../outils/kitty/index.md#installation)), plus
par apt. Kitty ne s'enregistre donc **pas** tout seul dans le système
d'alternatives Debian. Pour le déclarer terminal par défaut
(`x-terminal-emulator`), l'enregistrer manuellement :

```bash
sudo update-alternatives --install /usr/bin/x-terminal-emulator \
    x-terminal-emulator "$HOME/.local/kitty.app/bin/kitty" 50
sudo update-alternatives --set x-terminal-emulator \
    "$HOME/.local/kitty.app/bin/kitty"
```

!!! note "Optionnel sur cette machine"
    Le clic droit Nautilus passe par `nautilus-open-any-terminal`
    (qui trouve `kitty` dans le PATH), et le dock épingle
    `kitty.desktop` — l'alternative `x-terminal-emulator` ne sert
    qu'aux applications tierces qui demandent « un terminal » au
    système.

### Thème Catppuccin pour GNOME Terminal

```bash
curl -L https://raw.githubusercontent.com/catppuccin/gnome-terminal/v0.3.0/install.py \
    | python3 -
```

Ouvrez ensuite **GNOME Terminal** → **Édition** → **Préférences**, puis
activez le profil *Catppuccin Frappé* comme profil par défaut.

---

## 3. Nautilus

### Afficher le nombre d'éléments sous les dossiers

Dans Nautilus : **Édition** → **Préférences** → section **Libellés de la
vue grille** → sélectionnez **Taille** pour le premier libellé.
