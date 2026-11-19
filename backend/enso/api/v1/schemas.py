"""Schémas Pydantic de l'API v1 : ce que l'API accepte (entrées) et renvoie (sorties).

Pydantic valide automatiquement les entrées : une date mal formée ou une période
incohérente est refusée avec un code 422 avant même d'arriver au code métier.
Les schémas servent aussi à générer la documentation OpenAPI (/docs).
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------- Entrées ----------


class FiltrePeriode(BaseModel):
    """Paramètres de requête ?debut=AAAA-MM-JJ&fin=AAAA-MM-JJ (tous deux facultatifs)."""

    model_config = ConfigDict(extra="forbid")  # un paramètre inconnu est refusé

    debut: date | None = Field(
        default=None, description="Première période incluse", examples=["1997-01-01"]
    )
    fin: date | None = Field(
        default=None, description="Dernière période incluse", examples=["1998-12-01"]
    )

    @model_validator(mode="after")
    def verifier_ordre_des_dates(self) -> "FiltrePeriode":
        if self.debut is not None and self.fin is not None and self.debut > self.fin:
            raise ValueError("La date de début doit être antérieure ou égale à la date de fin.")
        return self


# ---------- Sorties ----------


class IndiceReponse(BaseModel):
    code: str = Field(examples=["ONI"])
    nom: str = Field(examples=["Oceanic Niño Index"])
    unite: str = Field(examples=["°C"])
    version: str = Field(examples=["ONI v6 (ERSST.v6)"])


class SourceReponse(BaseModel):
    nom: str = Field(examples=["NOAA Climate Prediction Center"])
    url: str
    derniere_extraction: datetime | None = Field(
        description="Date du dernier import réussi depuis la NOAA"
    )


class ObservationReponse(BaseModel):
    saison: str = Field(description="Saison glissante de trois mois", examples=["DJF"])
    annee: int = Field(examples=[1998])
    date_periode: date = Field(description="Premier jour du mois central", examples=["1998-01-01"])
    anomalie: float = Field(description="Valeur de l'ONI en °C", examples=[2.22])
    temperature_totale: float = Field(description="Température moyenne en °C", examples=[28.85])


class SerieObservationsReponse(BaseModel):
    indice: IndiceReponse
    source: SourceReponse
    debut: date | None
    fin: date | None
    nombre: int = Field(description="Nombre d'observations renvoyées")
    observations: list[ObservationReponse]
