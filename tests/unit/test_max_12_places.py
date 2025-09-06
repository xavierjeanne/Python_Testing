import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_purchasePlaces_more_than_12_places(client):
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '15'  # Plus de 12 places
    })
    html_content = response.data.decode('utf-8')    
    assert "Impossible to reserve more than 12 places per competition" in html_content
    assert response.status_code == 200

def test_purchasePlaces_exactly_12_places(client):
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '12'  # Exactement 12 places
    })
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200

def test_purchasePlaces_less_than_12_places(client):
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '5'  # Moins de 12 places
    })
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200

def test_purchasePlaces_1_place(client):
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '1'
    })
    html_content = response.data.decode('utf-8')
    assert "Great-booking complete" in html_content
    assert response.status_code == 200
