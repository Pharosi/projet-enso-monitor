"""Regroupe toutes les routes de la version 1 de l'API sous le préfixe /api/v1."""

from fastapi import APIRouter

from enso.api.v1.routes import observations, sante

routeur_v1 = APIRouter(prefix="/api/v1")
routeur_v1.include_router(sante.routeur)
routeur_v1.include_router(observations.routeur)
