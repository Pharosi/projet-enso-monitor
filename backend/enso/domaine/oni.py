"""Description de l'indice ONI, de sa source et des valeurs considérées comme plausibles.

Ces informations sont la référence unique du projet : la base de données (contraintes
CHECK), l'ETL (validation) et l'API (unité, source affichée) s'appuient dessus.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

# Bornes de plausibilité : l'ONI commence en 1950 et ses valeurs historiques restent
# entre -3 et +3 °C environ. Une marge à ±5 °C rejette les valeurs aberrantes
# (ex. une erreur de saisie) sans exclure un épisode exceptionnel.
ANNEE_MINIMALE = 1950
ANNEE_MAXIMALE = 2100
ANOMALIE_MAXIMALE_ABSOLUE = 5


@dataclass(frozen=True)
class DescriptionSource:
    nom: str
    url: str
    description: str


@dataclass(frozen=True)
class DescriptionIndice:
    code: str
    nom: str
    unite: str
    version: str
    description: str


@dataclass(frozen=True)
class MesureOni:
    """Une valeur de l'ONI pour une saison donnée, après validation."""

    saison: str
    annee: int
    date_periode: date
    temperature_totale: Decimal
    anomalie: Decimal


SOURCE_NOAA_CPC = DescriptionSource(
    nom="NOAA Climate Prediction Center",
    url="https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/index.php",
    description="Centre de prévision climatique de la NOAA (National Weather Service, États-Unis).",
)

INDICE_ONI = DescriptionIndice(
    code="ONI",
    nom="Oceanic Niño Index",
    unite="°C",
    version="ONI v6 (ERSST.v6)",
    description=(
        "Moyenne mobile sur trois mois des anomalies de température de surface de la mer "
        "dans la région Niño 3.4 (5°N-5°S, 120°-170°O), par rapport à des périodes de "
        "référence de 30 ans actualisées tous les 5 ans."
    ),
)
