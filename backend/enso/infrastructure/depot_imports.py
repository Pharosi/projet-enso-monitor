"""Accès à la table imports : trace de chaque exécution de l'ETL."""

from sqlalchemy import func
from sqlalchemy.orm import Session

from enso.infrastructure.modeles import Import


def demarrer_import(session: Session, indice_id: int, url_fichier: str) -> Import:
    import_ = Import(indice_id=indice_id, url_fichier=url_fichier, statut="en_cours")
    session.add(import_)
    session.flush()
    return import_


def enregistrer_succes(
    import_: Import,
    empreinte_sha256: str,
    lignes_lues: int,
    lignes_inserees: int,
    lignes_mises_a_jour: int,
    lignes_ignorees: int,
) -> None:
    import_.statut = "reussi"
    import_.termine_le = func.now()
    import_.empreinte_sha256 = empreinte_sha256
    import_.lignes_lues = lignes_lues
    import_.lignes_inserees = lignes_inserees
    import_.lignes_mises_a_jour = lignes_mises_a_jour
    import_.lignes_ignorees = lignes_ignorees


def enregistrer_echec(import_: Import, message_erreur: str) -> None:
    import_.statut = "echoue"
    import_.termine_le = func.now()
    import_.message_erreur = message_erreur
