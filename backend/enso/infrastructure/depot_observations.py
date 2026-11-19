"""Accès à la table observations : écriture par l'ETL, lecture par l'API."""

from datetime import date
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from enso.domaine.oni import MesureOni
from enso.infrastructure.modeles import Observation

ValeursParPeriode = dict[date, tuple[Decimal, Decimal]]


def lire_valeurs_existantes(session: Session, indice_id: int) -> ValeursParPeriode:
    """Retourne {date_periode: (temperature_totale, anomalie)} pour un indice."""
    lignes = session.execute(
        select(
            Observation.date_periode, Observation.temperature_totale, Observation.anomalie
        ).where(Observation.indice_id == indice_id)
    )
    return {ligne.date_periode: (ligne.temperature_totale, ligne.anomalie) for ligne in lignes}


def inserer_observations(
    session: Session, indice_id: int, import_id: int, mesures: list[MesureOni]
) -> None:
    session.add_all(
        [
            Observation(
                indice_id=indice_id,
                import_id=import_id,
                saison=mesure.saison,
                annee=mesure.annee,
                date_periode=mesure.date_periode,
                temperature_totale=mesure.temperature_totale,
                anomalie=mesure.anomalie,
            )
            for mesure in mesures
        ]
    )


def mettre_a_jour_observations(
    session: Session, indice_id: int, import_id: int, mesures: list[MesureOni]
) -> None:
    """Met à jour les valeurs révisées par la NOAA et note l'import qui les a modifiées."""
    for mesure in mesures:
        session.execute(
            update(Observation)
            .where(
                Observation.indice_id == indice_id,
                Observation.date_periode == mesure.date_periode,
            )
            .values(
                temperature_totale=mesure.temperature_totale,
                anomalie=mesure.anomalie,
                import_id=import_id,
            )
        )


def lister_mesures(
    session: Session, indice_id: int, debut: date | None, fin: date | None
) -> list[MesureOni]:
    """Observations d'un indice, triées par date, éventuellement limitées à une période.

    Les bornes sont transmises comme paramètres SQL (jamais concaténées) :
    SQLAlchemy génère « WHERE date_periode >= %(param)s ».
    """
    requete = (
        select(Observation)
        .where(Observation.indice_id == indice_id)
        .order_by(Observation.date_periode)
    )
    if debut is not None:
        requete = requete.where(Observation.date_periode >= debut)
    if fin is not None:
        requete = requete.where(Observation.date_periode <= fin)

    return [
        MesureOni(
            saison=observation.saison,
            annee=observation.annee,
            date_periode=observation.date_periode,
            temperature_totale=observation.temperature_totale,
            anomalie=observation.anomalie,
        )
        for observation in session.scalars(requete)
    ]
