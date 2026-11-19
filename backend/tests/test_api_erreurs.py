"""Tests du format d'erreur unique et de la politique CORS."""

from fastapi.testclient import TestClient

from enso.api.main import creer_application
from enso.infrastructure.base_de_donnees import obtenir_session

ROUTE = "/api/v1/observations"


def test_une_erreur_de_validation_indique_le_champ_en_cause(client_api):
    reponse = client_api.get(ROUTE, params={"debut": "1998-13-01"})

    assert reponse.status_code == 422
    erreur = reponse.json()["erreur"]
    assert erreur["code"] == 422
    assert erreur["message"] == "Paramètres de requête invalides."
    assert erreur["details"][0]["champ"] == "debut"


def test_une_periode_inversee_renvoie_un_message_en_francais(client_api):
    reponse = client_api.get(ROUTE, params={"debut": "1999-01-01", "fin": "1998-01-01"})

    message = reponse.json()["erreur"]["details"][0]["message"]
    assert message == "La date de début doit être antérieure ou égale à la date de fin."


def test_l_absence_de_donnees_suit_le_meme_format(client_api):
    reponse = client_api.get(ROUTE)

    assert reponse.status_code == 404
    assert "python -m enso.etl" in reponse.json()["erreur"]["message"]


def test_une_route_inconnue_suit_le_meme_format(client_api):
    reponse = client_api.get("/api/v1/inexistante")

    assert reponse.status_code == 404
    assert reponse.json()["erreur"]["code"] == 404


def test_une_erreur_inattendue_ne_revele_aucun_detail_technique():
    application = creer_application()

    def session_en_panne():
        raise RuntimeError("mot de passe de la base : secret")

    application.dependency_overrides[obtenir_session] = session_en_panne
    client = TestClient(application, raise_server_exceptions=False)

    reponse = client.get(ROUTE)

    assert reponse.status_code == 500
    assert reponse.json()["erreur"]["message"] == "Erreur interne du serveur."
    assert "secret" not in reponse.text


def test_cors_autorise_le_frontend_local(client_api):
    reponse = client_api.get("/api/v1/sante", headers={"Origin": "http://localhost:5173"})

    assert reponse.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_refuse_une_origine_inconnue(client_api):
    reponse = client_api.get("/api/v1/sante", headers={"Origin": "https://site-malveillant.test"})

    assert "access-control-allow-origin" not in reponse.headers
