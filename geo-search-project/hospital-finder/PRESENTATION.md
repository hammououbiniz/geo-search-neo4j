# 🎤 Guide de Présentation — Hospital Finder Fès

> Ce document est un guide complet pour préparer et dérouler votre présentation orale.
> Durée estimée : **15-20 minutes** (ajustable selon le temps alloué).

---

## 📌 Plan de la présentation

| # | Slide | Durée | Qui parle |
|---|---|---|---|
| 1 | Page de titre | 30s | Jaouad |
| 2 | Contexte & Problématique | 2 min | Amina |
| 3 | Objectifs du projet | 1 min | Amina |
| 4 | Architecture technique | 2 min | Jaouad |
| 5 | Les données (source, volume, nettoyage) | 2 min | Amina |
| 6 | Modèle Neo4j & Requêtes Cypher | 3 min | Hammou |
| 7 | Démo live de l'application | 4 min | Jaouad |
| 8 | Difficultés & Solutions | 2 min | Tous |
| 9 | Améliorations futures | 1 min | Hammou |
| 10 | Conclusion & Questions | 2 min | Tous |

---

## 🖼️ Contenu détaillé par slide

---

### SLIDE 1 — Page de titre

```
🏥 Hospital Finder - Fès
Système de Géolocalisation des Établissements de Santé

Mini-projet Big Data — BIAM 1ère année
2025-2026

Équipe :
  • Amina Akkal — Données & Infrastructure
  • Hammou Oubiniz — Requêtes Cypher
  • Jaouad El Morabit — Application Web
```

**Ce qu'il faut dire :**
> Bonjour, nous sommes [prénoms]. Nous allons vous présenter notre mini-projet Big Data :
> un système de géolocalisation des établissements de santé dans la ville de Fès.

---

### SLIDE 2 — Contexte & Problématique

```
📍 CONTEXTE
• Fès : 1,2 million d'habitants, une des plus grandes villes du Maroc
• Des centaines d'établissements de santé répartis dans toute la ville
• Les citoyens et visiteurs ont du mal à trouver rapidement
  l'établissement le plus proche

❓ PROBLÉMATIQUE
Comment exploiter les données géographiques ouvertes (OpenStreetMap)
et une base de données orientée graphe (Neo4j) pour fournir un outil
de recherche spatiale efficace des établissements de santé de Fès ?
```

**Ce qu'il faut dire :**
> Fès est une ville étendue avec des centaines d'hôpitaux, cliniques et pharmacies.
> Quand on est dans un quartier inconnu, il est difficile de trouver la pharmacie
> ou l'hôpital le plus proche. Notre question : peut-on utiliser les données
> OpenStreetMap et Neo4j pour résoudre ce problème ?

---

### SLIDE 3 — Objectifs

```
🎯 OBJECTIFS

1. Collecter les données des établissements de santé de Fès
   depuis OpenStreetMap (Overpass API)

2. Stocker ces données dans Neo4j en exploitant les types
   spatiaux natifs (point)

3. Développer une application web Flask avec recherche
   par proximité géographique

4. Visualiser les résultats sur une carte interactive
   (Leaflet.js + OpenStreetMap)
```

**Ce qu'il faut dire :**
> Nos quatre objectifs sont simples :
> collecter les données, les stocker dans Neo4j avec des coordonnées spatiales,
> créer une application web, et afficher tout sur une carte.

---

### SLIDE 4 — Architecture technique

```
🏗️ ARCHITECTURE

┌──────────────────────────────────────────┐
│           NAVIGATEUR WEB                  │
│   index.html    │    map.html             │
│  (statistiques) │  (Leaflet.js + OSM)     │
└────────┬─────────────────┬───────────────┘
         │    HTTP / JSON   │
         ▼                  ▼
┌──────────────────────────────────────────┐
│            FLASK (Python)                 │
│  app.py → hospital_finder.py              │
│  Routes    Requêtes Cypher paramétrées    │
└────────────────┬─────────────────────────┘
                 │  Bolt protocol
                 ▼
┌──────────────────────────────────────────┐
│              NEO4J 5.15                   │
│  433 nœuds HealthcareFacility             │
│  Propriété location: point()              │
│  Recherche: point.distance()              │
└──────────────────────────────────────────┘

Technologies : Flask 3.0 | Neo4j 5.15 | Leaflet.js 1.9.4 | Python 3.14
```

**Ce qu'il faut dire :**
> L'architecture est en 3 couches :
> - Le **navigateur** affiche les pages HTML et la carte Leaflet
> - Le **serveur Flask** expose des API REST et communique avec Neo4j via le driver Python
> - **Neo4j** stocke les 433 établissements avec des coordonnées spatiales (type `point`)
> La communication entre Flask et Neo4j se fait avec le protocole Bolt.
> La carte utilise les tuiles OpenStreetMap (gratuites et open source).

---

### SLIDE 5 — Les données

```
📊 LES DONNÉES

Source : OpenStreetMap (Overpass API)
  → Extraction des POI amenity=hospital|clinic|pharmacy
  → Bounding box : ville de Fès

Volume :
  ┌──────────────┬────────┐
  │ Type         │ Nombre │
  ├──────────────┼────────┤
  │ Hôpitaux     │     17 │
  │ Cliniques    │     26 │
  │ Pharmacies   │    390 │
  ├──────────────┼────────┤
  │ TOTAL        │    433 │
  └──────────────┴────────┘

Propriétés par nœud :
  osm_id, name, amenity, latitude, longitude,
  location (Point Neo4j), street, city

Pipeline :
  CSV brut → clean_csv() → CSV nettoyé → import_data() → Neo4j
```

**Ce qu'il faut dire :**
> Nous avons extrait 433 établissements de santé de Fès depuis OpenStreetMap
> via l'API Overpass. La majorité sont des pharmacies (390), avec 26 cliniques
> et 17 hôpitaux. Chaque établissement possède un nom, un type, des coordonnées
> GPS et une adresse. Le script `auto_import.py` nettoie le CSV et l'importe
> dans Neo4j par batches de 100 lignes.

---

### SLIDE 6 — Modèle Neo4j & Requêtes Cypher

```
🗄️ MODÈLE NEO4J

Nœud : (:HealthcareFacility)
  ├── osm_id     : "4822797821"
  ├── name       : "Pharmacie Amine"
  ├── amenity    : "pharmacy"
  ├── latitude   : 34.06078
  ├── longitude  : -4.97306
  ├── location   : point({latitude: 34.06078, longitude: -4.97306})
  ├── street     : "32 TRIK JDIDA RCIF"
  └── city       : "Fès"

REQUÊTE CLÉ — Recherche par proximité :

  MATCH (h:HealthcareFacility)
  WITH h, point.distance(
      h.location,
      point({latitude: 34.0632, longitude: -4.9998})
  ) AS dist
  WHERE dist <= 1000       ← rayon en mètres
  RETURN h.name, h.amenity, dist
  ORDER BY dist ASC

→ Résultat : 15 établissements dans un rayon d'1 km
→ Le plus proche : Pharmacie Al Mamalik à 406 m
```

**Ce qu'il faut dire :**
> Dans Neo4j, chaque établissement est un nœud avec le label HealthcareFacility.
> La propriété clé est `location`, de type `point` natif Neo4j.
> Cela nous permet d'utiliser `point.distance()` pour calculer la distance
> en mètres entre un point donné et chaque établissement.
> Par exemple, à 1 km de la Place R'cif, on trouve 15 établissements,
> le plus proche étant la Pharmacie Al Mamalik à 406 mètres.

**Tip :** Si vous avez accès à Neo4j Browser, montrez la requête en live !

---

### SLIDE 7 — Démo live

```
🖥️ DÉMONSTRATION

1. Page d'accueil → http://127.0.0.1:5000
   • Montrer les statistiques (17 hôpitaux, 26 cliniques, 390 pharmacies)
   • Montrer les positions prédéfinies

2. Carte interactive → http://127.0.0.1:5000/map
   • Afficher tous les 433 marqueurs
   • Cliquer sur un marqueur → détails
   • Sélectionner "Place R'cif" dans les positions prédéfinies
   • Rechercher avec rayon = 1 km → 15 résultats
   • Changer le rayon → montrer le changement de résultats

3. API JSON → http://127.0.0.1:5000/api/all
   • Montrer la structure JSON retournée
   • Montrer les coordonnées (latitude, longitude)

4. Test connexion → http://127.0.0.1:5000/test-connection
   • Montrer que la connexion Neo4j fonctionne
```

**Ce qu'il faut dire :**
> Passons à la démonstration.
> [Ouvrir le navigateur]
> Voici la page d'accueil avec les statistiques...
> [Naviguer vers /map]
> Sur la carte, on voit nos 433 établissements. Si je clique sur un marqueur,
> j'ai les détails. Maintenant, si je sélectionne Place R'cif et un rayon d'1 km...
> on obtient 15 résultats triés par distance.

**⚠️ Avant la présentation :** Lancer `python app.py` et vérifier que tout fonctionne !

---

### SLIDE 8 — Difficultés & Solutions

```
🐛 DIFFICULTÉS RENCONTRÉES

┌──────────────────────────────────┬────────────────────────────────────┐
│ Difficulté                       │ Solution                          │
├──────────────────────────────────┼────────────────────────────────────┤
│ Colonnes CSV avec backticks      │ Fonction clean_col_name() pour    │
│ (`@lat`, `@lon`)                 │ strip les backticks avant mapping │
├──────────────────────────────────┼────────────────────────────────────┤
│ Plugin Neo4j Spatial             │ Utilisation de point.distance()   │
│ non disponible                   │ natif (fonctionne sans plugin)    │
├──────────────────────────────────┼────────────────────────────────────┤
│ LOAD CSV nécessite le dossier    │ Import via Python + Cypher        │
│ import/ de Neo4j                 │ UNWIND $batch (batches de 100)    │
├──────────────────────────────────┼────────────────────────────────────┤
│ Incohérence des propriétés       │ Templates HTML robustes avec      │
│ entre CSV et templates           │ gestion des valeurs manquantes    │
└──────────────────────────────────┴────────────────────────────────────┘
```

**Ce qu'il faut dire :**
> Nous avons rencontré plusieurs difficultés techniques.
> La plus intéressante : les colonnes du CSV contenaient des backticks
> invisibles dans les noms (`@lat` au lieu de `@lat`), ce qui donnait
> des coordonnées nulles. On a résolu ça avec un nettoyage automatique.
> Aussi, le plugin Spatial de Neo4j n'était pas installé, mais
> la fonction native `point.distance()` suffit pour notre cas d'usage.

---

### SLIDE 9 — Améliorations futures

```
🚀 AMÉLIORATIONS POSSIBLES

• Géolocalisation du navigateur (GPS) pour détecter
  automatiquement la position de l'utilisateur

• Installer le plugin Neo4j Spatial pour des requêtes
  avancées (spatial.withinDistance, spatial.closest)

• Ajouter des relations entre établissements
  (ex : hôpital ↔ pharmacie la plus proche)

• Enrichir les données : horaires, téléphone, spécialités,
  urgences, avis

• Déploiement en production : Docker, Gunicorn, HTTPS

• Application mobile avec React Native ou Flutter
```

**Ce qu'il faut dire :**
> Pour aller plus loin, on pourrait utiliser le GPS du navigateur
> pour géolocaliser automatiquement l'utilisateur, ajouter des relations
> entre établissements dans le graphe, et enrichir les données.
> Un déploiement en production avec Docker est aussi envisageable.

---

### SLIDE 10 — Conclusion & Questions

```
✅ CONCLUSION

Ce projet démontre comment :
  1. Les données ouvertes (OpenStreetMap) peuvent alimenter
     des applications utiles au citoyen
  2. Neo4j et ses types spatiaux natifs permettent des recherches
     géographiques efficaces
  3. Flask + Leaflet.js offrent une stack simple et performante
     pour le prototypage rapide

📊 Résultat : 433 établissements indexés et recherchables
   par proximité en temps réel

Merci pour votre attention !
Des questions ?
```

**Ce qu'il faut dire :**
> En conclusion, ce projet montre qu'avec des données ouvertes,
> Neo4j et Flask, on peut créer rapidement un outil utile de
> recherche d'établissements de santé par proximité.
> Nous avons réussi à indexer 433 établissements et à les rendre
> recherchables en temps réel sur une carte interactive.
> Merci pour votre attention, nous sommes prêts pour vos questions !

---

## 🎯 Checklist avant la présentation

- [ ] Neo4j Desktop est démarré avec la base de données active
- [ ] `python auto_import.py` a été exécuté (433 établissements importés)
- [ ] `python app.py` est en cours d'exécution
- [ ] http://127.0.0.1:5000 fonctionne dans le navigateur
- [ ] La carte affiche les 433 marqueurs
- [ ] La recherche par proximité fonctionne (tester Place R'cif, 1 km)
- [ ] Neo4j Browser est ouvert (pour montrer des requêtes Cypher en live)
- [ ] Le projecteur / l'écran est connecté et testé

---

## 💡 Questions possibles du jury & réponses

### Q: Pourquoi Neo4j et pas PostgreSQL/PostGIS ?
> Neo4j est une base de données orientée graphe, ce qui nous permet de modéliser
> facilement des relations entre établissements (ex : proximité, référence).
> De plus, le type `point` natif et `point.distance()` offrent une solution
> spatiale sans configuration supplémentaire. C'est aussi le sujet du cours Big Data.

### Q: Pourquoi Flask et pas Django ?
> Flask est un micro-framework léger, idéal pour un prototype/MVP.
> Django serait surdimensionné pour une application de cette taille.
> Flask nous donne plus de contrôle et moins de code boilerplate.

### Q: Comment gérez-vous la sécurité ?
> Le mot de passe Neo4j peut être configuré via des variables d'environnement
> (pas hardcodé). Les requêtes Cypher sont paramétrées (`$parametre`)
> pour éviter les injections. En production, il faudrait ajouter HTTPS et
> une authentification utilisateur.

### Q: Comment sont calculées les distances ?
> On utilise `point.distance()` de Neo4j qui calcule la distance géodésique
> (en mètres) entre deux points sur le globe terrestre.
> C'est similaire à la formule de Haversine.

### Q: Pourquoi les données sont dans un CSV et pas directement depuis l'API ?
> On a choisi d'exporter un snapshot CSV pour travailler en mode hors-ligne
> et contrôler la qualité des données. En production, on pourrait
> mettre en place une mise à jour périodique depuis l'API Overpass.

### Q: Quelle est la complexité de la recherche spatiale ?
> Sans index spatial dédié, c'est O(n) — on parcourt tous les nœuds.
> Avec 433 nœuds, c'est instantané (< 50ms). Pour des millions de nœuds,
> il faudrait le plugin Neo4j Spatial qui utilise un R-tree pour du O(log n).

### Q: Est-ce que les données sont à jour ?
> Les données proviennent d'OpenStreetMap à la date d'extraction.
> OSM est collaboratif, donc les données peuvent évoluer.
> Notre script `auto_import.py` permet de ré-importer facilement
> un nouveau CSV mis à jour.

---

## 📝 Notes supplémentaires

### Commandes utiles pendant la démo

```bash
# Lancer l'application
python app.py

# Tester l'API dans un autre terminal
curl http://127.0.0.1:5000/api/statistics
curl http://127.0.0.1:5000/api/all | python -m json.tool | head -30

# Recherche par proximité (Place R'cif)
curl -X POST http://127.0.0.1:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"latitude": 34.0632, "longitude": -4.9998, "radius": 1}'
```

### Requête Cypher à montrer dans Neo4j Browser

```cypher
// Tous les hôpitaux
MATCH (h:HealthcareFacility)
WHERE h.amenity = 'hospital'
RETURN h.name, h.street, h.city
ORDER BY h.name

// Les 5 plus proches de la Place R'cif
MATCH (h:HealthcareFacility)
WITH h, point.distance(
    h.location,
    point({latitude: 34.0632, longitude: -4.9998})
) AS dist
RETURN h.name, h.amenity, round(dist) + ' m' AS distance
ORDER BY dist ASC
LIMIT 5

// Statistiques
MATCH (h:HealthcareFacility)
RETURN h.amenity AS type, count(h) AS nombre
ORDER BY nombre DESC
```
