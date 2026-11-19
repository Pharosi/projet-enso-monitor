"""Point d'entrée de l'API FastAPI.

Lancement en développement (depuis le dossier backend/) :
    uvicorn enso.api.main:app --reload
"""

from fastapi import FastAPI

from enso.api.v1.routeur import routeur_v1


def creer_application() -> FastAPI:
    """Construit l'application : une fonction dédiée facilite les tests."""
    application = FastAPI(
        title="ENSO Monitor API",
        description=(
            "Observations de l'indice ONI (NOAA CPC) et comparaison d'épisodes El Niño / La Niña."
        ),
        version="0.1.0",
    )
    application.include_router(routeur_v1)
    return application


app = creer_application()
