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

def test_negative_places_rejected(client):
    """Test that negative places are rejected"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '-1'  # Negative places
    })
    
    html_content = response.data.decode('utf-8')
    assert "Number of places must be greater than 0" in html_content
    assert response.status_code == 200
    
    # Verify no booking was created
    bookings = server.loadBookings()
    assert len(bookings) == 0

def test_zero_places_rejected(client):
    """Test that zero places are rejected"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '0'  # Zero places
    })
    
    html_content = response.data.decode('utf-8')
    assert "Number of places must be greater than 0" in html_content
    assert response.status_code == 200
    
    # Verify no booking was created
    bookings = server.loadBookings()
    assert len(bookings) == 0

def test_positive_places_accepted(client):
    """Test that positive places are accepted"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '1'  # Positive places
    })
    
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200
    
    # Verify booking was created
    bookings = server.loadBookings()
    assert len(bookings) == 1
    assert bookings[0]['places'] == 1

def test_large_negative_places_rejected(client):
    """Test that large negative numbers are rejected"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '-999'  # Large negative number
    })
    
    html_content = response.data.decode('utf-8')
    assert "Number of places must be greater than 0" in html_content
    assert response.status_code == 200
    
    # Verify no booking was created
    bookings = server.loadBookings()
    assert len(bookings) == 0
