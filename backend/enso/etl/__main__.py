"""Commande d'import : python -m enso.etl (depuis le dossier backend/).

Code de sortie 0 si l'import réussit, 1 sinon : un planificateur (cron) ou
Docker peut ainsi savoir si l'exécution s'est bien passée.
"""

import logging
import sys

from enso.config import obtenir_parametres
from enso.etl.pipeline import executer_import_oni
from enso.infrastructure.base_de_donnees import FabriqueDeSessions

journal = logging.getLogger("enso.etl")


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    url = obtenir_parametres().url_fichier_oni
    journal.info("Import de l'ONI depuis %s", url)

    with FabriqueDeSessions() as session:
        try:
            bilan = executer_import_oni(session, url)
        except Exception:
            journal.exception("Échec de l'import (statut enregistré dans la table imports)")
            return 1

    journal.info(
        "Import n°%s réussi : %s lues, %s insérées, %s mises à jour, %s inchangées, %s ignorées",
        bilan.import_id,
        bilan.lignes_lues,
        bilan.lignes_inserees,
        bilan.lignes_mises_a_jour,
        bilan.lignes_inchangees,
        bilan.lignes_ignorees,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
