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





@pytest.fixture
def clubs(monkeypatch):
    mock_clubs = [
        {
            "name": "Club one",
            "email": "corentin@gmail.com",
            "points": "18"
        },
        {
            "name": "Club two",
            "email": "bravo@gmail.com",
            "points": "4"
        },
        {
            "name": "Club three",
            "email": "cbravo@gmail.com",
            "points": "30"
        }
    ]
    monkeypatch.setattr("application.server.clubs", mock_clubs)


@pytest.fixture
def competitions(monkeypatch):
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
    monkeypatch.setattr("application.server.competitions", mock_competitions)
    

def test_cant_buy_places_if_places_are_over_twelve(clubs, competitions):
    competition = server.competitions[0]
    club = server.clubs[0]
    required_places = 15
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more than twelve places per competition!", False)


def test_cant_buy_places_if_total_places_are_over_twelve(clubs, competitions):
    competition = server.competitions[0]
    club = server.clubs[2]
    required_places = 8
    already_taken_places = 5
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more than twelve places per competition!", False)


def test_purchasing_places_increase_the_number_of_taken_places(client, clubs, competitions):
    request_form = {
        "competition": "Competition one",
        "club": "Club one",
        "places": "3"
    }
    client.post('/purchasePlaces', data=request_form)
    assert server.competitions[0]["places_taken"]["Club one"] == 3


def test_purchase_places_is_limited_to_available_places(clubs, competitions):
    competition = server.competitions[1]
    club = server.clubs[0]
    required_places = 9
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ("You can't buy more places than there are available!", False)


def test_cant_buy_places_if_club_doesnt_have_enough_points(clubs, competitions):
    competition = server.competitions[1]
    club = server.clubs[1]
    required_places = 3
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           (f"You don't have enough points for 3 places, you'd need at least 9" \
               f" points", False)


def test_purchasing_places_decreases_the_number_of_points_of_the_club(client, clubs, competitions):
    request_form = {
        "competition": "Competition one",
        "club": "Club one",
        "places": "1"
    }
    client.post('/purchasePlaces', data=request_form)
    assert server.clubs[0]["points"] == 15


def test_can_buy_places_return_true_for_valid_parameters(clubs, competitions):
    competition = server.competitions[1]
    club = server.clubs[1]
    required_places = 1
    already_taken_places = 5
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ('Great-booking complete!', True)


def test_login_works_with_valid_identifiants(client, clubs, competitions):
    request_form = {
        "email": "corentin@gmail.com"
    }
    response = client.post('/showSummary', data=request_form)
    assert response.status_code == 200


def test_login_sends_an_error_with_invalid_identifiants(client, clubs, competitions):
    request_form = {
        "email": "co@gmail.com"
    }
    response = client.post('/showSummary', data=request_form)
    assert response.status_code == 404


def test_cant_buy_places_if_later_than_competition_date(clubs, competitions):
    competition = server.competitions[2]
    club = server.clubs[1]
    required_places = 1
    already_taken_places = 0
    assert server.can_buy_places(club, competition, required_places, already_taken_places) == \
           ('You cannot reserve a competition that already took place!', False)
