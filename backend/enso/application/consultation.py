"""Cas d'utilisation : consulter la série d'un indice sur une période.

La couche application assemble ce dont l'API a besoin (indice, source, fraîcheur,
mesures) sans rien savoir du protocole HTTP.
"""

from dataclasses import dataclass
from datetime import date, datetime

from sqlalchemy.orm import Session

from enso.domaine.oni import DescriptionIndice, DescriptionSource, MesureOni
from enso.infrastructure.depot_imports import date_derniere_extraction
from enso.infrastructure.depot_observations import lister_mesures
from enso.infrastructure.depot_referentiel import trouver_indice


class IndiceIntrouvable(LookupError):
    """Aucun indice de ce code en base : l'ETL n'a probablement pas encore été exécuté."""


@dataclass(frozen=True)
class SerieObservations:
    indice: DescriptionIndice
    source: DescriptionSource
    derniere_extraction: datetime | None
    mesures: list[MesureOni]


def consulter_serie(
    session: Session, code_indice: str, debut: date | None, fin: date | None
) -> SerieObservations:
    indice = trouver_indice(session, code_indice)
    if indice is None:
        raise IndiceIntrouvable(
            f"Aucune donnée pour l'indice {code_indice} : lancer l'import (python -m enso.etl)."
        )

    return SerieObservations(
        indice=indice.description,
        source=indice.source,
        derniere_extraction=date_derniere_extraction(session, indice.id),
        mesures=lister_mesures(session, indice.id, debut, fin),
    )
