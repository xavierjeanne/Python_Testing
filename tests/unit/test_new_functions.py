"""
Tests unitaires pour les nouvelles fonctions créées
"""
import pytest
from unittest.mock import patch


class TestFindFunctions:
    """Tests pour les fonctions de recherche sécurisées"""
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
    ])
    def test_findClubByName_exists(self):
        """Test findClubByName avec un club existant"""
        from server import findClubByName
        
        result = findClubByName("Simply Lift")
        
        assert result is not None
        assert result['name'] == "Simply Lift"
        assert result['points'] == "13"
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
    ])
    def test_findClubByName_not_exists(self):
        """Test findClubByName avec un club inexistant"""
        from server import findClubByName
        
        result = findClubByName("Nonexistent Club")
        
        assert result is None
    
    @patch('server.clubs', [])
    def test_findClubByName_empty_list(self):
        """Test findClubByName avec liste vide"""
        from server import findClubByName
        
        result = findClubByName("Any Club")
        
        assert result is None
    
    @patch('server.competitions', [
        {"name": "Spring Festival", "date": "2025-03-27", "numberOfPlaces": "25"}
    ])
    def test_findCompetitionByName_exists(self):
        """Test findCompetitionByName avec compétition existante"""
        from server import findCompetitionByName
        
        result = findCompetitionByName("Spring Festival")
        
        assert result is not None
        assert result['name'] == "Spring Festival"
        assert result['numberOfPlaces'] == "25"
    
    @patch('server.competitions', [])
    def test_findCompetitionByName_not_exists(self):
        """Test findCompetitionByName avec compétition inexistante"""
        from server import findCompetitionByName
        
        result = findCompetitionByName("Nonexistent Competition")
        
        assert result is None
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
    ])
    def test_findClubByEmail_exists(self):
        """Test findClubByEmail avec email existant"""
        from server import findClubByEmail
        
        result = findClubByEmail("john@simplylift.co")
        
        assert result is not None
        assert result['name'] == "Simply Lift"
        assert result['email'] == "john@simplylift.co"
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
    ])
    def test_findClubByEmail_not_exists(self):
        """Test findClubByEmail avec email inexistant"""
        from server import findClubByEmail
        
        result = findClubByEmail("nonexistent@email.com")
        
        assert result is None


class TestCalculateBookingLimits:
    """Tests pour la fonction calculateBookingLimits"""
    
    @patch('server.getClubBookingsForCompetition')
    def test_calculateBookingLimits_no_existing_bookings(self, mock_get_bookings):
        """Test calcul des limites sans réservations existantes"""
        from server import calculateBookingLimits
        
        # Mock no existing bookings
        mock_get_bookings.return_value = []
        
        club = {"name": "Test Club", "points": "15"}
        competition = {"name": "Test Competition", "numberOfPlaces": "20"}
        
        result = calculateBookingLimits(club, competition)
        
        assert result['places_already_booked'] == 0
        assert result['remaining_from_12_limit'] == 12
        assert result['club_points'] == 15
        assert result['available_places'] == 20
        assert result['max_remaining'] == 12  # min(12, 15, 20)
    
    @patch('server.getClubBookingsForCompetition')
    def test_calculateBookingLimits_with_existing_bookings(self, mock_get_bookings):
        """Test calcul des limites avec réservations existantes"""
        from server import calculateBookingLimits
        
        # Mock existing bookings
        mock_get_bookings.return_value = [
            {"places": 3},
            {"places": 2}
        ]
        
        club = {"name": "Test Club", "points": "15"}
        competition = {"name": "Test Competition", "numberOfPlaces": "20"}
        
        result = calculateBookingLimits(club, competition)
        
        assert result['places_already_booked'] == 5
        assert result['remaining_from_12_limit'] == 7  # 12 - 5
        assert result['club_points'] == 15
        assert result['available_places'] == 20
        assert result['max_remaining'] == 7  # min(7, 15, 20)
    
    @patch('server.getClubBookingsForCompetition')
    def test_calculateBookingLimits_limited_by_points(self, mock_get_bookings):
        """Test calcul des limites quand les points sont limitants"""
        from server import calculateBookingLimits
        
        mock_get_bookings.return_value = []
        
        club = {"name": "Test Club", "points": "3"}  # Limitant
        competition = {"name": "Test Competition", "numberOfPlaces": "20"}
        
        result = calculateBookingLimits(club, competition)
        
        assert result['max_remaining'] == 3  # Limité par les points
    
    @patch('server.getClubBookingsForCompetition')
    def test_calculateBookingLimits_limited_by_competition_places(self, mock_get_bookings):
        """Test calcul des limites quand les places de compétition sont limitantes"""
        from server import calculateBookingLimits
        
        mock_get_bookings.return_value = []
        
        club = {"name": "Test Club", "points": "15"}
        competition = {"name": "Test Competition", "numberOfPlaces": "2"}  # Limitant
        
        result = calculateBookingLimits(club, competition)
        
        assert result['max_remaining'] == 2  # Limité par les places de compétition


class TestValidateBookingRequest:
    """Tests pour la fonction validateBookingRequest"""
    
    def test_validateBookingRequest_valid_request(self):
        """Test validation d'une demande valide"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 3,
            'club_points': 15,
            'available_places': 20
        }
        
        is_valid, error_message = validateBookingRequest(5, limits)
        
        assert is_valid is True
        assert error_message is None
    
    def test_validateBookingRequest_negative_places(self):
        """Test validation avec places négatives"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 0,
            'club_points': 15,
            'available_places': 20
        }
        
        is_valid, error_message = validateBookingRequest(-1, limits)
        
        assert is_valid is False
        assert error_message == 'Number of places must be greater than 0.'
    
    def test_validateBookingRequest_zero_places(self):
        """Test validation avec zéro places"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 0,
            'club_points': 15,
            'available_places': 20
        }
        
        is_valid, error_message = validateBookingRequest(0, limits)
        
        assert is_valid is False
        assert error_message == 'Number of places must be greater than 0.'
    
    def test_validateBookingRequest_more_than_12_places(self):
        """Test validation avec plus de 12 places en une fois"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 0,
            'club_points': 15,
            'available_places': 20
        }
        
        is_valid, error_message = validateBookingRequest(13, limits)
        
        assert is_valid is False
        assert error_message == 'Impossible to reserve more than 12 places at once per competition.'
    
    def test_validateBookingRequest_exceeds_total_limit(self):
        """Test validation dépassement limite totale de 12"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 8,  # Déjà 8 places
            'club_points': 15,
            'available_places': 20
        }
        
        is_valid, error_message = validateBookingRequest(7, limits)  # 8 + 7 = 15 > 12
        
        assert is_valid is False
        assert "Maximum 12 places per club per competition" in error_message
        assert "already have 8 places booked" in error_message
        assert "You can only book 4 more places" in error_message
    
    def test_validateBookingRequest_insufficient_competition_places(self):
        """Test validation places insuffisantes dans compétition"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 0,
            'club_points': 15,
            'available_places': 3  # Seulement 3 places disponibles
        }
        
        is_valid, error_message = validateBookingRequest(5, limits)  # Demande 5 > 3
        
        assert is_valid is False
        assert error_message == 'Not enough places available. Only 3 places left.'
    
    def test_validateBookingRequest_insufficient_points(self):
        """Test validation points insuffisants"""
        from server import validateBookingRequest
        
        limits = {
            'places_already_booked': 0,
            'club_points': 3,  # Seulement 3 points
            'available_places': 20
        }
        
        is_valid, error_message = validateBookingRequest(5, limits)  # Demande 5 > 3
        
        assert is_valid is False
        assert error_message == 'Not enough points. You need 5 points but only have 3.'


class TestProcessBooking:
    """Tests pour la fonction processBooking"""
    
    @patch('server.addBooking')
    @patch('server.saveCompetitions')
    @patch('server.saveClubs')
    def test_processBooking_success(self, mock_save_clubs, mock_save_competitions, mock_add_booking):
        """Test traitement réussi d'une réservation"""
        from server import processBooking
        
        club = {"name": "Test Club", "points": "15"}
        competition = {"name": "Test Competition", "numberOfPlaces": "20"}
        places_required = 5
        
        processBooking(club, competition, places_required)
        
        # Vérifier mise à jour des données
        assert club['points'] == "10"  # 15 - 5
        assert competition['numberOfPlaces'] == "15"  # 20 - 5
        
        # Vérifier appels aux fonctions
        mock_add_booking.assert_called_once_with("Test Club", "Test Competition", 5, 5)
        mock_save_competitions.assert_called_once()
        mock_save_clubs.assert_called_once()
    
    @patch('server.addBooking')
    @patch('server.saveCompetitions')
    @patch('server.saveClubs')
    def test_processBooking_edge_case_all_points_used(self, mock_save_clubs, mock_save_competitions, mock_add_booking):
        """Test traitement quand tous les points sont utilisés"""
        from server import processBooking
        
        club = {"name": "Test Club", "points": "5"}  # Exactement 5 points
        competition = {"name": "Test Competition", "numberOfPlaces": "20"}
        places_required = 5  # Utilise tous les points
        
        processBooking(club, competition, places_required)
        
        assert club['points'] == "0"  # 5 - 5 = 0
        assert competition['numberOfPlaces'] == "15"  # 20 - 5 = 15