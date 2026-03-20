"""Quick script to check Neo4j data"""
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "jawad12345@@"))
with driver.session() as session:
    result = session.run(
        "MATCH (h:HealthcareFacility) "
        "RETURN h.name AS name, h.latitude AS lat, h.longitude AS lon, h.location AS loc "
        "LIMIT 5"
    )
    for r in result:
        print(f"name={r['name']}, lat={r['lat']}, lon={r['lon']}, loc={r['loc']}")
    
    # Count nulls
    result2 = session.run(
        "MATCH (h:HealthcareFacility) "
        "RETURN count(h) AS total, "
        "count(h.latitude) AS has_lat, "
        "count(h.location) AS has_loc"
    )
    r2 = result2.single()
    print(f"\nTotal: {r2['total']}, with latitude: {r2['has_lat']}, with location: {r2['has_loc']}")

driver.close()
