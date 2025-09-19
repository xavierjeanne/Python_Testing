# GUDLFT Competition Booking Platform

## 📋 Vue d'ensemble

Application Flask légère pour la réservation de places dans des compétitions. Cette plateforme permet aux clubs de réserver des places en utilisant leurs points, avec un système de validation robuste et des limites dynamiques.

## 🚀 Technologies utilisées

- **Python 3.x+**
- **Flask** - Framework web minimaliste
- **JSON** - Stockage des données (clubs, compétitions, réservations)
- **pytest** - Framework de tests
- **Jinja2** - Moteur de templates

## 📦 Installation

### 1. Configuration de l'environnement
```bash
# Cloner le repository
git clone <repository-url>
cd Python_Testing

# Créer un environnement virtuel
python -m venv .
# Ou: virtualenv .

# Activer l'environnement virtuel
# Windows:
Scripts\activate
# Linux/Mac:
source bin/activate
```

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
```

### 3. Configuration Flask
```bash
# Windows PowerShell:
$env:FLASK_APP = "server.py"

# Linux/Mac:
export FLASK_APP=server.py
```

### 4. Lancement de l'application
```bash
flask run
# Ou:
python -m flask run --debug
```

L'application sera disponible sur `http://127.0.0.1:5000`

## 📊 Structure des données

### 🏛️ Fichiers de données principaux

- **`clubs.json`** - Liste des clubs avec emails et points
- **`competitions.json`** - Liste des compétitions avec dates et places disponibles  
- **`bookings.json`** - Historique des réservations

### 🎭 Utilisateurs de test

| Club | Email | Points initiaux |
|------|-------|----------------|
| Simply Lift | john@simplylift.co | 13 |
| Iron Temple | admin@irontemple.com | 4 |
| She Lifts | kate@shelifts.co.uk | 12 |

## ⚡ Fonctionnalités

### ✅ Système de réservation
- **Validation des places positives** - Empêche les réservations nulles/négatives
- **Limite de 12 places max** par club et par compétition
- **Système de points** - 1 point = 1 place
- **Limites dynamiques** - Calcul en temps réel des places disponibles
- **Historique des réservations** - Suivi complet des transactions

### 🔒 Règles métier
1. Maximum 12 places par réservation
2. Maximum 12 places total par club par compétition  
3. Points suffisants requis (1 point/place)
4. Places disponibles dans la compétition
5. Validation des données d'entrée

## 🧪 Tests

### 📁 Architecture des tests

```
tests/
├── unit/                          # Tests unitaires purs (>50 tests)
│   ├── test_data_loading.py       # Tests de chargement JSON
│   ├── test_data_saving.py        # Tests de sauvegarde
│   ├── test_booking_functions.py  # Tests des fonctions de réservation
│   ├── test_business_logic.py     # Tests de logique métier
│   ├── test_utils.py             # Tests des fonctions utilitaires
│   ├── test_lookup_functions.py   # Tests de recherche
│   ├── test_limit_calculations.py # Tests de calcul de limites
│   ├── test_data_updates.py       # Tests de mise à jour
│   └── test_error_handling.py     # Tests de gestion d'erreurs
├── integration/                   # Tests d'intégration Flask
│   ├── test_negative_places.py    # Tests validation places négatives
│   ├── test_points_validation.py  # Tests validation points
│   └── test_dynamic_limits.py     # Tests limites dynamiques
└── fixtures/                     # Données de test contrôlées
    ├── clubs_test.json           # Clubs pour tests
    ├── competitions_test.json    # Compétitions pour tests
    └── bookings_test.json        # Réservations pour tests
```

### 🏃‍♂️ Exécution des tests

#### Tests unitaires (recommandés)
```bash
# Tous les tests unitaires
python -m pytest tests/unit/ -v

# Par fichier spécifique
python -m pytest tests/unit/test_business_logic.py -v

# Par classe de tests
python -m pytest tests/unit/test_business_logic.py::TestValidationRules -v
```

#### Tests d'intégration
```bash
# Tous les tests d'intégration
python -m pytest tests/integration/ -v

# Test spécifique
python -m pytest tests/integration/test_dynamic_limits.py -v
```

#### Tous les tests
```bash
python -m pytest -v
```

### 📈 Couverture de tests

```bash
# Installation de coverage
pip install coverage

# Exécution avec couverture
coverage run -m pytest
coverage report
coverage html  # Génère un rapport HTML
```





