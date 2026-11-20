# ENSO Monitor

Plateforme d'analyse des épisodes **El Niño** et **La Niña** à partir de l'indice océanique **ONI** publié par la NOAA (Climate Prediction Center).

Projet individuel de certification — RNCP 36146, *Concepteur développeur de solutions digitales* (niveau 6), HETIC.

## Objectif

Transformer des observations climatiques réelles en visualisations compréhensibles, sourcées et vérifiables :

1. **Importer** la série ONI de la NOAA dans PostgreSQL (ETL Python), en traçant la source et en contrôlant les doublons ;
2. **Exposer** les observations via une API FastAPI documentée (`/api/v1`), avec filtrage temporel et validation des entrées ;
3. **Visualiser** l'indice dans une application React / TypeScript (courbe interactive et filtre de période) ;
4. **Comparer** deux épisodes historiques avec une interprétation prudente.

## Stack technique

| Couche   | Technologies                          |
| -------- | ------------------------------------- |
| Frontend | React, TypeScript, Vite               |
| API      | Python, FastAPI, Pydantic             |
| Données  | PostgreSQL, SQLAlchemy, Alembic       |
| ETL      | Python, Pandas, NumPy                 |
| Tests    | Pytest, Vitest                        |

## Structure du dépôt

```
projet-enso-monitor/
├── backend/                # API FastAPI et ETL (Python)
│   ├── enso/
│   │   ├── domaine/        # entités et règles métier pures
│   │   ├── application/    # cas d'utilisation
│   │   ├── infrastructure/ # PostgreSQL, dépôts, accès NOAA
│   │   ├── api/v1/         # routes HTTP et schémas Pydantic
│   │   └── config.py       # paramètres lus depuis l'environnement
│   ├── alembic/            # migrations du schéma PostgreSQL
│   ├── tests/
│   └── pyproject.toml      # dépendances et configuration des outils
├── frontend/               # application React + TypeScript (Vite)
│   └── src/
│       ├── composants/     # composants d'interface réutilisables
│       ├── hooks/          # logique d'état et de chargement (useObservations…)
│       ├── services/api.ts # seul point d'accès à l'API (fetch)
│       ├── types/api.ts    # types des réponses de l'API
│       └── tests/          # tests Vitest + Testing Library
├── compose.yaml            # PostgreSQL pour le développement local
└── .env.example            # modèle des variables d'environnement
```

## Démarrage local

### Prérequis

- Docker et Docker Compose
- Python 3.13 ou supérieur

### 1. Configuration

```bash
cp .env.example .env
```

Remplacer ensuite `changer-ce-mot-de-passe` par un mot de passe local (même valeur dans `POSTGRES_PASSWORD` et dans `URL_BASE_DE_DONNEES`).

### 2. Base de données

```bash
docker compose up -d db
```

### 3. Environnement Python et schéma de la base

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head      # crée les tables (migrations dans backend/alembic/versions)
```

### 4. Import des données NOAA (ETL)

```bash
python -m enso.etl
```

L'ETL télécharge le fichier officiel, valide chaque ligne et enregistre les observations. Il peut être relancé sans risque : les valeurs déjà présentes ne sont pas dupliquées, seules les valeurs révisées par la NOAA sont mises à jour. Chaque exécution est tracée dans la table `imports` (URL, date d'extraction, empreinte SHA-256, compteurs, statut).

### 5. API

```bash
uvicorn enso.api.main:app --reload
```

- Documentation interactive (OpenAPI) : http://localhost:8000/docs
- Santé de l'API : http://localhost:8000/api/v1/sante

#### Routes disponibles

| Méthode | Route                  | Description                                   | Paramètres                                  |
| ------- | ---------------------- | --------------------------------------------- | ------------------------------------------- |
| GET     | `/api/v1/sante`        | État de l'API et de la base                   | —                                           |
| GET     | `/api/v1/observations` | Observations ONI, avec unité et source        | `debut`, `fin` (facultatifs, `AAAA-MM-JJ`) |
| GET     | `/api/v1/episodes/references` | Épisodes historiques proposés à la comparaison | — |
| GET     | `/api/v1/episodes/comparaison` | Comparaison de deux périodes : pic, moyenne, durées, interprétation et limites | `debut_a`, `fin_a`, `debut_b`, `fin_b` (obligatoires) |

Exemples :
- `GET /api/v1/observations?debut=1997-01-01&fin=1998-12-01`
- `GET /api/v1/episodes/comparaison?debut_a=1997-01-01&fin_a=1998-06-01&debut_b=2015-01-01&fin_b=2016-06-01`

#### Règles de la comparaison

| Règle | Valeur | Origine |
| ----- | ------ | ------- |
| Épisode El Niño | ONI ≥ +0,5 °C pendant au moins 5 saisons consécutives | Définition opérationnelle NOAA CPC |
| Épisode La Niña | ONI ≤ −0,5 °C pendant au moins 5 saisons consécutives | Définition opérationnelle NOAA CPC |
| Intensité du pic | faible ≥ 0,5 · modérée ≥ 1,0 · forte ≥ 1,5 · très forte ≥ 2,0 °C | Convention d'usage, **non officielle** |

Chaque comparaison renvoie aussi ses limites (convention d'intensité, absence d'impacts mesurés, durée bornée à la période, tendance au réchauffement, révisions récentes, aucune prévision).

| Code | Cas                                                             |
| ---- | --------------------------------------------------------------- |
| 200  | Succès                                                          |
| 404  | Aucune donnée importée (lancer l'ETL)                           |
| 422  | Paramètre invalide : date mal formée, début après la fin, paramètre inconnu |
| 500  | Erreur inattendue (message générique, détail uniquement dans les journaux du serveur) |

Toutes les erreurs ont le même format :

```json
{
  "erreur": {
    "code": 422,
    "message": "Paramètres de requête invalides.",
    "details": [{ "champ": "debut", "message": "Input should be a valid date…" }]
  }
}
```

L'API n'accepte les appels navigateur (CORS) que depuis les origines listées dans `ORIGINES_CORS` (par défaut le frontend local `http://localhost:5173`), et uniquement en lecture (`GET`).

### 6. Frontend

```bash
cd frontend
npm install
npm run dev          # http://localhost:5173 (les appels /api sont relayés vers l'API sur le port 8000)
```

| Commande               | Rôle                                   |
| ---------------------- | -------------------------------------- |
| `npm test`             | Tests Vitest                           |
| `npm run lint`         | Analyse statique (oxlint)              |
| `npm run format:check` | Vérification du formatage (Prettier)   |
| `npm run build`        | Vérification des types et build de production |

## Données

| Élément              | Valeur                                                                                             |
| -------------------- | -------------------------------------------------------------------------------------------------- |
| Indice               | ONI — *Oceanic Niño Index*, version 6 (ERSST.v6)                                                   |
| Producteur           | NOAA Climate Prediction Center                                                                     |
| Fichier importé      | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt                                           |
| Documentation        | https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/index.php                   |
| Couverture           | DJF 1950 → ASO 2026 (921 saisons glissantes de trois mois)                                         |
| Unité                | °C (anomalie de température de surface de la mer, région Niño 3.4 : 5°N-5°S, 120°-170°O)          |
| Extraction de référence | 19/11/2026 (fichier publié le 03/11/2026)                                                       |

La NOAA indique que les valeurs des deux derniers mois peuvent encore être révisées ; l'ETL met donc à jour une valeur existante lorsqu'elle change. Depuis 2026, la NOAA utilise le RONI (*Relative ONI*) pour la surveillance officielle de l'ENSO ; ce projet utilise l'ONI pour l'analyse historique (voir le dossier de conception).

Un extrait authentique (1997-1998) est versionné dans `backend/tests/donnees/` pour les tests.

## Tests

```bash
cd backend
pytest -v
```

Les tests d'intégration utilisent une base dédiée `enso_test`, créée automatiquement dans le conteneur PostgreSQL (la base de développement n'est jamais modifiée). Ils sont ignorés si PostgreSQL n'est pas démarré.

| Fichier                        | Vérifie                                                                 |
| ------------------------------ | ----------------------------------------------------------------------- |
| `tests/test_transformation.py` | **Test minimal n°1** : conversion, doublons, saisons/années invalides  |
| `tests/test_chargement.py`     | Classement des mesures : nouvelles, révisées, inchangées                |
| `tests/test_pipeline_etl.py`   | ETL complet : traçabilité, ré-import sans doublon, révision, échec      |
| `tests/test_api_observations.py` | **Test minimal n°2** : route filtrée par période, entrées invalides (422), absence de données (404) |
| `tests/test_api_erreurs.py`    | Format d'erreur unique, aucune fuite d'information (500), CORS          |
| `tests/test_episodes.py`       | Seuils d'intensité, séquences consécutives, détection El Niño / La Niña, interprétation |
| `tests/test_api_episodes.py`   | Route de comparaison : réponse complète, 422, 404, épisodes de référence |

## Qualité du code

```bash
cd backend
ruff check .          # analyse statique
ruff format .         # formatage
```



## Conventions du projet

### Branches

| Branche     | Rôle                                                       |
| ----------- | ---------------------------------------------------------- |
| `main`      | Versions livrées et stables                                |
| `develop`   | Intégration des fonctionnalités terminées                  |
| `feature/*` | Nouvelle fonctionnalité (ex. `feature/4-etl-import-oni`)   |
| `fix/*`     | Correction d'une anomalie                                  |
| `test/*`    | Ajout ou modification de tests                             |
| `docs/*`    | Documentation                                              |
| `chore/*`   | Configuration et outillage                                 |
| `ci/*`      | Intégration continue                                       |

Chaque branche part de `develop`, porte le numéro de l'issue qu'elle traite et revient dans `develop` par une pull request (`Closes #n`). `develop` est fusionnée dans `main` à chaque version.

### Commits

Les messages suivent la spécification [Conventional Commits](https://www.conventionalcommits.org/fr/) : le type est en anglais (`feat`, `fix`, `test`, `docs`, `chore`, `ci`, `refactor`), la description en français.

```
feat(etl): importer la série ONI depuis la NOAA
fix(api): rejeter une période dont la date de début suit la date de fin
```

### Code

Les identifiants (variables, fonctions, classes, tables) sont écrits en français, sans accents. L'anglais est conservé uniquement lorsque le langage ou le framework l'impose (mots-clés, API des bibliothèques, hooks React `use…`).

Chaque langage garde sa convention de casse : `snake_case` en Python (`lister_mesures`), `camelCase` en TypeScript (`recupererObservations`), `PascalCase` pour les classes et les composants React (`GraphiqueOni`).

### Suivi du projet

Le backlog est géré par les [issues GitHub](https://github.com/Pharosi/projet-enso-monitor/issues), regroupées en jalons quotidiens (J1 à J6).
