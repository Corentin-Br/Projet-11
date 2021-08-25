import datetime

import pytest

from application import server


@pytest.fixture
def client():
    app = server.app
    with app.test_client() as client:
        yield client


now = datetime.datetime.now()
tomorrow = now.replace(day=now.day+1).strftime(server.DATE_PATTERN)
yesterday = now.replace(day=now.day-1).strftime(server.DATE_PATTERN)

mock_competitions = [{
    "name": "Competition one",
    "date": tomorrow,
    "numberOfPlaces": "25",
    "places_taken": {"Club three": 5}
},
    {
        "name": "Competition two",
        "date": tomorrow,
        "numberOfPlaces": "7",
        "places_taken": {}
    },
    {
        "name": "Competition three",
        "date": yesterday,
        "numberOfPlaces": "50",
        "places_taken": {}
    }
]

mock_clubs = [
    {
     "name": "Club one",
     "email": "corentin@gmail.com",
     "points": "18"
    },
    {
     "name": "Club two",
     "email": "bravo@gmail.com",
     "points": "2"
    },
    {
     "name": "Club three",
     "email": "cbravo@gmail.com",
     "points": "30"
    }
]


server.clubs = mock_clubs
server.competitions = mock_competitions


def test_cant_buy_places_if_places_are_over_twelve():
    competition = mock_competitions[0]
    club = mock_clubs[0]
    required_places = 15
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more than twelve places per competition!", False)


def test_cant_buy_places_if_total_places_are_over_twelve():
    competition = mock_competitions[0]
    club = mock_clubs[2]
    required_places = 8
    already_taken_places = 5
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more than twelve places per competition!", False)


def test_purchasing_places_increase_the_number_of_taken_places(client):
    request_form = {
        "competition": "Competition one",
        "club": "Club one",
        "places": "9"
    }
    client.post('/purchasePlaces', data=request_form)
    assert mock_competitions[0]["places_taken"]["Club one"] == 9


def test_purchase_places_is_limited_to_available_places():
    competition = mock_competitions[1]
    club = mock_clubs[0]
    required_places = 9
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more places than there are available!", False)


def test_cant_buy_places_if_club_doesnt_have_enough_points():
    competition = mock_competitions[1]
    club = mock_clubs[1]
    required_places = 3
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more places than you have points!", False)


def test_purchasing_places_decreases_the_number_of_points_of_the_club(client):
    request_form = {
        "competition": "Competition one",
        "club": "Club one",
        "places": "9"
    }
    client.post('/purchasePlaces', data=request_form)
    assert mock_clubs[0]["points"] == 9


def test_can_buy_places_return_true_for_valid_parameters():
    competition = mock_competitions[1]
    club = mock_clubs[1]
    required_places = 1
    already_taken_places = 5
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ('Great-booking complete!', True)


def test_login_works_with_valid_identifiants(client):
    request_form = {
        "email": "corentin@gmail.com"
    }
    response = client.post('/showSummary', data=request_form)
    assert response.status_code == 200


def test_login_sends_an_error_with_invalid_identifiants(client):
    request_form = {
        "email": "co@gmail.com"
    }
    response = client.post('/showSummary', data=request_form)
    assert response.status_code == 404


def test_cant_buy_places_if_later_than_competition_date():
    competition = mock_competitions[2]
    club = mock_clubs[1]
    required_places = 1
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ('You cannot reserve a competition that already took place!', False)
