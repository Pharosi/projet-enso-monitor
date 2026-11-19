"""Format d'erreur unique pour toute l'API.

Toutes les erreurs ont la même forme, quel que soit leur origine :

    {"erreur": {"code": 422, "message": "...", "details": [{"champ": "debut", "message": "..."}]}}

Le frontend n'a donc qu'une seule façon de lire une erreur. Une erreur inattendue
(bug) renvoie 500 avec un message générique : aucun détail technique n'est exposé.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from enso.application.consultation import IndiceIntrouvable
from enso.domaine.episodes import PeriodeVide

journal = logging.getLogger("enso.api")


class DetailErreur(BaseModel):
    champ: str
    message: str


class Erreur(BaseModel):
    code: int
    message: str
    details: list[DetailErreur] = []


class EnveloppeErreur(BaseModel):
    """Schéma documenté dans OpenAPI pour toutes les réponses d'erreur."""

    erreur: Erreur


def reponse_erreur(
    code: int, message: str, details: list[DetailErreur] | None = None
) -> JSONResponse:
    corps = EnveloppeErreur(erreur=Erreur(code=code, message=message, details=details or []))
    return JSONResponse(status_code=code, content=corps.model_dump())


async def gerer_erreur_http(requete: Request, erreur: HTTPException) -> JSONResponse:
    """Erreurs HTTP prévues : route inconnue (404), méthode non autorisée (405)…"""
    return reponse_erreur(erreur.status_code, str(erreur.detail))


async def gerer_donnees_absentes(
    requete: Request, erreur: IndiceIntrouvable | PeriodeVide
) -> JSONResponse:
    """Indice jamais importé ou période sans observation : la ressource n'existe pas (404)."""
    return reponse_erreur(status.HTTP_404_NOT_FOUND, str(erreur))


async def gerer_erreur_validation(requete: Request, erreur: RequestValidationError) -> JSONResponse:
    """Entrées refusées par Pydantic : on indique quel champ pose problème et pourquoi."""
    details = [
        DetailErreur(
            champ=".".join(str(partie) for partie in probleme["loc"][1:]) or "requete",
            message=probleme["msg"].removeprefix("Value error, "),
        )
        for probleme in erreur.errors()
    ]
    return reponse_erreur(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "Paramètres de requête invalides.", details
    )


async def gerer_erreur_inattendue(requete: Request, erreur: Exception) -> JSONResponse:
    """Bug ou panne : le détail va dans le journal du serveur, jamais dans la réponse."""
    journal.exception("Erreur inattendue sur %s %s", requete.method, requete.url.path)
    return reponse_erreur(status.HTTP_500_INTERNAL_SERVER_ERROR, "Erreur interne du serveur.")


def enregistrer_gestionnaires_erreurs(application: FastAPI) -> None:
    application.add_exception_handler(HTTPException, gerer_erreur_http)
    application.add_exception_handler(IndiceIntrouvable, gerer_donnees_absentes)
    application.add_exception_handler(PeriodeVide, gerer_donnees_absentes)
    application.add_exception_handler(RequestValidationError, gerer_erreur_validation)
    application.add_exception_handler(Exception, gerer_erreur_inattendue)
