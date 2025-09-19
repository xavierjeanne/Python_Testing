"""
Tests unitaires pour les fonctions de sauvegarde de données
"""
import pytest
import json
from unittest.mock import patch, mock_open, MagicMock
from server import saveClubs, saveCompetitions, saveBookings


class TestSaveClubs:
    """Tests unitaires pour saveClubs()"""
    
    @patch('server.clubs', [{"name": "Test Club", "email": "test@club.com", "points": "10"}])
    def test_saveClubs_success(self):
        """Test sauvegarde réussie des clubs"""
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            saveClubs()
        
        # Vérifier que le fichier a été ouvert en écriture
        mock_file.assert_called_once_with('clubs.json', 'w')
        
        # Vérifier que json.dump a été appelé avec les bonnes données
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)
        
        assert 'clubs' in parsed_data
        assert len(parsed_data['clubs']) == 1
        assert parsed_data['clubs'][0]['name'] == "Test Club"
    
    @patch('server.clubs', [])
    def test_saveClubs_empty_list(self):
        """Test sauvegarde avec liste vide"""
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            saveClubs()
        
        mock_file.assert_called_once_with('clubs.json', 'w')
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)
        
        assert parsed_data['clubs'] == []


class TestSaveCompetitions:
    """Tests unitaires pour saveCompetitions()"""
    
    @patch('server.competitions', [{"name": "Test Comp", "date": "2025-10-22", "numberOfPlaces": "25"}])
    def test_saveCompetitions_success(self):
        """Test sauvegarde réussie des compétitions"""
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            saveCompetitions()
        
        mock_file.assert_called_once_with('competitions.json', 'w')
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)
        
        assert 'competitions' in parsed_data
        assert len(parsed_data['competitions']) == 1
        assert parsed_data['competitions'][0]['name'] == "Test Comp"


class TestSaveBookings:
    """Tests unitaires pour saveBookings()"""
    
    @patch('server.bookings', [{"id": 1, "club": "Test Club", "competition": "Test Comp", "places": 5}])
    def test_saveBookings_success(self):
        """Test sauvegarde réussie des réservations"""
        mock_file = mock_open()
        
        with patch("builtins.open", mock_file):
            saveBookings()
        
        mock_file.assert_called_once_with('bookings.json', 'w')
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        parsed_data = json.loads(written_data)
        
        assert 'bookings' in parsed_data
        assert len(parsed_data['bookings']) == 1
        assert parsed_data['bookings'][0]['club'] == "Test Club"