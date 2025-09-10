import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime


def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


def loadBookings():
    """Load bookings data from JSON file"""
    try:
        with open('bookings.json') as b:
            listOfBookings = json.load(b)['bookings']
            return listOfBookings
    except FileNotFoundError:
        return []


def saveClubs():
    """Save clubs data to JSON file"""
    with open('clubs.json', 'w') as c:
        json.dump({'clubs': clubs}, c, indent=4)


def saveCompetitions():
    """Save competitions data to JSON file"""
    with open('competitions.json', 'w') as comps:
        json.dump({'competitions': competitions}, comps, indent=4)


def saveBookings():
    """Save bookings data to JSON file"""
    with open('bookings.json', 'w') as b:
        json.dump({'bookings': bookings}, b, indent=4)


def addBooking(club_name, competition_name, places_booked, points_used):
    """Add a new booking record"""
    booking = {
        'id': len(bookings) + 1,
        'club': club_name,
        'competition': competition_name,
        'places': places_booked,
        'points_used': points_used,
        'date': datetime.now().isoformat(),
        'status': 'confirmed'
    }
    bookings.append(booking)
    saveBookings()


def getClubBookings(club_name):
    """Get all bookings for a specific club"""
    return [b for b in bookings if b['club'] == club_name]


def getCompetitionBookings(competition_name):
    """Get all bookings for a specific competition"""
    return [b for b in bookings if b['competition'] == competition_name]


def getClubBookingsForCompetition(club_name, competition_name):
    """Get bookings for a specific club and competition"""
    return [b for b in bookings if b['club'] == club_name and b['competition'] == competition_name]


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()
bookings = loadBookings()

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
    
    # Check 1: maximum 12 places per club per competition (including previous bookings)
    existing_bookings = getClubBookingsForCompetition(club['name'], competition['name'])
    total_existing_places = sum(booking['places'] for booking in existing_bookings)
    total_places_after_booking = total_existing_places + placesRequired
    
    if placesRequired > 12:
        flash('Impossible to reserve more than 12 places at once per competition.')
        return render_template('booking.html', club=club, competition=competition)
    
    if total_places_after_booking > 12:
        flash(f'Maximum 12 places per club per competition. You already have {total_existing_places} places booked. You can only book {12 - total_existing_places} more places.')
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
    
    # Record the booking in history
    addBooking(club['name'], competition['name'], placesRequired, points_needed)
    
    # Save changes to files for persistence
    saveCompetitions()
    saveClubs()
    
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))