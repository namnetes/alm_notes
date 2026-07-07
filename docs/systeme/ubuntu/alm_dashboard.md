# alm_dashboard

`alm_dashboard` est le hub personnel de favoris web : un dashboard
**Homer** servi en local par Docker. Il remplace les marque-pages du
navigateur — c'est cette page qui sert de démarrage à Brave et
s'ouvre sur chaque nouvel onglet (voir
[Sécurité — Brave](../../securite/brave/reinstallation.md)), plutôt
que de dépendre du profil navigateur.

**Dépôt :** [github.com/namnetes/alm_dashboard](https://github.com/namnetes/alm_dashboard)

## Démarrer le dashboard

```bash
cd ~/alm_dashboard
make homer-start
```

!!! info "Dépendance Docker"
    Nécessite le groupe `docker` actif dans la session (voir
    [alm_tools — postinstall, module docker](alm_tools/postinstall/architecture.md#docker-ajoute-lutilisateur-au-groupe)).

## Procédure complète

Installation, prérequis, vérifications, icône dock GNOME, Ulauncher…
tout vit **dans le dépôt lui-même**, pas ici :

```bash
cd ~/alm_dashboard
make docs
```

## À retenir : `homer-stop` supprime, `homer-restart` conserve

| Commande | Effet sur le conteneur |
|---|---|
| `make homer-stop` puis `make homer-start` | **Supprime** le conteneur puis le recrée — nécessaire si le chemin du volume a changé |
| `make homer-restart` | Redémarre le conteneur **existant** sans le recréer — plus rapide pour appliquer un changement de `config.yml` |

## Docker : `systemctl enable` déjà automatique

`alm_dashboard/docs/setup.md` recommande `sudo systemctl enable docker`.
En pratique, le paquet `docker-ce` (installé par `alm_tools/postinstall`)
active déjà ce service au boot via son propre script d'installation —
ce n'est pas une étape manuelle à rejouer, juste une précaution
redondante documentée côté `alm_dashboard`.

---

## Références

- [Documentation Homer](https://github.com/bastienwirtz/homer)
