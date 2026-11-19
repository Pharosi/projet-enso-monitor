"""Cas d'utilisation : comparer deux périodes de l'indice ONI."""

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from enso.application.consultation import obtenir_indice
from enso.domaine.episodes import AnalysePeriode, analyser_periode
from enso.domaine.interpretation import LIMITES, rediger_interpretation
from enso.domaine.oni import DescriptionIndice, MesureOni
from enso.infrastructure.depot_observations import lister_mesures


@dataclass(frozen=True)
class Periode:
    debut: date
    fin: date


@dataclass(frozen=True)
class Comparaison:
    indice: DescriptionIndice
    analyse_a: AnalysePeriode
    analyse_b: AnalysePeriode
    mesures_a: list[MesureOni]
    mesures_b: list[MesureOni]
    interpretation: list[str]
    limites: list[str]


def comparer_periodes(
    session: Session, code_indice: str, periode_a: Periode, periode_b: Periode
) -> Comparaison:
    indice = obtenir_indice(session, code_indice)
    mesures_a = lister_mesures(session, indice.id, periode_a.debut, periode_a.fin)
    mesures_b = lister_mesures(session, indice.id, periode_b.debut, periode_b.fin)
    analyse_a = analyser_periode(periode_a.debut, periode_a.fin, mesures_a)
    analyse_b = analyser_periode(periode_b.debut, periode_b.fin, mesures_b)

    return Comparaison(
        indice=indice.description,
        analyse_a=analyse_a,
        analyse_b=analyse_b,
        mesures_a=mesures_a,
        mesures_b=mesures_b,
        interpretation=rediger_interpretation(analyse_a, analyse_b),
        limites=LIMITES,
    )
