# Lazydocker

**Lazydocker** est une interface graphique en mode texte (TUI — *Terminal User
Interface*) pour Docker. Elle permet de visualiser et gérer ses conteneurs,
images, volumes et réseaux depuis le terminal, sans avoir à mémoriser les
commandes Docker.

!!! info "Prérequis"
    - Docker installé et démarré (voir [Docker sur Alpine](docker.md))
    - Votre utilisateur doit être dans le groupe `docker`
    - Accès Internet pour le téléchargement

---

## Installation

Lazydocker n'est pas disponible dans les dépôts `apk` d'Alpine. Il s'installe
via un script qui télécharge le binaire précompilé.

### Via le script officiel

```bash
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | ash
```

!!! note "Pourquoi `ash` et pas `bash` ?"
    Alpine Linux utilise **ash** (Almquist Shell) comme shell par défaut,
    et non bash. Le script d'installation en tient compte. Si vous avez
    installé bash, remplacez `ash` par `bash`.

Le binaire est téléchargé dans `~/.local/bin/lazydocker`.

Vérifiez l'installation :

```bash
~/.local/bin/lazydocker --version
```

### Via téléchargement manuel

Si le script ne fonctionne pas (réseau restreint, proxy, etc.) :

1. Rendez-vous sur la [page des versions GitHub](https://github.com/jesseduffield/lazydocker/releases)
2. Téléchargez l'archive `lazydocker_*_Linux_x86_64.tar.gz`
3. Extrayez et installez :

```bash
# Exemple avec la version 0.24.1
VERSION="0.24.1"
curl -Lo /tmp/lazydocker.tar.gz \
  "https://github.com/jesseduffield/lazydocker/releases/download/v${VERSION}/lazydocker_${VERSION}_Linux_x86_64.tar.gz"

mkdir -p ~/.local/bin
tar -xzf /tmp/lazydocker.tar.gz -C ~/.local/bin lazydocker
chmod +x ~/.local/bin/lazydocker
```

---

## Configuration du PATH et alias

Pour lancer Lazydocker simplement avec `lzd`, ajoutez ces lignes dans
`~/.profile` :

```bash
# Répertoire des binaires personnels
export PATH="$HOME/.local/bin:$PATH"

# Alias court pour Lazydocker
alias lzd='lazydocker'
```

!!! warning "Sur Alpine : `~/.profile`, pas `~/.bashrc`"
    Alpine utilise `ash` qui lit `~/.profile` (shell de connexion) et non
    `~/.bashrc`. Si vous avez installé `bash` et l'utilisez, ajoutez les
    lignes dans `~/.bashrc` à la place.

Appliquez les modifications sans ouvrir une nouvelle session :

```bash
source ~/.profile
```

Vérifiez que la commande est reconnue :

```bash
lzd --version
```

---

## Lancement

```bash
lzd
# ou
lazydocker
```

!!! warning "Docker doit être démarré"
    Si Docker n'est pas actif, Lazydocker affiche une erreur de connexion.
    Démarrez-le d'abord :
    ```bash
    sudo rc-service docker start
    ```

---

## L'interface

L'interface est divisée en deux zones :

```
┌─────────────────┬────────────────────────────────────┐
│                 │                                    │
│   Panneau       │          Panneau de détail         │
│   gauche        │                                    │
│  (navigation)   │  Logs / Stats / Config / Top       │
│                 │                                    │
└─────────────────┴────────────────────────────────────┘
                      Barre d'état (raccourcis)
```

### Panneau gauche — les onglets

Naviguez entre les onglets avec les touches `[` et `]` ou en cliquant :

| Onglet | Contenu |
|---|---|
| **Containers** | Liste de tous les conteneurs (actifs et arrêtés) |
| **Services** | Services Docker Compose du projet courant |
| **Images** | Images Docker téléchargées localement |
| **Volumes** | Volumes persistants |
| **Networks** | Réseaux Docker |

### Panneau droit — les vues

Quand un conteneur est sélectionné, le panneau droit propose plusieurs vues
accessibles avec `Tab` :

| Vue | Contenu |
|---|---|
| **Logs** | Journaux en temps réel du conteneur |
| **Stats** | Utilisation CPU, mémoire, réseau, disque |
| **Config** | Configuration JSON du conteneur |
| **Top** | Processus en cours dans le conteneur |

---

## Navigation et raccourcis clavier

### Déplacements

| Touche | Action |
|---|---|
| `↑` / `↓` ou `k` / `j` | Naviguer dans la liste |
| `Tab` | Passer d'un panneau à l'autre |
| `[` / `]` | Changer d'onglet (Containers, Images, etc.) |
| `PgUp` / `PgDn` | Faire défiler les journaux rapidement |
| `g` | Aller au début des journaux |
| `G` | Aller à la fin des journaux |

### Actions sur les conteneurs

| Touche | Action |
|---|---|
| `Enter` | Sélectionner / afficher les détails |
| `x` | Ouvrir le menu d'actions |
| `s` | Arrêter le conteneur |
| `r` | Redémarrer le conteneur |
| `d` | Supprimer le conteneur |
| `e` | Ouvrir les journaux en plein écran |
| `ctrl+e` | Ouvrir les journaux dans `less` |

### Actions sur les images

| Touche | Action |
|---|---|
| `d` | Supprimer l'image |
| `x` | Menu d'actions (pull, tag, etc.) |

### Général

| Touche | Action |
|---|---|
| `?` | Aide — affiche tous les raccourcis |
| `q` ou `ctrl+c` | Quitter Lazydocker |
| `/` | Filtrer la liste (recherche) |

!!! tip "La touche `x` est votre meilleure alliée"
    En cas de doute sur les actions disponibles, appuyez sur `x`. Un menu
    contextuel liste toutes les opérations possibles pour l'élément sélectionné.

---

## Cas pratiques

### Suivre les journaux d'un conteneur

1. Lancez `lzd`
2. Sélectionnez le conteneur dans la liste avec les flèches
3. Le panneau droit affiche les journaux automatiquement
4. Appuyez sur `Tab` pour basculer sur la vue **Logs** si nécessaire
5. Appuyez sur `G` pour sauter au bas des journaux (temps réel)

### Arrêter ou redémarrer un conteneur

1. Sélectionnez le conteneur
2. Appuyez sur `s` pour l'arrêter (ou `r` pour redémarrer)
3. Confirmez si une demande de confirmation apparaît

### Supprimer les images inutilisées

1. Appuyez sur `]` pour aller dans l'onglet **Images**
2. Sélectionnez une image inutilisée (status `<none>` ou non utilisée)
3. Appuyez sur `d` puis confirmez

### Voir la consommation de ressources

1. Sélectionnez un conteneur actif
2. Appuyez sur `Tab` jusqu'à atteindre la vue **Stats**
3. Vous visualisez CPU, mémoire, réseau et disque en temps réel

---

## Configuration (optionnel)

Lazydocker se configure via le fichier `~/.config/lazydocker/config.yml`.
Il est créé automatiquement au premier lancement.

Exemple de personnalisation :

```yaml
gui:
  # Largeur du panneau gauche (en pourcentage)
  sidePanelWidth: 0.333

logs:
  # Afficher les horodatages dans les journaux
  timestamps: false
  # N'afficher que les journaux des dernières 24h
  since: "24h"
  # Nombre de lignes de journaux à charger
  tail: 200
```

Pour ouvrir et modifier le fichier :

```bash
nano ~/.config/lazydocker/config.yml
```

---

## Mise à jour

Pour mettre à jour Lazydocker, relancez simplement le script d'installation —
il détecte et remplace la version existante :

```bash
curl https://raw.githubusercontent.com/jesseduffield/lazydocker/master/scripts/install_update_linux.sh | ash
```

---

## Désinstallation

```bash
rm ~/.local/bin/lazydocker
rm -rf ~/.config/lazydocker
```

Retirez ensuite la ligne d'alias de `~/.profile` si vous l'avez ajoutée.
