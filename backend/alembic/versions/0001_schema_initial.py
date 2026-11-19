"""Schéma initial : sources, indices, imports et observations.

Migration générée par --autogenerate puis relue : contraintes nommées,
clés étrangères en RESTRICT (on ne supprime pas une source qui a des données)
et contrainte d'unicité (indice_id, date_periode) contre les doublons.

Revision ID: 0001
Revises:
Create Date: 2026-11-19 12:56:47.552278

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Crée les tables dans l'ordre des dépendances (parents avant enfants)."""
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nom", sa.String(length=150), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sources")),
        sa.UniqueConstraint("nom", name=op.f("uq_sources_nom")),
    )
    op.create_table(
        "indices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("nom", sa.String(length=150), nullable=False),
        sa.Column("unite", sa.String(length=20), nullable=False),
        sa.Column("version", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["sources.id"],
            name=op.f("fk_indices_source_id_sources"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_indices")),
        sa.UniqueConstraint("code", name=op.f("uq_indices_code")),
    )
    op.create_table(
        "imports",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("indice_id", sa.Integer(), nullable=False),
        sa.Column("url_fichier", sa.Text(), nullable=False),
        sa.Column(
            "date_extraction",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("termine_le", sa.DateTime(timezone=True), nullable=True),
        sa.Column("empreinte_sha256", sa.String(length=64), nullable=True),
        sa.Column("statut", sa.String(length=20), server_default="en_cours", nullable=False),
        sa.Column("lignes_lues", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lignes_inserees", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lignes_mises_a_jour", sa.Integer(), server_default="0", nullable=False),
        sa.Column("lignes_ignorees", sa.Integer(), server_default="0", nullable=False),
        sa.Column("message_erreur", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "statut IN ('en_cours', 'reussi', 'echoue')", name=op.f("ck_imports_statut_valide")
        ),
        sa.CheckConstraint(
            "lignes_lues >= 0 AND lignes_inserees >= 0 AND lignes_mises_a_jour >= 0 AND lignes_ignorees >= 0",
            name=op.f("ck_imports_compteurs_positifs"),
        ),
        sa.ForeignKeyConstraint(
            ["indice_id"],
            ["indices.id"],
            name=op.f("fk_imports_indice_id_indices"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_imports")),
    )
    op.create_index(op.f("ix_imports_indice_id"), "imports", ["indice_id"], unique=False)
    op.create_table(
        "observations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("indice_id", sa.Integer(), nullable=False),
        sa.Column("import_id", sa.Integer(), nullable=False),
        sa.Column("saison", sa.String(length=3), nullable=False),
        sa.Column("annee", sa.SmallInteger(), nullable=False),
        sa.Column("date_periode", sa.Date(), nullable=False),
        sa.Column("temperature_totale", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("anomalie", sa.Numeric(precision=4, scale=2), nullable=False),
        sa.CheckConstraint(
            "saison IN ('DJF', 'JFM', 'FMA', 'MAM', 'AMJ', 'MJJ', 'JJA', 'JAS', 'ASO', 'SON', 'OND', 'NDJ')",
            name=op.f("ck_observations_saison_valide"),
        ),
        sa.CheckConstraint(
            "annee BETWEEN 1950 AND 2100", name=op.f("ck_observations_annee_plausible")
        ),
        sa.CheckConstraint(
            "anomalie BETWEEN -5 AND 5", name=op.f("ck_observations_anomalie_plausible")
        ),
        sa.ForeignKeyConstraint(
            ["import_id"],
            ["imports.id"],
            name=op.f("fk_observations_import_id_imports"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["indice_id"],
            ["indices.id"],
            name=op.f("fk_observations_indice_id_indices"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_observations")),
        sa.UniqueConstraint("indice_id", "date_periode", name="uq_observations_indice_periode"),
    )
    op.create_index(op.f("ix_observations_import_id"), "observations", ["import_id"], unique=False)


def downgrade() -> None:
    """Supprime les tables dans l'ordre inverse (enfants avant parents)."""
    op.drop_index(op.f("ix_observations_import_id"), table_name="observations")
    op.drop_table("observations")
    op.drop_index(op.f("ix_imports_indice_id"), table_name="imports")
    op.drop_table("imports")
    op.drop_table("indices")
    op.drop_table("sources")
