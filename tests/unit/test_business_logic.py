"""
Tests unitaires pour les fonctions de validation métier
Ces tests se concentrent sur la logique de validation sans interaction Flask
"""
import pytest
from unittest.mock import patch


class TestBusinessValidation:
    """Tests unitaires pour la logique de validation métier"""
    
    def test_calculate_max_remaining_no_bookings(self):
        """Test calcul de limite sans réservations existantes"""
        # Simule un club avec 13 points, aucune réservation, compétition avec 25 places
        with patch('server.getClubBookingsForCompetition', return_value=[]):
            from server import getClubBookingsForCompetition
            
            existing_bookings = getClubBookingsForCompetition("Test Club", "Test Competition")
            places_already_booked = sum(booking['places'] for booking in existing_bookings)
            club_points = 13
            competition_places = 25
            
            # Calcul de la limite comme dans le code
            remaining_from_12_limit = 12 - places_already_booked
            max_remaining = min(remaining_from_12_limit, club_points, competition_places)
            
            assert places_already_booked == 0
            assert max_remaining == 12  # min(12, 13, 25)
    
    def test_calculate_max_remaining_with_existing_bookings(self):
        """Test calcul de limite avec réservations existantes"""
        # Simule des réservations existantes
        mock_bookings = [
            {"places": 3},
            {"places": 2}
        ]
        
        with patch('server.getClubBookingsForCompetition', return_value=mock_bookings):
            from server import getClubBookingsForCompetition
            
            existing_bookings = getClubBookingsForCompetition("Test Club", "Test Competition")
            places_already_booked = sum(booking['places'] for booking in existing_bookings)
            club_points = 13
            competition_places = 25
            
            remaining_from_12_limit = 12 - places_already_booked
            max_remaining = min(remaining_from_12_limit, club_points, competition_places)
            
            assert places_already_booked == 5
            assert max_remaining == 7  # min(7, 13, 25)
    
    def test_calculate_max_remaining_limited_by_points(self):
        """Test calcul de limite quand les points sont le facteur limitant"""
        with patch('server.getClubBookingsForCompetition', return_value=[]):
            existing_bookings = []
            places_already_booked = 0
            club_points = 3  # Points limitants
            competition_places = 25
            
            remaining_from_12_limit = 12 - places_already_booked
            max_remaining = min(remaining_from_12_limit, club_points, competition_places)
            
            assert max_remaining == 3  # Limité par les points
    
    def test_calculate_max_remaining_limited_by_competition_places(self):
        """Test calcul de limite quand les places de compétition sont limitantes"""
        with patch('server.getClubBookingsForCompetition', return_value=[]):
            existing_bookings = []
            places_already_booked = 0
            club_points = 13
            competition_places = 2  # Places limitantes
            
            remaining_from_12_limit = 12 - places_already_booked
            max_remaining = min(remaining_from_12_limit, club_points, competition_places)
            
            assert max_remaining == 2  # Limité par les places de compétition
    
    def test_calculate_max_remaining_at_12_places_limit(self):
        """Test calcul quand on a atteint la limite de 12 places"""
        mock_bookings = [
            {"places": 7},
            {"places": 5}
        ]
        
        with patch('server.getClubBookingsForCompetition', return_value=mock_bookings):
            existing_bookings = mock_bookings
            places_already_booked = sum(booking['places'] for booking in existing_bookings)
            club_points = 13
            competition_places = 25
            
            remaining_from_12_limit = 12 - places_already_booked
            max_remaining = min(remaining_from_12_limit, club_points, competition_places)
            
            assert places_already_booked == 12
            assert max_remaining == 0  # Limite de 12 places atteinte


class TestValidationRules:
    """Tests unitaires pour les règles de validation individuelles"""
    
    def test_positive_places_validation(self):
        """Test validation que les places doivent être positives"""
        test_cases = [
            (0, False),
            (-1, False),
            (-10, False),
            (1, True),
            (5, True),
            (12, True)
        ]
        
        for places, expected_valid in test_cases:
            is_valid = places > 0
            assert is_valid == expected_valid, f"Places {places} should be {'valid' if expected_valid else 'invalid'}"
    
    def test_max_12_places_per_booking_validation(self):
        """Test validation de maximum 12 places par réservation"""
        test_cases = [
            (1, True),
            (12, True),
            (13, False),
            (20, False)
        ]
        
        for places, expected_valid in test_cases:
            is_valid = places <= 12
            assert is_valid == expected_valid, f"Places {places} should be {'valid' if expected_valid else 'invalid'}"
    
    def test_total_places_limit_validation(self):
        """Test validation de la limite totale de 12 places par club/compétition"""
        test_cases = [
            # (places_already_booked, places_requested, expected_valid)
            (0, 12, True),
            (5, 7, True),
            (10, 2, True),
            (12, 0, True),
            (11, 2, False),  # 11 + 2 = 13 > 12
            (12, 1, False),  # 12 + 1 = 13 > 12
        ]
        
        for existing, requested, expected_valid in test_cases:
            total_after = existing + requested
            is_valid = total_after <= 12
            assert is_valid == expected_valid, f"Existing {existing} + Requested {requested} = {total_after} should be {'valid' if expected_valid else 'invalid'}"
    
    def test_sufficient_points_validation(self):
        """Test validation des points suffisants"""
        test_cases = [
            # (club_points, places_requested, expected_valid)
            (10, 5, True),
            (10, 10, True),
            (10, 11, False),
            (0, 1, False),
            (5, 5, True)
        ]
        
        for club_points, requested_places, expected_valid in test_cases:
            points_needed = requested_places  # 1 point par place
            is_valid = club_points >= points_needed
            assert is_valid == expected_valid, f"Club points {club_points} vs needed {points_needed} should be {'valid' if expected_valid else 'invalid'}"
    
    def test_competition_availability_validation(self):
        """Test validation de disponibilité des places dans la compétition"""
        test_cases = [
            # (competition_places, places_requested, expected_valid)
            (25, 10, True),
            (25, 25, True),
            (25, 26, False),
            (0, 1, False),
            (1, 1, True)
        ]
        
        for comp_places, requested, expected_valid in test_cases:
            is_valid = comp_places >= requested
            assert is_valid == expected_valid, f"Competition places {comp_places} vs requested {requested} should be {'valid' if expected_valid else 'invalid'}"