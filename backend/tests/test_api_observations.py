"""Test minimal n°2 du sujet : route FastAPI filtrée par période.

On vérifie la réponse attendue pour une période valide, puis le traitement
des entrées invalides (code 422) et l'absence de données (code 404).
"""

import pytest

ROUTE = "/api/v1/observations"


@pytest.mark.usefixtures("extrait_1997_1998_importe")
def test_une_periode_valide_renvoie_les_observations_attendues(client_api):
    reponse = client_api.get(ROUTE, params={"debut": "1998-01-01", "fin": "1998-12-01"})

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["nombre"] == 12
    assert [o["saison"] for o in corps["observations"]][:3] == ["DJF", "JFM", "FMA"]
    assert corps["observations"][0] == {
        "saison": "DJF",
        "annee": 1998,
        "date_periode": "1998-01-01",
        "anomalie": 2.22,
        "temperature_totale": 28.85,
    }


@pytest.mark.usefixtures("extrait_1997_1998_importe")
def test_la_reponse_indique_l_unite_et_la_source(client_api):
    corps = client_api.get(ROUTE).json()

    assert corps["nombre"] == 24
    assert corps["indice"]["unite"] == "°C"
    assert corps["indice"]["version"] == "ONI v6 (ERSST.v6)"
    assert corps["source"]["nom"] == "NOAA Climate Prediction Center"
    assert corps["source"]["derniere_extraction"] is not None


@pytest.mark.usefixtures("extrait_1997_1998_importe")
@pytest.mark.parametrize(
    "parametres",
    [
        {"debut": "1999-01-01", "fin": "1998-01-01"},  # début après la fin
        {"debut": "1998-13-01"},  # mois inexistant
        {"debut": "hier"},  # pas une date
        {"annee": "1998"},  # paramètre inconnu
    ],
)
def test_une_entree_invalide_renvoie_422(client_api, parametres):
    reponse = client_api.get(ROUTE, params=parametres)

    assert reponse.status_code == 422


def test_sans_donnees_importees_la_route_renvoie_404(client_api):
    reponse = client_api.get(ROUTE)

    assert reponse.status_code == 404
