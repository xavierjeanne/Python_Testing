import json
from flask import Flask,render_template,request,redirect,flash,url_for


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def saveClubs():
    """Save clubs data to JSON file"""
    with open('clubs.json', 'w') as c:
        json.dump({'clubs': clubs}, c, indent=4)


def saveCompetitions():
    """Save competitions data to JSON file"""
    with open('competitions.json', 'w') as comps:
        json.dump({'competitions': competitions}, comps, indent=4)


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    email = request.form['email']
    club_list = [club for club in clubs if club['email'] == email]
    if not club_list:
        # Email non trouvé, afficher un message d'erreur sur la page d'accueil
        return render_template('index.html', message="This email doesn't exist. Please try again.")
    club = club_list[0]
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
    placesRequired = int(request.form['places'])
    
    # Check 1: maximum 12 places per club per competition
    if placesRequired > 12:
        flash('Impossible to reserve more than 12 places per competition.')
        return render_template('booking.html', club=club, competition=competition)
    
    # Check 2: available places in competition
    available_places = int(competition['numberOfPlaces'])
    if placesRequired > available_places:
        flash(f'Not enough places available. Only {available_places} places left.')
        return render_template('booking.html', club=club, competition=competition)
    
    # Check 3: sufficient points (1 point per place)
    club_points = int(club['points'])
    points_needed = placesRequired  # 1 point per place
    if club_points < points_needed:
        flash(f'Not enough points. You need {points_needed} points but only have {club_points}.')
        return render_template('booking.html', club=club, competition=competition)
    
    # If all checks pass, proceed with booking
    competition['numberOfPlaces'] = str(available_places - placesRequired)
    club['points'] = str(club_points - points_needed)
    
    # Save changes to files for persistence
    saveCompetitions()
    saveClubs()
    
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))