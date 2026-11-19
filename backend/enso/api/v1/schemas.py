"""Schémas Pydantic de l'API v1 : ce que l'API accepte (entrées) et renvoie (sorties).

Pydantic valide automatiquement les entrées : une date mal formée ou une période
incohérente est refusée avec un code 422 avant même d'arriver au code métier.
Les schémas servent aussi à générer la documentation OpenAPI (/docs).
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from enso.domaine.oni import MesureOni

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


def observation_depuis_mesure(mesure: MesureOni) -> ObservationReponse:
    """Conversion commune domaine -> JSON (Decimal -> float), utilisée par toutes les routes."""
    return ObservationReponse(
        saison=mesure.saison,
        annee=mesure.annee,
        date_periode=mesure.date_periode,
        anomalie=float(mesure.anomalie),
        temperature_totale=float(mesure.temperature_totale),
    )


class SerieObservationsReponse(BaseModel):
    indice: IndiceReponse
    source: SourceReponse
    debut: date | None
    fin: date | None
    nombre: int = Field(description="Nombre d'observations renvoyées")
    observations: list[ObservationReponse]


# ---------- Comparaison d'épisodes ----------


class FiltreComparaison(BaseModel):
    """Deux périodes obligatoires : ?debut_a=…&fin_a=…&debut_b=…&fin_b=…"""

    model_config = ConfigDict(extra="forbid")

    debut_a: date = Field(examples=["1997-01-01"])
    fin_a: date = Field(examples=["1998-06-01"])
    debut_b: date = Field(examples=["2015-01-01"])
    fin_b: date = Field(examples=["2016-06-01"])

    @model_validator(mode="after")
    def verifier_ordre_des_dates(self) -> "FiltreComparaison":
        if self.debut_a > self.fin_a:
            raise ValueError("Période A : la date de début doit précéder la date de fin.")
        if self.debut_b > self.fin_b:
            raise ValueError("Période B : la date de début doit précéder la date de fin.")
        return self


class EpisodeDeReferenceReponse(BaseModel):
    identifiant: str = Field(examples=["el-nino-1997-1998"])
    libelle: str = Field(examples=["El Niño 1997-1998"])
    debut: date
    fin: date
    en_cours: bool


class AnalyseReponse(BaseModel):
    debut: date
    fin: date
    nombre_de_saisons: int
    pic: ObservationReponse
    creux: ObservationReponse
    anomalie_moyenne: float
    saisons_el_nino_consecutives: int
    saisons_la_nina_consecutives: int
    episode_el_nino: bool
    episode_la_nina: bool
    intensite_du_pic: str | None = Field(description="Convention d'usage, non officielle")
    observations: list[ObservationReponse]


class ReglesReponse(BaseModel):
    """Règles appliquées, affichées avec chaque résultat (exigence de transparence)."""

    indice: str = Field(examples=["ONI v6 (ERSST.v6)"])
    seuil_el_nino: float = Field(examples=[0.5])
    seuil_la_nina: float = Field(examples=[-0.5])
    duree_minimale_saisons: int = Field(examples=[5])
    categories_intensite: dict[str, float]


class ComparaisonReponse(BaseModel):
    periode_a: AnalyseReponse
    periode_b: AnalyseReponse
    regles: ReglesReponse
    interpretation: list[str]
    limites: list[str]
