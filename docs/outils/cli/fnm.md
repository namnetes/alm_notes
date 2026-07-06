# fnm — gestionnaire de versions Node.js

[fnm](https://github.com/Schniz/fnm) (*Fast Node Manager*) installe et
fait cohabiter plusieurs versions de Node.js, avec **bascule automatique
par répertoire** : entrer dans un projet contenant un `.nvmrc`,
`.node-version` ou `package.json` sélectionne la bonne version sans y
penser. Écrit en Rust — le shell démarre vite, contrairement à nvm.
Versions installées : **fnm 1.38.1**, Node **v24.18.0** (LTS, juillet 2026).

---

## Installation

Module dédié du process de post-installation
([alm_tools/postinstall](../../systeme/ubuntu/alm_tools/postinstall/index.md)) :

```bash
cd ~/alm_tools/postinstall
sudo make fnm          # fnm seul
sudo make node         # + installe la LTS et la définit par défaut
```

Le module utilise l'installeur officiel puis **restaure le `~/.bashrc`**
que celui-ci modifie sans demander — l'initialisation est du ressort de
`.bash_env` (versionné), pas d'un ajout sauvage.

fnm vit dans `~/.local/share/fnm/` (binaire + versions Node téléchargées).

---

## Configuration (alm_dots)

Bloc dans `alm_dots/.bash_env`, gardé par `[ -x "$FNM_PATH/fnm" ]` :

```bash
FNM_PATH="$HOME/.local/share/fnm"
if [ -x "$FNM_PATH/fnm" ]; then
  export PATH="$FNM_PATH:$PATH"
  eval "$(fnm env --use-on-cd)"           # bascule auto au cd
  eval "$(fnm completions --shell bash)"  # complétion des sous-commandes
  # + contrôle LTS quotidien (voir plus bas)
fi
```

!!! danger "L'ordre compte : fnm doit s'initialiser APRÈS zoxide"
    `fnm env --use-on-cd` pose un `alias cd=__fnmcd` ;
    [zoxide](zoxide.md) (`init --cmd cd`) définit une **fonction** `cd`
    et supprime tout alias existant. Si fnm passe en premier, zoxide
    **écrase silencieusement son hook** : plus de bascule de version au
    `cd` (bug réel, corrigé en juillet 2026 en déplaçant le bloc fnm après
    le bloc zoxide dans `.bash_env`).

    Dans le bon ordre, les deux s'enchaînent : `cd` → alias fnm → `\cd` →
    fonction zoxide (saut par motif) → détection `.nvmrc`. Vérifié :

    ```console
    $ type cd
    cd est un alias vers « __fnmcd »
    $ cd /tmp && cd notes && pwd    # saut zoxide à travers l'alias fnm
    /home/galan/alm_notes
    ```

### Contrôle de fraîcheur — fnm lui-même et la LTS Node

Depuis juillet 2026, ce contrôle n'est plus un bloc dédié dans
`.bash_env` : il est porté par
[`check_updates.sh`](../../systeme/ubuntu/alm_tools/postinstall/post-installation.md#verification-des-mises-a-jour-upstream),
un script partagé qui vérifie **tous** les outils upstream du poste
(fzf, xan, starship, fnm, uv, rclone, kitty), pas seulement fnm. La
LTS Node active reste vérifiée via `fnm ls-remote --lts`, comme avant.

```text
⚠ Outils upstream avec une mise à jour disponible :
  fnm        1.38.1     -> 1.39.0      rm -rf ~/.local/share/fnm ~/.local/bin/fnm && sudo make -C ~/alm_tools/postinstall fnm
  node(lts)  v24.17.0   -> v24.18.0    fnm install --lts && fnm default lts-latest
```

!!! info "Toujours un seul appel réseau par jour, jamais bloquant"
    Même principe que l'ancien bloc dédié : fichier témoin
    (`~/.cache/alm-tools-update-check`, TTL 24 h) et vérification en
    tâche de fond. Le chemin appelé à chaque shell ne fait qu'un `cat`
    d'un fichier de cache — jamais de réseau au démarrage, même hors
    ligne.

!!! warning "fnm était initialisé deux fois (bug trouvé et corrigé en juillet 2026)"
    Un audit a trouvé un second `eval "$(fnm env)"` (sans `--use-on-cd`)
    directement dans `~/.bashrc`, en plus de celui de `.bash_env` — malgré
    la protection décrite dans
    [Architecture](../../systeme/ubuntu/alm_tools/postinstall/architecture.md).
    Conséquence : ~92 dossiers orphelins accumulés dans
    `/run/user/<uid>/fnm_multishells/` (un par appel `fnm env`). Le hook
    `cd` restait correct (le second appel ne le redéfinit pas), mais
    c'était une accumulation inutile de fichiers à chaque shell. Corrigé
    en retirant le bloc de `.bashrc` — `.bash_env` reste la seule source.

---

## Exemples d'usage

### Gérer les versions

```console
$ fnm ls                        # versions installées
* v24.18.0 lts-latest, default
* system
$ fnm ls-remote --lts | tail -3 # dernières LTS disponibles
$ fnm install --lts             # installer la LTS la plus récente
$ fnm default lts-latest        # en faire la version par défaut
$ fnm current                   # version active dans CE shell
```

### Épingler une version par projet

```console
$ cd ~/workspaces/mon-extension-vscode
$ node --version > .node-version    # épingler la version courante
$ cd /tmp && cd -                   # au retour dans le projet :
$ fnm current                       # → la version épinglée, sans rien taper
```

`fnm use` lit aussi `"engines": { "node": ... }` dans `package.json`.

### Essayer une version sans changer le shell

```console
$ fnm exec --using=v22 node --version    # exécution ponctuelle
v22.21.0
```

---

## Pièges connus

!!! warning "Node n'existe pas dans les scripts non interactifs"
    `fnm env` n'est évalué que dans `.bash_env` (shells interactifs). Un
    cron, un service systemd ou un script `#!/bin/bash` ne voient **pas**
    `node`. Solutions :

    ```bash
    ~/.local/share/fnm/fnm exec --using=default node script.js
    # ou dans le script :
    eval "$(~/.local/share/fnm/fnm env)"
    ```

!!! note "Le PATH contient un « multishell » éphémère"
    `which node` → `/run/user/1000/fnm_multishells/<id>/bin/node` : chaque
    shell a son lien, c'est ce qui permet des versions différentes par
    terminal. Ne jamais coder ce chemin en dur — il change à chaque session.

---

## Références

- [Dépôt fnm](https://github.com/Schniz/fnm)
- `fnm --help`, `fnm <commande> --help`
- Init : `alm_dots/.bash_env`, bloc « Configuration de fnm » (après zoxide)
- Module : `alm_tools/postinstall/modules/cli/install_fnm.sh`
