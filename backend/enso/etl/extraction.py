"""Extraction : récupération du fichier ONI auprès de la NOAA."""

import hashlib

import httpx

DELAI_MAXIMAL_SECONDES = 30


def telecharger_fichier(url: str) -> bytes:
    """Télécharge le fichier et lève une erreur si la NOAA ne répond pas correctement."""
    reponse = httpx.get(url, timeout=DELAI_MAXIMAL_SECONDES, follow_redirects=True)
    reponse.raise_for_status()  # 404, 500… -> exception plutôt qu'un fichier vide
    return reponse.content


def calculer_empreinte(contenu: bytes) -> str:
    """Empreinte SHA-256 : identifie exactement la version du fichier importé."""
    return hashlib.sha256(contenu).hexdigest()
