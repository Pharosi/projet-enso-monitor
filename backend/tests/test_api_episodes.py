"""Tests des routes de comparaison d'épisodes."""

import pytest

ROUTE = "/api/v1/episodes/comparaison"
ANNEES_1997_ET_1998 = {
    "debut_a": "1997-01-01",
    "fin_a": "1997-12-01",
    "debut_b": "1998-01-01",
    "fin_b": "1998-12-01",
}


@pytest.mark.usefixtures("extrait_1997_1998_importe")
def test_la_comparaison_renvoie_analyses_regles_et_limites(client_api):
    reponse = client_api.get(ROUTE, params=ANNEES_1997_ET_1998)

    assert reponse.status_code == 200
    corps = reponse.json()
    assert corps["periode_a"]["pic"]["anomalie"] == 2.37
    assert corps["periode_a"]["episode_el_nino"] is True
    assert corps["periode_b"]["episode_la_nina"] is True
    assert len(corps["periode_a"]["observations"]) == 12
    assert corps["regles"]["seuil_el_nino"] == 0.5
    assert corps["regles"]["duree_minimale_saisons"] == 5
    assert len(corps["interpretation"]) == 4
    assert any("Super El Niño" in limite for limite in corps["limites"])


@pytest.mark.usefixtures("extrait_1997_1998_importe")
@pytest.mark.parametrize(
    "parametres",
    [
        {"debut_a": "1997-01-01"},  # périodes incomplètes
        {**ANNEES_1997_ET_1998, "fin_b": "1997-01-01"},  # période B inversée
    ],
)
def test_une_comparaison_invalide_renvoie_422(client_api, parametres):
    assert client_api.get(ROUTE, params=parametres).status_code == 422


@pytest.mark.usefixtures("extrait_1997_1998_importe")
def test_une_periode_sans_observation_renvoie_404(client_api):
    parametres = {**ANNEES_1997_ET_1998, "debut_a": "1960-01-01", "fin_a": "1960-12-01"}

    reponse = client_api.get(ROUTE, params=parametres)

    assert reponse.status_code == 404
    assert "1960-01-01" in reponse.json()["erreur"]["message"]


def test_les_episodes_de_reference_sont_proposes(client_api):
    episodes = client_api.get("/api/v1/episodes/references").json()

    libelles = [episode["libelle"] for episode in episodes]
    assert "El Niño 1997-1998" in libelles
    assert "El Niño 2015-2016" in libelles
    assert episodes[-1]["en_cours"] is True
