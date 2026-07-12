# Runbook — Tester le postinstall avec isoforge

Procédure pas à pas pour valider `sudo make all` de bout en bout sur une VM
Ubuntu Desktop jetable, sans risquer le poste réel. C'est la méthodologie
suivie lors de l'[audit d'intégration du
2026-07-12](architecture.md#audit-dintegration-complet-2026-07-12-methodologie-et-5-bugs-trouves)
(5 bugs trouvés et corrigés), formalisée ici comme procédure autonome pour
la prochaine fois. Outil utilisé : [isoforge](../outils/isoforge.md).

---

## Quand l'utiliser

- Une nouvelle version d'Ubuntu Desktop sort (LTS suivante, ou point
  release majeur du support actuel)
- Doute sur une régression après avoir modifié un module postinstall
- Ajout d'un nouveau module au Makefile
- Avant de fusionner un correctif qui touche plusieurs modules à la fois
  (comme le 2026-07-12)

!!! tip "Durée à prévoir"
    Cycle complet : ~30 à 45 minutes (autoinstall Ubuntu Desktop ~10 min +
    `sudo make all` ~15 à 20 min selon la bande passante et les paquets déjà
    en cache APT). Lancez-le en tâche de fond et revenez-y plutôt que de
    rester devant l'écran.

---

## Prérequis

- [isoforge installé](../outils/isoforge.md#installation)
- Connexion internet active (l'ISO Ubuntu Desktop fait ~6 Go si elle n'est
  pas déjà en cache local — `isoforge base status` pour vérifier)

---

## Étape 1 — Créer la VM de test

```bash
isoforge create postinstall-test --user galan --disk 40
```

!!! warning "Toujours `--disk 40`, jamais la valeur par défaut"
    Le disque par défaut (25G) s'est rempli lors de l'audit du 2026-07-12
    — Docker, Steam, VSCode, la suite Proton et les polices suffisent à le
    saturer avant la fin du cycle (`E: You don't have enough free space in
    /var/cache/apt/archives/`). Ce n'est pas une cause probable, c'est du
    vécu : toujours partir de 40G pour un test `sudo make all` complet.

Ajoutez `--autologin` si le test doit couvrir GSConnect ou tout autre
contrôle `session-checks` — l'activation de ces contrôles exige une vraie
session GNOME (voir [Étape 6](#gsconnect-necessite-un-vrai-reboot)) :

```bash
isoforge create postinstall-test --user galan --disk 40 --autologin
```

Notez l'IP et le mot de passe console affichés en fin de commande — vous en
aurez besoin pour les commandes `sudo` suivantes.

---

## Étape 2 — Transférer le dépôt local

```bash
rsync -az -e "ssh -i ~/.ssh/vm-automation_ed25519 -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" \
  ~/alm_tools/ galan@<IP_DE_LA_VM>:~/alm_tools/
```

!!! info "Pourquoi le dépôt local, pas `git clone` depuis origin"
    Décision méthodologique tranchée le 2026-07-12 : `rsync` transfère
    l'état **réellement présent sur ce poste**, y compris des commits pas
    encore poussés vers `origin`. C'est ce qu'on veut tester — l'état du
    dépôt tel qu'il existe maintenant, pas une version potentiellement en
    retard sur GitHub. Si vous voulez explicitement tester ce qui est
    publié (ex. avant de recommander cette version à quelqu'un d'autre),
    utilisez `git clone` à la place — mais ce n'est pas le cas par défaut.

---

## Étape 3 — Installer `make`

```bash
ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM>
sudo apt-get update
sudo apt-get install -y make
```

Rappel : `make` est absent par défaut d'une Ubuntu Desktop fraîche —
c'est un [prérequis documenté](deboguer.md#erreurs-frequentes), pas un bug
de ce dépôt. C'est le seul geste manuel légitime avant de cloner/transférer
le dépôt et de lancer `sudo make all`.

---

## Étape 4 — Snapshot pristine

Avant tout postinstall, immédiatement après le transfert du dépôt :

```bash
isoforge snapshot create postinstall-test pristine
```

Ce point de retour sert à l'[étape 8](#etape-8-revert-et-reproductibilite)
— revenir ici pour rejouer le cycle depuis zéro sans reconstruire la VM.

!!! tip "Test interrompu (pause, panne) ? Retrouvez où vous en étiez"
    ```bash
    isoforge snapshot list postinstall-test
    ```

    Si `pristine` est le seul snapshot listé, le cycle n'a pas encore
    commencé ou a échoué avant d'en créer d'autres. Rien n'empêche de créer
    des snapshots intermédiaires à vos propres points de contrôle (avant
    l'étape 7, par exemple) si un test s'annonce long ou risqué.

---

## Étape 5 — Lancer le cycle complet

```bash
cd ~/alm_tools/postinstall
sudo make all 2>&1 | tee /tmp/postinstall-test.log
```

!!! warning "CLI Claude Code : second prérequis manuel légitime"
    L'étape 18 du pipeline (`claude-terminal`) **vérifie** la présence de
    `claude`, elle ne l'installe jamais — voir l'encadré en tête de
    [Post-installation](post-installation.md). Sur une VM authentiquement
    neuve, `sudo make all` s'arrêtera net à cette étape avec :

    ```
    [ERROR] CLI 'claude' introuvable. Installez-la : curl -fsSL https://claude.ai/install.sh | bash
    ```

    Ce n'est **pas** un bug à investiguer — installez la CLI et relancez :

    ```bash
    curl -fsSL https://claude.ai/install.sh | bash
    sudo make all 2>&1 | tee -a /tmp/postinstall-test.log
    ```

!!! danger "Si le cycle s'arrête ailleurs — ne corrigez rien à la volée"
    Notez précisément **la cible** (la ligne `▶  <cible>` juste avant
    l'erreur) et **le message d'erreur exact**. Ajoutez l'entrée dans
    `postinstall/BACKLOG.md` avant toute chose — c'est la leçon retenue du
    2026-07-12 : corriger en plein test mélange diagnostic et correctif, et
    complique la question de savoir si le bug est reproductible. Une fois
    documenté, décidez au cas par cas : contourner manuellement pour
    continuer le test du reste du cycle (comme pour `proton-mail`/
    `proton-pass` cette fois-là), ou arrêter le test ici et corriger
    d'abord.

!!! danger "Un correctif se valide sur une VM fraîche, jamais sur la VM qui a servi à le trouver"
    Une fois le bug corrigé dans le code, ne vous contentez **pas** de
    contourner et continuer sur la VM actuelle pour déclarer le test
    réussi — elle porte déjà l'état du contournement manuel, pas celui du
    vrai correctif. Pattern suivi le 2026-07-12 pour chacun des 5 bugs
    trouvés : VM de découverte (celle-ci) → correctif écrit → **nouvelle**
    VM, créée depuis zéro (retour à l'[étape 1](#etape-1-creer-la-vm-de-test))
    → cycle rejoué avec le correctif en place, sans aucun contournement
    manuel cette fois. Seul ce second cycle, sur VM neuve, constitue une
    preuve que le correctif fonctionne — pas la poursuite du test initial.

---

## Étape 6 — Vérifications spécifiques

### zbar-tools

```bash
zbarimg --version
```

Doit afficher un numéro de version (ex. `0.23.93`) sans erreur.

### ufw

```bash
sudo ufw show added
```

Doit lister `ufw allow 1716/tcp` et `ufw allow 1716/udp` (règles GSConnect).
Normal que `sudo ufw status` affiche `inactive` — ufw n'est jamais activé
par ce dépôt, voir [Packages et dépôts](packages-et-depots.md).

### GSConnect (nécessite un vrai reboot)

L'activation de l'extension ne se finalise qu'au login GNOME suivant (voir
[session-checks](session-checks.md#le-controle-20-gsconnect)) — une session
SSH ne suffit pas, il faut un vrai redémarrage avec `--autologin`.

```bash
ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM> "sudo reboot"
```

Attendez que SSH revienne, puis que `gnome-shell` tourne réellement (pas
seulement que la VM ait redémarré) :

```bash
# Répéter jusqu'à obtenir un PID
ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM> "pgrep -u galan gnome-shell"
```

!!! note "Contournement propre à ce contexte de test — pas une étape normale"
    Sur une vraie machine, avec quelqu'un physiquement devant l'écran, la
    boîte de dialogue du premier contrôle `session-checks`
    (`10-nautilus-terminal`) se résout normalement : l'utilisateur clique
    Oui ou Non, et les contrôles suivants s'enchaînent. Ici, personne n'est
    présent pour cliquer — la boîte reste ouverte **indéfiniment** et
    **bloque** tous les contrôles suivants, dont `20-gsconnect`. Ce n'est
    pas un bug de `session-checks` à corriger, c'est une conséquence
    directe du test automatisé sans utilisateur : on simule un refus en
    tuant le processus `zenity` (conséquence identique à cliquer Non — voir
    le code de `10-nautilus-terminal` dans
    [session-checks](session-checks.md#le-controle-10-nautilus-terminal)) :

    ```bash
    ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM> \
      "pkill -f 'zenity --question.*Extension Nautilus manquante'"
    ```

Puis vérifiez, avec preuve à chaque niveau :

```bash
# Le journal du framework
ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM> \
  "journalctl -t session-checks --no-pager"
# Doit se terminer par : "20-gsconnect : activé (port 1716 en écoute)"
#                        "Tous les contrôles ont réussi."

# Le port réellement en écoute (pas seulement le journal qui le dit)
ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM> "ss -tuln | grep 1716"

# L'état de l'extension côté GNOME Shell
ssh -i ~/.ssh/vm-automation_ed25519 galan@<IP_DE_LA_VM> \
  "gnome-extensions info gsconnect@andyholmes.github.io" | grep -E 'Enabled|State'
# Attendu : Enabled: Yes / State: ACTIVE
```

Les trois preuves doivent concorder — voir
[Dépannage GSConnect](../../../../outils/gsconnect.md#depannage) si l'une
d'elles manque.

---

## Étape 7 — Test d'idempotence

Sans revert, relancer le cycle complet tel quel :

```bash
sudo make all 2>&1 | tee /tmp/postinstall-test-idempotence.log
```

Vérifiez dans le log :

- Chaque cible déjà installée affiche `[STATUT] ... déjà installé` — aucun
  téléchargement relancé
- `sudo ufw show added` retourne toujours **exactement** les mêmes règles
  qu'à l'étape 6, sans doublon (`ufw` dédoublonne nativement une règle
  identique, mais vérifiez quand même)

---

## Étape 8 — Revert et reproductibilité

```bash
isoforge snapshot revert postinstall-test pristine
```

Puis rejouez les étapes 3 à 6 (réinstaller `make`, relancer `sudo make
all`, gérer `claude` comme à l'étape 5) **depuis cet état pristine**.
Objectif : confirmer que chaque bug rencontré à la première passe (s'il y
en a) se reproduit à l'identique — pas un artefact ponctuel de la VM — et
que le cycle final aboutit au même résultat que la première fois.

---

## Étape 9 — Nettoyage

```bash
isoforge delete postinstall-test
```

---

## Référence rapide

| Besoin | Commande |
|--------|----------|
| Créer la VM (40G, avec GSConnect) | `isoforge create <nom> --user <user> --disk 40 --autologin` |
| Transférer le dépôt local | `rsync -az -e "ssh -i ~/.ssh/vm-automation_ed25519 ..." ~/alm_tools/ galan@<IP>:~/alm_tools/` |
| Snapshot pristine | `isoforge snapshot create <nom> pristine` |
| Lister les snapshots (reprise après pause/panne) | `isoforge snapshot list <nom>` |
| Lancer le cycle | `sudo make all 2>&1 \| tee /tmp/postinstall-test.log` |
| Vérifier zbar-tools | `zbarimg --version` |
| Vérifier ufw | `sudo ufw show added` |
| Débloquer le zenity bloquant | `pkill -f 'zenity --question.*Extension Nautilus manquante'` |
| Vérifier GSConnect (journal) | `journalctl -t session-checks --no-pager` |
| Vérifier GSConnect (port) | `ss -tuln \| grep 1716` |
| Vérifier GSConnect (extension) | `gnome-extensions info gsconnect@andyholmes.github.io` |
| Revenir au pristine | `isoforge snapshot revert <nom> pristine` |
| Nettoyer | `isoforge delete <nom>` |

**En cas de bug trouvé** : documenter dans
[`postinstall/BACKLOG.md`](https://github.com/namnetes/alm_tools/blob/main/postinstall/BACKLOG.md)
avant de corriger — voir l'encadré de l'[étape 5](#etape-5-lancer-le-cycle-complet).
