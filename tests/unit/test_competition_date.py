import pytest
from datetime import datetime, timedelta
from server import is_competition_date_passed

# Cas : date dépassée
def test_is_competition_date_passed_true():
    competition = {
        'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    }
    assert is_competition_date_passed(competition) is True

# Cas : date future
def test_is_competition_date_passed_false():
    competition = {
        'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    }
    assert is_competition_date_passed(competition) is False

# Cas : date invalide
def test_is_competition_date_passed_invalid():
    competition = {
        'date': 'invalid-date-format'
    }
    assert is_competition_date_passed(competition) is True
