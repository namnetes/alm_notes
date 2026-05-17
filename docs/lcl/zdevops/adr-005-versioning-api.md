# ADR-005 — Versioning de l'API : préfixe de chemin `/api/v1/`

!!! abstract "Qu'est-ce qu'un ADR ?"
    Un **ADR** (Architecture Decision Record) documente une décision technique :
    pourquoi elle a été prise, quelles alternatives ont été écartées, et dans quelles
    conditions elle devra être réexaminée. Voir [ADR-001](adr-001-next-artifact-number.md)
    pour la définition complète.

## Statut

**Accepté — Décision définitive**

---

## Contexte

L'API zDevOps sera consommée par plusieurs clients : une CLI, une extension VS Code,
potentiellement une extension Zed. Ces clients sont développés et déployés
indépendamment les uns des autres.

Sans versioning explicite, tout changement d'endpoint (renommage, modification du
contrat JSON) casse tous les clients simultanément, sans période de transition.

### Trois stratégies de versioning existent

| Stratégie | Exemple |
|---|---|
| Préfixe de chemin URL | `GET /api/v1/evolutions` |
| Header HTTP personnalisé | `Accept: application/vnd.zdevops.v1+json` |
| Paramètre de requête | `GET /evolutions?version=1` |

---

## Décision

**L'API utilise le préfixe de chemin `/api/v1/` pour toutes ses routes.**

```python
router = APIRouter(prefix="/api/v1", tags=["evolutions"])

@router.post("/evolutions", status_code=201)
async def create_evolution(...): ...

@router.get("/workspaces/status")
async def get_workspace_status(...): ...
```

Toutes les routes exposées :

```
POST   /api/v1/evolutions
GET    /api/v1/workspaces/status
POST   /api/v1/config/gitlab-token
GET    /api/v1/config/gitlab-token
DELETE /api/v1/config/gitlab-token
POST   /api/v1/config/jenkins-token/{toolchain}
GET    /api/v1/config/jenkins-token/{toolchain}
DELETE /api/v1/config/jenkins-token/{toolchain}
```

Routes hors versioning (infrastructure, pas métier) :

```
GET  /health     ← health check
GET  /docs       ← Swagger UI (FastAPI natif)
GET  /openapi.json
```

---

## Raisons du choix

**1. Visibilité maximale**

La version est visible dans l'URL, dans les logs, dans les captures réseau, dans
la documentation. Aucun outil intermédiaire (proxy, navigateur, `curl`) n'a besoin
de connaître les headers HTTP pour router correctement.

**2. Compatibilité universelle**

Un appel `curl http://localhost:8001/api/v1/evolutions` fonctionne sans option
supplémentaire. Les headers personnalisés nécessitent `-H "Accept: ..."` — friction
inutile pour les développeurs et les scripts de diagnostic.

**3. Coexistence de versions**

Quand v2 sera nécessaire, les deux versions coexistent sans conflit :

```
/api/v1/evolutions  ← clients existants non migrés
/api/v2/evolutions  ← nouveaux clients
```

FastAPI gère nativement plusieurs routeurs avec des préfixes différents :

```python
app.include_router(v1_router, prefix="/api/v1")
app.include_router(v2_router, prefix="/api/v2")
```

**4. Préfixe `/api/` : séparation claire**

Le préfixe `/api/` distingue les routes métier des endpoints d'infrastructure
(`/health`, `/docs`, `/metrics`). Il facilite aussi la configuration des proxies
et pare-feux qui peuvent filtrer ou router `/api/*` distinctement.

---

## Alternatives écartées

### Header HTTP `Accept` (versioning par contenu)

```http
GET /evolutions HTTP/1.1
Accept: application/vnd.zdevops.v1+json
```

**Pourquoi écarté :**
- Invisible dans les logs applicatifs standard (qui ne loggent que l'URL)
- Nécessite une configuration explicite dans tous les clients HTTP
- La documentation Swagger ne supporte pas nativement le versioning par header
- Plus complexe à tester (`curl` requiert `-H` explicite)

### Paramètre de requête `?version=`

```
GET /evolutions?version=1
```

**Pourquoi écarté :**
- Non standard — les paramètres de requête décrivent des filtres sur les
  ressources, pas la version du contrat
- Pollue les URLs de toutes les requêtes
- Risque d'oubli : une requête sans `?version=` ne sait pas quelle version utiliser

---

## Stratégie de dépréciation

Quand une V2 sera nécessaire :

1. **Déployer V2 en parallèle** de V1 — les deux routes coexistent
2. **Loguer un header de dépréciation** sur les réponses V1 :
   `Deprecation: true` + `Sunset: <date>`
3. **Période de transition** : V1 maintenue pendant la migration des clients
4. **Retirer V1** une fois tous les clients migrés

```python
# Middleware de dépréciation V1 (exemple pour le futur)
@app.middleware("http")
async def deprecation_header(request: Request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/api/v1/"):
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "2027-01-01"
    return response
```

---

## Conditions de révision

Cette décision est **définitive pour le schéma de versioning**. Elle sera complétée
(pas remplacée) lors de l'introduction d'une V2 :

1. Un changement **cassant du contrat** d'un endpoint existant nécessite une V2
2. Un **ajout d'endpoint** ne nécessite pas de nouvelle version (rétro-compatible)
3. Un **ajout de champ optionnel** dans une réponse ne nécessite pas de nouvelle version

---

## Liens

- [Architecture générale](architecture-generale.md)
- [ADR-001 — next_artifact_number](adr-001-next-artifact-number.md)
