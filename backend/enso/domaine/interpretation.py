"""Rédaction d'une interprétation prudente de la comparaison de deux périodes.

Les phrases décrivent uniquement ce que mesure l'ONI ; elles ne parlent ni
d'impacts ni de prévision. Les limites sont toujours affichées avec le résultat.
"""

from decimal import Decimal

from enso.domaine.episodes import DUREE_MINIMALE_SAISONS, SEUIL_EL_NINO, AnalysePeriode
from enso.domaine.oni import MesureOni

LIMITES = [
    "Les catégories d'intensité (faible à très forte) sont une convention d'usage, pas une "
    "classification officielle de la NOAA. Le terme « Super El Niño » n'a pas de définition "
    "scientifique.",
    "L'ONI décrit uniquement la température de surface de la mer dans la région Niño 3.4 : "
    "il ne mesure pas les impacts (pluies, sécheresses, températures locales).",
    "Les durées sont comptées à l'intérieur des périodes choisies : un épisode commencé "
    "avant le début de la période peut être plus long.",
    "L'ONI ne retire pas la tendance au réchauffement global ; le RONI, utilisé par la NOAA "
    "pour la surveillance officielle depuis 2026, la corrige. Comparer des décennies "
    "éloignées demande donc de la prudence.",
    "Les valeurs des deux derniers mois peuvent encore être révisées par la NOAA.",
    "Aucune prévision n'est réalisée : la comparaison porte uniquement sur des mesures passées.",
]


def formater_anomalie(valeur: Decimal) -> str:
    """Decimal("2.37") -> "+2,37 °C" (notation française, signe toujours affiché)."""
    return f"{valeur:+.2f} °C".replace(".", ",")


def decrire_mesure(mesure: MesureOni) -> str:
    return f"{formater_anomalie(mesure.anomalie)} ({mesure.saison} {mesure.annee})"


def phrase_pic(nom: str, analyse: AnalysePeriode) -> str:
    phrase = f"Période {nom} : pic de l'ONI à {decrire_mesure(analyse.pic)}"
    if analyse.intensite_du_pic is None:
        return phrase + ", sans épisode El Niño au sens de la NOAA."
    return phrase + f", intensité « {analyse.intensite_du_pic} » selon la convention usuelle."


def phrase_ecart_des_pics(analyse_a: AnalysePeriode, analyse_b: AnalysePeriode) -> str:
    ecart = analyse_b.pic.anomalie - analyse_a.pic.anomalie
    if ecart == 0:
        return "Les deux pics ont la même valeur."
    plus_fort, plus_faible = ("B", "A") if ecart > 0 else ("A", "B")
    ecart_texte = formater_anomalie(abs(ecart)).removeprefix("+")
    return (
        f"Le pic de la période {plus_fort} dépasse celui de la période {plus_faible} "
        f"de {ecart_texte}."
    )


def phrase_durees(analyse_a: AnalysePeriode, analyse_b: AnalysePeriode) -> str:
    seuil = formater_anomalie(SEUIL_EL_NINO)
    return (
        f"Seuil El Niño ({seuil}) dépassé pendant {analyse_a.saisons_el_nino_consecutives} "
        f"saisons consécutives pour la période A, contre "
        f"{analyse_b.saisons_el_nino_consecutives} pour la période B "
        f"(un épisode exige au moins {DUREE_MINIMALE_SAISONS} saisons)."
    )


def rediger_interpretation(analyse_a: AnalysePeriode, analyse_b: AnalysePeriode) -> list[str]:
    return [
        phrase_pic("A", analyse_a),
        phrase_pic("B", analyse_b),
        phrase_ecart_des_pics(analyse_a, analyse_b),
        phrase_durees(analyse_a, analyse_b),
    ]
