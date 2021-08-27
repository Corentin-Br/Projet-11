import pytest

from application import server
from .test_unit_server import clubs, competitions


@pytest.fixture
def client():
    app = server.app
    with app.test_client() as client:
        yield client


def test_purchase_places_sends_code_500_if_cant_buy_places(client, clubs, competitions):
    request_form = {
        "competition": "Competition one",
        "club": "Club one",
        "places": "13"
    }
    response = client.post('/purchasePlaces', data=request_form)
    assert response.status_code == 500


def test_purchase_places_sends_code_200_if_can_buy_places(client, clubs, competitions):
    request_form = {
        "competition": "Competition one",
        "club": "Club one",
        "places": "1"
    }
    response = client.post('/purchasePlaces', data=request_form)
    assert response.status_code == 200
