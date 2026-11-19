"""Transformation : du fichier texte de la NOAA à des mesures validées.

Format du fichier source (colonnes séparées par des espaces) :

     SEAS  YR   TOTAL   ANOM
      DJF 1950  25.01  -1.32
      JFM 1950  25.36  -1.20

Étapes : lecture -> conversion des types -> rejet des lignes invalides
-> suppression des doublons -> calcul de la date de période.
Une ligne incorrecte est écartée et comptée : elle ne fait pas échouer tout l'import.
"""

import io
from dataclasses import dataclass
from decimal import Decimal

import numpy as np
import pandas as pd

from enso.domaine.oni import (
    ANNEE_MAXIMALE,
    ANNEE_MINIMALE,
    ANOMALIE_MAXIMALE_ABSOLUE,
    MesureOni,
)
from enso.domaine.saisons import SAISONS_VALIDES, date_de_periode

# Correspondance entre les colonnes NOAA et les noms utilisés dans le projet.
COLONNES_NOAA = {
    "SEAS": "saison",
    "YR": "annee",
    "TOTAL": "temperature_totale",
    "ANOM": "anomalie",
}


class FormatFichierInvalide(ValueError):
    """Le fichier ne contient pas les colonnes attendues : il ne s'agit pas du fichier ONI."""


@dataclass(frozen=True)
class ResultatTransformation:
    mesures: list[MesureOni]
    lignes_lues: int
    lignes_invalides: int
    doublons: int

    @property
    def lignes_ignorees(self) -> int:
        return self.lignes_invalides + self.doublons


def lire_fichier_oni(contenu: bytes) -> pd.DataFrame:
    """Lit le fichier brut ; toutes les valeurs restent du texte à ce stade."""
    tableau = pd.read_csv(io.BytesIO(contenu), sep=r"\s+", dtype=str)

    colonnes_manquantes = set(COLONNES_NOAA) - set(tableau.columns)
    if colonnes_manquantes:
        raise FormatFichierInvalide(f"Colonnes manquantes : {sorted(colonnes_manquantes)}")

    return tableau.rename(columns=COLONNES_NOAA)[list(COLONNES_NOAA.values())]


def transformer_observations(brutes: pd.DataFrame) -> ResultatTransformation:
    """Enchaîne les étapes de nettoyage et compte ce qui a été écarté."""
    typees = convertir_types(brutes)
    valides = typees[masque_lignes_valides(typees)]
    sans_doublons = valides.drop_duplicates(subset=["saison", "annee"], keep="first")

    return ResultatTransformation(
        mesures=vers_mesures(sans_doublons),
        lignes_lues=len(brutes),
        lignes_invalides=len(typees) - len(valides),
        doublons=len(valides) - len(sans_doublons),
    )


def convertir_types(brutes: pd.DataFrame) -> pd.DataFrame:
    """Convertit le texte en nombres. errors="coerce" : une valeur illisible devient NaN
    (valeur manquante) au lieu d'interrompre le programme ; elle sera rejetée ensuite."""
    return pd.DataFrame(
        {
            "saison": brutes["saison"].str.strip().str.upper(),
            "annee": pd.to_numeric(brutes["annee"], errors="coerce"),
            "temperature_totale": pd.to_numeric(brutes["temperature_totale"], errors="coerce"),
            "anomalie": pd.to_numeric(brutes["anomalie"], errors="coerce"),
        }
    )


def masque_lignes_valides(typees: pd.DataFrame) -> pd.Series:
    """Retourne True pour chaque ligne qui respecte toutes les règles du domaine."""
    saison_valide = typees["saison"].isin(SAISONS_VALIDES)
    annee_entiere = typees["annee"] % 1 == 0
    annee_plausible = typees["annee"].between(ANNEE_MINIMALE, ANNEE_MAXIMALE)
    # np.isfinite rejette à la fois les valeurs manquantes (NaN) et infinies.
    valeurs_finies = np.isfinite(typees[["temperature_totale", "anomalie"]]).all(axis=1)
    anomalie_plausible = typees["anomalie"].abs() <= ANOMALIE_MAXIMALE_ABSOLUE

    return saison_valide & annee_entiere & annee_plausible & valeurs_finies & anomalie_plausible


def vers_mesures(valides: pd.DataFrame) -> list[MesureOni]:
    """Transforme chaque ligne validée en MesureOni (valeurs décimales exactes)."""
    return [
        MesureOni(
            saison=ligne.saison,
            annee=int(ligne.annee),
            date_periode=date_de_periode(ligne.saison, int(ligne.annee)),
            temperature_totale=vers_decimal(ligne.temperature_totale),
            anomalie=vers_decimal(ligne.anomalie),
        )
        for ligne in valides.itertuples(index=False)
    ]


def vers_decimal(valeur: float) -> Decimal:
    """Arrondit à deux décimales, comme dans le fichier NOAA : 1.3200000001 -> Decimal('1.32')."""
    return Decimal(f"{valeur:.2f}")
