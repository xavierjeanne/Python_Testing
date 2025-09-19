"""
Tests unitaires pour les fonctions de chargement de données
"""
import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open
from server import loadClubs, loadCompetitions, loadBookings


class TestLoadClubs:
    """Tests unitaires pour loadClubs()"""
    
    def test_loadClubs_valid_file(self):
        """Test chargement réussi des clubs"""
        mock_data = {
            "clubs": [
                {"name": "Test Club", "email": "test@club.com", "points": "10"}
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = loadClubs()
            
        assert len(result) == 1
        assert result[0]["name"] == "Test Club"
        assert result[0]["email"] == "test@club.com"
        assert result[0]["points"] == "10"
    
    def test_loadClubs_empty_clubs_list(self):
        """Test chargement avec liste vide"""
        mock_data = {"clubs": []}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = loadClubs()
            
        assert result == []
    
    def test_loadClubs_file_not_found(self):
        """Test comportement quand le fichier n'existe pas"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError):
                loadClubs()
    
    def test_loadClubs_invalid_json(self):
        """Test comportement avec JSON invalide"""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            with pytest.raises(json.JSONDecodeError):
                loadClubs()


class TestLoadCompetitions:
    """Tests unitaires pour loadCompetitions()"""
    
    def test_loadCompetitions_valid_file(self):
        """Test chargement réussi des compétitions"""
        mock_data = {
            "competitions": [
                {
                    "name": "Test Competition",
                    "date": "2025-10-22 13:30:00",
                    "numberOfPlaces": "25"
                }
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = loadCompetitions()
            
        assert len(result) == 1
        assert result[0]["name"] == "Test Competition"
        assert result[0]["numberOfPlaces"] == "25"
    
    def test_loadCompetitions_multiple_competitions(self):
        """Test chargement avec plusieurs compétitions"""
        mock_data = {
            "competitions": [
                {"name": "Comp1", "date": "2025-10-22 13:30:00", "numberOfPlaces": "25"},
                {"name": "Comp2", "date": "2025-11-15 10:00:00", "numberOfPlaces": "13"}
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = loadCompetitions()
            
        assert len(result) == 2
        assert result[0]["name"] == "Comp1"
        assert result[1]["name"] == "Comp2"


class TestLoadBookings:
    """Tests unitaires pour loadBookings()"""
    
    def test_loadBookings_valid_file(self):
        """Test chargement réussi des réservations"""
        mock_data = {
            "bookings": [
                {
                    "id": 1,
                    "club": "Test Club",
                    "competition": "Test Competition",
                    "places": 5,
                    "points_used": 5
                }
            ]
        }
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = loadBookings()
            
        assert len(result) == 1
        assert result[0]["club"] == "Test Club"
        assert result[0]["places"] == 5
    
    def test_loadBookings_file_not_found(self):
        """Test comportement quand le fichier n'existe pas - doit retourner liste vide"""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = loadBookings()
            
        assert result == []
    
    def test_loadBookings_empty_bookings(self):
        """Test chargement avec liste vide"""
        mock_data = {"bookings": []}
        
        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = loadBookings()
            
        assert result == []