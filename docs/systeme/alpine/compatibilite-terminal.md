# Compatibilité des terminaux via SSH

Lorsqu'on se connecte à une machine Alpine Linux en SSH depuis un terminal
moderne, il arrive que des commandes simples comme `nano` ou `htop` affichent
une erreur :

```
Error opening terminal: xterm-kitty.
```

ou encore :

```
Error opening terminal: foot.
```

Ce guide explique pourquoi cette erreur se produit et comment la corriger
définitivement.

---

## Comprendre le problème

### La variable `$TERM`

Chaque terminal émulateur s'identifie auprès des programmes via la variable
d'environnement `$TERM`. Cette variable indique quel type de terminal est
utilisé, ce qui permet aux applications (`nano`, `htop`, `vim`…) de savoir
comment afficher du texte, des couleurs, des curseurs, etc.

Vérifiez la valeur de `$TERM` sur votre machine locale :

```bash
echo $TERM
```

### La base terminfo

Alpine Linux (comme tous les systèmes Unix) maintient une base de données
appelée **terminfo**. Elle contient les descriptions de tous les terminaux
reconnus. Si votre terminal n'y figure pas, les applications ne savent pas
comment lui parler — d'où l'erreur.

```
Votre terminal        Alpine Linux
┌───────────────┐     ┌──────────────────────┐
│ $TERM=        │ SSH │ Cherche "xterm-kitty"│
│ xterm-kitty   │────▶│ dans terminfo…       │
└───────────────┘     │ ❌ Introuvable !     │
                      └──────────────────────┘
```

### Terminaux concernés

Les terminaux modernes qui utilisent leur propre valeur `$TERM` ne sont
généralement pas présents dans la base terminfo d'Alpine par défaut :

| Terminal           | `$TERM` envoyé              | Reconnu par Alpine ?                   |
| ------------------ | --------------------------- | -------------------------------------- |
| **Kitty**          | `xterm-kitty`               | Non                                    |
| **foot**           | `foot`                      | Non                                    |
| **Ghostty**        | `xterm-ghostty`             | Non                                    |
| **WezTerm**        | `wezterm`                   | Non                                    |
| **Alacritty**      | `alacritty`                 | Non (utilise souvent `xterm-256color`) |
| **GNOME Terminal** | `xterm-256color`            | Oui                                    |
| **xterm**          | `xterm` ou `xterm-256color` | Oui                                    |

!!! info "Alacritty est souvent épargné"
La plupart des configurations récentes d'Alacritty utilisent
`xterm-256color` comme valeur de `$TERM`, ce qui est universellement
reconnu.

---

## Solution rapide (temporaire)

Avant de lancer une commande qui échoue, forcez une valeur universellement
reconnue :

```bash
export TERM=xterm-256color
```

Puis lancez votre commande :

```bash
sudo nano /etc/hostname
```

!!! warning "Valable uniquement pour la session en cours"
Cette variable est réinitialisée à la prochaine connexion SSH.
C'est une solution de dépannage, pas une solution permanente.

---

## Solution permanente — installer les définitions terminfo

La meilleure solution consiste à installer sur la VM Alpine la définition
terminfo de votre terminal. Une fois installée, l'erreur disparaît
définitivement.

### Étape 1 — Exporter les définitions depuis la machine hôte

Sur **votre machine locale** (celle avec le terminal), exportez les
définitions :

=== "Kitty"

    ```bash
    infocmp xterm-kitty > xterm-kitty.terminfo
    ```

=== "foot"

    ```bash
    infocmp foot > foot.terminfo
    ```

=== "Ghostty"

    ```bash
    infocmp xterm-ghostty > xterm-ghostty.terminfo
    ```

=== "WezTerm"

    ```bash
    infocmp wezterm > wezterm.terminfo
    ```

=== "Autre terminal"

    Utilisez le nom affiché dans le message d'erreur :

    ```bash
    # Exemple si l'erreur dit "Error opening terminal: mon-terminal"
    infocmp mon-terminal > mon-terminal.terminfo
    ```

!!! note "La commande `infocmp`"
`infocmp` lit la base terminfo locale et exporte la description du
terminal demandé au format texte lisible. Si cette commande échoue,
votre terminal n'est pas défini même sur votre propre machine — cas
rare mais possible.

### Étape 2 — Transférer le fichier vers la VM

Toujours depuis **votre machine locale**, envoyez le fichier sur la VM :

=== "Kitty"

    ```bash
    scp xterm-kitty.terminfo votre-utilisateur@IP-DE-LA-VM:/tmp/
    ```

=== "foot"

    ```bash
    scp foot.terminfo votre-utilisateur@IP-DE-LA-VM:/tmp/
    ```

=== "Ghostty"

    ```bash
    scp xterm-ghostty.terminfo votre-utilisateur@IP-DE-LA-VM:/tmp/
    ```

=== "WezTerm"

    ```bash
    scp wezterm.terminfo votre-utilisateur@IP-DE-LA-VM:/tmp/
    ```

=== "Autre terminal"

    ```bash
    scp mon-terminal.terminfo votre-utilisateur@IP-DE-LA-VM:/tmp/
    ```

### Étape 3 — Installer sur la VM Alpine

Connectez-vous à la VM et exécutez ces commandes :

```bash
# Installer les outils terminfo si nécessaire
sudo apk add ncurses ncurses-terminfo
```

=== "Kitty"

    ```bash
    tic -x /tmp/xterm-kitty.terminfo
    ```

=== "foot"

    ```bash
    tic -x /tmp/foot.terminfo
    ```

=== "Ghostty"

    ```bash
    tic -x /tmp/xterm-ghostty.terminfo
    ```

=== "WezTerm"

    ```bash
    tic -x /tmp/wezterm.terminfo
    ```

=== "Autre terminal"

    ```bash
    tic -x /tmp/mon-terminal.terminfo
    ```

!!! note "La commande `tic`"
`tic` (terminfo compiler) compile le fichier texte `.terminfo` en une
version binaire stockée dans `~/.terminfo/`. L'option `-x` inclut les
extensions non standard utilisées par les terminaux modernes.

### Étape 4 — Vérifier

Déconnectez-vous puis reconnectez-vous en SSH. Testez une commande qui
échouait auparavant :

```bash
nano --version
```

Si elle s'ouvre sans erreur, l'installation est réussie.

??? warning "Avertissement possible lors de `tic`"
Vous pouvez rencontrer ce message :

    ```
    "xterm-kitty.terminfo", line 2, col 22, terminal 'xterm-kitty':
    older tic versions may treat the description field as an alias
    ```

    **Ce n'est pas une erreur** — c'est un simple avertissement. Il
    indique que de très anciennes versions de `tic` pourraient mal
    interpréter un champ de description. Sur Alpine Linux et tout système
    récent, cet avertissement peut être ignoré sans risque.

---

## Solution alternative — forcer `$TERM` à la connexion

Si vous ne souhaitez pas toucher à la VM (par exemple sur une machine que
vous n'administrez pas), vous pouvez forcer la valeur de `$TERM` côté client
dans votre configuration SSH.

Ajoutez ceci dans `~/.ssh/config` sur **votre machine locale** :

```ssh-config
Host ma-vm-alpine
    HostName IP-DE-LA-VM
    User votre-utilisateur
    SetEnv TERM=xterm-256color
```

!!! info "Connexion avec l'alias"
Avec cette configuration, vous pouvez vous connecter via :
`bash
    ssh ma-vm-alpine
    `
au lieu de `ssh votre-utilisateur@IP-DE-LA-VM`.

!!! warning "Nécessite l'accord du serveur"
Pour que `SetEnv` fonctionne, le serveur SSH doit accepter les variables
d'environnement entrantes. Sur Alpine, vérifiez que `/etc/ssh/sshd_config`
contient :
`     AcceptEnv TERM
    `
Si cette ligne est absente, ajoutez-la et redémarrez SSH :
`bash
    sudo rc-service sshd restart
    `

---

## Récapitulatif

| Situation                          | Solution recommandée                              |
| ---------------------------------- | ------------------------------------------------- |
| Dépannage ponctuel                 | `export TERM=xterm-256color` avant la commande    |
| Machine que vous administrez       | Installer les définitions terminfo sur la VM      |
| Machine que vous n'administrez pas | `SetEnv TERM=xterm-256color` dans `~/.ssh/config` |
