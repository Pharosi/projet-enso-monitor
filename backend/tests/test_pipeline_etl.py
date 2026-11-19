"""Tests d'intégration de l'ETL complet sur la base de test.

Le téléchargement est remplacé par la lecture d'un extrait réel du fichier NOAA :
les tests ne dépendent ni d'Internet ni de la disponibilité du site de la NOAA.
"""

import hashlib
from pathlib import Path

import pytest
from sqlalchemy import func, select, update

from enso.etl.pipeline import executer_import_oni
from enso.infrastructure.modeles import Import, Observation

EXTRAIT_REEL = Path(__file__).parent / "donnees" / "oni_extrait_1997_1998.txt"
URL_FICTIVE = "https://exemple.test/oni.ascii.txt"


def telecharger_extrait(url: str) -> bytes:
    return EXTRAIT_REEL.read_bytes()


def compter_observations(session) -> int:
    return session.scalar(select(func.count()).select_from(Observation))


def test_le_premier_import_insere_et_trace_les_observations(session_de_test):
    bilan = executer_import_oni(session_de_test, URL_FICTIVE, telecharger=telecharger_extrait)

    assert bilan.lignes_inserees == 24
    assert compter_observations(session_de_test) == 24

    import_ = session_de_test.get(Import, bilan.import_id)
    assert import_.statut == "reussi"
    assert import_.url_fichier == URL_FICTIVE
    assert import_.empreinte_sha256 == hashlib.sha256(EXTRAIT_REEL.read_bytes()).hexdigest()


def test_reimporter_le_meme_fichier_ne_cree_aucun_doublon(session_de_test):
    executer_import_oni(session_de_test, URL_FICTIVE, telecharger=telecharger_extrait)
    second = executer_import_oni(session_de_test, URL_FICTIVE, telecharger=telecharger_extrait)

    assert second.lignes_inserees == 0
    assert second.lignes_inchangees == 24
    assert compter_observations(session_de_test) == 24


def test_une_valeur_revisee_par_la_noaa_est_mise_a_jour(session_de_test):
    premier = executer_import_oni(session_de_test, URL_FICTIVE, telecharger=telecharger_extrait)
    session_de_test.execute(update(Observation).where(Observation.annee == 1998).values(anomalie=0))
    session_de_test.commit()

    second = executer_import_oni(session_de_test, URL_FICTIVE, telecharger=telecharger_extrait)

    assert second.lignes_mises_a_jour == 12
    assert second.import_id != premier.import_id


def test_un_echec_est_trace_et_aucune_observation_n_est_ecrite(session_de_test):
    def telechargement_en_panne(url: str) -> bytes:
        raise ConnectionError("NOAA injoignable")

    with pytest.raises(ConnectionError):
        executer_import_oni(session_de_test, URL_FICTIVE, telecharger=telechargement_en_panne)

    import_ = session_de_test.scalar(select(Import))
    assert import_.statut == "echoue"
    assert "NOAA injoignable" in import_.message_erreur
    assert compter_observations(session_de_test) == 0
