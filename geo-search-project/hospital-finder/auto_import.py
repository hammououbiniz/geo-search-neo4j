# auto_import.py
"""
Script automatique pour importer les données dans Neo4j
Exécute toutes les étapes : nettoyage CSV + import Neo4j
"""

import csv
import sys
from neo4j import GraphDatabase
from config import Config

class DataImporter:
    def __init__(self, uri, user, password):
        """Initialise la connexion Neo4j"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.layer = 'fes_layer'
        self.spatial_available = False
    
    def close(self):
        """Ferme la connexion"""
        self.driver.close()
    
    def clean_csv(self, input_file, output_file):
        """
        Nettoie le fichier CSV
        
        Args:
            input_file: Fichier CSV source
            output_file: Fichier CSV nettoyé
        
        Returns:
            int: Nombre de lignes traitées
        """
        print(f"\n📂 ÉTAPE 1 : Nettoyage du CSV")
        print(f"   Lecture de {input_file}...")
        
        # Mapping des colonnes (on strip les backticks en plus)
        column_mapping = {
            '@id': 'osm_id',
            '@lat': 'latitude',
            '@lon': 'longitude',
            'addr:street': 'street',
            'addr:city': 'city'
        }
        
        def clean_col_name(col):
            """Nettoie un nom de colonne : strip espaces et backticks"""
            return col.strip().strip('`').strip()
        
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            # Nettoyer les noms de colonnes (strip backticks)
            fieldnames = [column_mapping.get(clean_col_name(col), clean_col_name(col)) for col in reader.fieldnames]
            
            # Lire toutes les lignes
            rows = []
            for row in reader:
                clean_row = {}
                for old_col, value in row.items():
                    new_col = column_mapping.get(clean_col_name(old_col), clean_col_name(old_col))
                    clean_row[new_col] = value.strip() if value else ''
                rows.append(clean_row)
        
        # Écrire le fichier nettoyé
        with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        
        print(f"   ✅ {len(rows)} lignes nettoyées")
        
        # Statistiques
        amenity_count = {}
        for row in rows:
            amenity = row.get('amenity', 'unknown')
            amenity_count[amenity] = amenity_count.get(amenity, 0) + 1
        
        print(f"   📊 Statistiques :")
        for amenity, count in sorted(amenity_count.items(), key=lambda x: x[1], reverse=True):
            print(f"      - {amenity}: {count}")
        
        return len(rows)
    
    def clean_database(self):
        """Supprime les anciennes données"""
        print(f"\n🗑️  ÉTAPE 2 : Nettoyage de la base Neo4j")
        
        with self.driver.session() as session:
            # Supprimer les nœuds
            result = session.run("MATCH (h:Hospital) DETACH DELETE h RETURN count(h) as deleted")
            deleted = result.single()['deleted']
            print(f"   ✅ {deleted} nœuds Hospital supprimés")
            
            result = session.run("MATCH (h:HealthcareFacility) DETACH DELETE h RETURN count(h) as deleted")
            deleted = result.single()['deleted']
            print(f"   ✅ {deleted} nœuds HealthcareFacility supprimés")
            
            # Supprimer les couches spatiales
            try:
                session.run("CALL spatial.removeLayer('fes_layer')")
                print(f"   ✅ Couche 'fes_layer' supprimée")
            except:
                pass
            
            try:
                session.run("CALL spatial.removeLayer('hopitaux')")
                print(f"   ✅ Couche 'hopitaux' supprimée")
            except:
                pass
    
    def create_spatial_layer(self):
        """Crée la couche spatiale (optionnel - nécessite le plugin neo4j-spatial)"""
        print(f"\n🗺️  ÉTAPE 3 : Création de la couche spatiale")
        
        with self.driver.session() as session:
            try:
                # Créer la couche
                session.run("CALL spatial.addLayer($layer, 'SimplePoint', 'latitude:longitude')", 
                           layer=self.layer)
                print(f"   ✅ Couche '{self.layer}' créée")
                
                # Vérifier
                result = session.run("CALL spatial.layers() YIELD name RETURN name")
                layers = [record['name'] for record in result]
                print(f"   📊 Couches disponibles : {layers}")
                self.spatial_available = True
            except Exception as e:
                print(f"   ⚠️  Plugin Neo4j Spatial non disponible : {e}")
                print(f"   ℹ️  L'application fonctionnera avec point.distance() natif")
                print(f"   ℹ️  Les routes /api/advanced/ nécessitent le plugin spatial")
                self.spatial_available = False
    
    def import_data(self, csv_file):
        """
        Importe les données depuis CSV en utilisant Python + Cypher paramétré
        (Plus fiable que LOAD CSV qui nécessite le dossier import de Neo4j)
        
        Args:
            csv_file: Chemin local du fichier CSV nettoyé
        
        Returns:
            int: Nombre d'établissements importés
        """
        print(f"\n📥 ÉTAPE 4 : Import des données depuis {csv_file}")
        
        # Lire le CSV avec Python
        rows = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        
        print(f"   📄 {len(rows)} lignes lues depuis le CSV")
        
        # Import par batch de 100 pour performance
        batch_size = 100
        total_imported = 0
        
        query = """
        UNWIND $batch AS row
        CREATE (h:HealthcareFacility:Hospital {
            osm_id: row.osm_id,
            name: CASE WHEN row.name IS NULL OR row.name = '' 
                       THEN 'Établissement ' + row.osm_id 
                       ELSE row.name END,
            amenity: row.amenity,
            street: row.street,
            city: row.city,
            latitude: toFloat(row.latitude),
            longitude: toFloat(row.longitude),
            location: point({latitude: toFloat(row.latitude), longitude: toFloat(row.longitude)})
        })
        RETURN count(h) as imported
        """
        
        with self.driver.session() as session:
            for i in range(0, len(rows), batch_size):
                batch = rows[i:i + batch_size]
                result = session.run(query, batch=batch)
                imported = result.single()['imported']
                total_imported += imported
                print(f"   ... {total_imported}/{len(rows)} importés")
        
        print(f"   ✅ {total_imported} établissements importés au total")
        return total_imported
    
    def add_to_spatial_layer(self):
        """Ajoute les nœuds à la couche spatiale"""
        print(f"\n🔗 ÉTAPE 5 : Configuration spatiale")
        print(f"   ℹ️  Pas de couche spatiale nécessaire")
        print(f"   ✅ Les propriétés 'location' (point) sont déjà créées")
        return 0  # Pas d'ajout nécessaire
    
    def create_indexes(self):
        """Crée les index pour performance"""
        print(f"\n📇 ÉTAPE 6 : Création des index")
        
        indexes = [
            ("healthcare_osm_id", "osm_id"),
            ("healthcare_amenity", "amenity"),
            ("healthcare_name", "name")
        ]
        
        with self.driver.session() as session:
            for index_name, property_name in indexes:
                query = f"""
                CREATE INDEX {index_name} IF NOT EXISTS
                FOR (h:HealthcareFacility) ON (h.{property_name})
                """
                session.run(query)
                print(f"   ✅ Index '{index_name}' créé")
    
    def verify_import(self):
        """Vérifie l'import"""
        print(f"\n✅ ÉTAPE 7 : Vérification")
        
        with self.driver.session() as session:
            # Compter le total
            result = session.run("MATCH (h:HealthcareFacility) RETURN count(h) as total")
            total = result.single()['total']
            print(f"   Total : {total} établissements")
            
            # Compter par type
            result = session.run("""
                MATCH (h:HealthcareFacility)
                RETURN h.amenity as type, count(*) as count
                ORDER BY count DESC
            """)
            print(f"   Répartition :")
            for record in result:
                print(f"      - {record['type']}: {record['count']}")
            
            # Vérifier les coordonnées
            result = session.run("""
                MATCH (h:HealthcareFacility)
                WHERE h.location IS NULL
                RETURN count(h) as missing
            """)
            missing = result.single()['missing']
            if missing == 0:
                print(f"   ✅ Toutes les coordonnées sont présentes")
            else:
                print(f"   ⚠️  {missing} établissements sans coordonnées")
            
            # Test recherche spatiale
            if self.spatial_available:
                try:
                    result = session.run("""
                        CALL spatial.closest($layer, 
                            point({latitude: 34.0632, longitude: -4.9998}), 
                            1) 
                        YIELD node
                        RETURN node.name as name
                    """, layer=self.layer)
                    
                    closest = result.single()
                    if closest:
                        print(f"   ✅ Recherche spatiale fonctionne")
                        print(f"   🏥 Plus proche de Place R'cif : {closest['name']}")
                    else:
                        print(f"   ⚠️  Recherche spatiale ne fonctionne pas")
                except Exception:
                    print(f"   ⚠️  Recherche spatiale non disponible")
            else:
                # Test avec point.distance() natif
                try:
                    result = session.run("""
                        MATCH (h:HealthcareFacility)
                        WITH h, point.distance(
                            h.location,
                            point({latitude: 34.0632, longitude: -4.9998})
                        ) AS dist
                        RETURN h.name as name, dist
                        ORDER BY dist ASC
                        LIMIT 1
                    """)
                    closest = result.single()
                    if closest:
                        dist = closest['dist']
                        dist_str = f"{dist:.0f}m" if dist is not None else "?"
                        print(f"   ✅ Recherche point.distance() fonctionne")
                        print(f"   🏥 Plus proche de Place R'cif : {closest['name']} ({dist_str})")
                except Exception as e:
                    print(f"   ⚠️  Recherche spatiale non disponible: {e}")

def main():
    """Fonction principale"""
    print("=" * 60)
    print("🏥 IMPORT AUTOMATIQUE DES DONNÉES FÈS")
    print("=" * 60)
    
    # Fichiers
    input_csv = 'database/hospitals_clinics_pharmacy_fes.csv'
    output_csv = 'database/fes_healthcare_clean.csv'
    
    # Initialiser l'importeur
    print(f"\n🔌 Connexion à Neo4j...")
    print(f"   URI: {Config.NEO4J_URI}")
    print(f"   User: {Config.NEO4J_USER}")
    
    try:
        importer = DataImporter(
            Config.NEO4J_URI,
            Config.NEO4J_USER,
            Config.NEO4J_PASSWORD
        )
        
        # Étape 1 : Nettoyer le CSV
        total_rows = importer.clean_csv(input_csv, output_csv)
        
        # Étape 2 : Nettoyer la base
        importer.clean_database()
        
        # Étape 3 : Créer la couche spatiale
        importer.create_spatial_layer()
        
        # Étape 4 : Importer les données (depuis le CSV local nettoyé)
        imported = importer.import_data(output_csv)
        
        # Étape 5 : Ajouter à la couche spatiale
        added = importer.add_to_spatial_layer()
        
        # Étape 6 : Créer les index
        importer.create_indexes()
        
        # Étape 7 : Vérifier
        importer.verify_import()
        
        # Fermer la connexion
        importer.close()
        
        print("\n" + "=" * 60)
        print("✅ IMPORT TERMINÉ AVEC SUCCÈS !")
        print("=" * 60)
        print(f"\n📊 Résumé :")
        print(f"   - Fichier CSV nettoyé : {output_csv}")
        print(f"   - Établissements importés : {imported}")
        print(f"   - Nœuds ajoutés à la couche : {added}")
        print(f"   - Couche spatiale : {importer.layer}")
        print(f"\n🚀 Vous pouvez maintenant lancer l'application :")
        print(f"   python app.py")
        
    except FileNotFoundError:
        print(f"\n❌ ERREUR : Fichier {input_csv} introuvable")
        print(f"   Assurez-vous que le fichier CSV est dans database/")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ ERREUR : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()