# app.py
"""
Application Flask COMPLÈTE avec requêtes avancées
Système de géolocalisation des établissements de santé - Fès
"""

from flask import Flask, render_template, request, jsonify
from hospital_finder import HospitalFinder
from advanced_queries import AdvancedQueries
from config import Config

# Initialisation de Flask
app = Flask(__name__)
app.config.from_object(Config)

# Initialisation de la connexion Neo4j
finder = HospitalFinder(
    Config.NEO4J_URI,
    Config.NEO4J_USER,
    Config.NEO4J_PASSWORD
)

# Initialisation des requêtes avancées
advanced = AdvancedQueries(finder.driver, layer=Config.SPATIAL_LAYER)

# ============================================
# ROUTES PRINCIPALES
# ============================================

@app.route('/')
def index():
    """Page d'accueil avec statistiques"""
    try:
        stats = finder.get_statistics()
        return render_template('index.html',
            stats=stats,
            positions=Config.PREDEFINED_LOCATIONS,
            center_lat=Config.DEFAULT_LAT,
            center_lon=Config.DEFAULT_LON,
        )
    except Exception as e:
        return render_template('error.html', error=str(e))

@app.route('/map')
def map_view():
    """Page carte interactive"""
    return render_template('map.html',
        positions=Config.PREDEFINED_LOCATIONS,
        center_lat=Config.DEFAULT_LAT,
        center_lon=Config.DEFAULT_LON,
    )

@app.route('/test-connection')
def test_connection():
    """Teste la connexion à Neo4j"""
    result = finder.test_connection()
    return jsonify(result)

# ============================================
# API DE BASE (utilisées par map.html)
# ============================================

@app.route('/api/all')
def api_all():
    """Retourne tous les établissements (pour la carte)"""
    try:
        hospitals = finder.get_all_hospitals()
        return jsonify(hospitals)
    except Exception as e:
        return jsonify([])

@app.route('/api/search', methods=['POST'])
def api_search():
    """Recherche par proximité (pour la carte)"""
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        radius = float(data.get('radius', 2))
        
        hospitals = finder.find_hospitals_within_distance(lat, lon, radius)
        return jsonify(hospitals)
    except Exception as e:
        return jsonify([])

# ============================================
# ROUTES AVANCÉES (Nouvelles - Étudiant 2)
# ============================================

@app.route('/api/advanced/within-500m', methods=['POST'])
def advanced_within_500m():
    """
    Tous les établissements dans un rayon de 500m
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.find_within_radius_500m(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'radius': '500m',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/clinics-1km', methods=['POST'])
def advanced_clinics_1km():
    """
    Cliniques uniquement dans un rayon de 1km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.find_clinics_within_1km(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'radius': '1km',
            'type': 'clinic',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/emergency-3km', methods=['POST'])
def advanced_emergency_3km():
    """
    Hôpitaux pour urgences dans un rayon de 3km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.find_hospitals_for_emergency_3km(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'radius': '3km',
            'type': 'hospital (emergency)',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/avenue-far', methods=['POST'])
def advanced_avenue_far():
    """
    Établissements sur avenue FAR (800m)
    
    Body JSON:
        - latitude: float (ex: 34.034)
        - longitude: float (ex: -5.002)
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude', 34.034))
        lon = float(data.get('longitude', -5.002))
        
        results = advanced.find_on_avenue_far_800m(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'street': 'Avenue des Forces Armées Royales',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/count-types', methods=['POST'])
def advanced_count_types():
    """
    Compter les types d'établissements dans 2km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.count_types_within_2km(lat, lon)
        
        return jsonify({
            'success': True,
            'radius': '2km',
            'statistics': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/closest', methods=['POST'])
def advanced_closest():
    """
    L'établissement le plus proche
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        result = advanced.find_closest_facility(lat, lon)
        
        if result:
            return jsonify({
                'success': True,
                'facility': result
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Aucun établissement trouvé'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/5-closest-clinics', methods=['POST'])
def advanced_5_closest_clinics():
    """
    Les 5 cliniques les plus proches
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.find_5_closest_clinics(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'type': 'clinic',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/downtown-hospitals', methods=['GET'])
def advanced_downtown_hospitals():
    """
    Les 3 hôpitaux les plus proches du centre-ville (position fixe)
    """
    try:
        results = advanced.find_3_closest_hospitals_downtown()
        
        return jsonify({
            'success': True,
            'count': len(results),
            'location': 'Centre-ville (34.039, -5.004)',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/neighbors/<clinic_name>', methods=['GET'])
def advanced_neighbors(clinic_name):
    """
    Établissements voisins d'une clinique spécifique
    
    URL params:
        - clinic_name: Nom de la clinique
    Query params:
        - radius: Rayon en km (optionnel, défaut 0.4)
    """
    try:
        radius = float(request.args.get('radius', 0.4))
        
        results = advanced.find_neighbors_of_clinic(clinic_name, radius)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'clinic': clinic_name,
            'radius': f'{radius}km',
            'neighbors': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/unnamed', methods=['POST'])
def advanced_unnamed():
    """
    Établissements sans nom dans 1.5km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.find_unnamed_facilities_1_5km(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'radius': '1.5km',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/hospital-neighbors', methods=['GET'])
def advanced_hospital_neighbors():
    """
    Voisin le plus proche de chaque hôpital
    """
    try:
        results = advanced.find_nearest_neighbor_for_each_hospital()
        
        return jsonify({
            'success': True,
            'count': len(results),
            'pairs': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/west-zone', methods=['POST'])
def advanced_west_zone():
    """
    Établissements à l'ouest (longitude < -5.0) dans 2km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.find_west_facilities_2km(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'zone': 'Ouest (longitude < -5.0)',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/map-10-closest', methods=['POST'])
def advanced_map_10_closest():
    """
    10 établissements les plus proches pour affichage carte
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.extract_10_closest_for_map(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/verify-no-amenity', methods=['POST'])
def advanced_verify_no_amenity():
    """
    Établissements sans type (amenity) dans 5km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.verify_facilities_without_amenity_5km(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'radius': '5km',
            'issue': 'Missing amenity type',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/clinics-sorted', methods=['POST'])
def advanced_clinics_sorted():
    """
    Cliniques triées par nom dans un rayon donné
    
    Body JSON:
        - latitude: float
        - longitude: float
        - radius: float (optionnel, défaut 1.2)
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        radius = float(data.get('radius', 1.2))
        
        results = advanced.search_clinics_sorted_by_name(lat, lon, radius)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'radius': f'{radius}km',
            'sorted_by': 'name',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/north-zone', methods=['POST'])
def advanced_north_zone():
    """
    Établissements au nord du point dans 2km
    
    Body JSON:
        - latitude: float
        - longitude: float
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        
        results = advanced.search_north_zone_2km(lat, lon)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'zone': f'Nord de {lat}',
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/clinics-distance', methods=['POST'])
def advanced_clinics_distance():
    """
    Cliniques avec distance exacte
    
    Body JSON:
        - latitude: float
        - longitude: float
        - limit: int (optionnel, défaut 5)
    """
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        limit = int(data.get('limit', 5))
        
        results = advanced.calculate_exact_distance_clinics(lat, lon, limit)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'facilities': results
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/advanced/statistics', methods=['GET'])
def advanced_statistics():
    """
    Statistiques générales avancées
    """
    try:
        stats = advanced.get_all_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================
# ROUTES API STRUCTURÉES
# ============================================

@app.route('/api/search/proximity', methods=['POST'])
def search_proximity():
    """Recherche par proximité"""
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        distance = float(data.get('distance', 5))
        
        hospitals = finder.find_hospitals_within_distance(lat, lon, distance)
        
        return jsonify({
            'success': True,
            'count': len(hospitals),
            'hospitals': hospitals,
            'search': {
                'latitude': lat,
                'longitude': lon,
                'distance': distance
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/search/closest', methods=['POST'])
def search_closest():
    """Trouver les plus proches"""
    try:
        data = request.get_json()
        lat = float(data.get('latitude'))
        lon = float(data.get('longitude'))
        limit = int(data.get('limit', 5))
        
        hospitals = finder.find_closest_hospitals(lat, lon, limit)
        
        return jsonify({
            'success': True,
            'count': len(hospitals),
            'hospitals': hospitals
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/hospitals')
def get_all_hospitals():
    """Liste tous les établissements"""
    try:
        hospitals = finder.get_all_hospitals()
        return jsonify({
            'success': True,
            'count': len(hospitals),
            'hospitals': hospitals
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/statistics')
def get_statistics():
    """Statistiques"""
    try:
        stats = finder.get_statistics()
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================
# GESTION DES ERREURS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error="Page non trouvée"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Erreur interne du serveur"), 500

# ============================================
# DÉMARRAGE DE L'APPLICATION
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 SYSTÈME DE GÉOLOCALISATION - FÈS")
    print("=" * 60)
    print(f"🌐 URL: http://localhost:5000")
    print(f"🗄️  Neo4j: {Config.NEO4J_URI}")
    print("=" * 60)
    
    # Test de connexion au démarrage
    test = finder.test_connection()
    if test['success']:
        print(f"✅ Connexion Neo4j: {test['message']}")
    else:
        print(f"❌ Erreur Neo4j: {test['message']}")
        print("⚠️  Vérifiez que Neo4j Desktop est lancé!")
    
    print("=" * 60)
    print("\n📡 ROUTES DISPONIBLES:")
    print("  Pages:")
    print("  • /          → Accueil")
    print("  • /map        → Carte interactive")
    print("  API de base:")
    print("  • /api/all              → Tous les établissements")
    print("  • /api/search           → Recherche par proximité")
    print("  • /api/hospitals        → Liste complète")
    print("  • /api/statistics       → Statistiques")
    print("  API avancées:")
    print("  • /api/advanced/within-500m")
    print("  • /api/advanced/clinics-1km")
    print("  • /api/advanced/emergency-3km")
    print("  • /api/advanced/closest")
    print("  • /api/advanced/statistics")
    print("  • ... et 15+ autres routes")
    print("=" * 60)
    
    # Démarrage du serveur Flask
    app.run(
        debug=Config.DEBUG,
        host='0.0.0.0',
        port=5000
    )