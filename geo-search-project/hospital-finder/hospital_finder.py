"""
Classe pour interagir avec Neo4j
Gère toutes les requêtes pour les établissements de santé de Fès

Labels utilisés : HealthcareFacility (créé par auto_import.py)
Propriétés : osm_id, name, amenity, street, city, latitude, longitude, location
"""

from neo4j import GraphDatabase


class HospitalFinder:
    """
    Classe principale pour chercher des établissements de santé dans Neo4j
    Utilise les fonctions natives point.distance() pour les recherches spatiales
    """
    
    def __init__(self, uri, user, password):
        """
        Initialisation : connexion à Neo4j
        
        Args:
            uri: URI de connexion Neo4j (ex: bolt://localhost:7687)
            user: Nom d'utilisateur Neo4j
            password: Mot de passe Neo4j
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            self.driver.verify_connectivity()
            print("✅ Connexion à Neo4j réussie!")
        except Exception as e:
            print(f"❌ Erreur de connexion à Neo4j: {e}")
            raise
    
    def close(self):
        """Fermer la connexion à Neo4j"""
        if self.driver:
            self.driver.close()
            print("🔌 Connexion à Neo4j fermée")
    
    def test_connection(self):
        """
        Teste la connexion à Neo4j et retourne le nombre d'établissements
        
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            with self.driver.session() as session:
                result = session.run(
                    "MATCH (h:HealthcareFacility) RETURN count(h) as total"
                )
                total = result.single()['total']
                return {
                    'success': True,
                    'message': f'Connecté - {total} établissements en base'
                }
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    # ========== FONCTION 1 : TOUS LES ÉTABLISSEMENTS ==========
    def get_all_hospitals(self):
        """
        Récupérer tous les établissements de la base
        
        Returns:
            list: Liste de tous les établissements avec leurs infos
        """
        query = """
        MATCH (h:HealthcareFacility)
        RETURN h.osm_id AS id,
               h.name AS name,
               h.amenity AS type,
               h.latitude AS latitude,
               h.longitude AS longitude,
               h.street AS street,
               h.city AS city
        ORDER BY h.name
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            hospitals = [dict(record) for record in result]
            print(f"📊 {len(hospitals)} établissements trouvés")
            return hospitals
    
    # ========== FONCTION 2 : RECHERCHE PAR DISTANCE ==========
    def find_hospitals_within_distance(self, latitude, longitude, radius_km=2.0):
        """
        Trouver les établissements dans un rayon donné
        Utilise point.distance() natif Neo4j (pas besoin de couche spatiale)
        
        Args:
            latitude (float): Latitude du point de départ
            longitude (float): Longitude du point de départ
            radius_km (float): Rayon de recherche en kilomètres
        
        Returns:
            list: Liste des établissements trouvés avec distance en mètres
        """
        query = """
        MATCH (h:HealthcareFacility)
        WITH h, point.distance(
            h.location,
            point({latitude: $lat, longitude: $lon})
        ) AS dist
        WHERE dist <= $radius_m
        RETURN h.osm_id AS id,
               h.name AS name,
               h.amenity AS type,
               h.latitude AS latitude,
               h.longitude AS longitude,
               h.street AS street,
               h.city AS city,
               dist AS distance
        ORDER BY dist ASC
        """
        
        with self.driver.session() as session:
            result = session.run(query,
                                lat=latitude,
                                lon=longitude,
                                radius_m=radius_km * 1000)
            hospitals = [dict(record) for record in result]
            print(f"📍 {len(hospitals)} établissements dans un rayon de {radius_km}km")
            return hospitals
    
    # ========== FONCTION 3 : N PLUS PROCHES ==========
    def find_closest_hospitals(self, latitude, longitude, limit=5):
        """
        Trouver les N établissements les plus proches
        
        Args:
            latitude (float): Latitude du point de départ
            longitude (float): Longitude du point de départ
            limit (int): Nombre d'établissements à retourner
        
        Returns:
            list: Liste des N établissements les plus proches
        """
        query = """
        MATCH (h:HealthcareFacility)
        WITH h, point.distance(
            h.location,
            point({latitude: $lat, longitude: $lon})
        ) AS dist
        RETURN h.osm_id AS id,
               h.name AS name,
               h.amenity AS type,
               h.latitude AS latitude,
               h.longitude AS longitude,
               h.street AS street,
               h.city AS city,
               dist AS distance
        ORDER BY dist ASC
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query,
                                lat=latitude,
                                lon=longitude,
                                limit=limit)
            hospitals = [dict(record) for record in result]
            print(f"🎯 {len(hospitals)} établissements les plus proches")
            return hospitals
    
    # ========== FONCTION 4 : RECHERCHE AVEC FILTRES ==========
    def find_hospitals_with_filters(self, latitude, longitude, radius_km=2.0,
                                    type_filter=None):
        """
        Trouver les établissements avec des filtres (sécurisé contre injection)
        
        Args:
            latitude (float): Latitude du point de départ
            longitude (float): Longitude du point de départ
            radius_km (float): Rayon de recherche en km
            type_filter (str): Type d'établissement (hospital, clinic, pharmacy)
        
        Returns:
            list: Liste des établissements filtrés
        """
        where_clauses = ["dist <= $radius_m"]
        params = {
            'lat': latitude,
            'lon': longitude,
            'radius_m': radius_km * 1000
        }
        
        if type_filter:
            where_clauses.append("h.amenity = $type_filter")
            params['type_filter'] = type_filter
        
        where_clause = " AND ".join(where_clauses)
        
        query = f"""
        MATCH (h:HealthcareFacility)
        WITH h, point.distance(
            h.location,
            point({{latitude: $lat, longitude: $lon}})
        ) AS dist
        WHERE {where_clause}
        RETURN h.osm_id AS id,
               h.name AS name,
               h.amenity AS type,
               h.latitude AS latitude,
               h.longitude AS longitude,
               h.street AS street,
               h.city AS city,
               dist AS distance
        ORDER BY dist ASC
        """
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            hospitals = [dict(record) for record in result]
            print(f"🔍 {len(hospitals)} établissements trouvés avec filtres")
            return hospitals
    
    # ========== FONCTION 5 : STATISTIQUES ==========
    def get_statistics(self):
        """
        Obtenir des statistiques sur les établissements
        
        Returns:
            dict: Statistiques globales (total, hospitals, clinics, pharmacies)
        """
        query = """
        MATCH (h:HealthcareFacility)
        RETURN count(h) AS total,
               count(CASE WHEN h.amenity = 'hospital' THEN 1 END) AS hospitals,
               count(CASE WHEN h.amenity = 'clinic' THEN 1 END) AS clinics,
               count(CASE WHEN h.amenity = 'pharmacy' THEN 1 END) AS pharmacies
        """
        
        with self.driver.session() as session:
            result = session.run(query)
            stats = dict(result.single())
            print(f"📈 Statistiques: {stats['total']} établissements au total")
            return stats
    
    # ========== FONCTION 6 : ÉTABLISSEMENT LE PLUS PROCHE ==========
    def find_nearest_hospital(self, latitude, longitude):
        """
        Trouver l'établissement le plus proche
        
        Args:
            latitude (float): Latitude du point de départ
            longitude (float): Longitude du point de départ
        
        Returns:
            dict: L'établissement le plus proche ou None
        """
        query = """
        MATCH (h:HealthcareFacility)
        WITH h, point.distance(
            h.location,
            point({latitude: $lat, longitude: $lon})
        ) AS dist
        RETURN h.name AS name,
               h.amenity AS type,
               h.street AS street,
               dist AS distance
        ORDER BY dist ASC
        LIMIT 1
        """
        
        with self.driver.session() as session:
            result = session.run(query, lat=latitude, lon=longitude)
            nearest = result.single()
            if nearest:
                hospital = dict(nearest)
                print(f"🎯 Plus proche: {hospital['name']} à {hospital['distance']:.0f}m")
                return hospital
            return None


# ========== TEST DE LA CLASSE ==========
if __name__ == "__main__":
    """
    Test de la classe HospitalFinder
    Exécutez ce fichier pour tester la connexion
    """
    from config import Config
    
    print("\n" + "="*60)
    print("TEST DE LA CLASSE HospitalFinder")
    print("="*60 + "\n")
    
    try:
        # Créer l'instance
        finder = HospitalFinder(
            Config.NEO4J_URI,
            Config.NEO4J_USER,
            Config.NEO4J_PASSWORD
        )
        
        # Test 1 : Connexion
        print("\n📊 TEST 1 : Connexion")
        print("-" * 40)
        test = finder.test_connection()
        print(f"Résultat: {test}")
        
        # Test 2 : Statistiques
        print("\n📊 TEST 2 : Statistiques")
        print("-" * 40)
        stats = finder.get_statistics()
        print(f"Total: {stats['total']}")
        print(f"Hôpitaux: {stats['hospitals']}")
        print(f"Cliniques: {stats['clinics']}")
        print(f"Pharmacies: {stats['pharmacies']}")
        
        # Test 3 : Tous les établissements
        print("\n📋 TEST 3 : Tous les établissements (5 premiers)")
        print("-" * 40)
        all_hospitals = finder.get_all_hospitals()
        for i, hospital in enumerate(all_hospitals[:5], 1):
            print(f"{i}. {hospital['name']} ({hospital['type']})")
        
        # Test 4 : Établissements proches du centre
        print("\n📍 TEST 4 : Établissements à 3km du centre-ville")
        print("-" * 40)
        nearby = finder.find_hospitals_within_distance(34.0331, -5.0003, 3.0)
        for hospital in nearby[:5]:
            print(f"- {hospital['name']}: {hospital['distance']:.0f}m")
        
        # Test 5 : Plus proche
        print("\n🎯 TEST 5 : Établissement le plus proche de Place R'cif")
        print("-" * 40)
        nearest = finder.find_nearest_hospital(34.0632, -4.9998)
        if nearest:
            print(f"Le plus proche: {nearest['name']}")
            print(f"Distance: {nearest['distance']:.0f}m")
        
        # Fermer la connexion
        finder.close()
        
        print("\n✅ TOUS LES TESTS RÉUSSIS!\n")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}\n")