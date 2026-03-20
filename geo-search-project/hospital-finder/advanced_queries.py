# advanced_queries.py
"""
Requêtes Cypher Spatial avancées - Étudiant 2
Toutes les requêtes utilisent Neo4j Spatial (spatial.withinDistance, spatial.closest)

IMPORTANT : 
- Couche spatiale : 'fes_layer' (au lieu de 'hopitaux')
- Structure des nœuds : HealthcareFacility avec propriétés location, amenity, etc.
"""

from neo4j import GraphDatabase

class AdvancedQueries:
    def __init__(self, driver, layer='fes_layer'):
        """
        Initialise les requêtes avancées
        
        Args:
            driver: Driver Neo4j
            layer: Nom de la couche spatiale (par défaut 'fes_layer')
        """
        self.driver = driver
        self.layer = layer
    
    # ============================================
    # RECHERCHE PAR RAYON (spatial.withinDistance)
    # ============================================
    
    def find_within_radius_500m(self, latitude, longitude):
        """
        Tous les établissements dans un rayon de 500m
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Établissements trouvés avec nom et type
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            0.5) 
        YIELD node 
        RETURN node.name as name, 
               node.amenity as amenity,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def find_clinics_within_1km(self, latitude, longitude):
        """
        Cliniques uniquement dans un rayon de 1km
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Cliniques trouvées avec nom et rue
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            1.0) 
        YIELD node 
        WHERE node.amenity = 'clinic' 
        RETURN node.name as name, 
               node.street as street,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def find_hospitals_for_emergency_3km(self, latitude, longitude):
        """
        Hôpitaux dans un rayon de 3km pour les urgences
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Hôpitaux avec urgences
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            3.0) 
        YIELD node 
        WHERE node.amenity = 'hospital' 
        RETURN node.name as name, 
               node.location as location,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def find_on_avenue_far_800m(self, latitude, longitude):
        """
        Établissements sur l'avenue FAR à moins de 800m
        
        Args:
            latitude: Latitude du point de recherche (ex: 34.034)
            longitude: Longitude du point de recherche (ex: -5.002)
        
        Returns:
            list: Établissements sur avenue des Forces Armées Royales
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            0.8) 
        YIELD node 
        WHERE node.street CONTAINS 'Armée Royale' 
        RETURN node.name as name, 
               node.street as street,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def count_types_within_2km(self, latitude, longitude):
        """
        Compter les types d'établissements dans un rayon de 2km
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Types d'établissements avec leur nombre
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            2.0) 
        YIELD node 
        RETURN node.amenity as amenity, 
               count(*) AS nombre
        ORDER BY nombre DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    # ============================================
    # RECHERCHE DE PROXIMITÉ (spatial.closest)
    # ============================================
    
    def find_closest_facility(self, latitude, longitude):
        """
        L'établissement de santé le plus proche de l'utilisateur
        
        Args:
            latitude: Latitude de l'utilisateur
            longitude: Longitude de l'utilisateur
        
        Returns:
            dict: Établissement le plus proche
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            1) 
        YIELD node 
        RETURN node.name as name, 
               node.amenity as amenity,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            record = result.single()
            return dict(record) if record else None
    
    def find_5_closest_clinics(self, latitude, longitude):
        """
        Les 5 cliniques les plus proches
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: 5 cliniques les plus proches
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            5) 
        YIELD node 
        WHERE node.amenity = 'clinic' 
        RETURN node.name as name, 
               node.location as location,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def find_3_closest_hospitals_downtown(self, latitude=34.039, longitude=-5.004):
        """
        Les 3 hôpitaux les plus proches du centre-ville
        
        Args:
            latitude: Latitude centre-ville (par défaut 34.039)
            longitude: Longitude centre-ville (par défaut -5.004)
        
        Returns:
            list: 3 hôpitaux les plus proches
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            3) 
        YIELD node 
        WHERE node.amenity = 'hospital' 
        RETURN node.name as name, 
               node.street as street,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    # ============================================
    # REQUÊTES AVANCÉES ET ANALYSE
    # ============================================
    
    def find_neighbors_of_clinic(self, clinic_name, radius=0.4):
        """
        Établissements voisins d'une clinique spécifique (rayon 400m)
        
        Args:
            clinic_name: Nom de la clinique (ex: 'Clinique Al karaouiyine')
            radius: Rayon de recherche en km (par défaut 0.4)
        
        Returns:
            list: Établissements voisins
        """
        query = """
        MATCH (h:HealthcareFacility {name: $clinic_name})
        CALL spatial.withinDistance($layer, h.location, $radius) 
        YIELD node 
        WHERE node <> h
        RETURN node.name as name, 
               node.amenity as amenity,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                layer=self.layer, 
                clinic_name=clinic_name, 
                radius=radius)
            return [dict(record) for record in result]
    
    def find_unnamed_facilities_1_5km(self, latitude, longitude):
        """
        Trouver les établissements sans nom répertorié dans un rayon de 1.5km
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Établissements sans nom avec leur OSM ID
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            1.5) 
        YIELD node 
        WHERE node.name IS NULL 
        RETURN node.osm_id as osm_id, 
               node.location as location,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def find_nearest_neighbor_for_each_hospital(self):
        """
        Trouver le voisin le plus proche pour chaque hôpital
        
        Returns:
            list: Paires hôpital-voisin le plus proche
        """
        query = """
        MATCH (h:HealthcareFacility) 
        WHERE h.amenity = 'hospital'
        CALL spatial.closest($layer, h.location, 2) 
        YIELD node 
        WHERE node <> h
        RETURN h.name AS hopital, 
               node.name AS voisin_proche,
               h.latitude as hopital_lat,
               h.longitude as hopital_lon,
               node.latitude as voisin_lat,
               node.longitude as voisin_lon
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer)
            return [dict(record) for record in result]
    
    def find_west_facilities_2km(self, latitude, longitude, lon_threshold=-5.0):
        """
        Établissements situés à l'ouest (Longitude < -5.0) dans un rayon de 2km
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
            lon_threshold: Seuil de longitude (par défaut -5.0)
        
        Returns:
            list: Établissements à l'ouest
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            2.0) 
        YIELD node 
        WHERE node.longitude < $lon_threshold
        RETURN node.name as name, 
               node.longitude as longitude,
               node.latitude as latitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                layer=self.layer, 
                lat=latitude, 
                lon=longitude,
                lon_threshold=lon_threshold)
            return [dict(record) for record in result]
    
    def extract_10_closest_for_map(self, latitude, longitude):
        """
        Extraction des coordonnées des 10 points les plus proches pour affichage MAP
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: 10 établissements les plus proches avec coordonnées
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            10) 
        YIELD node 
        RETURN node.name as name, 
               node.latitude as latitude, 
               node.longitude as longitude,
               node.amenity as amenity
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def verify_facilities_without_amenity_5km(self, latitude, longitude):
        """
        Vérifier les données : établissements sans type défini (amenity) dans un rayon de 5km
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Établissements sans type défini
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            5.0) 
        YIELD node 
        WHERE NOT EXISTS(node.amenity)
        RETURN node.osm_id as osm_id,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def search_clinics_sorted_by_name(self, latitude, longitude, radius=1.2):
        """
        Recherche combinée : Cliniques proches d'un point spécifique avec tri par nom
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
            radius: Rayon de recherche en km (par défaut 1.2)
        
        Returns:
            list: Cliniques triées alphabétiquement
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            $radius) 
        YIELD node 
        WHERE node.amenity = 'clinic'
        RETURN node.name as name,
               node.latitude as latitude,
               node.longitude as longitude
        ORDER BY node.name ASC
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                layer=self.layer, 
                lat=latitude, 
                lon=longitude,
                radius=radius)
            return [dict(record) for record in result]
    
    def search_north_zone_2km(self, latitude, longitude):
        """
        Recherche filtrée par zone géographique (Nord)
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
        
        Returns:
            list: Établissements au nord du point
        """
        query = """
        CALL spatial.withinDistance($layer, 
            point({latitude: $lat, longitude: $lon}), 
            2.0) 
        YIELD node 
        WHERE node.latitude > $lat
        RETURN node.name as name, 
               node.latitude as latitude, 
               node.amenity as amenity,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, layer=self.layer, lat=latitude, lon=longitude)
            return [dict(record) for record in result]
    
    def calculate_exact_distance_clinics(self, latitude, longitude, limit=5):
        """
        Calcul de la distance exacte pour les cliniques proches
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
            limit: Nombre de cliniques à retourner
        
        Returns:
            list: Cliniques avec distance exacte en mètres
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            $limit) 
        YIELD node 
        WHERE node.amenity = 'clinic'
        RETURN node.name as name,
               node.latitude as latitude,
               node.longitude as longitude,
               point.distance(
                   node.location, 
                   point({latitude: $lat, longitude: $lon})
               ) AS distance_metres
        ORDER BY distance_metres
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                layer=self.layer, 
                lat=latitude, 
                lon=longitude,
                limit=limit)
            return [dict(record) for record in result]
    
    def identify_incomplete_data_closest(self, latitude, longitude, limit=3):
        """
        Identification des données incomplètes les plus proches
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
            limit: Nombre d'établissements à analyser
        
        Returns:
            list: Établissements sans type défini
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            $limit) 
        YIELD node 
        WHERE node.amenity IS NULL
        RETURN node.osm_id as osm_id, 
               node.location as location,
               node.latitude as latitude,
               node.longitude as longitude
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                layer=self.layer, 
                lat=latitude, 
                lon=longitude,
                limit=limit)
            return [dict(record) for record in result]
    
    def verify_named_facilities_with_distance(self, latitude, longitude, limit=5):
        """
        Vérifier les données : établissements avec nom et leur distance
        
        Args:
            latitude: Latitude du point de recherche
            longitude: Longitude du point de recherche
            limit: Nombre d'établissements à retourner
        
        Returns:
            list: Établissements nommés avec distance
        """
        query = """
        CALL spatial.closest($layer, 
            point({latitude: $lat, longitude: $lon}), 
            $limit) 
        YIELD node 
        WHERE node.name IS NOT NULL
        RETURN node.name as name,
               node.latitude as latitude,
               node.longitude as longitude,
               point.distance(
                   node.location, 
                   point({latitude: $lat, longitude: $lon})
               ) AS distance_m
        ORDER BY distance_m
        """
        
        with self.driver.session() as session:
            result = session.run(query, 
                layer=self.layer, 
                lat=latitude, 
                lon=longitude,
                limit=limit)
            return [dict(record) for record in result]
    
    # ============================================
    # STATISTIQUES GÉNÉRALES
    # ============================================
    
    def get_all_statistics(self):
        """
        Statistiques générales sur tous les établissements
        
        Returns:
            dict: Statistiques complètes
        """
        query_total = """
        MATCH (h:HealthcareFacility)
        RETURN count(h) as total
        """
        
        query_by_type = """
        MATCH (h:HealthcareFacility)
        RETURN h.amenity as type, count(h) as count
        ORDER BY count DESC
        """
        
        query_named = """
        MATCH (h:HealthcareFacility)
        RETURN 
            count(CASE WHEN h.name IS NOT NULL THEN 1 END) as with_name,
            count(CASE WHEN h.name IS NULL THEN 1 END) as without_name
        """
        
        with self.driver.session() as session:
            # Total
            result_total = session.run(query_total)
            total = result_total.single()['total']
            
            # Par type
            result_types = session.run(query_by_type)
            by_type = [dict(record) for record in result_types]
            
            # Avec/sans nom
            result_named = session.run(query_named)
            named_stats = dict(result_named.single())
            
            return {
                'total': total,
                'by_type': by_type,
                'with_name': named_stats['with_name'],
                'without_name': named_stats['without_name']
            }