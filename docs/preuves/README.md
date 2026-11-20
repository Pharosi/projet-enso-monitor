# Preuves d'exécution

Sorties réelles des commandes, conservées comme preuves pour le livrable A (« preuves des trois tests minimaux »). Chaque fichier indique la date, le commit et l'environnement d'exécution.

## Les trois tests minimaux du sujet

| Test exigé | Fichier de test | Preuve | Résultat |
| ---------- | --------------- | ------ | -------- |
| n°1 — transformation Python d'observations NOAA (doublons, date invalide) | `backend/tests/test_transformation.py` | [`test-1-transformation.txt`](test-1-transformation.txt) | 11 réussis |
| n°2 — route FastAPI filtrée par période, réponse attendue et entrée invalide | `backend/tests/test_api_observations.py` | [`test-2-api.txt`](test-2-api.txt) | 7 réussis |
| n°3 — un changement de période actualise les valeurs affichées | `frontend/src/tests/SectionSerie.test.tsx` | [`test-3-frontend.txt`](test-3-frontend.txt) | 6 réussis |

Suites complètes : [`suites-completes.txt`](suites-completes.txt) — **47 tests backend et 30 tests frontend réussis**.

## Intégration continue

Les mêmes tests, ainsi que le lint, les migrations (`alembic upgrade head` + `alembic check` sur PostgreSQL) et le build, sont exécutés par GitHub Actions à chaque pull request et à chaque fusion : onglet [Actions](https://github.com/Pharosi/projet-enso-monitor/actions) du dépôt. Exemple : exécution réussie après la fusion du README complet (PR #41) — [run 44737830048](https://github.com/Pharosi/projet-enso-monitor/actions/runs/44737830048).

## Corrections d'anomalies et non-régression

### Issue #36 — contraste du contour de focus (audit d'accessibilité)

| Étape | Preuve |
| ----- | ------ |
| Le test reproduit l'anomalie : contraste du focus 2,07:1 et 1,96:1 (3:1 exigé) → 2 échecs | [`anomalie-36-avant-correction.txt`](anomalie-36-avant-correction.txt) |
| Après correction (`#b45309`, 5,02:1) : test vert et suite frontend complète verte | [`anomalie-36-apres-correction.txt`](anomalie-36-apres-correction.txt) |
| Contour de focus visible au clavier | [`anomalie-36-focus-apres.png`](anomalie-36-focus-apres.png) |

### Issue #44 — filtre de période inutilisable dans Safari (test manuel)

| Étape | Preuve |
| ----- | ------ |
| Constat dans Safari : champ texte libre, saisie `01/01/1997` → erreur 422 | [`anomalie-44-safari-avant.webp`](anomalie-44-safari-avant.webp) |
| Les tests reproduisent l'anomalie (listes mois/année absentes, champ libre présent) → 4 échecs | [`anomalie-44-avant-correction.txt`](anomalie-44-avant-correction.txt) |
| Après correction (listes mois/année) : 6/6 et suite frontend complète verte (30) | [`anomalie-44-apres-correction.txt`](anomalie-44-apres-correction.txt) |
| Filtre corrigé : janvier 1997 → décembre 1998, 24 saisons | [`anomalie-44-filtre-apres.png`](anomalie-44-filtre-apres.png) |

## Déploiement de production exécuté en local

[`deploiement-local.txt`](deploiement-local.txt) : services démarrés (Docker Compose), santé de l'API via Caddy en HTTPS, en-têtes de sécurité, import NOAA par le worker ETL. Procédure complète : [`deploy/README.md`](../../deploy/README.md).

## Régénérer les preuves

```bash
docker compose up -d db
cd backend && pytest -v tests/test_transformation.py tests/test_api_observations.py
cd ../frontend && npx vitest run --reporter=verbose src/tests/SectionSerie.test.tsx
```
