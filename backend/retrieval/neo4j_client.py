import os
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("neo4j_client")

class Neo4jGraphClient:
    # Shared in-memory graph across all instances when Neo4j service is offline
    _shared_in_memory_graph: List[Dict[str, Any]] = []

    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "bis_neo4j_password")
        self.driver = None

        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {uri}")
            self._create_schema_constraints()
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}. Operating with in-memory graph fallback.")
            self.driver = None

    def _create_schema_constraints(self):
        if not self.driver:
            return
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Standard) REQUIRE s.number IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Product) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Certification) REQUIRE c.scheme IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Laboratory) REQUIRE l.name IS UNIQUE"
        ]
        with self.driver.session() as session:
            for q in queries:
                try:
                    session.run(q)
                except Exception:
                    pass

    def sync_regulatory_chain(
        self,
        standard_number: str,
        product_name: str,
        material: str,
        industry: str,
        certification_scheme: str,
        testing_requirement: str,
        laboratory_name: str,
        applicable_rule: str
    ):
        """
        Builds the 8-node regulatory chain:
        Standard -> Product -> Material -> Industry -> Certification -> Testing -> Laboratory -> Applicable Rule
        """
        record = {
            "standard_number": standard_number,
            "product_name": product_name,
            "material": material,
            "industry": industry,
            "certification_scheme": certification_scheme,
            "testing_requirement": testing_requirement,
            "laboratory_name": laboratory_name,
            "applicable_rule": applicable_rule
        }
        Neo4jGraphClient._shared_in_memory_graph.append(record)

        if self.driver:
            cypher = """
            MERGE (s:Standard {number: $standard_number})
            MERGE (p:Product {name: $product_name})
            MERGE (m:Material {name: $material})
            MERGE (i:Industry {name: $industry})
            MERGE (c:Certification {scheme: $certification_scheme})
            MERGE (t:Testing {requirement: $testing_requirement})
            MERGE (l:Laboratory {name: $laboratory_name})
            MERGE (r:Rule {name: $applicable_rule})

            MERGE (s)-[:COVERS_PRODUCT]->(p)
            MERGE (p)-[:USES_MATERIAL]->(m)
            MERGE (p)-[:BELONGS_TO_INDUSTRY]->(i)
            MERGE (s)-[:MANDATES_CERTIFICATION]->(c)
            MERGE (s)-[:REQUIRES_TESTING]->(t)
            MERGE (t)-[:PERFORMED_BY]->(l)
            MERGE (c)-[:GOVERNED_BY]->(r)
            """
            try:
                with self.driver.session() as session:
                    session.run(cypher, **record)
            except Exception as e:
                logger.error(f"Failed to sync regulatory chain to Neo4j: {e}")

    def find_relationships(self, standards: List[str] = None, products: List[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieves regulatory chain paths for given standards or product keywords.
        """
        if self.driver:
            cypher = """
            MATCH (s:Standard)
            OPTIONAL MATCH (s)-[:COVERS_PRODUCT]->(p:Product)
            OPTIONAL MATCH (p)-[:USES_MATERIAL]->(m:Material)
            OPTIONAL MATCH (p)-[:BELONGS_TO_INDUSTRY]->(i:Industry)
            OPTIONAL MATCH (s)-[:MANDATES_CERTIFICATION]->(c:Certification)
            OPTIONAL MATCH (s)-[:REQUIRES_TESTING]->(t:Testing)-[:PERFORMED_BY]->(l:Laboratory)
            OPTIONAL MATCH (c)-[:GOVERNED_BY]->(r:Rule)
            WHERE ($standards IS NOT NULL AND s.number IN $standards) 
               OR ($products IS NOT NULL AND any(prod IN $products WHERE toLower(p.name) CONTAINS toLower(prod)))
            RETURN 
                s.number AS standard,
                p.name AS product,
                m.name AS material,
                i.name AS industry,
                c.scheme AS certification,
                t.requirement AS testing,
                l.name AS laboratory,
                r.name AS rule
            LIMIT 15
            """
            try:
                with self.driver.session() as session:
                    records = session.run(cypher, standards=standards or [], products=products or [])
                    results = []
                    for rec in records:
                        results.append({
                            "standard": rec["standard"],
                            "product": rec["product"],
                            "material": rec["material"],
                            "industry": rec["industry"],
                            "certification": rec["certification"],
                            "testing": rec["testing"],
                            "laboratory": rec["laboratory"],
                            "rule": rec["rule"],
                            "retrieval_method": "graph_neo4j"
                        })
                    if results:
                        return results
            except Exception as e:
                logger.error(f"Neo4j query error: {e}")

        # In-memory graph search fallback
        return self._in_memory_graph_search(standards, products)

    def _in_memory_graph_search(self, standards: List[str], products: List[str]) -> List[Dict[str, Any]]:
        results = []
        stds = [s.lower().replace(" ", "") for s in (standards or [])]
        prods = [p.lower() for p in (products or [])]

        for item in Neo4jGraphClient._shared_in_memory_graph:
            match = False
            item_std = item["standard_number"].lower().replace(" ", "")
            if any(s in item_std or item_std in s for s in stds):
                match = True
            elif any(p in item["product_name"].lower() for p in prods):
                match = True

            if match:
                results.append({
                    "standard": item["standard_number"],
                    "product": item["product_name"],
                    "material": item["material"],
                    "industry": item["industry"],
                    "certification": item["certification_scheme"],
                    "testing": item["testing_requirement"],
                    "laboratory": item["laboratory_name"],
                    "rule": item["applicable_rule"],
                    "retrieval_method": "graph_in_memory"
                })
        return results

    def close(self):
        if self.driver:
            self.driver.close()
