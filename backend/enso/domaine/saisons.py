"""Saisons glissantes de trois mois utilisées par l'indice ONI.

L'ONI est une moyenne mobile sur trois mois. Chaque saison est notée par les
initiales anglaises de ses trois mois (notation NOAA) : DJF = décembre-janvier-février.
Le mois central sert de date de référence : DJF 1998 -> 1er janvier 1998.
"""

from datetime import date

MOIS_CENTRAL_PAR_SAISON: dict[str, int] = {
    "DJF": 1,
    "JFM": 2,
    "FMA": 3,
    "MAM": 4,
    "AMJ": 5,
    "MJJ": 6,
    "JJA": 7,
    "JAS": 8,
    "ASO": 9,
    "SON": 10,
    "OND": 11,
    "NDJ": 12,
}

# Les 12 saisons, dans l'ordre de l'année.
SAISONS_VALIDES: tuple[str, ...] = tuple(MOIS_CENTRAL_PAR_SAISON)


def date_de_periode(saison: str, annee: int) -> date:
    """Retourne le premier jour du mois central de la saison (ex. NDJ 2015 -> 2015-12-01)."""
    return date(annee, MOIS_CENTRAL_PAR_SAISON[saison], 1)
