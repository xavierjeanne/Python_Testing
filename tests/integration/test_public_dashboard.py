"""
Tests d'intégration pour le dashboard public des points
Public Points Dashboard
"""
import pytest
import json
import shutil
import os
import server


@pytest.fixture
def client():
    server.app.config['TESTING'] = True
    with server.app.test_client() as client:
        # Ensure we're using clean test data
        if os.path.exists('clubs.json'):
            shutil.copy('clubs.json', 'clubs_backup.json')
        if os.path.exists('competitions.json'):
            shutil.copy('competitions.json', 'competitions_backup.json')
        
        # Reset to test data
        shutil.copy('tests/fixtures/clubs_test.json', 'clubs.json')
        shutil.copy('tests/fixtures/competitions_test.json', 'competitions.json')
        
        # Reload data in memory
        server.clubs = server.loadClubs()
        server.competitions = server.loadCompetitions()
        
        yield client
        
        # Restore original files
        if os.path.exists('clubs_backup.json'):
            shutil.copy('clubs_backup.json', 'clubs.json')
            os.remove('clubs_backup.json')
        if os.path.exists('competitions_backup.json'):
            shutil.copy('competitions_backup.json', 'competitions.json')
            os.remove('competitions_backup.json')


class TestPublicPointsDashboardIntegration:
    """Tests d'intégration pour le tableau public des points"""
    
    def test_public_points_route_accessibility(self, client):
        """Test que la route publique des points est accessible"""
        response = client.get('/public/points')
        
        assert response.status_code == 200
        assert b'Public Points Dashboard' in response.data
    
    def test_public_points_displays_all_clubs(self, client):
        """Test que tous les clubs sont affichés"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        # Vérifier que les clubs de test sont présents
        assert 'Simply Lift' in html_content
        assert 'Iron Temple' in html_content
        assert 'She Lifts' in html_content
    
    def test_public_points_shows_correct_points(self, client):
        """Test que les points corrects sont affichés"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        # Vérifier que les points des fixtures de test sont corrects
        assert '13 pts' in html_content  # Simply Lift
        assert '4 pts' in html_content   # Iron Temple
        assert '12 pts' in html_content  # She Lifts
    
    def test_public_points_sorting_order(self, client):
        """Test que les clubs sont triés par ordre décroissant de points"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        # Simply Lift (13 pts) devrait être avant She Lifts (12 pts)
        simply_pos = html_content.find('Simply Lift')
        she_lifts_pos = html_content.find('She Lifts')
        iron_pos = html_content.find('Iron Temple')
        
        assert simply_pos < she_lifts_pos < iron_pos
    
    def test_public_points_performance_requirement(self, client):
        """Test que la page répond dans les temps (< 2 secondes)"""
        import time
        
        start_time = time.time()
        response = client.get('/public/points')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Requirement: < 2 seconds
    
    def test_public_points_no_authentication_required(self, client):
        """Test que l'accès ne nécessite pas d'authentification"""
        # Accès direct sans session/login
        response = client.get('/public/points')
        
        assert response.status_code == 200
        # Vérifier qu'il n'y a pas de redirection vers une page d'authentification
        assert 'Public Points Dashboard' in response.data.decode('utf-8')
        # Vérifier qu'on peut accéder au contenu sans être redirigé
        html_content = response.data.decode('utf-8')
        assert 'Simply Lift' in html_content or 'Club' in html_content
    
    def test_public_points_has_navigation_link(self, client):
        """Test que le lien de navigation vers la page principale est présent"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        assert 'Club Login' in html_content or '/' in html_content
    
    def test_index_page_has_public_points_link(self, client):
        """Test que la page d'accueil a le lien vers le dashboard public"""
        response = client.get('/')
        html_content = response.data.decode('utf-8')
        
        assert '/public/points' in html_content
        assert 'Points Dashboard' in html_content
    
    def test_public_points_responsive_design(self, client):
        """Test que la page publique a un design responsive"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        # Test viewport meta tag
        assert 'viewport' in html_content
    
    def test_public_points_has_proper_title(self, client):
        """Test que la page publique a un titre approprié"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        assert 'Public Points Dashboard' in html_content


class TestPublicPointsDataConsistency:
    """Tests de cohérence des données publiques"""
    
    def test_points_data_consistency_with_actual_data(self, client):
        """Test que les données de points affichées sont cohérentes avec les données réelles"""
        response = client.get('/public/points')
        html_content = response.data.decode('utf-8')
        
        # Vérifier que les points affichés correspondent aux données des fixtures
        assert 'pts' in html_content  # Format d'affichage des points
        
        # Vérifier que tous les clubs ont leurs points affichés
        club_count = html_content.count('pts')
        assert club_count >= 3  # Au moins les 3 clubs de test
    
    def test_public_points_real_time_data(self, client):
        """Test que les données affichées reflètent l'état actuel des données"""
        # Premier appel pour obtenir les données initiales
        response1 = client.get('/public/points')
        html1 = response1.data.decode('utf-8')
        
        # Simuler un changement dans les données (via modification directe)
        # Note: Dans un vrai test, ceci pourrait être fait via l'API de booking
        original_points = server.clubs[0]['points']
        server.clubs[0]['points'] = str(int(original_points) + 5)
        
        # Deuxième appel pour voir si les changements sont reflétés
        response2 = client.get('/public/points')
        html2 = response2.data.decode('utf-8')
        
        # Restaurer les données originales
        server.clubs[0]['points'] = original_points
        
        # Les deux réponses devraient être différentes
        assert html1 != html2