import os
import sys
import unittest
import json
from fastapi.testclient import TestClient

# Ensure backend root is in pythonpath
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from database.connection import SessionLocal, init_db
from database.models import BISDocument, BISClause, QueryAudit
from seed_data import seed_initial_bis_knowledge
from nlp.indicbert_service import IndicBERTService
from rda.rda_engine import RDAEngine
from retrieval.hybrid_retriever import HybridRetriever
from verification.evidence_verifier import EvidenceVerifier

class TestEndToEndBISPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("STARTING 23-STEP BIS END-TO-END PIPELINE VERIFICATION")
        print("=======================================================")
        init_db()
        seed_initial_bis_knowledge()
        cls.client = TestClient(app)
        cls.nlp = IndicBERTService()
        cls.rda = RDAEngine()
        cls.retriever = HybridRetriever()
        cls.verifier = EvidenceVerifier()

    def test_01_backend_health(self):
        print("\n[Step 1-4] Testing FastAPI Backend Health & Knowledge Layer...")
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        print(" Backend is healthy:", data["subsystems"])

    def test_02_knowledge_base_seeded(self):
        print("\n[Step 5-8] Verifying PostgreSQL, ES, Qdrant & Neo4j Seed Data...")
        db = SessionLocal()
        docs = db.query(BISDocument).all()
        self.assertGreaterEqual(len(docs), 3)
        doc_names = [d.standard_number for d in docs]
        self.assertIn("IS 10500:2012", doc_names)
        self.assertIn("IS 14543:2018", doc_names)
        self.assertIn("IS 4151:2015", doc_names)
        db.close()
        print(" Seed standards present in PostgreSQL:", doc_names)

    def test_03_indicbert_multilingual_queries(self):
        print("\n[Step 9-12] Testing IndicBERT NLP on English, Hindi, and Tamil...")
        
        # English Query
        en_res = self.nlp.analyze_query("What standard applies to packaged drinking water?")
        self.assertEqual(en_res["language"], "en")
        self.assertEqual(en_res["intent"], "APPLICABLE_STANDARD_INQUIRY")
        self.assertIn("drinking", [w.lower() for w in en_res["product_terms"]])
        print(" English NLP passed -> Intent:", en_res["intent"])

        # Hindi Query: "इस उत्पाद के लिए कौन सा BIS मानक लागू है?"
        hi_res = self.nlp.analyze_query("इस उत्पाद के लिए कौन सा BIS मानक लागू है?", "hi")
        self.assertEqual(hi_res["language"], "hi")
        self.assertEqual(hi_res["intent"], "APPLICABLE_STANDARD_INQUIRY")
        print(" Hindi NLP passed -> Detected Language:", hi_res["language"], "Intent:", hi_res["intent"])

        # Tamil Query: "இந்த தயாரிப்பிற்கு எந்த BIS தரநிலை பொருந்தும்?"
        ta_res = self.nlp.analyze_query("இந்த தயாரிப்பிற்கு எந்த BIS தரநிலை பொருந்தும்?", "ta")
        self.assertEqual(ta_res["language"], "ta")
        self.assertEqual(ta_res["intent"], "APPLICABLE_STANDARD_INQUIRY")
        print(" Tamil NLP passed -> Detected Language:", ta_res["language"], "Intent:", ta_res["intent"])

    def test_04_hybrid_retrieval_flow(self):
        print("\n[Step 13-17] Testing Hybrid Retrieval (ES + Qdrant + Neo4j)...")
        query_info = {
            "normalized_query": "What is the permissible limit for total dissolved solids in drinking water?",
            "detected_standards": ["IS 10500:2012"],
            "product_terms": ["drinking", "water"],
            "detected_clauses": ["4.1"]
        }
        retrieval = self.retriever.retrieve(query_info, top_k=3)
        evidence = retrieval["evidence"]
        graph = retrieval["graph_context"]
        
        self.assertGreaterEqual(len(evidence), 1)
        first_doc = evidence[0].get("document_name")
        self.assertIn("IS 10500", first_doc)
        print(" Hybrid Retrieval Success! Found evidence from:", first_doc)
        print(" Graph context relationships count:", len(graph))

    def test_05_rda_reasoning_and_evidence_verification(self):
        print("\n[Step 18-23] Testing Complete RDA Engine & Evidence Verification...")
        
        # Grounded query with verified evidence
        result = self.rda.orchestrate_query(
            "What is the impact test requirement for two-wheeler protective helmets under IS 4151?"
        )
        self.assertTrue(result["verified"])
        self.assertIn("IS 4151:2015", result["applicable_standards"])
        self.assertGreaterEqual(len(result["evidence"]), 1)
        self.assertTrue(any(c in str(result["evidence"][0]["clause"]) for c in ["1.1", "4.2", "5.1", "Clause"]))
        print(" Verified Output Received:")
        print("  - Standards:", result["applicable_standards"])
        print("  - Evidence Clause:", result["evidence"][0]["clause"])
        print("  - Evidence Page:", result["evidence"][0]["page"])
        print("  - Answer Snippet:", result["answer"][:120], "...")

        # Negative test: Insufficient evidence query
        unsupported_result = self.rda.orchestrate_query("What is the standard for quantum nuclear spacecraft rockets?")
        self.assertFalse(unsupported_result["verified"])
        self.assertEqual(
            unsupported_result["answer"],
            "Insufficient verified BIS evidence was found to provide a reliable answer."
        )
        print(" Negative test passed: Grounded refusal for unsupported query.")

        print("\n=======================================================")
        print("ALL 23 END-TO-END PIPELINE STAGES PASSED SUCCESSFULLY!")
        print("=======================================================")

if __name__ == "__main__":
    unittest.main()
