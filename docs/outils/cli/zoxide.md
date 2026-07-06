# zoxide — le `cd` qui apprend

[zoxide](https://github.com/ajeetdsouza/zoxide) mémorise les répertoires
visités et leur attribue un score de fréquence/récence (*frecency*). Ensuite,
`cd` accepte un simple **motif** : `cd notes` saute vers `~/alm_notes` où que
l'on soit. Version installée : **0.9.3** (paquet Ubuntu, juillet 2026).

---

## Installation

Installé par le process de post-installation via la **liste de paquets APT**
(`config/packages_to_install.list` dans
[alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)).

```bash
zoxide --version
```

---

## Configuration (alm_dots)

Bloc dans `alm_dots/.bash_env` (stowé), gardé par `command -v zoxide` :

```bash
if command -v zoxide >/dev/null 2>&1; then
  # Enregistrer le chemin réel des liens symboliques (pas de doublons)
  export _ZO_RESOLVE_SYMLINKS=1

  # Décommenter pour afficher la destination après chaque saut
  # export _ZO_ECHO=1

  # Remplace `cd` ; `cdi` = sélection interactive (fzf)
  eval "$(zoxide init --cmd cd bash)"
fi
```

**Choix fait ici : le mode remplacement** (`--cmd cd`). Pas de nouvelle
commande à apprendre — `cd` devient simplement plus malin :

- `cd chemin/qui/existe` → comportement classique, inchangé ;
- `cd motif` (pas un chemin réel) → saute au **meilleur score** qui matche ;
- `cdi` → sélection interactive dans [fzf](fzf.md) quand plusieurs
  candidats se valent.

La base vit dans `~/.local/share/zoxide/db.zo` (spécifique à la machine,
non versionnée — elle se reconstruit à l'usage après une réinstallation).

---

## Exemples d'usage

### Navigation quotidienne

```console
$ pwd
/tmp
$ cd notes          # → /home/galan/alm_notes (meilleur score pour « notes »)
$ cd dots           # → /home/galan/alm_dots
$ cd al no          # plusieurs mots : tous doivent matcher, dans l'ordre
$ cd -              # revenir au dossier précédent (inchangé)
```

### `cdi` — quand plusieurs dossiers matchent

```console
$ cdi post
❯ post
> /home/galan/alm_tools/postinstall
  /home/galan/alm_notes/docs/systeme/ubuntu/alm_tools/postinstall
```

### Interroger et entretenir la base

```console
$ zoxide query notes            # quel dossier gagnerait ? (sans y aller)
/home/galan/alm_notes
$ zoxide query --list --score | head -5    # top de la base (93 entrées)
$ zoxide add /chemin/projet     # forcer un ajout
$ zoxide remove /vieux/chemin   # retirer une entrée obsolète
```

---

## Pièges connus

!!! warning "Les scripts ne doivent pas dépendre du `cd` zoxide"
    Le remplacement n'existe que dans les shells **interactifs**
    (`.bash_env`). Dans un script, `cd motif` échouera normalement — c'est
    voulu : un script doit utiliser des chemins réels.

!!! note "Un dossier jamais visité est inconnu"
    zoxide ne propose que ce qu'il a vu passer. Après une réinstallation,
    la base est vide : les premiers `cd` se font en chemins complets
    (ou via ++alt+c++ de fzf), la magie revient en quelques heures d'usage.

!!! tip "`cd` + ++alt+c++ + `fcd` se complètent"
    zoxide saute vers les dossiers **déjà connus** ; ++alt+c++
    ([fzf](fzf.md)) explore les dossiers **sous le répertoire courant** —
    les deux réflexes couvrent tous les cas.

---

## Références

- [Dépôt zoxide](https://github.com/ajeetdsouza/zoxide)
- `man zoxide`
- Config : `alm_dots/.bash_env`, section « Configuration de zoxide »
