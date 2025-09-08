import pytest
from server import app, loadClubs, loadCompetitions
import server

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Reset data before each test
        server.clubs = loadClubs()
        server.competitions = loadCompetitions()
        yield client

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
        'competition': 'Winter Cup',  # Has 25 places
        'club': 'Simply Lift',
        'places': '11'  # Asking for more than available (30 > 25)
    })
    html_content = response.data.decode('utf-8')
    assert "Not enough places available" in html_content
    assert "Only 10 places left" in html_content
    assert response.status_code == 200

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


