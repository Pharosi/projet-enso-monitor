"""Règles d'analyse des épisodes El Niño / La Niña à partir de l'ONI.

Définition opérationnelle de la NOAA (Climate Prediction Center) :
- El Niño : ONI ≥ +0,5 °C pendant au moins 5 saisons glissantes consécutives ;
- La Niña : ONI ≤ -0,5 °C pendant au moins 5 saisons glissantes consécutives.

Les catégories d'intensité (faible → très forte) sont une CONVENTION d'usage,
pas une classification officielle de la NOAA. Aucune prévision n'est calculée ici.
"""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from enso.domaine.oni import MesureOni

SEUIL_EL_NINO = Decimal("0.5")
SEUIL_LA_NINA = Decimal("-0.5")
DUREE_MINIMALE_SAISONS = 5

# Du plus fort au plus faible : la première catégorie atteinte est retenue.
CATEGORIES_INTENSITE: list[tuple[Decimal, str]] = [
    (Decimal("2.0"), "très forte"),
    (Decimal("1.5"), "forte"),
    (Decimal("1.0"), "modérée"),
    (Decimal("0.5"), "faible"),
]


class PeriodeVide(LookupError):
    """Aucune observation dans la période demandée."""


@dataclass(frozen=True)
class EpisodeDeReference:
    """Période suggérée à l'utilisateur dans le formulaire de comparaison."""

    identifiant: str
    libelle: str
    debut: date
    fin: date
    en_cours: bool = False


def episode(identifiant: str, annee: int, en_cours: bool = False) -> EpisodeDeReference:
    """Fenêtre de janvier de l'année du début à juin de l'année suivante (18 saisons) :
    un El Niño se développe au printemps, culmine en hiver et décline au printemps suivant."""
    if en_cours:
        return EpisodeDeReference(
            identifiant, f"El Niño {annee} (en cours)", date(annee, 1, 1), date(annee, 12, 1), True
        )
    return EpisodeDeReference(
        identifiant, f"El Niño {annee}-{annee + 1}", date(annee, 1, 1), date(annee + 1, 6, 1)
    )


EPISODES_DE_REFERENCE = [
    episode("el-nino-1972-1973", 1972),
    episode("el-nino-1982-1983", 1982),
    episode("el-nino-1997-1998", 1997),
    episode("el-nino-2015-2016", 2015),
    episode("el-nino-2023-2024", 2023),
    episode("el-nino-2026", 2026, en_cours=True),
]


@dataclass(frozen=True)
class AnalysePeriode:
    debut: date
    fin: date
    nombre_de_saisons: int
    pic: MesureOni
    creux: MesureOni
    anomalie_moyenne: Decimal
    saisons_el_nino_consecutives: int
    saisons_la_nina_consecutives: int

    @property
    def episode_el_nino(self) -> bool:
        return self.saisons_el_nino_consecutives >= DUREE_MINIMALE_SAISONS

    @property
    def episode_la_nina(self) -> bool:
        return self.saisons_la_nina_consecutives >= DUREE_MINIMALE_SAISONS

    @property
    def intensite_du_pic(self) -> str | None:
        """Catégorie du pic chaud, seulement si un épisode El Niño est détecté."""
        if not self.episode_el_nino:
            return None
        return categorie_intensite(self.pic.anomalie)


def categorie_intensite(anomalie: Decimal) -> str | None:
    """Ex. 2.37 -> "très forte" ; 0.3 -> None (sous le seuil). Fonctionne aussi pour La Niña."""
    for seuil, libelle in CATEGORIES_INTENSITE:
        if abs(anomalie) >= seuil:
            return libelle
    return None


def plus_longue_sequence(anomalies: list[Decimal], condition: Callable[[Decimal], bool]) -> int:
    """Nombre maximal de saisons consécutives qui respectent la condition."""
    meilleure = 0
    en_cours = 0
    for anomalie in anomalies:
        en_cours = en_cours + 1 if condition(anomalie) else 0
        meilleure = max(meilleure, en_cours)
    return meilleure


def analyser_periode(debut: date, fin: date, mesures: list[MesureOni]) -> AnalysePeriode:
    """Calcule pic, creux, moyenne et durées au-dessus des seuils (mesures triées par date)."""
    if not mesures:
        raise PeriodeVide(f"Aucune observation entre {debut} et {fin}.")

    anomalies = [mesure.anomalie for mesure in mesures]
    moyenne = sum(anomalies) / len(anomalies)

    return AnalysePeriode(
        debut=debut,
        fin=fin,
        nombre_de_saisons=len(mesures),
        pic=max(mesures, key=lambda mesure: mesure.anomalie),
        creux=min(mesures, key=lambda mesure: mesure.anomalie),
        anomalie_moyenne=moyenne.quantize(Decimal("0.01")),
        saisons_el_nino_consecutives=plus_longue_sequence(
            anomalies, lambda anomalie: anomalie >= SEUIL_EL_NINO
        ),
        saisons_la_nina_consecutives=plus_longue_sequence(
            anomalies, lambda anomalie: anomalie <= SEUIL_LA_NINA
        ),
    )
