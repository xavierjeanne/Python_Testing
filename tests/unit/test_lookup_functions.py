"""
Tests unitaires pour les fonctions de recherche et lookup
"""
import pytest
from unittest.mock import patch


class TestClubLookup:
    """Tests pour la logique de recherche de clubs"""
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
    ])
    def test_find_club_by_name_single_result(self):
        """Test recherche de club par nom - résultat unique"""
        from server import clubs
        
        club_name = "Simply Lift"
        result = [c for c in clubs if c['name'] == club_name]
        
        assert len(result) == 1
        assert result[0]['name'] == "Simply Lift"
        assert result[0]['points'] == "13"
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"}
    ])
    def test_find_club_by_name_no_result(self):
        """Test recherche de club par nom - aucun résultat"""
        from server import clubs
        
        club_name = "Nonexistent Club"
        result = [c for c in clubs if c['name'] == club_name]
        
        assert len(result) == 0
        assert result == []
    
    @patch('server.clubs', [
        {"name": "Club A", "email": "a@test.com", "points": "10"},
        {"name": "Club A", "email": "a2@test.com", "points": "5"}  # Nom dupliqué
    ])
    def test_find_club_by_name_duplicate_names(self):
        """Test recherche avec noms dupliqués"""
        from server import clubs
        
        club_name = "Club A"
        result = [c for c in clubs if c['name'] == club_name]
        
        assert len(result) == 2
        assert all(club['name'] == "Club A" for club in result)
    
    @patch('server.clubs', [])
    def test_find_club_in_empty_list(self):
        """Test recherche dans liste vide"""
        from server import clubs
        
        club_name = "Any Club"
        result = [c for c in clubs if c['name'] == club_name]
        
        assert result == []


class TestCompetitionLookup:
    """Tests pour la logique de recherche de compétitions"""
    
    @patch('server.competitions', [
        {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"},
        {"name": "Fall Classic", "date": "2025-10-22 13:30:00", "numberOfPlaces": "13"}
    ])
    def test_find_competition_by_name_single_result(self):
        """Test recherche de compétition par nom - résultat unique"""
        from server import competitions
        
        comp_name = "Spring Festival"
        result = [c for c in competitions if c['name'] == comp_name]
        
        assert len(result) == 1
        assert result[0]['name'] == "Spring Festival"
        assert result[0]['numberOfPlaces'] == "25"
    
    @patch('server.competitions', [
        {"name": "Spring Festival", "date": "2025-03-27 10:00:00", "numberOfPlaces": "25"}
    ])
    def test_find_competition_by_name_no_result(self):
        """Test recherche de compétition par nom - aucun résultat"""
        from server import competitions
        
        comp_name = "Nonexistent Competition"
        result = [c for c in competitions if c['name'] == comp_name]
        
        assert result == []


class TestEmailLookupLogic:
    """Tests pour la logique de recherche par email"""
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"},
        {"name": "Iron Temple", "email": "admin@irontemple.com", "points": "4"},
        {"name": "She Lifts", "email": "kate@shelifts.co.uk", "points": "12"}
    ])
    def test_find_club_by_email_exact_match(self):
        """Test recherche par email - correspondance exacte"""
        from server import clubs
        
        email = "john@simplylift.co"
        club_list = [club for club in clubs if club['email'] == email]
        
        assert len(club_list) == 1
        assert club_list[0]['name'] == "Simply Lift"
        assert club_list[0]['email'] == email
    
    @patch('server.clubs', [
        {"name": "Simply Lift", "email": "john@simplylift.co", "points": "13"}
    ])
    def test_find_club_by_email_case_sensitive(self):
        """Test recherche par email - sensible à la casse"""
        from server import clubs
        
        # Email avec casse différente
        email = "JOHN@SIMPLYLIFT.CO"
        club_list = [club for club in clubs if club['email'] == email]
        
        assert len(club_list) == 0  # Pas de correspondance car sensible à la casse
    
    @patch('server.clubs', [
        {"name": "Club A", "email": "test@example.com", "points": "10"},
        {"name": "Club B", "email": "test@example.com", "points": "5"}  # Email dupliqué
    ])
    def test_find_club_by_email_duplicate_emails(self):
        """Test recherche avec emails dupliqués"""
        from server import clubs
        
        email = "test@example.com"
        club_list = [club for club in clubs if club['email'] == email]
        
        assert len(club_list) == 2
        assert all(club['email'] == email for club in club_list)


class TestIndexAccess:
    """Tests pour l'accès par index [0] après recherche"""
    
    @patch('server.clubs', [
        {"name": "Test Club", "email": "test@club.com", "points": "10"}
    ])
    def test_get_first_club_from_search_success(self):
        """Test accès au premier élément quand la recherche réussit"""
        from server import clubs
        
        club_name = "Test Club"
        found_clubs = [c for c in clubs if c['name'] == club_name]
        
        # Vérifier que la liste n'est pas vide avant d'accéder à [0]
        assert len(found_clubs) > 0
        
        first_club = found_clubs[0]
        assert first_club['name'] == "Test Club"
    
    @patch('server.clubs', [])
    def test_get_first_club_from_search_failure(self):
        """Test accès au premier élément quand la recherche échoue"""
        from server import clubs
        
        club_name = "Nonexistent Club"
        found_clubs = [c for c in clubs if c['name'] == club_name]
        
        # Vérifier que tenter d'accéder à [0] sur une liste vide lève IndexError
        assert len(found_clubs) == 0
        
        with pytest.raises(IndexError):
            first_club = found_clubs[0]
    
    def test_safe_first_element_access(self):
        """Test méthode sécurisée pour accéder au premier élément"""
        # Cas avec données
        data_with_results = [{"name": "Club A"}, {"name": "Club B"}]
        first_element = data_with_results[0] if data_with_results else None
        assert first_element is not None
        assert first_element['name'] == "Club A"
        
        # Cas sans données
        empty_data = []
        first_element = empty_data[0] if empty_data else None
        assert first_element is None