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
├── frontend/               # application React (à venir)
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

### 4. API

```bash
uvicorn enso.api.main:app --reload
```

- Documentation interactive (OpenAPI) : http://localhost:8000/docs
- Santé de l'API : http://localhost:8000/api/v1/sante

### Qualité du code

```bash
cd backend
ruff check .          # analyse statique
ruff format .         # formatage
```

> Les instructions d'import des données, de lancement du frontend et des tests seront complétées au fil du développement.

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

### Suivi du projet

Le backlog est géré par les [issues GitHub](https://github.com/Pharosi/projet-enso-monitor/issues), regroupées en jalons quotidiens (J1 à J6).
