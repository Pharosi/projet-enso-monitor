"""Modèles SQLAlchemy : traduction du modèle de domaine en tables PostgreSQL.

    sources 1 ──< indices 1 ──< imports 1 ──< observations
                          └────────────────────<┘

- Une source (NOAA CPC) publie un ou plusieurs indices (ONI).
- Un indice est importé plusieurs fois (une ligne par exécution de l'ETL).
- Une observation appartient à un indice et garde la trace de l'import qui l'a écrite.

Les règles d'intégrité sont posées dans la base (UNIQUE, CHECK, clés étrangères) :
elles restent vraies même si le code applicatif contient un bug.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    MetaData,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from enso.domaine.oni import ANNEE_MAXIMALE, ANNEE_MINIMALE, ANOMALIE_MAXIMALE_ABSOLUE
from enso.domaine.saisons import SAISONS_VALIDES

# Nommage explicite des contraintes : des noms stables rendent les migrations
# Alembic prévisibles et les messages d'erreur lisibles.
CONVENTION_DE_NOMMAGE = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

STATUTS_IMPORT = ("en_cours", "reussi", "echoue")


def liste_sql(valeurs: tuple[str, ...]) -> str:
    """Transforme des constantes du code en liste SQL : ('a', 'b') -> 'a', 'b'.

    Utilisé uniquement pour des constantes définies ici, jamais pour une saisie utilisateur.
    """
    return ", ".join(f"'{valeur}'" for valeur in valeurs)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=CONVENTION_DE_NOMMAGE)


class Source(Base):
    """Organisme qui publie les données (ex. NOAA Climate Prediction Center)."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    nom: Mapped[str] = mapped_column(String(150), unique=True)
    url: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    indices: Mapped[list["Indice"]] = relationship(back_populates="source")


class Indice(Base):
    """Indice climatique suivi (ex. ONI), avec son unité et sa version méthodologique."""

    __tablename__ = "indices"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    nom: Mapped[str] = mapped_column(String(150))
    unite: Mapped[str] = mapped_column(String(20))
    version: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id", ondelete="RESTRICT"))

    source: Mapped[Source] = relationship(back_populates="indices")
    imports: Mapped[list["Import"]] = relationship(back_populates="indice")
    observations: Mapped[list["Observation"]] = relationship(back_populates="indice")


class Import(Base):
    """Trace d'une exécution de l'ETL : provenance, empreinte du fichier et compteurs."""

    __tablename__ = "imports"
    __table_args__ = (
        CheckConstraint(f"statut IN ({liste_sql(STATUTS_IMPORT)})", name="statut_valide"),
        CheckConstraint(
            "lignes_lues >= 0 AND lignes_inserees >= 0 "
            "AND lignes_mises_a_jour >= 0 AND lignes_ignorees >= 0",
            name="compteurs_positifs",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    indice_id: Mapped[int] = mapped_column(
        ForeignKey("indices.id", ondelete="RESTRICT"), index=True
    )
    url_fichier: Mapped[str] = mapped_column(Text)
    date_extraction: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    termine_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    empreinte_sha256: Mapped[str | None] = mapped_column(String(64))
    statut: Mapped[str] = mapped_column(String(20), server_default="en_cours")
    lignes_lues: Mapped[int] = mapped_column(server_default="0")
    lignes_inserees: Mapped[int] = mapped_column(server_default="0")
    lignes_mises_a_jour: Mapped[int] = mapped_column(server_default="0")
    lignes_ignorees: Mapped[int] = mapped_column(server_default="0")
    message_erreur: Mapped[str | None] = mapped_column(Text)

    indice: Mapped[Indice] = relationship(back_populates="imports")
    observations: Mapped[list["Observation"]] = relationship(back_populates="import_")


class Observation(Base):
    """Valeur de l'indice pour une saison glissante de trois mois (ex. DJF 1998).

    `date_periode` est le premier jour du mois central de la saison
    (DJF 1998 -> 1998-01-01) : c'est elle qui sert au filtrage temporel.
    """

    __tablename__ = "observations"
    __table_args__ = (
        # Une seule valeur par indice et par période : c'est le contrôle des doublons.
        # L'index créé par cette contrainte (indice_id, date_periode) sert aussi
        # au filtrage temporel de l'API.
        UniqueConstraint("indice_id", "date_periode", name="uq_observations_indice_periode"),
        CheckConstraint(f"saison IN ({liste_sql(SAISONS_VALIDES)})", name="saison_valide"),
        CheckConstraint(
            f"annee BETWEEN {ANNEE_MINIMALE} AND {ANNEE_MAXIMALE}", name="annee_plausible"
        ),
        CheckConstraint(
            f"anomalie BETWEEN -{ANOMALIE_MAXIMALE_ABSOLUE} AND {ANOMALIE_MAXIMALE_ABSOLUE}",
            name="anomalie_plausible",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    indice_id: Mapped[int] = mapped_column(ForeignKey("indices.id", ondelete="RESTRICT"))
    import_id: Mapped[int] = mapped_column(
        ForeignKey("imports.id", ondelete="RESTRICT"), index=True
    )
    saison: Mapped[str] = mapped_column(String(3))
    annee: Mapped[int] = mapped_column(SmallInteger)
    date_periode: Mapped[date] = mapped_column(Date)
    temperature_totale: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    anomalie: Mapped[Decimal] = mapped_column(Numeric(4, 2))

    indice: Mapped[Indice] = relationship(back_populates="observations")
    import_: Mapped[Import] = relationship(back_populates="observations")
