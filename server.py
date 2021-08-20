import json
from flask import Flask, render_template, request, redirect, flash, url_for, jsonify
from werkzeug.exceptions import abort, InternalServerError


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         for competition in listOfCompetitions:
             competition["places_taken"] = {}
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    places_already_taken = competition["places_taken"].get(club["name"], 0)
    placesRequired = int(request.form['places'])
    if placesRequired > 12 - places_already_taken:
        flash("You can't buy more than twelve places per competition")
        return render_template('welcome.html', club=club, competitions=competitions), 500
    competition['numberOfPlaces'] = int(competition['numberOfPlaces'])-placesRequired
    competition["places_taken"][club["name"]] = places_already_taken + placesRequired
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)

class TooManyPlacesAskedError(Exception):
    def __init__(self, club):
        super().__init__(self)
        self.club = club

# TODO: Add route for points display
@app.errorhandler(TooManyPlacesAskedError)
def handle_invalid_usage(error):
    flash("You can only take 12 places at most.")
    return render_template('welcome.html', club=error.club, competitions=competitions)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))




