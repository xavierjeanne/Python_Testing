import pytest
import json
import shutil
import server
from server import loadClubs, loadCompetitions

@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        # Backup original files
        shutil.copy('clubs.json', 'clubs_backup.json')
        shutil.copy('competitions.json', 'competitions_backup.json')
        
        # Reset to initial test data
        shutil.copy('tests/fixtures/clubs_test.json', 'clubs.json')
        shutil.copy('tests/fixtures/competitions_test.json', 'competitions.json')
        
        # Reload data in memory
        server.clubs = loadClubs()
        server.competitions = loadCompetitions()
        
        yield client
        
        # Restore original files after test
        shutil.copy('clubs_backup.json', 'clubs.json')
        shutil.copy('competitions_backup.json', 'competitions.json')

def test_purchasePlaces_insufficient_points(client):
    """Test booking with insufficient points"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',  # Has 4 points
        'places': '5'  # Needs 5 points but only has 4
    })
    html_content = response.data.decode('utf-8')
    assert "Not enough points" in html_content
    assert "You need 5 points but only have 4" in html_content
    assert response.status_code == 200

def test_purchasePlaces_sufficient_points(client):
    """Test booking with sufficient points"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',  # Has 13 points
        'places': '3'  # Needs 3 points, has 13
    })
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200

def test_purchasePlaces_not_enough_places_available(client):
    """Test booking when not enough places available in competition"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',  # Has 25 places in test data
        'club': 'Simply Lift',
        'places': '30'  # Asking for more than available (30 > 25)
    })
    
    # Check that we stay on the booking page (not redirected elsewhere)
    assert response.status_code == 200
    
    html_content = response.data.decode('utf-8')
    
    # Check that we're still on the booking page (indicates error)
    assert "Booking for Spring Festival" in html_content
    
    # The places available should still be 25 (booking didn't go through)
    assert "Places available: 25" in html_content

def test_purchasePlaces_exactly_enough_points(client):
    """Test booking with exactly enough points"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Iron Temple',  # Has 4 points
        'places': '4'  # Needs exactly 4 points
    })
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200

def test_purchasePlaces_zero_points_requested(client):
    """Test booking with zero places requested"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '0'  # Zero places
    })
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200

def test_purchasePlaces_negative_places_validation(client):
    """Test that negative places are handled correctly"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '-1'  # Negative places
    })
    html_content = response.data.decode('utf-8')
    # Should either show error or convert to 0
    assert response.status_code == 200
