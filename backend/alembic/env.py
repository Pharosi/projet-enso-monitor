"""Environnement Alembic : relie les migrations à la configuration et aux modèles.

Commandes usuelles (depuis backend/) :
    alembic upgrade head                      # appliquer toutes les migrations
    alembic downgrade -1                      # annuler la dernière migration
    alembic revision --autogenerate -m "..."  # proposer une migration à relire
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from enso.config import obtenir_parametres
from enso.infrastructure.modeles import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# L'URL vient du fichier .env (via pydantic-settings), jamais d'alembic.ini.
config.set_main_option("sqlalchemy.url", obtenir_parametres().url_base_de_donnees)

# Les modèles SQLAlchemy servent de référence pour --autogenerate.
target_metadata = Base.metadata


def executer_migrations_hors_ligne() -> None:
    """Génère le SQL sans se connecter (alembic upgrade head --sql)."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def executer_migrations_en_ligne() -> None:
    """Applique les migrations directement sur la base."""
    moteur = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with moteur.connect() as connexion:
        context.configure(connection=connexion, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    executer_migrations_hors_ligne()
else:
    executer_migrations_en_ligne()
