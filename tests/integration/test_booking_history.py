import pytest
import json
import shutil
import os
import server
from server import loadClubs, loadCompetitions, loadBookings
from datetime import datetime

@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        # Backup original files
        shutil.copy('clubs.json', 'clubs_backup.json')
        shutil.copy('competitions.json', 'competitions_backup.json')
        if os.path.exists('bookings.json'):
            shutil.copy('bookings.json', 'bookings_backup.json')
        
        # Reset to initial test data
        shutil.copy('tests/fixtures/clubs_test.json', 'clubs.json')
        shutil.copy('tests/fixtures/competitions_test.json', 'competitions.json')
        shutil.copy('tests/fixtures/bookings_test.json', 'bookings.json')
        
        # Reload data in memory
        server.clubs = loadClubs()
        server.competitions = loadCompetitions()
        server.bookings = loadBookings()
        
        yield client
        
        # Restore original files after test
        shutil.copy('clubs_backup.json', 'clubs.json')
        shutil.copy('competitions_backup.json', 'competitions.json')
        if os.path.exists('bookings_backup.json'):
            shutil.copy('bookings_backup.json', 'bookings.json')
        else:
            # If no backup exists, remove the test file
            if os.path.exists('bookings.json'):
                os.remove('bookings.json')

def test_booking_is_recorded(client):
    """Test that bookings are properly recorded in bookings.json"""
    # Make a booking
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '3'
    })
    
    # Check booking was successful
    assert "Great-booking complete" in response.data.decode('utf-8')
    
    # Check that booking was recorded
    bookings = loadBookings()
    assert len(bookings) == 1
    
    booking = bookings[0]
    assert booking['club'] == 'Simply Lift'
    assert booking['competition'] == 'Spring Festival'
    assert booking['places'] == 3
    assert booking['points_used'] == 3
    assert booking['status'] == 'confirmed'
    assert 'date' in booking
    assert 'id' in booking

def test_multiple_bookings_recorded(client):
    """Test that multiple bookings are properly recorded"""
    # Make first booking
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '2'
    })

    # Make second booking
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '1'
    })

    # Check both bookings were recorded
    bookings = loadBookings()
    assert len(bookings) == 2

    # Check first booking
    booking1 = next(b for b in bookings if b['club'] == 'Simply Lift')
    assert booking1['competition'] == 'Spring Festival'
    assert booking1['places'] == 2

    # Check second booking
    booking2 = next(b for b in bookings if b['club'] == 'Iron Temple')
    assert booking2['competition'] == 'Spring Festival'
    assert booking2['places'] == 1

def test_booking_history_functions(client):
    """Test the booking history utility functions"""
    # Make some bookings
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '2'
    })

    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '1'
    })

    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',
        'places': '3'
    })

    # Test getClubBookings
    simply_lift_bookings = server.getClubBookings('Simply Lift')
    assert len(simply_lift_bookings) == 2

    # Test getCompetitionBookings
    spring_festival_bookings = server.getCompetitionBookings('Spring Festival')
    assert len(spring_festival_bookings) == 3

    # Test getClubBookingsForCompetition
    specific_bookings = server.getClubBookingsForCompetition('Simply Lift', 'Spring Festival')
    assert len(specific_bookings) == 2
    assert specific_bookings[0]['places'] == 2

def test_max_12_places_with_booking_history(client):
    """Test that 12 places limit considers booking history"""
    # First booking: 8 places
    response1 = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '8'
    })
    assert "Great-booking complete" in response1.data.decode('utf-8')
    
    # Second booking: try to book 5 more places (total would be 13)
    response2 = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '5'
    })
    html_content = response2.data.decode('utf-8')
    assert "Maximum 12 places per club per competition" in html_content
    assert "You already have 8 places booked" in html_content
    assert "You can only book 4 more places" in html_content
    
    # Third booking: book exactly the remaining 4 places (should work)
    response3 = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '4'
    })
    assert "Great-booking complete" in response3.data.decode('utf-8')
    
    # Fourth booking: try to book 1 more place (should fail, total would be 13)
    response4 = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '1'
    })
    html_content = response4.data.decode('utf-8')
    assert "You already have 12 places booked" in html_content

def test_different_competitions_separate_limits(client):
    """Test that 12 places limit is per competition, not global"""
    
    # Check initial state
    initial_bookings = server.loadBookings()
    assert len(initial_bookings) == 0, f"Expected 0 initial bookings, got {len(initial_bookings)}"
    
    # First booking: Spring Festival
    response1 = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '5'
    })
    
    assert "Great-booking complete" in response1.data.decode('utf-8'), f"First booking failed: {response1.data.decode('utf-8')[:300]}"
    
        # On ne teste plus l'indépendance entre compétitions, mais le cumul sur Spring Festival
    booking2 = {
        'club': 'Simply Lift',
        'competition': 'Spring Festival',
        'places': 2
    }
    response2 = client.post('/purchasePlaces', data=booking2, follow_redirects=True)
    assert "Great-booking complete" in response2.data.decode('utf-8'), f"Second booking failed: {response2.data.decode('utf-8')[:300]}"
    spring_festival_bookings = server.getCompetitionBookings('Spring Festival')
    assert len(spring_festival_bookings) == 2, f"Expected 2 Spring Festival bookings, got {len(spring_festival_bookings)}"
    specific_bookings = server.getClubBookingsForCompetition('Simply Lift', 'Spring Festival')
    assert len(specific_bookings) == 2, f"Expected 2 Spring Festival bookings for Simply Lift, got {len(specific_bookings)}"
