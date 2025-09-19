import pytest
import json
import shutil
import os
from server import app, loadClubs, loadCompetitions, loadBookings
import server

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
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
            if os.path.exists('bookings.json'):
                os.remove('bookings.json')

def test_data_persistence_after_booking(client):
    """Test that booking changes are saved to JSON files"""
    # Reload fresh data to ensure clean state
    server.clubs = loadClubs()
    server.competitions = loadCompetitions()
    
    # Get initial state
    initial_clubs = loadClubs()
    initial_competitions = loadCompetitions()
    
    simply_lift_initial = next(c for c in initial_clubs if c['name'] == 'Simply Lift')
    spring_festival_initial = next(c for c in initial_competitions if c['name'] == 'Spring Festival')
    
    initial_points = int(simply_lift_initial['points'])
    initial_places = int(spring_festival_initial['numberOfPlaces'])
    
    # Make a booking
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '3'
    })
    
    # Verify booking was successful
    assert "Great-booking complete" in response.data.decode('utf-8')
    
    # Reload data from files to check persistence
    clubs_after = loadClubs()
    competitions_after = loadCompetitions()
    
    simply_lift_after = next(c for c in clubs_after if c['name'] == 'Simply Lift')
    spring_festival_after = next(c for c in competitions_after if c['name'] == 'Spring Festival')
    
    # Verify points were deducted and saved
    assert int(simply_lift_after['points']) == initial_points - 3
    
    # Verify places were deducted and saved
    assert int(spring_festival_after['numberOfPlaces']) == initial_places - 3

def test_file_structure_preserved(client):
    """Test that JSON file structure is preserved after saving"""
    # Make a booking
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '2'
    })
    
    # Check clubs.json structure
    with open('clubs.json', 'r') as f:
        clubs_data = json.load(f)
    
    assert 'clubs' in clubs_data
    assert isinstance(clubs_data['clubs'], list)
    assert len(clubs_data['clubs']) > 0
    
    # Check competitions.json structure
    with open('competitions.json', 'r') as f:
        competitions_data = json.load(f)
    
    assert 'competitions' in competitions_data
    assert isinstance(competitions_data['competitions'], list)
    assert len(competitions_data['competitions']) > 0
