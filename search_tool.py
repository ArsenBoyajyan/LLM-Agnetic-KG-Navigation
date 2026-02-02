# search_tool.py
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Load environment variables from .env file
load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")
print(f"DEBUG: URI loaded: {URI}")
print(f"DEBUG: User loaded: {USER}")

def search_kg(entity_name: str) -> list[dict]:
    """
    Executes a one-hop search from the given entity in the KG.
    Returns a list of neighbors (relation, neighbor_name, neighbor_type).
    """
    driver = None
    records = []
    try:
        # Create a single driver instance (thread-safe, efficient)
        driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
        # Verify connection and ensure the driver is active
        driver.verify_connectivity() 

        # The core Cypher query: find the entity by name, then find all 
        # outgoing relationships [r] and neighbors (t).
        query = """
        MATCH (s:Person) WHERE s.name = $entityName
        OPTIONAL MATCH (s)-[r]->(t)
        RETURN 
            type(r) AS relation, 
            CASE WHEN t.name IS NOT NULL THEN t.name ELSE t.title END AS neighbor, 
            labels(t) AS neighbor_labels
        """
        
        with driver.session() as session:
            # Use execute_read for safe, read-only transactions
            result = session.run(query, entityName=entity_name)
            
            for record in result:
                # Only include results where a relationship was found
                if record["relation"] is not None:
                    records.append({
                        "relation": record["relation"],
                        "neighbor": record["neighbor"],
                        "neighbor_type": record["neighbor_labels"][0] if record["neighbor_labels"] else 'Unknown'
                    })
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if driver:
            driver.close()
    
    return records

# --- Test Case ---
if __name__ == "__main__":
    # NOTE: AuraDB instance must have the Movie dataset loaded
    # (using the `:play movie-graph` command in the Neo4j Browser)
    
    print("--- Testing Connection and Search Function ---")
    
    # Example 1: Find all connections from a known actor
    results_hanks = search_kg("Tom Hanks")
    print(f"\nResults for 'Tom Hanks' ({len(results_hanks)} connections found):")
    for res in results_hanks[:5]: # Show top 5 results for brevity
        print(f"  -> ({res['relation']}) -> {res['neighbor']} ({res['neighbor_type']})")

    # Example 2: Test a non-existent entity
    results_fake = search_kg("Arsen Boyajyan")
    print(f"\nResults for 'Arsen Boyajyan': {results_fake}")

    if results_hanks:
        print("\nConnection and search function successful! You have your MVP tool.")
    else:
        print("\nConnection Failed or KG is Empty. Check your credentials and verify the Movie Graph is loaded.")