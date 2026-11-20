# Déploiement de production — ENSO Monitor

Procédure de mise en production sur un **VPS Linux** avec **Docker Compose** et **Caddy**.
Le déploiement réel est facultatif pour le projet : cette procédure a été **exécutée intégralement en local** (`DOMAINE=localhost`), preuves en fin de document.

## 1. Architecture cible

```
                         Internet
                            │  80 (redirigé) / 443 HTTPS
                  ┌─────────▼─────────┐
                  │       caddy       │  certificat Let's Encrypt, en-têtes de sécurité,
                  │ frontend statique │  fichiers du frontend, /api/* → api:8000
                  └─────────┬─────────┘
      réseau « interne » (internal: true — aucun accès Internet)
             ┌──────────────┼───────────────────────┐
     ┌───────▼──────┐ ┌─────▼──────┐ ┌──────────────▼───────────┐
     │     api      │ │ migration  │ │ etl (à la demande / cron) │──▶ NOAA (réseau « public »)
     │ FastAPI ×2   │ │ Alembic 1× │ └──────────────┬───────────┘
     └───────┬──────┘ └─────┬──────┘                │
             └──────────────▼───────────────────────┘
                     ┌─────────────┐
                     │ db Postgres │  volume donnees_postgres, aucun port publié
                     └─────────────┘
```

| Service | Image | Rôle | Réseaux | Ports publiés |
|---|---|---|---|---|
| `caddy` | construite (`deploy/caddy/Dockerfile`) : build du frontend + Caddy | point d'entrée unique, HTTPS | public, interne | 80, 443 (TCP/UDP) |
| `api` | `enso-monitor-backend` | API FastAPI (2 workers Uvicorn, utilisateur non-root) | interne | aucun |
| `migration` | `enso-monitor-backend` | `alembic upgrade head` puis arrêt ; l'API attend sa réussite | interne | aucun |
| `etl` | `enso-monitor-backend` | `python -m enso.etl`, lancé à la demande (profil `etl`) | interne, public | aucun |
| `db` | `postgres:17-alpine` | données | interne | aucun |

## 2. Hébergement proposé (sans achat)

| Élément | Choix | Justification |
|---|---|---|
| Fournisseur | VPS Hetzner Cloud (ex. CX22) ou équivalent | prix bas, centres de données dans l'UE (RGPD), IPv4/IPv6 |
| Dimensionnement | **2 vCPU, 4 Go RAM, 40 Go SSD** | PostgreSQL (~300 Mo), API 2 workers (~150 Mo), Caddy (~30 Mo), build Docker ponctuel (~1 Go) ; données ONI < 1 Mo |
| Système | Ubuntu Server 24.04 LTS | support long terme, Docker officiel disponible |
| Domaine | sous-domaine (ex. `enso.exemple.fr`) | enregistrement DNS A/AAAA vers l'IP du VPS |

## 3. Préparation du serveur (une seule fois)

```bash
# Connexion initiale, puis création d'un utilisateur dédié
ssh root@IP_DU_VPS
adduser deploiement && usermod -aG sudo deploiement

# SSH : clé uniquement, pas de connexion root (dans /etc/ssh/sshd_config)
#   PermitRootLogin no
#   PasswordAuthentication no
systemctl restart ssh

# Pare-feu : uniquement SSH, HTTP et HTTPS
ufw default deny incoming && ufw default allow outgoing
ufw allow OpenSSH && ufw allow 80/tcp && ufw allow 443/tcp && ufw allow 443/udp
ufw enable

# Mises à jour de sécurité automatiques
apt install -y unattended-upgrades && dpkg-reconfigure -plow unattended-upgrades

# Docker Engine + plugin Compose (dépôt officiel Docker)
curl -fsSL https://get.docker.com | sh
usermod -aG docker deploiement
```

> Docker publie ses ports en contournant `ufw` : c'est pourquoi **seul Caddy publie des ports** ; la base et l'API ne sont jamais exposées.

## 4. Premier déploiement

```bash
git clone https://github.com/Pharosi/projet-enso-monitor.git && cd projet-enso-monitor
git checkout v1.0.0                    # toujours déployer une version étiquetée

cd deploy
cp .env.example .env && chmod 600 .env
# Éditer .env : DOMAINE, EMAIL_ACME, et un mot de passe généré par :
openssl rand -hex 24

docker compose up -d --build           # construit les images, applique les migrations, démarre
docker compose run --rm etl            # premier import des données NOAA
docker compose ps                      # api « healthy », caddy « running »
```

Caddy obtient le certificat HTTPS automatiquement au premier accès (le DNS doit déjà pointer vers le serveur).

## 5. Configuration et secrets

| Variable | Où | Rôle |
|---|---|---|
| `DOMAINE`, `EMAIL_ACME` | `deploy/.env` | nom de domaine servi par Caddy, contact Let's Encrypt |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | `deploy/.env` | identifiants de la base |
| `URL_BASE_DE_DONNEES`, `ORIGINES_CORS` | construites dans `compose.yaml` | lues par l'API et l'ETL |

- `.env` n'est **jamais versionné** (`.gitignore`), droits `600` (lisible par son seul propriétaire).
- Le mot de passe est hexadécimal car il est inséré dans une URL de connexion.

## 6. Tâches planifiées (cron de l'utilisateur `deploiement`)

```cron
# Import NOAA : la NOAA publie l'ONI vers le 5 de chaque mois → import le 6 à 6 h
0 6 6 * *  cd ~/projet-enso-monitor/deploy && docker compose run --rm etl >> etl.log 2>&1
# Sauvegarde de la base chaque nuit à 3 h (14 jours conservés)
0 3 * * *  ~/projet-enso-monitor/deploy/sauvegarder.sh >> sauvegardes.log 2>&1
```

## 7. Sauvegardes et restauration

- `./sauvegarder.sh` : `pg_dump` au format compressé dans `deploy/sauvegardes/`, rotation à 14 jours.
- **Copie hors du serveur** (une sauvegarde sur la même machine ne protège pas d'une panne disque) :
  ```bash
  rsync -a ~/projet-enso-monitor/deploy/sauvegardes/ sauvegarde@autre-serveur:enso/
  ```
- `./restaurer.sh sauvegardes/enso_AAAA-MM-JJ_HHMM.dump` : arrête l'API, restaure (`pg_restore --clean`), redémarre l'API.
- Les données ONI sont aussi **reconstructibles** depuis la NOAA (`docker compose run --rm etl`) ; la sauvegarde protège surtout l'**historique des imports** (traçabilité).
- Volume `caddy_donnees` : contient les certificats, à ne pas supprimer (limites de fréquence de Let's Encrypt).

## 8. Mise à jour et retour arrière

```bash
cd ~/projet-enso-monitor && git fetch --tags
./deploy/sauvegarder.sh                       # toujours sauvegarder avant
git checkout v1.1.0                           # nouvelle version étiquetée
cd deploy && docker compose up -d --build     # migrations appliquées automatiquement
```

**Retour arrière** : `git checkout v1.0.0 && docker compose up -d --build`. Si la nouvelle version contenait une migration de schéma : `docker compose run --rm migration alembic downgrade -1` avant de revenir, ou restauration de la sauvegarde faite juste avant la mise à jour.

## 9. Journalisation, supervision et pannes

| Besoin | Moyen |
|---|---|
| Journaux | `docker compose logs -f api` / `caddy` (accès au format JSON) ; ETL dans `etl.log` |
| État des services | `docker compose ps` : contrôles de santé `db` (`pg_isready`) et `api` (`/api/v1/sante`) |
| Supervision externe | sonde HTTP toutes les 5 min sur `https://DOMAINE/api/v1/sante` (ex. Uptime Kuma, UptimeRobot) : **503** si la base est indisponible |
| Redémarrage | `restart: unless-stopped` : un service qui plante redémarre seul, y compris après un redémarrage du serveur |

| Panne | Diagnostic | Action |
|---|---|---|
| Site inaccessible | `docker compose ps`, `logs caddy` | vérifier DNS, pare-feu, certificat |
| `/api/v1/sante` renvoie 503 | `logs db` | redémarrer `db`, vérifier l'espace disque |
| Import échoué | table `imports` (`statut = echoue`, `message_erreur`), `etl.log` | NOAA indisponible : relancer plus tard (les données existantes restent servies) |
| Données corrompues | — | `./restaurer.sh` avec la dernière sauvegarde |

## 10. Capacité et limites

- **Charge** : ~900 lignes, réponses de quelques Ko ; un VPS 2 vCPU sert sans difficulté plusieurs centaines de requêtes par seconde pour ce volume.
- **Point unique de défaillance** : un seul serveur. Une panne matérielle interrompt le service jusqu'à la restauration (≈ 30 min avec la procédure ci-dessus).
- **Restauration** : coupure de l'API de quelques secondes.
- **Pistes simples d'optimisation** : en-têtes de cache sur `/api/v1/observations` (données mensuelles), découpage du JavaScript du graphique (*code splitting*), limitation du débit par IP au niveau de Caddy, réplication PostgreSQL ou base managée si le besoin de disponibilité augmente.

## 11. Démonstration locale (preuves)

```bash
cd deploy && cp .env.example .env    # DOMAINE=localhost, mot de passe généré
docker compose up -d --build && docker compose run --rm etl
curl -k https://localhost/api/v1/sante
```

Résultats obtenus le 20/11/2026 :

| Vérification | Résultat |
|---|---|
| Migration au démarrage | `Running upgrade -> 0001` puis arrêt du conteneur |
| Import NOAA via Docker | 921 lues, 921 insérées |
| `http://localhost/` | `308` → `https://localhost/` |
| `https://localhost/api/v1/sante` | `200 {"statut":"ok","base_de_donnees":"ok"}` |
| Frontend et route inconnue | `200` (fichiers statiques, repli sur `index.html`) |
| En-têtes | HSTS, CSP, `nosniff`, `Referrer-Policy`, en-tête `Server` retiré |
| Accès Internet depuis l'API | **bloqué** (réseau interne) |
| Port PostgreSQL publié | aucun |
| Utilisateur du processus API | `enso` (non-root) |
| Sauvegarde → suppression de 600 lignes → restauration | 921 → 321 → **921** |

En local, Caddy signe lui-même le certificat de `localhost` : le navigateur affiche un avertissement (ou `docker compose exec caddy caddy trust` pour l'approuver). En production, le certificat est délivré par Let's Encrypt.
