"""Connexion à PostgreSQL via SQLAlchemy.

- le moteur (engine) gère un pool de connexions réutilisables ;
- une session représente une unité de travail : on l'ouvre, on l'utilise, on la ferme.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from enso.config import obtenir_parametres

moteur = create_engine(
    obtenir_parametres().url_base_de_donnees,
    pool_pre_ping=True,  # vérifie qu'une connexion est vivante avant de la réutiliser
)

FabriqueDeSessions = sessionmaker(bind=moteur, autoflush=False, expire_on_commit=False)


def obtenir_session() -> Iterator[Session]:
    """Fournit une session à une route FastAPI, puis la ferme quoi qu'il arrive."""
    session = FabriqueDeSessions()
    try:
        yield session
    finally:
        session.close()
