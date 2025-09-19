"""
Tests unitaires pour les fonctions de gestion des réservations
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from server import addBooking, getClubBookings, getCompetitionBookings, getClubBookingsForCompetition


class TestAddBooking:
    """Tests unitaires pour addBooking()"""
    
    @patch('server.bookings', [])
    @patch('server.saveBookings')
    def test_addBooking_first_booking(self, mock_save):
        """Test ajout de la première réservation"""
        with patch('server.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2025-09-19T10:00:00"
            
            addBooking("Test Club", "Test Competition", 5, 5)
        
        # Import bookings after the function call to see the updated state
        from server import bookings
        
        assert len(bookings) == 1
        assert bookings[0]['id'] == 1
        assert bookings[0]['club'] == "Test Club"
        assert bookings[0]['competition'] == "Test Competition"
        assert bookings[0]['places'] == 5
        assert bookings[0]['points_used'] == 5
        assert bookings[0]['date'] == "2025-09-19T10:00:00"
        assert bookings[0]['status'] == 'confirmed'
        
        mock_save.assert_called_once()
    
    @patch('server.bookings', [{"id": 1, "club": "Existing Club", "competition": "Existing Comp", "places": 3, "points_used": 3, "date": "2025-09-18", "status": "confirmed"}])
    @patch('server.saveBookings')
    def test_addBooking_subsequent_booking(self, mock_save):
        """Test ajout d'une réservation quand il y en a déjà"""
        with patch('server.datetime') as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = "2025-09-19T11:00:00"
            
            addBooking("New Club", "New Competition", 7, 7)
        
        from server import bookings
        
        assert len(bookings) == 2
        assert bookings[1]['id'] == 2  # Should increment ID
        assert bookings[1]['club'] == "New Club"
        assert bookings[1]['places'] == 7
        
        mock_save.assert_called_once()


class TestGetClubBookings:
    """Tests unitaires pour getClubBookings()"""
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5},
        {"club": "Club B", "competition": "Comp 1", "places": 3},
        {"club": "Club A", "competition": "Comp 2", "places": 7}
    ])
    def test_getClubBookings_existing_club(self):
        """Test récupération des réservations d'un club existant"""
        result = getClubBookings("Club A")
        
        assert len(result) == 2
        assert all(booking['club'] == "Club A" for booking in result)
        assert result[0]['competition'] == "Comp 1"
        assert result[1]['competition'] == "Comp 2"
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5},
        {"club": "Club B", "competition": "Comp 1", "places": 3}
    ])
    def test_getClubBookings_nonexistent_club(self):
        """Test récupération des réservations d'un club inexistant"""
        result = getClubBookings("Club C")
        
        assert result == []
    
    @patch('server.bookings', [])
    def test_getClubBookings_empty_bookings(self):
        """Test récupération quand aucune réservation"""
        result = getClubBookings("Any Club")
        
        assert result == []


class TestGetCompetitionBookings:
    """Tests unitaires pour getCompetitionBookings()"""
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5},
        {"club": "Club B", "competition": "Comp 1", "places": 3},
        {"club": "Club A", "competition": "Comp 2", "places": 7}
    ])
    def test_getCompetitionBookings_existing_competition(self):
        """Test récupération des réservations d'une compétition existante"""
        result = getCompetitionBookings("Comp 1")
        
        assert len(result) == 2
        assert all(booking['competition'] == "Comp 1" for booking in result)
        assert result[0]['club'] == "Club A"
        assert result[1]['club'] == "Club B"
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5}
    ])
    def test_getCompetitionBookings_nonexistent_competition(self):
        """Test récupération des réservations d'une compétition inexistante"""
        result = getCompetitionBookings("Comp 99")
        
        assert result == []


class TestGetClubBookingsForCompetition:
    """Tests unitaires pour getClubBookingsForCompetition()"""
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5},
        {"club": "Club B", "competition": "Comp 1", "places": 3},
        {"club": "Club A", "competition": "Comp 2", "places": 7}
    ])
    def test_getClubBookingsForCompetition_existing_combination(self):
        """Test récupération des réservations d'un club pour une compétition spécifique"""
        result = getClubBookingsForCompetition("Club A", "Comp 1")
        
        assert len(result) == 1
        assert result[0]['club'] == "Club A"
        assert result[0]['competition'] == "Comp 1"
        assert result[0]['places'] == 5
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5},
        {"club": "Club B", "competition": "Comp 1", "places": 3}
    ])
    def test_getClubBookingsForCompetition_nonexistent_combination(self):
        """Test récupération pour une combinaison club/compétition inexistante"""
        result = getClubBookingsForCompetition("Club C", "Comp 1")
        
        assert result == []
    
    @patch('server.bookings', [
        {"club": "Club A", "competition": "Comp 1", "places": 5},
        {"club": "Club A", "competition": "Comp 1", "places": 3},
        {"club": "Club A", "competition": "Comp 2", "places": 7}
    ])
    def test_getClubBookingsForCompetition_multiple_bookings_same_combination(self):
        """Test récupération avec plusieurs réservations pour la même combinaison"""
        result = getClubBookingsForCompetition("Club A", "Comp 1")
        
        assert len(result) == 2
        assert all(booking['club'] == "Club A" and booking['competition'] == "Comp 1" for booking in result)
        total_places = sum(booking['places'] for booking in result)
        assert total_places == 8