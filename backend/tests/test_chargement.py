"""Tests de la logique de chargement : insertion, mise à jour ou aucune action."""

from datetime import date
from decimal import Decimal

from enso.domaine.oni import MesureOni
from enso.etl.chargement import planifier_chargement


def mesure(mois: int, anomalie: str) -> MesureOni:
    return MesureOni(
        saison="DJF",
        annee=1998,
        date_periode=date(1998, mois, 1),
        temperature_totale=Decimal("28.85"),
        anomalie=Decimal(anomalie),
    )


def test_le_plan_distingue_nouvelles_revisees_et_inchangees():
    existantes = {
        date(1998, 1, 1): (Decimal("28.85"), Decimal("2.22")),  # identique
        date(1998, 2, 1): (Decimal("28.85"), Decimal("1.50")),  # révisée par la NOAA
    }
    mesures = [mesure(1, "2.22"), mesure(2, "1.93"), mesure(3, "1.40")]

    plan = planifier_chargement(mesures, existantes)

    assert [m.date_periode.month for m in plan.a_inserer] == [3]
    assert [m.date_periode.month for m in plan.a_mettre_a_jour] == [2]
    assert plan.inchangees == 1
