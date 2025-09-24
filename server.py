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


def findClubByName(club_name):
    """Find a club by name - returns first match or None"""
    matches = [c for c in clubs if c['name'] == club_name]
    return matches[0] if matches else None


def findCompetitionByName(competition_name):
    """Find a competition by name - returns first match or None"""
    matches = [c for c in competitions if c['name'] == competition_name]
    return matches[0] if matches else None


def findClubByEmail(email):
    """Find a club by email - returns first match or None"""
    matches = [club for club in clubs if club['email'] == email]
    return matches[0] if matches else None


def calculateBookingLimits(club, competition):
    """Calculate all booking limits for a club and competition"""
    existing_bookings = getClubBookingsForCompetition(club['name'], competition['name'])
    places_already_booked = sum(booking['places'] for booking in existing_bookings)
    
    # Constraint 1: Maximum 12 places per club per competition
    remaining_from_12_limit = max(0, 12 - places_already_booked)
    
    # Constraint 2: Available points (1 point per place)
    club_points = int(club['points'])
    
    # Constraint 3: Available places in competition
    available_places = int(competition['numberOfPlaces'])
    
    # The actual maximum is the minimum of all constraints
    max_remaining = min(remaining_from_12_limit, club_points, available_places)
    
    return {
        'places_already_booked': places_already_booked,
        'max_remaining': max_remaining,
        'club_points': club_points,
        'available_places': available_places,
        'remaining_from_12_limit': remaining_from_12_limit
    }


def validateBookingRequest(places_required, limits):
    """Validate a booking request against all constraints
    
    Args:
        places_required (int): Number of places requested
        limits (dict): Result from calculateBookingLimits()
    
    Returns:
        tuple: (is_valid, error_message)
    """
    places_already_booked = limits['places_already_booked']
    club_points = limits['club_points']
    available_places = limits['available_places']
    
    # Check 0: places must be positive
    if places_required <= 0:
        return False, 'Number of places must be greater than 0.'
    
    # Check 1: maximum 12 places per club per competition (including previous bookings)
    total_places_after_booking = places_already_booked + places_required
    
    if places_required > 12:
        return False, 'Impossible to reserve more than 12 places at once per competition.'
    
    if total_places_after_booking > 12:
        remaining_allowed = 12 - places_already_booked
        return False, f'Maximum 12 places per club per competition. You already have {places_already_booked} places booked. You can only book {remaining_allowed} more places.'
    
    # Check 2: available places in competition
    if places_required > available_places:
        return False, f'Not enough places available. Only {available_places} places left.'
    
    # Check 3: sufficient points (1 point per place)
    points_needed = places_required  # 1 point per place
    if club_points < points_needed:
        return False, f'Not enough points. You need {points_needed} points but only have {club_points}.'
    
    # All validations passed
    return True, None


def processBooking(club, competition, places_required):
    """Process a valid booking - update data and save
    
    Args:
        club (dict): Club data
        competition (dict): Competition data
        places_required (int): Number of places to book
    """
    club_points = int(club['points'])
    available_places = int(competition['numberOfPlaces'])
    points_needed = places_required  # 1 point per place
    
    # Update data
    competition['numberOfPlaces'] = str(available_places - places_required)
    club['points'] = str(club_points - points_needed)
    
    # Record the booking in history
    addBooking(club['name'], competition['name'], places_required, points_needed)
    
    # Save changes to files for persistence
    saveCompetitions()
    saveClubs()


def renderBookingPageWithLimits(club, competition, limits, error_message=None):
    """Render booking page with calculated limits and optional error message
    
    Args:
        club (dict): Club data
        competition (dict): Competition data
        limits (dict): Result from calculateBookingLimits()
        error_message (str, optional): Error message to flash
    
    Returns:
        Flask response
    """
    if error_message:
        flash(error_message)
    
    return render_template('booking.html',
                         club=club,
                         competition=competition,
                         max_remaining=limits['max_remaining'],
                         places_already_booked=limits['places_already_booked'],
                         club_points=limits['club_points'],
                         available_places=limits['available_places'])


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
    club = findClubByEmail(email)
    if not club:
        # Email non trouvé, afficher un message d'erreur sur la page d'accueil
        return render_template('index.html', message="This email doesn't exist. Please try again.")
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = findClubByName(club)
    foundCompetition = findCompetitionByName(competition)
    
    if foundClub and foundCompetition:
        limits = calculateBookingLimits(foundClub, foundCompetition)
        return renderBookingPageWithLimits(foundClub, foundCompetition, limits)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = findCompetitionByName(request.form['competition'])
    club = findClubByName(request.form['club'])
    placesRequired = int(request.form['places'])
    
    if not club or not competition:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # Calculate limits for validation and error display
    limits = calculateBookingLimits(club, competition)
    
    # Validate the booking request
    is_valid, error_message = validateBookingRequest(placesRequired, limits)
    
    if not is_valid:
        return renderBookingPageWithLimits(club, competition, limits, error_message)
    
    # If all checks pass, proceed with booking
    processBooking(club, competition, placesRequired)
    
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/public/points')
def public_points():
    """
    Public dashboard showing all clubs' points totals
    Accessible without login for transparency
    Performance optimized: < 2 seconds target
    """
    # Get all clubs data (optimized for performance)
    clubs_data = []
    for club in clubs:
        clubs_data.append({
            'name': club['name'],
            'points': int(club['points'])
        })
    
    # Sort by points descending for better UX
    clubs_data.sort(key=lambda x: x['points'], reverse=True)
    
    # Add ranking
    for i, club in enumerate(clubs_data, 1):
        club['rank'] = i
    
    return render_template('public_points.html', clubs=clubs_data)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))