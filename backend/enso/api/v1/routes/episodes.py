"""Routes de comparaison de deux épisodes historiques de l'ONI."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from enso.api.erreurs import EnveloppeErreur
from enso.api.v1.schemas import (
    AnalyseReponse,
    ComparaisonReponse,
    EpisodeDeReferenceReponse,
    FiltreComparaison,
    ReglesReponse,
    observation_depuis_mesure,
)
from enso.application.comparaison import Comparaison, Periode, comparer_periodes
from enso.domaine.episodes import (
    CATEGORIES_INTENSITE,
    DUREE_MINIMALE_SAISONS,
    EPISODES_DE_REFERENCE,
    SEUIL_EL_NINO,
    SEUIL_LA_NINA,
    AnalysePeriode,
)
from enso.domaine.oni import INDICE_ONI, MesureOni
from enso.infrastructure.base_de_donnees import obtenir_session

routeur = APIRouter(prefix="/episodes", tags=["Épisodes"])


@routeur.get(
    "/references",
    summary="Lister les épisodes historiques proposés à la comparaison",
    response_model=list[EpisodeDeReferenceReponse],
)
def lister_episodes_de_reference() -> list[EpisodeDeReferenceReponse]:
    return [
        EpisodeDeReferenceReponse(
            identifiant=episode.identifiant,
            libelle=episode.libelle,
            debut=episode.debut,
            fin=episode.fin,
            en_cours=episode.en_cours,
        )
        for episode in EPISODES_DE_REFERENCE
    ]


@routeur.get(
    "/comparaison",
    summary="Comparer deux périodes de l'ONI avec une interprétation prudente",
    response_model=ComparaisonReponse,
    responses={
        404: {"model": EnveloppeErreur, "description": "Aucune observation dans une période"},
        422: {"model": EnveloppeErreur, "description": "Période absente ou inversée"},
    },
)
def comparer_episodes(
    filtre: Annotated[FiltreComparaison, Query()],
    session: Annotated[Session, Depends(obtenir_session)],
) -> ComparaisonReponse:
    comparaison = comparer_periodes(
        session,
        INDICE_ONI.code,
        Periode(filtre.debut_a, filtre.fin_a),
        Periode(filtre.debut_b, filtre.fin_b),
    )
    return construire_reponse(comparaison)


def construire_reponse(comparaison: Comparaison) -> ComparaisonReponse:
    return ComparaisonReponse(
        periode_a=analyse_vers_reponse(comparaison.analyse_a, comparaison.mesures_a),
        periode_b=analyse_vers_reponse(comparaison.analyse_b, comparaison.mesures_b),
        regles=ReglesReponse(
            indice=comparaison.indice.version,
            seuil_el_nino=float(SEUIL_EL_NINO),
            seuil_la_nina=float(SEUIL_LA_NINA),
            duree_minimale_saisons=DUREE_MINIMALE_SAISONS,
            categories_intensite={libelle: float(seuil) for seuil, libelle in CATEGORIES_INTENSITE},
        ),
        interpretation=comparaison.interpretation,
        limites=comparaison.limites,
    )


def analyse_vers_reponse(analyse: AnalysePeriode, mesures: list[MesureOni]) -> AnalyseReponse:
    return AnalyseReponse(
        debut=analyse.debut,
        fin=analyse.fin,
        nombre_de_saisons=analyse.nombre_de_saisons,
        pic=observation_depuis_mesure(analyse.pic),
        creux=observation_depuis_mesure(analyse.creux),
        anomalie_moyenne=float(analyse.anomalie_moyenne),
        saisons_el_nino_consecutives=analyse.saisons_el_nino_consecutives,
        saisons_la_nina_consecutives=analyse.saisons_la_nina_consecutives,
        episode_el_nino=analyse.episode_el_nino,
        episode_la_nina=analyse.episode_la_nina,
        intensite_du_pic=analyse.intensite_du_pic,
        observations=[observation_depuis_mesure(mesure) for mesure in mesures],
    )
