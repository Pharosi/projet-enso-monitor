"""Orchestration de l'ETL : Extraction -> Transformation -> Chargement, avec traçabilité.

Transactions :
1. la ligne d'import « en_cours » est validée tout de suite (trace conservée quoi qu'il arrive) ;
2. les observations et le bilan sont validés ensemble, en une seule transaction :
   en cas d'erreur, rien n'est écrit à moitié (annulation), et l'import passe « echoue ».
"""

from collections.abc import Callable
from dataclasses import dataclass

from sqlalchemy.orm import Session

from enso.domaine.oni import INDICE_ONI, SOURCE_NOAA_CPC
from enso.etl.chargement import charger_mesures
from enso.etl.extraction import calculer_empreinte, telecharger_fichier
from enso.etl.transformation import lire_fichier_oni, transformer_observations
from enso.infrastructure.depot_imports import (
    demarrer_import,
    enregistrer_echec,
    enregistrer_succes,
)
from enso.infrastructure.depot_referentiel import obtenir_ou_creer_indice, obtenir_ou_creer_source
from enso.infrastructure.modeles import Import


@dataclass(frozen=True)
class BilanImport:
    import_id: int
    lignes_lues: int
    lignes_inserees: int
    lignes_mises_a_jour: int
    lignes_inchangees: int
    lignes_ignorees: int


def executer_import_oni(
    session: Session,
    url: str,
    telecharger: Callable[[str], bytes] = telecharger_fichier,
) -> BilanImport:
    """Importe la série ONI. `telecharger` est remplaçable pour tester sans Internet."""
    source = obtenir_ou_creer_source(session, SOURCE_NOAA_CPC)
    indice = obtenir_ou_creer_indice(session, INDICE_ONI, source)
    import_ = demarrer_import(session, indice.id, url)
    session.commit()

    try:
        bilan = importer_observations(session, indice.id, import_, url, telecharger)
    except Exception as erreur:
        session.rollback()
        enregistrer_echec(import_, f"{type(erreur).__name__} : {erreur}")
        session.commit()
        raise  # l'erreur est tracée puis remontée : elle n'est jamais cachée

    session.commit()
    return bilan


def importer_observations(
    session: Session,
    indice_id: int,
    import_: Import,
    url: str,
    telecharger: Callable[[str], bytes],
) -> BilanImport:
    contenu = telecharger(url)  # Extraction
    resultat = transformer_observations(lire_fichier_oni(contenu))  # Transformation
    plan = charger_mesures(session, indice_id, import_.id, resultat.mesures)  # Chargement

    enregistrer_succes(
        import_,
        empreinte_sha256=calculer_empreinte(contenu),
        lignes_lues=resultat.lignes_lues,
        lignes_inserees=len(plan.a_inserer),
        lignes_mises_a_jour=len(plan.a_mettre_a_jour),
        lignes_ignorees=resultat.lignes_ignorees,
    )
    return BilanImport(
        import_id=import_.id,
        lignes_lues=resultat.lignes_lues,
        lignes_inserees=len(plan.a_inserer),
        lignes_mises_a_jour=len(plan.a_mettre_a_jour),
        lignes_inchangees=plan.inchangees,
        lignes_ignorees=resultat.lignes_ignorees,
    )
