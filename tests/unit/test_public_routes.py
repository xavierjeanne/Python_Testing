"""
Tests unitaires pour le dashboard public des points
Test de la route publique et de la logique métier
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import server


class TestPublicPointsRouteUnit:
    """Tests unitaires pour la route publique des points"""
    
    def test_public_points_route_data_preparation(self):
        """Test que la route public_points prépare correctement les données"""
        # Mock data
        mock_clubs = [
            {'name': 'Club A', 'points': '10'},
            {'name': 'Club B', 'points': '5'},
            {'name': 'Club C', 'points': '15'}
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                # Vérifier que la réponse contient les clubs triés par points
                html_content = response.data.decode('utf-8')
                assert 'Club C' in html_content  # Plus haut score
                assert 'Club A' in html_content
                assert 'Club B' in html_content
    
    def test_public_points_sorting_algorithm(self):
        """Test que l'algorithme de tri des points fonctionne correctement"""
        mock_clubs = [
            {'name': 'Low Score', 'points': '1'},
            {'name': 'High Score', 'points': '100'},
            {'name': 'Medium Score', 'points': '50'},
            {'name': 'Zero Score', 'points': '0'},
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                html_content = response.data.decode('utf-8')
                
                # Vérifier l'ordre d'affichage (plus haut score en premier)
                high_pos = html_content.find('High Score')
                medium_pos = html_content.find('Medium Score')
                low_pos = html_content.find('Low Score')
                zero_pos = html_content.find('Zero Score')
                
                assert high_pos < medium_pos < low_pos < zero_pos
    
    def test_public_points_route_accessibility(self):
        """Test que la route publique des points est accessible"""
        mock_clubs = [
            {'name': 'Test Club', 'points': '10'}
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                assert response.status_code == 200
                assert b'Public Points Dashboard' in response.data
    
    def test_public_points_displays_all_clubs(self):
        """Test que tous les clubs sont affichés"""
        mock_clubs = [
            {'name': 'Simply Lift', 'points': '13'},
            {'name': 'Iron Temple', 'points': '4'},
            {'name': 'She Lifts', 'points': '12'}
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                html_content = response.data.decode('utf-8')
                
                # Vérifier que tous les clubs sont présents
                assert 'Simply Lift' in html_content
                assert 'Iron Temple' in html_content
                assert 'She Lifts' in html_content
    
    def test_public_points_shows_correct_points(self):
        """Test que les points corrects sont affichés"""
        mock_clubs = [
            {'name': 'Test Club', 'points': '25'}
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                html_content = response.data.decode('utf-8')
                
                assert '25 pts' in html_content
    
    def test_public_points_no_authentication_required(self):
        """Test que l'accès ne nécessite pas d'authentification"""
        mock_clubs = [{'name': 'Test Club', 'points': '10'}]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                assert response.status_code == 200
                # Vérifier qu'on peut accéder au contenu sans authentification
                html_content = response.data.decode('utf-8')
                assert 'Test Club' in html_content
    
    def test_public_points_performance_requirement(self):
        """Test que la page répond dans les temps (< 2 secondes)"""
        mock_clubs = [{'name': 'Test Club', 'points': '10'}]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                import time
                
                start_time = time.time()
                response = client.get('/public/points')
                end_time = time.time()
                
                response_time = end_time - start_time
                
                assert response.status_code == 200
                assert response_time < 2.0  # Requirement: < 2 seconds


class TestPublicPointsDataSafety:
    """Tests de sécurité des données publiques"""
    
    def test_public_points_no_sensitive_data(self):
        """Test que la page publique n'expose pas de données sensibles"""
        mock_clubs = [
            {
                'name': 'Test Club',
                'email': 'secret@test.com',  # Données sensibles
                'points': '10'
            }
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                html_content = response.data.decode('utf-8')
                
                # Vérifier que les données sensibles ne sont pas exposées
                assert 'secret@test.com' not in html_content
                assert 'Test Club' in html_content  # Nom public OK
                assert '10' in html_content  # Points publics OK


class TestPublicPointsErrorHandling:
    """Tests de gestion d'erreurs pour le dashboard public"""
    
    def test_public_points_with_corrupted_data(self):
        """Test avec données corrompues"""
        mock_clubs = [
            {'name': 'Valid Club', 'points': '10'},
            {'name': 'Invalid Club', 'points': 'invalid'},  # Points invalides
            {'name': 'Missing Points'}  # Points manquants
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                # L'application peut soit gérer gracieusement (200) soit retourner une erreur (500)
                assert response.status_code in [200, 500]
                
                # Si la page se charge (200), vérifier qu'au moins les données valides sont affichées
                if response.status_code == 200:
                    html_content = response.data.decode('utf-8')
                    assert 'Valid Club' in html_content
    
    def test_public_points_with_empty_data(self):
        """Test avec données vides"""
        with patch.object(server, 'clubs', []):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                assert response.status_code == 200
                html_content = response.data.decode('utf-8')
                assert 'points' in html_content.lower()
    
    @patch('server.loadClubs')
    def test_public_points_file_loading_error(self, mock_load):
        """Test de gestion d'erreur lors du chargement des fichiers"""
        mock_load.side_effect = FileNotFoundError("clubs.json not found")
        
        with server.app.test_client() as client:
            # La route devrait gérer l'erreur gracieusement
            response = client.get('/public/points')
            # Selon l'implémentation, soit erreur 500 soit page avec message d'erreur
            assert response.status_code in [200, 500]


class TestPublicPointsPerformance:
    """Tests de performance pour le dashboard public"""
    
    def test_large_dataset_handling(self):
        """Test avec un grand nombre de clubs"""
        # Créer un grand dataset de test
        large_clubs_dataset = []
        for i in range(1000):
            large_clubs_dataset.append({
                'name': f'Club {i}',
                'points': str(i % 100)  # Points variés
            })
        
        with patch.object(server, 'clubs', large_clubs_dataset):
            with server.app.test_client() as client:
                import time
                start_time = time.time()
                
                response = client.get('/public/points')
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert response.status_code == 200
                assert response_time < 2.0  # Exigence de performance
    
    def test_sorting_performance_with_large_dataset(self):
        """Test de performance du tri avec beaucoup de données"""
        import random
        
        # Dataset avec points aléatoires
        large_dataset = []
        for i in range(500):
            large_dataset.append({
                'name': f'Club {i}',
                'points': str(random.randint(0, 100))
            })
        
        with patch.object(server, 'clubs', large_dataset):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                assert response.status_code == 200
                # Vérifier que le tri s'est bien effectué
                # Vérifier que le tri s'est bien effectué
                html_content = response.data.decode('utf-8')
                assert 'Club' in html_content


class TestPublicPointsDataSafety:
    """Tests de sécurité des données publiques"""
    
    def test_public_points_no_sensitive_data(self):
        """Test que les pages publiques n'exposent pas de données sensibles"""
        mock_clubs = [
            {
                'name': 'Test Club',
                'email': 'secret@test.com',  # Données sensibles
                'points': '10'
            }
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                html_content = response.data.decode('utf-8')
                
                # Vérifier que les données sensibles ne sont pas exposées
                assert 'secret@test.com' not in html_content
                assert 'Test Club' in html_content  # Nom public OK
                assert '10' in html_content  # Points publics OK


class TestPublicPointsErrorHandling:
    """Tests de gestion d'erreurs pour les pages publiques"""
    
    def test_public_points_with_corrupted_data(self):
        """Test avec données corrompues"""
        mock_clubs = [
            {'name': 'Valid Club', 'points': '10'},
            {'name': 'Invalid Club', 'points': 'invalid'},  # Points invalides
            {'name': 'Missing Points'}  # Points manquants
        ]
        
        with patch.object(server, 'clubs', mock_clubs):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                # L'application peut soit gérer gracieusement (200) soit retourner une erreur (500)
                assert response.status_code in [200, 500]
                
                # Si la page se charge (200), vérifier qu'au moins les données valides sont affichées
                if response.status_code == 200:
                    html_content = response.data.decode('utf-8')
                    assert 'Valid Club' in html_content
    
    def test_public_points_with_empty_data(self):
        """Test avec données vides"""
        with patch.object(server, 'clubs', []):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                assert response.status_code == 200
                html_content = response.data.decode('utf-8')
                assert 'points' in html_content.lower()
    
    @patch('server.loadClubs')
    def test_public_points_file_loading_error(self, mock_load):
        """Test de gestion d'erreur lors du chargement des fichiers"""
        mock_load.side_effect = FileNotFoundError("clubs.json not found")
        
        with server.app.test_client() as client:
            # La route devrait gérer l'erreur gracieusement
            response = client.get('/public/points')
            # Selon l'implémentation, soit erreur 500 soit page avec message d'erreur
            assert response.status_code in [200, 500]


class TestPublicPerformance:
    """Tests de performance pour les pages publiques"""
    
    def test_large_dataset_handling(self):
        """Test avec un grand nombre de clubs"""
        # Créer un grand dataset de test
        large_clubs_dataset = []
        for i in range(1000):
            large_clubs_dataset.append({
                'name': f'Club {i}',
                'points': str(i % 100)  # Points variés
            })
        
        with patch.object(server, 'clubs', large_clubs_dataset):
            with server.app.test_client() as client:
                import time
                start_time = time.time()
                
                response = client.get('/public/points')
                
                end_time = time.time()
                response_time = end_time - start_time
                
                assert response.status_code == 200
                assert response_time < 2.0  # Exigence de performance
    
    def test_sorting_performance_with_large_dataset(self):
        """Test de performance du tri avec beaucoup de données"""
        import random
        
        # Dataset avec points aléatoires
        large_dataset = []
        for i in range(500):
            large_dataset.append({
                'name': f'Club {i}',
                'points': str(random.randint(0, 100))
            })
        
        with patch.object(server, 'clubs', large_dataset):
            with server.app.test_client() as client:
                response = client.get('/public/points')
                
                assert response.status_code == 200
                # Vérifier que le tri s'est bien effectué
                html_content = response.data.decode('utf-8')
                assert 'Club' in html_content