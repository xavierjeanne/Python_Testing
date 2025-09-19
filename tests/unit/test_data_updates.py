"""
Tests unitaires pour la logique de mise à jour des données
"""
import pytest
from unittest.mock import patch


class TestDataUpdateLogic:
    """Tests pour la logique de mise à jour des points et places"""
    
    def test_update_competition_places_after_booking(self):
        """Test mise à jour des places de compétition après réservation"""
        # État initial
        initial_places = 25
        places_required = 7
        
        # Calcul de mise à jour
        new_places = initial_places - places_required
        
        assert new_places == 18
        assert new_places >= 0  # Ne doit pas être négatif
    
    def test_update_competition_places_string_conversion(self):
        """Test conversion en string pour les places de compétition"""
        initial_places = 25  # int
        places_required = 7
        new_places = initial_places - places_required
        
        # Conversion en string comme dans le code
        places_as_string = str(new_places)
        
        assert places_as_string == "18"
        assert isinstance(places_as_string, str)
    
    def test_update_club_points_after_booking(self):
        """Test mise à jour des points de club après réservation"""
        initial_points = 13
        points_needed = 5  # 1 point par place
        
        # Calcul de mise à jour
        new_points = initial_points - points_needed
        
        assert new_points == 8
        assert new_points >= 0  # Ne doit pas être négatif
    
    def test_update_club_points_string_conversion(self):
        """Test conversion en string pour les points de club"""
        initial_points = 13  # int
        points_needed = 5
        new_points = initial_points - points_needed
        
        # Conversion en string comme dans le code
        points_as_string = str(new_points)
        
        assert points_as_string == "8"
        assert isinstance(points_as_string, str)
    
    def test_update_both_club_and_competition_data(self):
        """Test mise à jour simultanée club et compétition"""
        # État initial
        club_data = {"name": "Test Club", "points": "13"}
        competition_data = {"name": "Test Competition", "numberOfPlaces": "25"}
        places_required = 5
        
        # Conversions pour calculs
        initial_points = int(club_data['points'])
        initial_places = int(competition_data['numberOfPlaces'])
        
        # Calculs
        new_points = initial_points - places_required
        new_places = initial_places - places_required
        
        # Mise à jour (simulation)
        updated_club = club_data.copy()
        updated_competition = competition_data.copy()
        updated_club['points'] = str(new_points)
        updated_competition['numberOfPlaces'] = str(new_places)
        
        assert updated_club['points'] == "8"
        assert updated_competition['numberOfPlaces'] == "20"
    
    def test_update_edge_case_zero_remaining(self):
        """Test mise à jour quand il reste exactement zéro"""
        # Club avec exactement les points nécessaires
        club_points = 5
        points_needed = 5
        new_points = club_points - points_needed
        
        assert new_points == 0
        
        # Compétition avec exactement les places nécessaires
        comp_places = 10
        places_required = 10
        new_places = comp_places - places_required
        
        assert new_places == 0
    
    def test_update_prevents_negative_values_defensive(self):
        """Test défensif pour éviter les valeurs négatives"""
        # Cas où on pourrait avoir des valeurs négatives
        club_points = 3
        points_needed = 5  # Plus que disponible
        
        # Mise à jour défensive
        new_points = max(0, club_points - points_needed)
        
        assert new_points == 0  # Pas négatif
        
        # Pareil pour les places
        comp_places = 2
        places_required = 5  # Plus que disponible
        
        new_places = max(0, comp_places - places_required)
        
        assert new_places == 0  # Pas négatif


class TestStringIntConversions:
    """Tests pour les conversions string/int dans les données"""
    
    def test_convert_string_points_to_int(self):
        """Test conversion des points de string vers int"""
        test_cases = [
            ("0", 0),
            ("5", 5),
            ("13", 13),
            ("100", 100)
        ]
        
        for string_val, expected_int in test_cases:
            result = int(string_val)
            assert result == expected_int
            assert isinstance(result, int)
    
    def test_convert_string_places_to_int(self):
        """Test conversion des places de string vers int"""
        test_cases = [
            ("0", 0),
            ("10", 10),
            ("25", 25),
            ("13", 13)
        ]
        
        for string_val, expected_int in test_cases:
            result = int(string_val)
            assert result == expected_int
            assert isinstance(result, int)
    
    def test_convert_int_to_string_for_storage(self):
        """Test conversion int vers string pour stockage"""
        test_cases = [
            (0, "0"),
            (5, "5"),
            (13, "13"),
            (25, "25")
        ]
        
        for int_val, expected_string in test_cases:
            result = str(int_val)
            assert result == expected_string
            assert isinstance(result, str)
    
    def test_roundtrip_conversion(self):
        """Test conversion aller-retour string->int->string"""
        original_values = ["0", "5", "13", "25"]
        
        for original in original_values:
            # String -> Int -> String
            as_int = int(original)
            back_to_string = str(as_int)
            
            assert back_to_string == original
    
    def test_invalid_string_conversion_raises_error(self):
        """Test que les conversions invalides lèvent des erreurs"""
        invalid_values = ["abc", "10.5", "", "10abc", None]
        
        for invalid_val in invalid_values:
            if invalid_val is None:
                with pytest.raises(TypeError):
                    int(invalid_val)
            else:
                with pytest.raises(ValueError):
                    int(invalid_val)


class TestDataIntegrityChecks:
    """Tests pour vérifier l'intégrité des données après mise à jour"""
    
    def test_club_points_remain_valid_after_update(self):
        """Test que les points de club restent valides après mise à jour"""
        club = {"name": "Test Club", "points": "10"}
        places_required = 3
        
        initial_points = int(club['points'])
        new_points = initial_points - places_required
        
        # Vérifications d'intégrité
        assert new_points >= 0  # Pas négatif
        assert isinstance(new_points, int)  # Type correct
        
        # Mise à jour
        club['points'] = str(new_points)
        
        # Vérification après mise à jour
        assert club['points'] == "7"
        assert int(club['points']) == 7  # Toujours convertible
    
    def test_competition_places_remain_valid_after_update(self):
        """Test que les places de compétition restent valides après mise à jour"""
        competition = {"name": "Test Competition", "numberOfPlaces": "20"}
        places_required = 5
        
        initial_places = int(competition['numberOfPlaces'])
        new_places = initial_places - places_required
        
        # Vérifications d'intégrité
        assert new_places >= 0  # Pas négatif
        assert isinstance(new_places, int)  # Type correct
        
        # Mise à jour
        competition['numberOfPlaces'] = str(new_places)
        
        # Vérification après mise à jour
        assert competition['numberOfPlaces'] == "15"
        assert int(competition['numberOfPlaces']) == 15  # Toujours convertible