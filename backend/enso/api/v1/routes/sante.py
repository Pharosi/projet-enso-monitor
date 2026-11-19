"""Route de santé : indique si l'API fonctionne et si la base répond."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from enso.infrastructure.base_de_donnees import obtenir_session

routeur = APIRouter(tags=["Santé"])


class EtatDeSante(BaseModel):
    statut: str
    base_de_donnees: str


@routeur.get(
    "/sante",
    summary="Vérifier l'état de l'API et de la base de données",
    response_model=EtatDeSante,
    responses={503: {"description": "Base de données indisponible (statut « degrade »)"}},
)
def verifier_sante(
    reponse: Response, session: Annotated[Session, Depends(obtenir_session)]
) -> EtatDeSante:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError:
        reponse.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return EtatDeSante(statut="degrade", base_de_donnees="indisponible")
    return EtatDeSante(statut="ok", base_de_donnees="ok")
