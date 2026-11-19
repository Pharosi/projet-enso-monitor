"""Tests des règles d'analyse des épisodes (domaine pur, sans base de données)."""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from enso.domaine.episodes import (
    PeriodeVide,
    analyser_periode,
    categorie_intensite,
    plus_longue_sequence,
)
from enso.domaine.interpretation import rediger_interpretation
from enso.etl.transformation import lire_fichier_oni, transformer_observations

EXTRAIT_REEL = Path(__file__).parent / "donnees" / "oni_extrait_1997_1998.txt"


@pytest.fixture
def mesures_par_annee():
    """Mesures réelles 1997 et 1998, séparées par année."""
    resultat = transformer_observations(lire_fichier_oni(EXTRAIT_REEL.read_bytes()))
    return {annee: [m for m in resultat.mesures if m.annee == annee] for annee in (1997, 1998)}


@pytest.mark.parametrize(
    ("anomalie", "attendue"),
    [
        ("2.37", "très forte"),
        ("2.00", "très forte"),
        ("1.99", "forte"),
        ("1.00", "modérée"),
        ("0.50", "faible"),
        ("0.49", None),
        ("-1.60", "forte"),  # La Niña : on compare la valeur absolue
    ],
)
def test_categorie_intensite_respecte_les_seuils(anomalie, attendue):
    assert categorie_intensite(Decimal(anomalie)) == attendue


def test_plus_longue_sequence_compte_les_saisons_consecutives():
    anomalies = [Decimal(v) for v in ("0.6", "0.7", "0.2", "0.5", "0.5", "0.5")]

    assert plus_longue_sequence(anomalies, lambda a: a >= Decimal("0.5")) == 3


def test_el_nino_1997_est_detecte_et_classe(mesures_par_annee):
    analyse = analyser_periode(date(1997, 1, 1), date(1997, 12, 1), mesures_par_annee[1997])

    assert (analyse.pic.saison, analyse.pic.anomalie) == ("NDJ", Decimal("2.37"))
    assert analyse.saisons_el_nino_consecutives == 8  # AMJ -> NDJ 1997
    assert analyse.episode_el_nino is True
    assert analyse.intensite_du_pic == "très forte"


def test_la_duree_est_comptee_dans_la_periode_choisie(mesures_par_annee):
    """1998 seule : la fin de l'El Niño (4 saisons) ne suffit pas, La Niña apparaît (6)."""
    analyse = analyser_periode(date(1998, 1, 1), date(1998, 12, 1), mesures_par_annee[1998])

    assert analyse.saisons_el_nino_consecutives == 4
    assert analyse.episode_el_nino is False
    assert analyse.intensite_du_pic is None
    assert analyse.saisons_la_nina_consecutives == 6
    assert analyse.episode_la_nina is True


def test_une_periode_sans_mesure_est_refusee():
    with pytest.raises(PeriodeVide):
        analyser_periode(date(1940, 1, 1), date(1941, 1, 1), [])


def test_l_interpretation_compare_les_pics_avec_prudence(mesures_par_annee):
    analyse_1997 = analyser_periode(date(1997, 1, 1), date(1997, 12, 1), mesures_par_annee[1997])
    analyse_1998 = analyser_periode(date(1998, 1, 1), date(1998, 12, 1), mesures_par_annee[1998])

    phrases = rediger_interpretation(analyse_1997, analyse_1998)

    assert "convention usuelle" in phrases[0]
    assert "sans épisode El Niño au sens de la NOAA" in phrases[1]
    assert phrases[2] == "Le pic de la période A dépasse celui de la période B de 0,15 °C."
