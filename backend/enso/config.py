"""Configuration de l'application, lue depuis les variables d'environnement.

Aucun secret n'est écrit dans le code : les valeurs viennent du fichier .env
(en développement) ou de l'environnement du conteneur (en production).
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Racine du dépôt : backend/enso/config.py -> parents[2]
RACINE_DU_DEPOT = Path(__file__).resolve().parents[2]


class Parametres(BaseSettings):
    """Paramètres validés par Pydantic : une valeur manquante bloque le démarrage."""

    model_config = SettingsConfigDict(
        env_file=RACINE_DU_DEPOT / ".env",
        extra="ignore",  # le .env contient aussi les variables POSTGRES_* de Docker
    )

    url_base_de_donnees: str

    # Fichier officiel de l'ONI v6 publié par la NOAA CPC (mis à jour chaque mois).
    url_fichier_oni: str = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"

    # Origines autorisées à appeler l'API depuis un navigateur (frontend Vite en local).
    # Dans le .env, au format JSON : ORIGINES_CORS=["https://enso.exemple.fr"]
    origines_cors: list[str] = ["http://localhost:5173"]


@lru_cache
def obtenir_parametres() -> Parametres:
    """Charge les paramètres une seule fois puis les réutilise (cache)."""
    return Parametres()
