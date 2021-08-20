import pytest

from application import server


@pytest.fixture
def client():
    app = server.app
    with app.test_client() as client:
        yield client


mock_competitions = [{
    "name": "A specific competition",
    "date": "2020-03-27 10:00:00",
    "numberOfPlaces": "25",
    "places_taken": {}
},
    {
        "name": "Another competition",
        "date": "2020-03-27 10:00:00",
        "numberOfPlaces": "7",
        "places_taken": {}
    }
]

mock_clubs = [
    {
     "name": "A specific club",
     "email": "corentin@gmail.com",
     "points": "18"
    },
    {
     "name": "Another club",
     "email": "bravo@gmail.com",
     "points": "2"
    },
]


server.clubs = mock_clubs
server.competitions = mock_competitions


def test_one_time_purchase_places_is_limited_to_twelve(client):
    request_form = {
        "competition": "A specific competition",
        "club": "A specific club",
        "places": "15"
    }
    response = client.post('/purchasePlaces', data=request_form)
    assert response.status_code == 500


def test_multiple_time_purchase_places_is_limited_to_twelve(client):
    request_forms = [{
        "competition": "A specific competition",
        "club": "A specific club",
        "places": "8"},
        {"competition": "A specific competition",
         "club": "A specific club",
         "places": "5"}
        ]
    first_response = client.post('/purchasePlaces', data=request_forms[0])
    assert first_response.status_code == 200
    second_response = client.post('/purchasePlaces', data=request_forms[1])
    assert second_response.status_code == 500


def test_purchase_places_is_limited_to_available_places(client):
    request_form = {
        "competition": "Another competition",
        "club": "A specific club",
        "places": "9"
    }
    response = client.post('/purchasePlaces', data=request_form)
    assert response.status_code == 500
