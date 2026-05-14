# Configuration

Le plugin utilise deux tokens personnels stockés de manière sécurisée dans le coffre-fort Eclipse (Equinox Secure Storage) : un token GitLab et un token Jenkins.

---

## Stockage sécurisé Eclipse

!!! success "Aucun fichier en clair"
    Les tokens ne sont **jamais stockés dans un fichier texte**. Ils sont chiffrés dans l'Equinox Secure Storage d'Eclipse, lié au compte utilisateur du système d'exploitation.

---

## GitLab Token

**Raccourci :** `Ctrl+E` — Menu : zDevOps > GitLab Token

### Rôle

Authentifie le plugin auprès de GitLab pour toutes les opérations :

- Appels API REST (`gitlab4j`) : liste des branches, lecture des manifests, création de branches, téléchargement des copybooks
- Opérations JGit : `clone`, `push`, `pull`, `fetch` (via `UsernamePasswordCredentialsProvider`)

### Caractéristiques

| Attribut | Valeur |
|---|---|
| Portée | **Partagé entre tous les toolchains** (dev, rec, frm, prd) |
| Format | Token d'accès personnel GitLab |
| Stockage | Equinox Secure Storage |
| Synchronisation | Met à jour automatiquement le `CredentialsProvider` JGit |

### Comment générer le token GitLab

1. Se connecter à GitLab
2. **User Settings > Access Tokens > Add new token**
3. Droits requis : `read_repository`, `write_repository`, `api`
4. Copier le token (affiché une seule fois)
5. Le coller dans la boîte de dialogue `Ctrl+E`

!!! warning "Validation différée"
    Le plugin ne vérifie pas la validité du token à la saisie. L'erreur apparaît lors de la première opération GitLab (`GitLabAuthenticationException` ou `InvalidTokenException`).

### Initialisation au démarrage

Au démarrage du plugin (`Activator`), le token est récupéré depuis le stockage sécurisé et le `CredentialsProvider` JGit est initialisé. Si aucun token n'est stocké, les opérations Git échoueront.

---

## Jenkins Token

**Raccourci :** `Ctrl+K` — Menu : zDevOps > Jenkins Token

### Rôle

Authentifie le plugin auprès de Jenkins FabCI pour déclencher les pipelines (build, déploiement, audit, promote/clean unitaire).

### Caractéristiques

| Attribut | Valeur |
|---|---|
| Portée | **Spécifique à chaque toolchain** (dev, rec, frm, prd) |
| Format | Token API Jenkins |
| Stockage | Equinox Secure Storage |
| Authentification | HTTP Basic Auth — `Base64("<login>@id.fr.cly:<token>")` |

Le login est déduit automatiquement du compte Windows (`System.getProperty("user.name")`).

### Déclenchement automatique

La boîte de saisie du token Jenkins s'ouvre **automatiquement** (sans passer par `Ctrl+K`) si le token est absent lors d'une tentative de Builder, Déployer, Audit, Promote ou Clean Unitaire.

### Comment générer le token Jenkins

1. Se connecter à l'instance Jenkins FabCI du toolchain cible
2. Cliquer sur son nom d'utilisateur → **Configure**
3. Section **API Token > Add new Token**
4. Copier le token (affiché une seule fois)
5. Le coller dans la boîte de dialogue `Ctrl+K`

!!! warning "Un token par toolchain"
    Si vous changez de toolchain dans `zdevops.ini`, pensez à reconfigurer le token Jenkins correspondant à ce nouvel environnement.

---

## Comparatif des deux tokens

| Critère | GitLab Token | Jenkins Token |
|---|---|---|
| Raccourci | `Ctrl+E` | `Ctrl+K` |
| Portée | Tous les toolchains | Par toolchain |
| Utilisation | API GitLab + JGit | API REST Jenkins |
| Authentification | Token seul | Basic Auth (`login:token` en Base64) |
| Login | Déduit du système | Déduit du système |
| Déclenchement auto | Non | Oui (si absent avant une action Jenkins) |
