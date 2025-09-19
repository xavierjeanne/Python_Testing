"""
Tests unitaires pour les fonctions utilitaires et helpers
"""
import pytest
from unittest.mock import patch


class TestEmailValidation:
    """Tests unitaires pour la validation d'email"""
    
    @patch('server.clubs', [
        {"name": "Club A", "email": "test@cluba.com", "points": "10"},
        {"name": "Club B", "email": "admin@clubb.com", "points": "5"}
    ])
    def test_find_club_by_email_existing_email(self):
        """Test recherche de club par email existant"""
        from server import clubs
        
        email = "test@cluba.com"
        club_list = [club for club in clubs if club['email'] == email]
        
        assert len(club_list) == 1
        assert club_list[0]['name'] == "Club A"
        assert club_list[0]['email'] == "test@cluba.com"
    
    @patch('server.clubs', [
        {"name": "Club A", "email": "test@cluba.com", "points": "10"},
        {"name": "Club B", "email": "admin@clubb.com", "points": "5"}
    ])
    def test_find_club_by_email_nonexistent_email(self):
        """Test recherche de club par email inexistant"""
        from server import clubs
        
        email = "nonexistent@email.com"
        club_list = [club for club in clubs if club['email'] == email]
        
        assert len(club_list) == 0
        assert club_list == []
    
    @patch('server.clubs', [])
    def test_find_club_by_email_empty_clubs_list(self):
        """Test recherche dans une liste de clubs vide"""
        from server import clubs
        
        email = "test@email.com"
        club_list = [club for club in clubs if club['email'] == email]
        
        assert len(club_list) == 0


class TestClubAndCompetitionLookup:
    """Tests unitaires pour la recherche de clubs et compétitions"""
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
    ])
    def test_find_club_by_name_existing(self):
        """Test recherche de club par nom existant"""
        from server import clubs
        
        club_name = "Simply Lift"
        found_clubs = [c for c in clubs if c['name'] == club_name]
        
        assert len(found_clubs) == 1
        assert found_clubs[0]['name'] == "Simply Lift"
        assert found_clubs[0]['email'] == "john@simplylift.co"
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
    ])
    def test_find_club_by_name_nonexistent(self):
        """Test recherche de club par nom inexistant"""
        from server import clubs
        
        club_name = "Nonexistent Club"
        found_clubs = [c for c in clubs if c['name'] == club_name]
        
        assert len(found_clubs) == 0
    
    @patch('server.competitions', [
        {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"},
        {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "13"}
    ])
    def test_find_competition_by_name_existing(self):
        """Test recherche de compétition par nom existant"""
        from server import competitions
        
        comp_name = "Spring Festival"
        found_competitions = [c for c in competitions if c['name'] == comp_name]
        
        assert len(found_competitions) == 1
        assert found_competitions[0]['name'] == "Spring Festival"
        assert found_competitions[0]['numberOfPlaces'] == "25"
    
    @patch('server.competitions', [
        {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"}
    ])
    def test_find_competition_by_name_nonexistent(self):
        """Test recherche de compétition par nom inexistant"""
        from server import competitions
        
        comp_name = "Nonexistent Competition"
        found_competitions = [c for c in competitions if c['name'] == comp_name]
        
        assert len(found_competitions) == 0


class TestDataTypeConversions:
    """Tests unitaires pour les conversions de types de données"""
    
    def test_string_to_int_conversion_valid(self):
        """Test conversion string vers int pour des valeurs valides"""
        test_cases = [
            ("10", 10),
            ("0", 0),
            ("25", 25),
            ("13", 13)
        ]
        
        for string_val, expected_int in test_cases:
            result = int(string_val)
            assert result == expected_int
            assert isinstance(result, int)
    
    def test_string_to_int_conversion_invalid(self):
        """Test conversion string vers int pour des valeurs invalides"""
        invalid_values = ["abc", "10.5", "", "10abc", None]
        
        for invalid_val in invalid_values:
            if invalid_val is None:
                with pytest.raises(TypeError):
                    int(invalid_val)
            else:
                with pytest.raises(ValueError):
                    int(invalid_val)
    
    def test_form_data_processing(self):
        """Test traitement des données de formulaire"""
        # Simule request.form['places']
        form_data_cases = [
            ("5", 5),
            ("12", 12),
            ("0", 0),
            ("1", 1)
        ]
        
        for form_value, expected in form_data_cases:
            # Simule int(request.form['places'])
            places_required = int(form_value)
            assert places_required == expected
            assert isinstance(places_required, int)


class TestUtilityFunctions:
    """Tests unitaires pour les fonctions utilitaires"""
    
    def test_sum_booking_places(self):
        """Test calcul de la somme des places réservées"""
        bookings_cases = [
            ([], 0),
            ([{"places": 5}], 5),
            ([{"places": 3}, {"places": 2}], 5),
            ([{"places": 1}, {"places": 1}, {"places": 1}], 3),
            ([{"places": 0}, {"places": 5}], 5)
        ]
        
        for bookings, expected_sum in bookings_cases:
            result = sum(booking['places'] for booking in bookings)
            assert result == expected_sum
    
    def test_min_calculation_for_limits(self):
        """Test calcul du minimum pour les limites"""
        limit_cases = [
            # (remaining_from_12, club_points, competition_places, expected_min)
            (12, 13, 25, 12),  # Limité par rule des 12
            (7, 13, 25, 7),    # Limité par places déjà réservées
            (12, 3, 25, 3),    # Limité par points du club
            (12, 13, 2, 2),    # Limité par places de compétition
            (0, 13, 25, 0),    # Limite de 12 atteinte
            (5, 3, 2, 2)       # Multiple contraintes, la plus restrictive gagne
        ]
        
        for remaining, points, comp_places, expected in limit_cases:
            result = min(remaining, points, comp_places)
            assert result == expected
    
    def test_max_calculation_for_safety(self):
        """Test calcul max(0, value) pour éviter les valeurs négatives"""
        test_cases = [
            (5, 5),
            (0, 0),
            (-3, 0),
            (-10, 0),
            (12, 12)
        ]
        
        for value, expected in test_cases:
            result = max(0, value)
            assert result == expected
            assert result >= 0  # Toujours non-négatif