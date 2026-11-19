"""Route de consultation des observations de l'indice ONI."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from enso.api.erreurs import EnveloppeErreur
from enso.api.v1.schemas import (
    FiltrePeriode,
    IndiceReponse,
    ObservationReponse,
    SerieObservationsReponse,
    SourceReponse,
)
from enso.application.consultation import SerieObservations, consulter_serie
from enso.domaine.oni import INDICE_ONI
from enso.infrastructure.base_de_donnees import obtenir_session

routeur = APIRouter(tags=["Observations"])


@routeur.get(
    "/observations",
    summary="Lister les observations ONI, éventuellement sur une période",
    response_model=SerieObservationsReponse,
    responses={
        404: {"model": EnveloppeErreur, "description": "Aucune donnée importée pour l'indice"},
        422: {"model": EnveloppeErreur, "description": "Date mal formée, début après la fin…"},
    },
)
def lister_observations(
    filtre: Annotated[FiltrePeriode, Query()],
    session: Annotated[Session, Depends(obtenir_session)],
) -> SerieObservationsReponse:
    # Si aucune donnée n'existe, IndiceIntrouvable est levée et transformée en 404
    # par le gestionnaire d'erreurs commun (enso/api/erreurs.py).
    serie = consulter_serie(session, INDICE_ONI.code, filtre.debut, filtre.fin)
    return construire_reponse(serie, filtre)


def construire_reponse(serie: SerieObservations, filtre: FiltrePeriode) -> SerieObservationsReponse:
    """Traduit les objets du domaine en schéma de réponse JSON."""
    return SerieObservationsReponse(
        indice=IndiceReponse(
            code=serie.indice.code,
            nom=serie.indice.nom,
            unite=serie.indice.unite,
            version=serie.indice.version,
        ),
        source=SourceReponse(
            nom=serie.source.nom,
            url=serie.source.url,
            derniere_extraction=serie.derniere_extraction,
        ),
        debut=filtre.debut,
        fin=filtre.fin,
        nombre=len(serie.mesures),
        observations=[
            ObservationReponse(
                saison=mesure.saison,
                annee=mesure.annee,
                date_periode=mesure.date_periode,
                anomalie=float(mesure.anomalie),
                temperature_totale=float(mesure.temperature_totale),
            )
            for mesure in serie.mesures
        ],
    )
