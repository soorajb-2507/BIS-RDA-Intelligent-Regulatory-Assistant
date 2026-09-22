import os
from database.connection import SessionLocal
from database.models import BISDocument, BISClause, BISLaboratory, CertificationScheme
from retrieval.elasticsearch_client import ElasticClient
from retrieval.qdrant_client import QdrantStoreClient
from retrieval.neo4j_client import Neo4jGraphClient
from utils.logger import get_logger

logger = get_logger("seed_data")

def seed_initial_bis_knowledge():
    """
    Seeds initial benchmark BIS standards into PostgreSQL, Elasticsearch, Qdrant, and Neo4j:
    - IS 10500:2012 (Drinking Water)
    - IS 14543:2018 (Packaged Drinking Water)
    - IS 4151:2015 (Protective Helmets)
    """
    db = SessionLocal()
    es = ElasticClient()
    qdrant = QdrantStoreClient()
    neo4j = Neo4jGraphClient()

    try:
        logger.info("Ensuring baseline BIS standards exist in PostgreSQL, Elasticsearch, Qdrant, and Neo4j...")

        seeds = [
            {
                "standard_number": "IS 10500:2012",
                "title": "Drinking Water — Specification",
                "version": "2.0",
                "doc_type": "Standard",
                "clauses": [
                    {
                        "clause_number": "3.1",
                        "clause_title": "Scope",
                        "page_number": 1,
                        "text": "This standard prescribes the requirements and the methods of sampling and test for drinking water (potable water) supplied through piped distribution network or public stand posts."
                    },
                    {
                        "clause_number": "4.1",
                        "clause_title": "Organoleptic and Physical Parameters",
                        "page_number": 2,
                        "text": "The drinking water shall comply with the requirements given in Table 1. Total dissolved solids (TDS) shall not exceed 500 mg/l acceptable limit and 2000 mg/l permissible limit in the absence of alternate source."
                    },
                    {
                        "clause_number": "5.2",
                        "clause_title": "Bacteriological Quality",
                        "page_number": 4,
                        "text": "All water intended for drinking shall be free from Escherichia coli or thermotolerant coliform bacteria in any 100 ml sample tested per IS 1622."
                    }
                ],
                "graph": {
                    "product": "Potable Drinking Water",
                    "material": "Water",
                    "industry": "Municipal & Water Supply",
                    "scheme": "Scheme-I (ISI Mark Certification)",
                    "testing": "Bacteriological & Chemical Analysis per IS 1622",
                    "lab": "BIS Central Laboratory, Sahibabad",
                    "rule": "Bureau of Indian Standards Act 2016"
                }
            },
            {
                "standard_number": "IS 14543:2018",
                "title": "Packaged Drinking Water (Other Than Packaged Natural Mineral Water) — Specification",
                "version": "3.0",
                "doc_type": "Standard",
                "clauses": [
                    {
                        "clause_number": "1.1",
                        "clause_title": "Scope and Definition",
                        "page_number": 1,
                        "text": "This standard specifies requirements and methods of sampling and testing for packaged drinking water other than packaged natural mineral water. Mandatory ISI certification applies under Food Safety regulations."
                    },
                    {
                        "clause_number": "3.2",
                        "clause_title": "Treatment and Disinfection",
                        "page_number": 2,
                        "text": "Water shall be derived from any source of potable water and shall be subjected to treatments such as filtration, aeration, reverse osmosis, demineralization, and disinfection by ozone or UV to meet parameters."
                    },
                    {
                        "clause_number": "6.1",
                        "clause_title": "Packaging and Marking",
                        "page_number": 5,
                        "text": "Packaged drinking water shall be filled in clean, hygienic, tamper-proof food-grade containers conforming to IS 15410 or IS 12252. The container shall bear the Standard Mark (ISI Mark) with license number CM/L."
                    }
                ],
                "graph": {
                    "product": "Packaged Drinking Water",
                    "material": "Treated Water & Food-grade PET",
                    "industry": "Food & Beverage Processing",
                    "scheme": "Scheme-I (Mandatory ISI Mark Certification)",
                    "testing": "Pesticide Residues, Heavy Metals & Microbial Safety",
                    "lab": "National Accreditation Board for Testing Laboratories (NABL)",
                    "rule": "Food Safety and Standards (Packaging) Regulations, 2018"
                }
            },
            {
                "standard_number": "IS 4151:2015",
                "title": "Protective Helmets for Two Wheeler Riders — Specification",
                "version": "4.0",
                "doc_type": "Standard",
                "clauses": [
                    {
                        "clause_number": "1.1",
                        "clause_title": "Scope",
                        "page_number": 1,
                        "text": "This standard covers the requirements for protective helmets for riders of two-wheeled motor vehicles for protection against head injuries during impact."
                    },
                    {
                        "clause_number": "4.2",
                        "clause_title": "Impact Absorption Test",
                        "page_number": 3,
                        "text": "The helmet shell and protective padding shall absorb shock such that the resultant acceleration measured at the headform does not exceed 300 g during drop test per Clause 7.2."
                    },
                    {
                        "clause_number": "5.1",
                        "clause_title": "Retention System and Chin Strap",
                        "page_number": 4,
                        "text": "The retention system chin strap shall have a width of not less than 20 mm under load. Dynamic displacement shall not exceed 35 mm under 150 N load."
                    }
                ],
                "graph": {
                    "product": "Two-Wheeler Protective Helmets",
                    "material": "Polycarbonate, Expanded Polystyrene (EPS)",
                    "industry": "Automotive Safety Equipment",
                    "scheme": "Scheme-I (Mandatory ISI Mark)",
                    "testing": "Impact Attenuation & Retention Dynamic Test",
                    "lab": "Automotive Research Association of India (ARAI)",
                    "rule": "Central Motor Vehicles Rules (CMVR) 138(4)(f)"
                }
            }
        ]

        for s in seeds:
            # 1. Check/Add to PostgreSQL
            doc = db.query(BISDocument).filter(BISDocument.standard_number == s["standard_number"]).first()
            if not doc:
                doc = BISDocument(
                    title=s["title"],
                    standard_number=s["standard_number"],
                    version=s["version"],
                    doc_type=s["doc_type"],
                    file_path=f"seed_documents/{s['standard_number'].replace(' ', '_')}.pdf",
                    page_count=len(s["clauses"]),
                    processing_status="completed"
                )
                db.add(doc)
                db.commit()
                db.refresh(doc)

                for c in s["clauses"]:
                    clause_rec = BISClause(
                        document_id=doc.id,
                        clause_number=c["clause_number"],
                        page_number=c["page_number"],
                        clause_title=c["clause_title"],
                        content=c["text"]
                    )
                    db.add(clause_rec)
                db.commit()

            # 2. ALWAYS index chunks in Elasticsearch & Qdrant
            for c in s["clauses"]:
                chunk_dict = {
                    "document_name": s["standard_number"],
                    "standard_number": s["standard_number"],
                    "clause": c["clause_number"],
                    "clause_title": c["clause_title"],
                    "page_number": c["page_number"],
                    "version": s["version"],
                    "doc_type": s["doc_type"],
                    "source": f"{s['standard_number']} (Ver {s['version']}, Page {c['page_number']})",
                    "text": c["text"]
                }
                es_id = f"{s['standard_number']}_{c['clause_number']}_{c['page_number']}"
                es.index_chunk(chunk_dict, es_id)
                qdrant.upsert_chunk(chunk_dict)

            # 3. ALWAYS sync Neo4j Knowledge Graph
            g = s["graph"]
            neo4j.sync_regulatory_chain(
                standard_number=s["standard_number"],
                product_name=g["product"],
                material=g["material"],
                industry=g["industry"],
                certification_scheme=g["scheme"],
                testing_requirement=g["testing"],
                laboratory_name=g["lab"],
                applicable_rule=g["rule"]
            )

        logger.info("Successfully synced baseline BIS standards to all knowledge stores!")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding initial BIS knowledge: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial_bis_knowledge()
