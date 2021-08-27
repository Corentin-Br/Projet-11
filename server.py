import json
from flask import Flask, render_template, request, redirect, flash, url_for
import datetime


def load_clubs():
    with open('clubs.json') as c:
        all_clubs = json.load(c)['clubs']
        return all_clubs


def load_competitions():
    with open('competitions.json') as comps:
        all_competitions = json.load(comps)['competitions']
        for competition in all_competitions:
            competition["places_taken"] = {}
        return all_competitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = load_competitions()
clubs = load_clubs()
DATE_PATTERN = "%Y-%m-%d %H:%M:%S"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/showSummary', methods=['POST'])
def show_summary():
    potential_clubs = [club for club in clubs if club['email'] == request.form['email']]
    if potential_clubs:
        club = potential_clubs[0]
        return render_template('welcome.html', club=club, competitions=competitions)
    else:
        flash("Your email has not been found.")
        return render_template('index.html'), 404


@app.route('/showpoints')
def show_points():
    return render_template('points.html', clubs=clubs)


@app.route('/book/<competition>/<club>')
def book(competition, club):
    found_clubs = [c for c in clubs if c['name'] == club]
    found_competitions = [c for c in competitions if c['name'] == competition]
    if found_clubs and found_competitions:
        return render_template('booking.html', club=found_clubs[0], competition=found_competitions[0])
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions), 500


@app.route('/purchasePlaces', methods=['POST'])
def purchase_places():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    required_places = int(request.form['places'])
    already_taken_places = competition["places_taken"].get(club["name"], 0)
    message, allowed = can_buy_places(club, competition, required_places, already_taken_places)
    status = 200 if allowed else 500
    if allowed:
        competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-required_places
        competition["places_taken"][club["name"]] = already_taken_places + required_places
        club["points"] = int(club['points']) - 3 * required_places
    flash(message)
    return render_template('welcome.html', club=club, competitions=competitions), status


def can_buy_places(club: dict, competition: dict, required_places: int, already_taken_places: int) -> tuple:
    if datetime.datetime.now() >= datetime.datetime.strptime(competition["date"], DATE_PATTERN):
        return 'You cannot reserve a competition that already took place!', False
    if required_places > 12 - already_taken_places:
        return "You can't buy more than twelve places per competition!", False
    elif required_places > int(competition['numberOfPlaces']):
        return "You can't buy more places than there are available!", False
    elif 3 * required_places > int(club["points"]):
        return f"You don't have enough points for {required_places} places, you'd need at least {required_places * 3}" \
               f" points", False
    else:
        return 'Great-booking complete!', True


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
