# prepare_csv.py
"""
Script pour nettoyer le fichier CSV avant import dans Neo4j
- Renomme les colonnes (@id -> osm_id, @lat -> latitude, @lon -> longitude)
- Supprime les backticks
- Nettoie les valeurs vides
"""

import csv
import sys

def clean_csv(input_file, output_file):
    """
    Nettoie le fichier CSV pour Neo4j
    
    Args:
        input_file: Chemin du fichier CSV source
        output_file: Chemin du fichier CSV nettoyé
    """
    
    # Mapping des noms de colonnes
    column_mapping = {
        '@id': 'osm_id',
        '@lat': 'latitude',
        '@lon': 'longitude',
        '`addr:street`': 'street',
        'addr:city': 'city'
    }
    
    print(f"📂 Lecture de {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        
        # Nettoyer les noms de colonnes
        fieldnames = [column_mapping.get(col.strip(), col.strip()) for col in reader.fieldnames]
        
        print(f"✅ Colonnes détectées : {fieldnames}")
        
        # Lire toutes les lignes
        rows = []
        for row in reader:
            # Créer un nouveau dictionnaire avec les colonnes nettoyées
            clean_row = {}
            for old_col, value in row.items():
                new_col = column_mapping.get(old_col.strip(), old_col.strip())
                clean_row[new_col] = value.strip() if value else ''
            rows.append(clean_row)
        
        print(f"✅ {len(rows)} lignes lues")
    
    # Écrire le fichier nettoyé
    print(f"💾 Écriture de {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Fichier nettoyé créé : {output_file}")
    
    # Statistiques
    print("\n📊 STATISTIQUES :")
    amenity_count = {}
    no_name_count = 0
    
    for row in rows:
        amenity = row.get('amenity', 'unknown')
        amenity_count[amenity] = amenity_count.get(amenity, 0) + 1
        
        if not row.get('name'):
            no_name_count += 1
    
    print(f"   Total : {len(rows)} établissements")
    for amenity, count in sorted(amenity_count.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {amenity}: {count}")
    print(f"   - Sans nom: {no_name_count}")

if __name__ == '__main__':
    input_file = 'hospitals_clinics_pharmacy_fes.csv'
    output_file = 'fes_healthcare_clean.csv'
    
    try:
        clean_csv(input_file, output_file)
        print("\n✅ SUCCÈS !")
        print(f"👉 Placez {output_file} dans le dossier import/ de Neo4j")
        
    except FileNotFoundError:
        print(f"❌ ERREUR : Fichier {input_file} introuvable")
        print("   Assurez-vous que le fichier CSV est dans le même dossier que ce script")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        sys.exit(1)