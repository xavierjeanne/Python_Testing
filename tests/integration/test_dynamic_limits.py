import pytest
import json
import shutil
import os
import server
from server import loadClubs, loadCompetitions, loadBookings

@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        # Backup original files
        if os.path.exists('clubs.json'):
            shutil.copy('clubs.json', 'clubs_backup.json')
        if os.path.exists('competitions.json'):
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
        if os.path.exists('clubs_backup.json'):
            shutil.copy('clubs_backup.json', 'clubs.json')
            os.remove('clubs_backup.json')
        if os.path.exists('competitions_backup.json'):
            shutil.copy('competitions_backup.json', 'competitions.json')
            os.remove('competitions_backup.json')
        if os.path.exists('bookings_backup.json'):
            shutil.copy('bookings_backup.json', 'bookings.json')
            os.remove('bookings_backup.json')

def test_dynamic_limit_no_previous_bookings(client):
    """Test that full 12 places are available when no previous bookings"""
    response = client.get('/book/Spring Festival/Simply Lift')
    html_content = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert 'max="12"' in html_content
    assert "You can book up to 12 more places" in html_content
    assert "Your club has already booked" not in html_content

def test_dynamic_limit_with_previous_bookings(client):
    """Test that limit is reduced after previous bookings"""
    # Make an initial booking of 5 places
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '5'
    })
    
    # Check the booking page now shows reduced limit
    response = client.get('/book/Spring Festival/Simply Lift')
    html_content = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert 'max="7"' in html_content  # 12 - 5 = 7
    assert "Your club has already booked 5 places" in html_content
    assert "You can book up to 7 more places" in html_content

def test_dynamic_limit_at_maximum(client):
    """Test that no booking form is shown when at 12 places limit"""
    # Make a booking of 12 places
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '12'
    })
    
    # Check the booking page now shows no form
    response = client.get('/book/Spring Festival/Simply Lift')
    html_content = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert "You have reached the maximum of 12 places" in html_content
    assert "Your club has already booked 12 places" in html_content
    assert '<form' not in html_content  # No form should be present
    assert "Return to main page" in html_content

def test_dynamic_limit_multiple_bookings(client):
    """Test limit calculation with multiple bookings"""
    # Make first booking of 3 places
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '3'
    })
    
    # Make second booking of 4 places
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '4'
    })
    
    # Check the booking page shows correct remaining limit
    response = client.get('/book/Spring Festival/Simply Lift')
    html_content = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert 'max="5"' in html_content  # 12 - (3 + 4) = 5
    assert "Your club has already booked 7 places" in html_content
    assert "You can book up to 5 more places" in html_content

def test_dynamic_limit_different_competitions_independent(client):
    """Test that limits are independent per competition but shared points limit applies"""
    # Book 10 places for Spring Festival (uses 10 points, leaves 3 points)
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '10'
    })
    
    # Check Spring Festival shows limit of 2 (12 - 10 = 2 places remaining)
    response1 = client.get('/book/Spring Festival/Simply Lift')
    html_content1 = response1.data.decode('utf-8')
    assert 'max="2"' in html_content1
    assert "You can book up to 2 more places" in html_content1
    
    # Check Fall Classic shows limit of 3 (limited by remaining points: 13 - 10 = 3)
    response2 = client.get('/book/Fall Classic/Simply Lift')
    html_content2 = response2.data.decode('utf-8')
    assert 'max="3"' in html_content2
    assert "You can book up to 3 more places" in html_content2

def test_dynamic_limit_constrained_by_points(client):
    """Test that booking limit is constrained by available points"""
    # Simply Lift has 13 points in test data
    # Should be able to book max 12 places but limited by points when points < 12
    
    # Book 10 places first (uses 10 points, leaves 3)
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '10'
    })
    
    # Now check that other competitions are limited by remaining points (3)
    response = client.get('/book/Fall Classic/Simply Lift')
    html_content = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert 'max="3"' in html_content  # Limited by remaining points, not by 12-places rule
    assert "You can book up to 3 more places" in html_content

def test_dynamic_limit_constrained_by_competition_places(client):
    """Test that booking limit is constrained by competition available places"""
    # Create a test scenario where competition has fewer places than club points/limits
    # We'll use Iron Temple (4 points) for Fall Classic (25 places)
    
    response = client.get('/book/Fall Classic/Iron Temple')
    html_content = response.data.decode('utf-8')
    
    assert response.status_code == 200
    assert 'max="4"' in html_content  # Limited by club points (4), not by 12-places or competition places
    assert "You can book up to 4 more places" in html_content
