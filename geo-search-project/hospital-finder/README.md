# 🏥 Hospital Finder - Fès

> Application web de géolocalisation des établissements de santé à Fès, Maroc.
> Mini-projet Big Data — BIAM 1ère année, 2025-2026

---

## 📋 Description

**Hospital Finder** permet de localiser et rechercher des hôpitaux, cliniques et pharmacies dans la ville de Fès à partir de données OpenStreetMap, stockées dans une base de données graphe **Neo4j** et affichées sur une carte interactive **Leaflet.js**.

### Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| 🗺️ Carte interactive | Affichage de 433 établissements sur OpenStreetMap via Leaflet.js |
| 🔍 Recherche par proximité | Trouver les établissements dans un rayon donné (km) autour d'un point |
| 🏷️ Filtrage par type | Hôpitaux (17), cliniques (26), pharmacies (390) |
| 📊 Statistiques | Nombre d'établissements par catégorie |
| 📍 Positions prédéfinies | Gare de Fès, Place R'cif, CHU Hassan II, Bab Boujloud, Ville Nouvelle |

---

## 🛠️ Technologies

| Composant | Technologie | Version |
|---|---|---|
| Backend | Python / Flask | 3.14 / 3.0.0 |
| Base de données | Neo4j (graphe) | 5.15.0 |
| Carte | Leaflet.js / OpenStreetMap | 1.9.4 |
| Spatial | `point.distance()` natif Neo4j | — |
| Frontend | HTML / CSS / JavaScript | — |

---

## 📦 Installation

### Prérequis

- **Python** 3.10+
- **Neo4j Desktop** (avec une base de données démarrée sur `bolt://localhost:7687`)
- **Git** (optionnel)

### Étapes

```bash
# 1. Cloner le projet
git clone <votre-repo>
cd hospital-finder

# 2. Créer et activer l'environnement virtuel
python -m venv venv
source venv/Scripts/activate     # Windows (Git Bash)
# OU venv\Scripts\activate       # Windows (CMD)
# OU source venv/bin/activate    # Mac/Linux

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer Neo4j (modifier le mot de passe dans config.py)
#    OU utiliser les variables d'environnement :
#    set NEO4J_PASSWORD=votre_mot_de_passe

# 5. Importer les données dans Neo4j
python auto_import.py

# 6. Lancer l'application
python app.py
```

> L'application est disponible sur **http://127.0.0.1:5000**

### Dépannage

| Problème | Solution |
|---|---|
| `python` n'est pas reconnu | Utiliser `python3` à la place |
| `pip` n'est pas reconnu | Utiliser `python -m pip install ...` |
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt` |
| Neo4j connexion refusée | Vérifier que Neo4j Desktop est démarré |

---

## 📁 Structure du projet

```
hospital-finder/
├── app.py                     # Application Flask (routes & API)
├── hospital_finder.py         # Classe HospitalFinder (requêtes Neo4j)
├── advanced_queries.py        # Requêtes avancées (plugin spatial requis)
├── auto_import.py             # Script d'import CSV → Neo4j
├── config.py                  # Configuration (Neo4j, Flask, carte)
├── requirements.txt           # Dépendances Python
│
├── database/
│   ├── hospitals_clinics_pharmacy_fes.csv   # Données brutes OSM
│   ├── fes_healthcare_clean.csv             # Données nettoyées (auto-généré)
│   ├── export-hopitaux.cypher               # Export Cypher
│   └── prepare_csv.py                       # Script de préparation CSV
│
├── templates/
│   ├── base.html              # Template de base
│   ├── index.html             # Page d'accueil (statistiques)
│   ├── map.html               # Page carte interactive
│   └── error.html             # Page d'erreur
│
└── static/
    ├── css/style.css          # Feuille de styles
    └── images/                # Images
```

---

## 🚀 Routes & API

### Pages web

| Route | Description |
|---|---|
| `GET /` | Page d'accueil avec statistiques |
| `GET /map` | Carte interactive Leaflet |

### API REST

| Route | Méthode | Description |
|---|---|---|
| `/api/all` | GET | Tous les établissements (JSON) |
| `/api/search` | POST | Recherche par proximité (`latitude`, `longitude`, `radius` en km) |
| `/api/statistics` | GET | Statistiques par type |
| `/test-connection` | GET | Test connexion Neo4j |

### Exemple – Recherche par proximité

```bash
curl -X POST http://127.0.0.1:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"latitude": 34.0632, "longitude": -4.9998, "radius": 1}'
```

Réponse (15 résultats dans un rayon de 1 km autour de Place R'cif) :

```json
{
  "name": "Pharmacie Al Mamalik صيدلية الممالك",
  "type": "pharmacy",
  "latitude": 34.0658698,
  "longitude": -4.9968004,
  "distance": 406.01,
  "street": "",
  "city": "Fès"
}
```

---

## 🗄️ Modèle de données Neo4j

### Nœud : `HealthcareFacility`

| Propriété | Type | Description |
|---|---|---|
| `osm_id` | String | Identifiant OpenStreetMap |
| `name` | String | Nom de l'établissement |
| `amenity` | String | Type : `hospital`, `clinic`, `pharmacy` |
| `latitude` | Float | Latitude GPS |
| `longitude` | Float | Longitude GPS |
| `location` | Point | Point spatial Neo4j natif |
| `street` | String | Adresse (rue) |
| `city` | String | Ville |

### Requête Cypher — Recherche par proximité

```cypher
MATCH (h:HealthcareFacility)
WHERE point.distance(
    h.location,
    point({latitude: $lat, longitude: $lon})
) <= $radius_m
RETURN h.name AS name, h.amenity AS type,
       h.latitude AS latitude, h.longitude AS longitude,
       point.distance(h.location, point({latitude: $lat, longitude: $lon})) AS distance
ORDER BY distance ASC
```

---

## 👥 Auteurs

| Rôle | Nom |
|---|---|
| Données & Infrastructure | Amina Akkal |
| Requêtes Cypher | Hammou Oubiniz |
| Application Web | Jaouad El Morabit |

## 📚 Sources de données

- **OpenStreetMap** — Overpass API (extraction des POI santé à Fès)

## 📄 Licence

Projet académique — BIAM 1ère année, 2025-2026