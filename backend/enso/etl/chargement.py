"""Chargement : écriture des mesures validées dans PostgreSQL, sans doublon.

Pour chaque mesure, on compare avec ce qui est déjà en base :
- période absente          -> insertion ;
- période présente, valeur différente -> mise à jour (la NOAA révise les mois récents) ;
- période présente, même valeur      -> rien à faire.
Ré-exécuter l'import ne crée donc jamais de doublon (import idempotent).
"""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from enso.domaine.oni import MesureOni
from enso.infrastructure.depot_observations import (
    ValeursParPeriode,
    inserer_observations,
    lire_valeurs_existantes,
    mettre_a_jour_observations,
)


@dataclass(frozen=True)
class PlanDeChargement:
    a_inserer: list[MesureOni]
    a_mettre_a_jour: list[MesureOni]
    inchangees: int


def planifier_chargement(
    mesures: list[MesureOni], existantes: ValeursParPeriode
) -> PlanDeChargement:
    """Classe chaque mesure (logique pure, testable sans base de données)."""
    a_inserer: list[MesureOni] = []
    a_mettre_a_jour: list[MesureOni] = []
    inchangees = 0

    for mesure in mesures:
        valeurs_en_base = existantes.get(mesure.date_periode)
        if valeurs_en_base is None:
            a_inserer.append(mesure)
        elif valeurs_en_base != (mesure.temperature_totale, mesure.anomalie):
            a_mettre_a_jour.append(mesure)
        else:
            inchangees += 1

    return PlanDeChargement(a_inserer, a_mettre_a_jour, inchangees)


def charger_mesures(
    session: Session, indice_id: int, import_id: int, mesures: list[MesureOni]
) -> PlanDeChargement:
    existantes = lire_valeurs_existantes(session, indice_id)
    plan = planifier_chargement(mesures, existantes)

    inserer_observations(session, indice_id, import_id, plan.a_inserer)
    mettre_a_jour_observations(session, indice_id, import_id, plan.a_mettre_a_jour)
    return plan
