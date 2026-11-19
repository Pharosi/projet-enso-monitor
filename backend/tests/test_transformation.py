"""Test minimal n°1 du sujet : transformation Python des observations NOAA.

On vérifie que la transformation convertit correctement les lignes valides,
élimine les doublons et rejette les dates (saison / année) ou valeurs invalides.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from enso.etl.transformation import (
    FormatFichierInvalide,
    lire_fichier_oni,
    transformer_observations,
)

EN_TETE = "SEAS  YR   TOTAL   ANOM\n"
EXTRAIT_REEL = Path(__file__).parent / "donnees" / "oni_extrait_1997_1998.txt"


def transformer_texte(lignes: str):
    """Raccourci : transforme un petit fichier ONI écrit directement dans le test."""
    contenu = (EN_TETE + lignes).encode()
    return transformer_observations(lire_fichier_oni(contenu))


def test_une_ligne_valide_devient_une_mesure():
    resultat = transformer_texte("DJF 1998  28.85   2.22\n")

    assert len(resultat.mesures) == 1
    mesure = resultat.mesures[0]
    assert mesure.saison == "DJF"
    assert mesure.annee == 1998
    assert mesure.date_periode == date(1998, 1, 1)
    assert mesure.temperature_totale == Decimal("28.85")
    assert mesure.anomalie == Decimal("2.22")


def test_la_date_correspond_au_mois_central_de_la_saison():
    resultat = transformer_texte("NDJ 1997  28.96   2.37\nJJA 1997  28.40   1.48\n")

    dates = [mesure.date_periode for mesure in resultat.mesures]
    assert dates == [date(1997, 12, 1), date(1997, 7, 1)]


def test_les_doublons_sont_supprimes_et_comptes():
    resultat = transformer_texte(
        "DJF 1998  28.85   2.22\n"
        "DJF 1998  28.85   2.22\n"  # même saison, même année : doublon
        "JFM 1998  28.85   1.93\n"
    )

    assert len(resultat.mesures) == 2
    assert resultat.doublons == 1
    assert resultat.lignes_lues == 3
    assert resultat.lignes_ignorees == 1


@pytest.mark.parametrize(
    "ligne_invalide",
    [
        "XYZ 1998  28.85   2.22",  # saison inexistante
        "DJF 19A8  28.85   2.22",  # année illisible
        "DJF 1949  28.85   2.22",  # année antérieure au début de l'ONI
        "DJF 1998.5  28.85   2.22",  # année non entière
        "DJF 1998  28.85   abc",  # anomalie illisible
        "DJF 1998  28.85   9.99",  # anomalie aberrante
    ],
)
def test_une_ligne_invalide_est_rejetee_sans_bloquer_les_autres(ligne_invalide):
    resultat = transformer_texte(ligne_invalide + "\nJFM 1998  28.85   1.93\n")

    assert [mesure.saison for mesure in resultat.mesures] == ["JFM"]
    assert resultat.lignes_invalides == 1


def test_un_fichier_sans_les_colonnes_attendues_est_refuse():
    with pytest.raises(FormatFichierInvalide):
        lire_fichier_oni(b"date valeur\n2020-01 1.5\n")


def test_extrait_reel_noaa_1997_1998():
    """Extrait authentique du fichier oni.ascii.txt (NOAA CPC, extrait le 19/11/2026)."""
    resultat = transformer_observations(lire_fichier_oni(EXTRAIT_REEL.read_bytes()))

    assert len(resultat.mesures) == 24  # 12 saisons x 2 ans
    assert resultat.lignes_ignorees == 0
    pic = max(resultat.mesures, key=lambda mesure: mesure.anomalie)
    assert (pic.saison, pic.annee, pic.anomalie) == ("NDJ", 1997, Decimal("2.37"))
