"""
Application Flask - Hospital Finder Fès
Application web pour trouver des hôpitaux et cliniques
"""

from flask import Flask, render_template, request, jsonify
from hospital_finder import HospitalFinder
import config

# Créer l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = config.FLASK_SECRET_KEY

# Créer une instance de HospitalFinder (connexion Neo4j)
try:
    finder = HospitalFinder()
except Exception as e:
    print(f"❌ Erreur lors de l'initialisation: {e}")
    finder = None


# ========== PAGE D'ACCUEIL ==========
@app.route('/')
def index():
    """
    Page d'accueil de l'application
    """
    stats = finder.get_statistics()
    return render_template('index.html', 
                         stats=stats,
                         positions=config.POSITIONS_FES)


# ========== PAGE AVEC CARTE ==========
@app.route('/map')
def map_page():
    """
    Page avec carte OpenStreetMap interactive
    """
    return render_template('map.html', 
                         positions=config.POSITIONS_FES)


# ========== API : RECHERCHER ==========
@app.route('/api/search', methods=['POST'])
def api_search():
    """
    API pour rechercher des hôpitaux
    
    Reçoit: {latitude, longitude, radius}
    Retourne: Liste des hôpitaux trouvés
    """
    try:
        data = request.get_json()
        
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        radius = float(data.get('radius', 2.0))
        
        # Filtres optionnels
        type_filter = data.get('type')
        urgences_only = data.get('urgences_only', False)
        
        # Recherche
        if type_filter or urgences_only:
            hospitals = finder.find_hospitals_with_filters(
                lat, lon, radius, type_filter, urgences_only
            )
        else:
            hospitals = finder.find_nearby_hospitals(lat, lon, radius)
        
        return jsonify(hospitals)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========== API : TOUS LES HÔPITAUX ==========
@app.route('/api/all')
def api_all():
    """
    API pour obtenir tous les hôpitaux
    """
    try:
        hospitals = finder.get_all_hospitals()
        return jsonify(hospitals)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========== API : LE PLUS PROCHE ==========
@app.route('/api/nearest', methods=['POST'])
def api_nearest():
    """
    API pour trouver l'hôpital le plus proche
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        nearest = finder.find_nearest_hospital(lat, lon)
        return jsonify(nearest)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========== API : STATISTIQUES ==========
@app.route('/api/stats')
def api_stats():
    """
    API pour obtenir les statistiques
    """
    try:
        stats = finder.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ========== GESTION DES ERREURS ==========
@app.errorhandler(404)
def page_not_found(e):
    """Page 404 personnalisée"""
    return render_template('index.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Page 500 personnalisée"""
    return "Erreur interne du serveur", 500


# ========== FERMETURE PROPRE ==========
@app.teardown_appcontext
def shutdown_session(exception=None):
    """
    Fermer la connexion Neo4j à la fin
    """
    pass  # La connexion reste ouverte pendant que l'app tourne


# ========== DÉMARRAGE DE L'APPLICATION ==========
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏥 HOSPITAL FINDER - FÈS")
    print("="*60)
    print("🌐 Application démarrée sur: http://127.0.0.1:5000")
    print("📍 Page d'accueil: http://127.0.0.1:5000")
    print("🗺️  Carte: http://127.0.0.1:5000/map")
    print("⏹️  Pour arrêter: Ctrl+C")
    print("="*60 + "\n")
    
    app.run(
        debug=config.DEBUG,
        host='127.0.0.1',
        port=5000
    )