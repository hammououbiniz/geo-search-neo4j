# 📄 Résumé du Projet — Hospital Finder Fès

## Informations générales

| | |
|---|---|
| **Titre** | Système de Géolocalisation des Établissements de Santé — Fès |
| **Module** | Big Data |
| **Niveau** | BIAM 1ère année, 2025-2026 |
| **Équipe** | Amina Akkal, Hammou Oubiniz, Jaouad El Morabit |

---

## 1. Contexte & Problématique

La ville de Fès dispose de centaines d'établissements de santé (hôpitaux, cliniques, pharmacies) répartis sur un large territoire. Pour un citoyen ou un visiteur, il est souvent difficile de trouver rapidement l'établissement le plus proche adapté à son besoin.

**Problématique :** Comment exploiter les données géographiques ouvertes (OpenStreetMap) et une base de données graphe (Neo4j) pour fournir un outil de recherche spatiale efficace des établissements de santé de Fès ?

---

## 2. Objectifs

1. Collecter les données des établissements de santé de Fès depuis OpenStreetMap
2. Stocker ces données dans Neo4j en exploitant les types spatiaux (`point`)
3. Développer une application web permettant la recherche par proximité géographique
4. Visualiser les résultats sur une carte interactive

---

## 3. Architecture technique

```
┌─────────────────────────────────────────────────────────┐
│                    NAVIGATEUR WEB                        │
│  ┌──────────┐  ┌────────────────────────────────────┐   │
│  │ index.html│  │          map.html                  │   │
│  │(statistiques)│  │  Leaflet.js + OpenStreetMap tiles │   │
│  └──────────┘  └────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (JSON)
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   FLASK (Python)                         │
│  app.py  →  hospital_finder.py  →  advanced_queries.py  │
│  Routes      Requêtes Cypher       Requêtes avancées    │
└────────────────────────┬────────────────────────────────┘
                         │ Bolt protocol
                         ▼
┌─────────────────────────────────────────────────────────┐
│                     NEO4J                                │
│  Label: HealthcareFacility                              │
│  Props: osm_id, name, amenity, latitude, longitude,     │
│         location (point), street, city                   │
│  433 nœuds | Index sur name, amenity, osm_id            │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Pile technologique

| Couche | Outil | Rôle |
|---|---|---|
| Données | OpenStreetMap / Overpass API | Source des POI santé |
| Nettoyage | Python (csv, auto_import.py) | Nettoyage CSV, import batch |
| Stockage | Neo4j 5.15 | Base de données graphe avec types spatiaux |
| Backend | Flask 3.0 | API REST + rendu HTML |
| Frontend | Leaflet.js 1.9.4 | Carte interactive OpenStreetMap |
| Spatial | `point.distance()` natif | Calcul de distances (mètres) |

---

## 5. Données

### Source
- **Overpass API** (OpenStreetMap) — extraction des POI `amenity=hospital|clinic|pharmacy` dans la bounding box de Fès

### Volume
| Type | Nombre |
|---|---|
| Hôpitaux | 17 |
| Cliniques | 26 |
| Pharmacies | 390 |
| **Total** | **433** |

### Propriétés par nœud
`osm_id`, `name`, `amenity`, `latitude`, `longitude`, `location` (Point Neo4j), `street`, `city`

---

## 6. Fonctionnalités réalisées

| # | Fonctionnalité | Endpoint | Statut |
|---|---|---|---|
| 1 | Page d'accueil avec statistiques | `GET /` | ✅ |
| 2 | Carte interactive (tous les établissements) | `GET /map` | ✅ |
| 3 | Recherche par proximité (rayon configurable) | `POST /api/search` | ✅ |
| 4 | API JSON de tous les établissements | `GET /api/all` | ✅ |
| 5 | Statistiques par type | `GET /api/statistics` | ✅ |
| 6 | Filtrage par type (hospital/clinic/pharmacy) | `POST /api/search` + filtre | ✅ |
| 7 | Positions prédéfinies (Gare, R'cif, CHU…) | Interface carte | ✅ |
| 8 | Test connexion Neo4j | `GET /test-connection` | ✅ |

---

## 7. Requêtes Cypher principales

### 7.1 Recherche par proximité

```cypher
MATCH (h:HealthcareFacility)
WITH h, point.distance(
    h.location,
    point({latitude: $lat, longitude: $lon})
) AS dist
WHERE dist <= $radius_m
RETURN h.name AS name, h.amenity AS type,
       h.latitude AS latitude, h.longitude AS longitude,
       dist AS distance
ORDER BY dist ASC
```

### 7.2 Statistiques

```cypher
MATCH (h:HealthcareFacility)
RETURN h.amenity AS type, count(h) AS count
```

### 7.3 Établissement le plus proche

```cypher
MATCH (h:HealthcareFacility)
RETURN h.name AS name,
       point.distance(h.location, point({latitude: $lat, longitude: $lon})) AS distance
ORDER BY distance ASC
LIMIT 1
```

---

## 8. Pipeline d'import des données

```
hospitals_clinics_pharmacy_fes.csv (brut, colonnes avec backticks)
        │
        ▼  auto_import.py — Étape 1 : clean_csv()
fes_healthcare_clean.csv (colonnes normalisées)
        │
        ▼  auto_import.py — Étape 4 : import_data()
Neo4j (433 nœuds HealthcareFacility avec propriété location: point())
        │
        ▼  auto_import.py — Étape 6 : create_indexes()
Index sur osm_id, name, amenity, location
```

---

## 9. Répartition du travail

| Membre | Responsabilités |
|---|---|
| **Amina Akkal** | Collecte des données OSM, nettoyage CSV, infrastructure Neo4j |
| **Hammou Oubiniz** | Modélisation graphe, requêtes Cypher, index spatiaux |
| **Jaouad El Morabit** | Application Flask, API REST, interface Leaflet.js |

---

## 10. Difficultés rencontrées & solutions

| Difficulté | Solution |
|---|---|
| Colonnes CSV avec backticks (`` `@lat` ``) | Fonction `clean_col_name()` qui strip les backticks avant mapping |
| Plugin Neo4j Spatial non installé | Utilisation de `point.distance()` natif (fonctionne sans plugin) |
| LOAD CSV nécessite dossier `import/` Neo4j | Import via Python + `UNWIND $batch` (batches de 100) |
| Propriétés incohérentes (urgences, telephone) | Templates HTML avec gestion `hospital.street \|\| ''` |

---

## 11. Améliorations possibles

- Installer le plugin Neo4j Spatial pour les requêtes avancées (`spatial.withinDistance`, `spatial.closest`)
- Ajouter la géolocalisation du navigateur (GPS)
- Intégrer des relations entre établissements (ex : hôpital ↔ pharmacie la plus proche)
- Ajouter des données supplémentaires (horaires, téléphone, spécialités)
- Déploiement en production (Docker, Gunicorn, HTTPS)source 