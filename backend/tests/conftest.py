"""Fixtures partagées par les tests qui ont besoin de PostgreSQL.

Les tests utilisent une base dédiée, « enso_test », dans le même conteneur que la base
de développement : les données de développement ne sont jamais touchées.
Chaque test démarre avec des tables vides.
"""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from enso.api.main import creer_application
from enso.config import obtenir_parametres
from enso.etl.pipeline import executer_import_oni
from enso.infrastructure.base_de_donnees import obtenir_session
from enso.infrastructure.modeles import Base

NOM_BASE_DE_TEST = "enso_test"
EXTRAIT_REEL = Path(__file__).parent / "donnees" / "oni_extrait_1997_1998.txt"


def creer_base_si_absente(url: URL) -> None:
    """Crée la base de test au premier lancement (CREATE DATABASE exige l'autocommit)."""
    moteur_admin = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with moteur_admin.connect() as connexion:
        existe = connexion.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :nom"), {"nom": url.database}
        )
        if not existe:
            # Nom fixe défini dans ce fichier (pas une saisie utilisateur).
            connexion.execute(text(f'CREATE DATABASE "{url.database}"'))
    moteur_admin.dispose()


@pytest.fixture(scope="session")
def moteur_de_test() -> Iterator[Engine]:
    """Un moteur pour toute la session de tests, avec un schéma recréé à neuf."""
    url = make_url(obtenir_parametres().url_base_de_donnees).set(database=NOM_BASE_DE_TEST)
    try:
        creer_base_si_absente(url)
    except OperationalError:
        pytest.skip("PostgreSQL indisponible : lancer `docker compose up -d db`")

    moteur = create_engine(url)
    # create_all suffit ici : `alembic check` garantit que modèles et migrations sont identiques.
    Base.metadata.drop_all(moteur)
    Base.metadata.create_all(moteur)
    yield moteur
    moteur.dispose()


@pytest.fixture
def session_de_test(moteur_de_test: Engine) -> Iterator[Session]:
    """Une session par test, puis vidage des tables pour isoler le test suivant."""
    with Session(moteur_de_test, expire_on_commit=False) as session:
        yield session

    with moteur_de_test.begin() as connexion:
        connexion.execute(
            text("TRUNCATE observations, imports, indices, sources RESTART IDENTITY CASCADE")
        )


@pytest.fixture
def extrait_1997_1998_importe(session_de_test: Session) -> None:
    """Remplit la base de test avec l'extrait réel 1997-1998 (24 saisons) via le vrai ETL."""

    def lire_extrait(url: str) -> bytes:
        return EXTRAIT_REEL.read_bytes()

    executer_import_oni(session_de_test, "https://exemple.test/oni.ascii.txt", lire_extrait)


@pytest.fixture
def client_api(session_de_test: Session) -> Iterator[TestClient]:
    """Client HTTP de test : l'API utilise la session de test au lieu de la vraie base."""
    application = creer_application()

    def obtenir_session_de_test() -> Iterator[Session]:
        yield session_de_test

    application.dependency_overrides[obtenir_session] = obtenir_session_de_test
    with TestClient(application) as client:
        yield client
