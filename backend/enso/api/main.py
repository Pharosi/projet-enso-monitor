"""Point d'entrée de l'API FastAPI.

Lancement en développement (depuis le dossier backend/) :
    uvicorn enso.api.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from enso.api.erreurs import enregistrer_gestionnaires_erreurs
from enso.api.v1.routeur import routeur_v1
from enso.config import obtenir_parametres

DESCRIPTION = """
API de consultation de l'indice **ONI** (*Oceanic Niño Index*, version 6) publié par la
**NOAA Climate Prediction Center**, et de comparaison d'épisodes El Niño / La Niña.

- Données : https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt
- Unité : °C (anomalie de température de surface de la mer, région Niño 3.4)
- Aucune prévision climatique n'est fournie.

Toutes les erreurs suivent le format `{"erreur": {"code", "message", "details"}}`.
"""

TAGS = [
    {"name": "Observations", "description": "Valeurs de l'indice ONI, filtrables par période."},
    {"name": "Épisodes", "description": "Comparaison de deux épisodes historiques."},
    {"name": "Santé", "description": "Disponibilité de l'API et de la base de données."},
]


def creer_application() -> FastAPI:
    """Construit l'application : une fonction dédiée facilite les tests."""
    application = FastAPI(
        title="ENSO Monitor API",
        description=DESCRIPTION,
        version="0.2.0",
        openapi_tags=TAGS,
        # Documentation sous /api : en production, Caddy ne relaie vers l'API que /api/*.
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        redoc_url=None,
    )

    # CORS : seul le frontend déclaré peut appeler l'API depuis un navigateur,
    # et uniquement en lecture (GET).
    application.add_middleware(
        CORSMiddleware,
        allow_origins=obtenir_parametres().origines_cors,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )
    enregistrer_gestionnaires_erreurs(application)
    application.include_router(routeur_v1)
    return application


app = creer_application()
