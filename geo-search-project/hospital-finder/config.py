# config.py
"""
Configuration pour la connexion à Neo4j Desktop
"""
import os


class Config:
    # Configuration Neo4j Desktop
    # Utilisez des variables d'environnement pour la sécurité :
    #   set NEO4J_URI=bolt://localhost:7687
    #   set NEO4J_USER=neo4j
    #   set NEO4J_PASSWORD=votre_mot_de_passe
    NEO4J_URI = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "Password")
    
    # Configuration Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    DEBUG = True
    
    # Configuration de la carte (Fès, Maroc)
    DEFAULT_LAT = 34.0331
    DEFAULT_LON = -5.0003
    DEFAULT_ZOOM = 13
    
    # Configuration Neo4j Spatial
    SPATIAL_LAYER = "fes_layer"
    
    # Positions prédéfinies pour Fès (chaque valeur doit avoir name, lat, lon)
    PREDEFINED_LOCATIONS = {
        "place_rcif": {"name": "Place R'cif (Centre-ville)", "lat": 34.0632, "lon": -4.9998},
        "medina": {"name": "Médina (Bab Boujloud)", "lat": 34.0628, "lon": -4.9775},
        "chu": {"name": "CHU Hassan II", "lat": 34.0185, "lon": -5.0160},
        "ville_nouvelle": {"name": "Ville Nouvelle", "lat": 34.0331, "lon": -5.0003},
        "agdal": {"name": "Quartier Agdal", "lat": 34.0270, "lon": -5.0100},
    }
    
    # Types d'établissements (correspond aux valeurs 'amenity' du CSV OpenStreetMap)
    FACILITY_TYPES = ["hospital", "clinic", "pharmacy"]
    
    # Distances de recherche (km)
    SEARCH_DISTANCES = [0.5, 1, 2, 3, 5, 10]