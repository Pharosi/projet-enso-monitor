"""Accès aux données de référence : sources et indices.

« Obtenir ou créer » rend l'ETL ré-exécutable : la source et l'indice ne sont
créés qu'au premier import, puis simplement relus.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from enso.domaine.oni import DescriptionIndice, DescriptionSource
from enso.infrastructure.modeles import Indice, Source


def obtenir_ou_creer_source(session: Session, description: DescriptionSource) -> Source:
    source = session.scalar(select(Source).where(Source.nom == description.nom))
    if source is not None:
        return source

    source = Source(nom=description.nom, url=description.url, description=description.description)
    session.add(source)
    session.flush()  # envoie l'INSERT pour obtenir l'identifiant, sans valider la transaction
    return source


def obtenir_ou_creer_indice(
    session: Session, description: DescriptionIndice, source: Source
) -> Indice:
    indice = session.scalar(select(Indice).where(Indice.code == description.code))
    if indice is not None:
        return indice

    indice = Indice(
        code=description.code,
        nom=description.nom,
        unite=description.unite,
        version=description.version,
        description=description.description,
        source_id=source.id,
    )
    session.add(indice)
    session.flush()
    return indice
