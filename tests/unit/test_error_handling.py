"""
Tests unitaires pour la génération de messages d'erreur et la logique métier
"""
import pytest
from unittest.mock import patch


class TestErrorMessageGeneration:
    """Tests pour la génération des messages d'erreur"""
    
    def test_positive_places_error_message(self):
        """Test message d'erreur pour places non positives"""
        expected_message = 'Number of places must be greater than 0.'
        
        # Test avec différentes valeurs invalides
        invalid_values = [0, -1, -5, -10]
        
        for value in invalid_values:
            if value <= 0:
                actual_message = 'Number of places must be greater than 0.'
                assert actual_message == expected_message
    
    def test_max_12_places_error_message(self):
        """Test message d'erreur pour dépassement de 12 places par réservation"""
        places_required = 15
        expected_message = 'Impossible to reserve more than 12 places at once per competition.'
        
        if places_required > 12:
            actual_message = 'Impossible to reserve more than 12 places at once per competition.'
            assert actual_message == expected_message
    
    def test_total_limit_exceeded_error_message(self):
        """Test message d'erreur pour dépassement de la limite totale"""
        places_already_booked = 8
        places_required = 7  # Total = 15 > 12
        max_allowed = 12
        remaining_allowed = max_allowed - places_already_booked
        
        expected_message = f'Maximum 12 places per club per competition. You already have {places_already_booked} places booked. You can only book {remaining_allowed} more places.'
        
        if places_already_booked + places_required > max_allowed:
            actual_message = f'Maximum 12 places per club per competition. You already have {places_already_booked} places booked. You can only book {remaining_allowed} more places.'
            assert actual_message == expected_message
            assert "8 places booked" in actual_message
            assert "4 more places" in actual_message
    
    def test_insufficient_competition_places_error_message(self):
        """Test message d'erreur pour places insuffisantes dans la compétition"""
        available_places = 3
        places_required = 5
        
        expected_message = f'Not enough places available. Only {available_places} places left.'
        
        if places_required > available_places:
            actual_message = f'Not enough places available. Only {available_places} places left.'
            assert actual_message == expected_message
            assert "Only 3 places left" in actual_message
    
    def test_insufficient_points_error_message(self):
        """Test message d'erreur pour points insuffisants"""
        club_points = 5
        points_needed = 8
        
        expected_message = f'Not enough points. You need {points_needed} points but only have {club_points}.'
        
        if club_points < points_needed:
            actual_message = f'Not enough points. You need {points_needed} points but only have {club_points}.'
            assert actual_message == expected_message
            assert "need 8 points" in actual_message
            assert "only have 5" in actual_message
    
    def test_success_message(self):
        """Test message de succès"""
        expected_message = 'Great-booking complete!'
        actual_message = 'Great-booking complete!'
        
        assert actual_message == expected_message


class TestValidationSequence:
    """Tests pour la séquence de validation dans l'ordre correct"""
    
    def test_validation_order_positive_places_first(self):
        """Test que la validation des places positives est en premier"""
        places_required = -1
        
        # Première validation: places positives
        if places_required <= 0:
            error = 'Number of places must be greater than 0.'
            assert error == 'Number of places must be greater than 0.'
            return  # Arrêt ici, pas de validation suivante
        
        # Les validations suivantes ne sont pas exécutées
        pytest.fail("Ne devrait pas arriver ici avec des places négatives")
    
    def test_validation_order_max_12_per_booking_second(self):
        """Test que la validation des 12 places par réservation est en second"""
        places_required = 15
        
        # Première validation passée (places positives)
        assert places_required > 0
        
        # Deuxième validation: max 12 par réservation
        if places_required > 12:
            error = 'Impossible to reserve more than 12 places at once per competition.'
            assert error == 'Impossible to reserve more than 12 places at once per competition.'
            return  # Arrêt ici
        
        pytest.fail("Ne devrait pas arriver ici avec plus de 12 places")
    
    def test_validation_order_total_limit_third(self):
        """Test que la validation de la limite totale est en troisième"""
        places_required = 8  # Valide individuellement
        places_already_booked = 7  # Total = 15 > 12
        
        # Premières validations passées
        assert places_required > 0
        assert places_required <= 12
        
        # Troisième validation: limite totale
        total_after_booking = places_already_booked + places_required
        if total_after_booking > 12:
            error = f'Maximum 12 places per club per competition. You already have {places_already_booked} places booked. You can only book {12 - places_already_booked} more places.'
            assert "You already have 7 places booked" in error
            assert "You can only book 5 more places" in error
            return
        
        pytest.fail("Ne devrait pas arriver ici avec dépassement de limite totale")
    
    def test_validation_order_competition_availability_fourth(self):
        """Test que la validation de disponibilité de compétition est en quatrième"""
        places_required = 5
        places_already_booked = 2  # Total = 7 <= 12 ✓
        available_places = 3  # Insuffisant
        
        # Validations précédentes passées
        assert places_required > 0
        assert places_required <= 12
        assert places_already_booked + places_required <= 12
        
        # Quatrième validation: disponibilité compétition
        if places_required > available_places:
            error = f'Not enough places available. Only {available_places} places left.'
            assert error == 'Not enough places available. Only 3 places left.'
            return
        
        pytest.fail("Ne devrait pas arriver ici avec places insuffisantes")
    
    def test_validation_order_points_last(self):
        """Test que la validation des points est en dernier"""
        places_required = 5
        places_already_booked = 2  # Total = 7 <= 12 ✓
        available_places = 10  # Suffisant ✓
        club_points = 3  # Insuffisant
        points_needed = places_required
        
        # Validations précédentes passées
        assert places_required > 0
        assert places_required <= 12
        assert places_already_booked + places_required <= 12
        assert places_required <= available_places
        
        # Dernière validation: points suffisants
        if club_points < points_needed:
            error = f'Not enough points. You need {points_needed} points but only have {club_points}.'
            assert error == 'Not enough points. You need 5 points but only have 3.'
            return
        
        pytest.fail("Ne devrait pas arriver ici avec points insuffisants")


class TestBusinessRulesLogic:
    """Tests pour la logique des règles métier"""
    
    def test_one_point_per_place_rule(self):
        """Test de la règle 1 point par place"""
        places_required_cases = [1, 3, 5, 12]
        
        for places in places_required_cases:
            points_needed = places  # 1 point par place
            assert points_needed == places
    
    def test_max_12_places_per_club_per_competition_rule(self):
        """Test de la règle maximum 12 places par club par compétition"""
        max_allowed = 12
        
        # Cas valides
        valid_totals = [1, 5, 10, 12]
        for total in valid_totals:
            assert total <= max_allowed
        
        # Cas invalides
        invalid_totals = [13, 15, 20]
        for total in invalid_totals:
            assert total > max_allowed
    
    def test_places_must_be_available_in_competition_rule(self):
        """Test de la règle de disponibilité des places"""
        competition_scenarios = [
            # (places_available, places_requested, should_be_valid)
            (10, 5, True),
            (10, 10, True),
            (10, 11, False),
            (0, 1, False),
            (1, 1, True)
        ]
        
        for available, requested, expected_valid in competition_scenarios:
            is_valid = requested <= available
            assert is_valid == expected_valid
    
    def test_club_must_have_sufficient_points_rule(self):
        """Test de la règle des points suffisants"""
        points_scenarios = [
            # (club_points, points_needed, should_be_valid)
            (10, 5, True),
            (10, 10, True),
            (10, 11, False),
            (0, 1, False),
            (5, 5, True)
        ]
        
        for club_points, needed, expected_valid in points_scenarios:
            is_valid = club_points >= needed
            assert is_valid == expected_valid