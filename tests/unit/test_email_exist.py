import pytest
from server import app

def test_showSummary_email_not_found(client):
    response = client.post('/showSummary', data={'email': 'notfound@email.com'})
    html_content = response.data.decode('utf-8')
    # L'apostrophe est échappée en HTML : doesn&#39;t
    assert "This email doesn&#39;t exist" in html_content
    assert response.status_code == 200

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_showSummary_email_found(client):
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert "welcome" in response.data.decode('utf-8').lower()
    assert response.status_code == 200
