# Starship — invite de commandes cross-shell

[Starship](https://starship.rs) est une invite de commandes universelle
(bash, zsh, fish...) écrite en Rust : elle affiche le contexte pertinent
(dossier, branche Git, version de langage détectée, code de sortie...)
sans configuration lourde, et reste rapide même avec beaucoup de modules
actifs. Version installée : **1.26.0** (upstream, binaire officiel).

---

## Installation

Module dédié du process de post-installation
([alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)) :

```bash
cd ~/alm_tools/postinstall
sudo make starship
```

Le module télécharge et exécute le script officiel `starship.rs`, avec
`STARSHIP_INSTALL_PATH=/usr/local/bin/starship` — pas de paquet APT.

!!! warning "Pas de mise à jour automatique"
    Comme `fzf`, `xan`, `fnm`... starship ne suit pas `apt upgrade`. Pour
    savoir si une nouvelle version est disponible et comment l'installer,
    voir
    [Vérification des mises à jour upstream](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#verification-des-mises-a-jour-upstream)
    (`check_updates.sh`).

---

## Configuration (alm_dots)

Fichier versionné `alm_dots/.config/starship.toml`, stowé vers
`~/.config/starship.toml`. Initialisation dans `.bash_env` :

```bash
if command -v starship &>/dev/null; then
  eval "$(starship init bash)"
fi
```

!!! danger "starship était initialisé deux fois (bug trouvé, corrigé, puis régressé — corrigé définitivement en juillet 2026)"
    `install_starship.sh` ajoutait automatiquement
    `eval "$(starship init $(basename $SHELL))"` dans `.bashrc` pour tous
    les comptes du système — sans savoir que `alm_dots/.bash_env` le fait
    déjà. Résultat : starship s'initialisait deux fois à chaque ouverture
    de shell (impact réel négligeable, ~quelques ms, mais redondant et
    source de confusion — même famille de bug que le doublon
    [fnm](fnm.md), documenté dans sa propre page).

    Un premier correctif (retirer le bloc de `.bashrc` directement) a été
    appliqué début juillet 2026, mais **`.bashrc` n'est pas versionné** :
    la ligne est réapparue peu après, très probablement réinjectée par une
    réinstallation/mise à jour de starship (`sudo make -C
    ~/alm_tools/postinstall starship`), puisque `install_starship.sh` ne
    vérifiait que `.bashrc` lui-même pour décider d'ajouter la ligne, sans
    savoir que `.bash_env` s'en charge déjà.

    Correctif définitif : `install_starship.sh` vérifie désormais aussi
    `~/.bash_env` avant d'écrire dans `.bashrc` — s'il y trouve déjà
    `starship init`, il n'ajoute rien. `.bash_env` reste la seule source
    d'initialisation, de façon durable cette fois. Voir
    [Architecture du postinstall](../../systeme/ubuntu/alm_tools/postinstall/architecture.md)
    pour le détail des deux cas.

### Modules activés qui ne l'étaient pas

Starship désactive certains modules **par défaut**, même quand ils ont un
`symbol` configuré — définir une icône ne suffit pas à afficher le
module. Un audit (juillet 2026) a trouvé quatre réglages inertes dans
`starship.toml`, corrigés en ajoutant `disabled = false` :

| Module | Symbole déjà configuré | Effet une fois activé |
|---|---|---|
| `[status]` | `` | Code de sortie de la dernière commande, **uniquement en cas d'échec** |
| `[memory_usage]` | `󰍛` | Alerte RAM, seulement si l'usage dépasse le seuil par défaut (75 %) |
| `[os]` | 40+ icônes par distribution | Icône de l'OS local — utile surtout en SSH vers d'autres systèmes |
| `[git_commit].tag_symbol` | `  ` | Affichage des tags Git (le module `git_commit` lui-même était actif, seul `tag_disabled` bloquait les tags) |

Vérifié empiriquement (`starship print-config` pour voir la config
**effective**, pas juste ce qui est écrit dans le fichier) : sans
`disabled = false`, ces symboles ne s'affichent jamais, quoi qu'on mette
dans `symbol`.

```console
$ STARSHIP_CONFIG=~/.config/starship.toml starship print-config \
    | grep -A1 "^\[status\]"
[status]
disabled = false
```

### Réglages ajoutés lors de l'audit de juillet 2026

En plus des modules réactivés ci-dessus :

- **`[directory].truncation_symbol = "…/"`** — signale visuellement qu'une
  partie du chemin est masquée. Utile avec `zoxide`, qui saute directement
  dans des arborescences profondes. Piège : `truncate_to_repo` étant actif
  par défaut, ce symbole s'affiche **dès qu'on est dans un repo Git, même
  à sa racine** — techniquement correct (tout ce qu'il y a au-dessus du
  repo, ex. `/home/galan/`, est bien tronqué), mais plus visible qu'on
  pourrait s'y attendre au quotidien.
- **`[directory].repo_root_style = "bold #c6a0f6"`** — met en évidence le
  nom du repo Git dans la même teinte mauve que `active_border_color` de
  `kitty.conf` (cohérence visuelle Catppuccin Macchiato).
- **`[time]` activé** (`time_format = "%R"`, soit `HH:MM`) — affiche
  l'heure courante dans le prompt.

---

## Pièges connus

!!! warning "`right_format` ne fonctionne pas sous Bash sans `ble.sh`"
    Contrairement à zsh/fish, Bash n'a pas de prompt droit natif (pas de
    `RPROMPT`). Le script d'init de starship n'appelle
    `starship prompt --right` (la commande qui produit `right_format`) que
    si `ble.sh` (Bash Line Editor) est attaché à la session — sinon ce
    réglage est silencieusement ignoré, sans erreur ni avertissement.
    `ble.sh` n'est pas installé sur ce poste (évalué puis écarté en
    juillet 2026 : gain jugé trop faible face à la complexité ajoutée sur
    un `.bash_env` déjà riche en hooks). Conséquence pratique : pas de
    `right_format` dans `starship.toml` ici — `$cmd_duration` et `$time`
    restent dans le format principal, à gauche.

!!! warning "Un module configuré n'est pas forcément un module actif"
    Starship n'affiche jamais d'erreur pour un module désactivé avec des
    réglages inutilisés — il ignore silencieusement `symbol`, `format`...
    tant que `disabled = true` (valeur par défaut pour `status`,
    `memory_usage`, `os`, et `tag_disabled` pour les tags Git). Pour
    auditer ce qui est *réellement* actif, comparer avec
    `starship print-config`, pas seulement relire `starship.toml`.

!!! note "Deux init = pas cassé, mais gaspillé"
    Contrairement à [fnm](fnm.md) (qui crée un nouveau dossier
    « multishell » à chaque appel, donc une vraie accumulation de
    fichiers), un second `eval "$(starship init ...)"` réécrit
    proprement le même état — aucune casse fonctionnelle, juste un appel
    processus inutile à chaque ouverture de shell.

---

## Références

- [Documentation officielle](https://starship.rs/config/)
- [Schéma de configuration](https://starship.rs/config-schema.json)
- `starship print-config` — config effective (défauts + overrides)
- `starship explain` — explique ce qui s'affiche dans le prompt actuel
- Config : `alm_dots/.config/starship.toml` · init : `alm_dots/.bash_env`
- Module : `alm_tools/postinstall/modules/cli/install_starship.sh`
