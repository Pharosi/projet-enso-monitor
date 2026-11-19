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

> Les instructions d'installation et de lancement seront complétées au fil du développement.

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
