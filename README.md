# BIS Regulatory & Standards AI Question Answering System

An enterprise-grade, full-stack AI application for **Bureau of Indian Standards (BIS)** Question Answering, Regulatory Reasoning, and Evidence Verification based on the **10-Stage Regulatory Decision Architecture (RDA)** methodology.

---

## Architecture Overview

```
BIS Data Ingestion (PDFs / Scanned Standards)
        ↓
Document Processing (PyMuPDF + PaddleOCR)
        ↓
Knowledge Base Creation (PostgreSQL + Neo4j + Elasticsearch + Qdrant)
        ↓
User Query (Text / Voice / Document in English & Indian Languages)
        ↓
IndicBERT NLP (Multilingual Intent & Entity Extraction)
        ↓
RDA Engine (Regulatory DNA Orchestrator)
        ↓
Hybrid Retrieval (Elasticsearch [Lexical] + Qdrant [Vector] + Neo4j [Graph])
        ↓
AI Reasoning (LlamaIndex + Ollama [Qwen/Llama])
        ↓
Evidence Verification (Clause, Page, Version & Source Grounding)
        ↓
Final Output (Next.js Dashboard with Clauses & Source Links)
        ↓
Continuous Regulatory Learning & Knowledge Improvement
        ↓
RDA Engine
```

---

## Technology Stack Mapping

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | **Next.js 14, TypeScript, Tailwind CSS** | Professional dashboard with text/voice/document queries, multi-language Indian support, evidence badges, and audit history. |
| **Backend** | **Python, FastAPI** | High-performance modular API server connecting all layers. |
| **Document Processing** | **PyMuPDF (fitz) + PaddleOCR** | PyMuPDF extracts text, pages, and metadata. Scanned/image pages automatically trigger PaddleOCR fallback. |
| **Relational Database** | **PostgreSQL** | Stores structured metadata, documents, versions, clauses, labs, schemes, audits, and verification records. |
| **Knowledge Graph** | **Neo4j** | Models the 8-node regulatory chain: `Standard -> Product -> Material -> Industry -> Certification -> Testing -> Laboratory -> Applicable Rule`. |
| **Lexical Search** | **Elasticsearch** | Lexical & keyword search for exact standards (`IS 10500`), clause numbers, and regulatory terminology. |
| **Vector Search** | **Qdrant** | Semantic vector search using chunk embeddings for conceptual matching. |
| **Multilingual NLP** | **IndicBERT (`ai4bharat/indic-bert`)** | Understands Indian languages (Hindi, Tamil, Telugu, Bengali, Marathi, etc.), extracts intent and products. |
| **Local LLM** | **Ollama (`qwen2.5:7b-instruct` / `llama3`)** | Local LLM inference for evidence-grounded regulatory reasoning (zero external API calls). |
| **RAG Orchestrator** | **LlamaIndex** | Orchestrates context construction and strictly grounded zero-hallucination prompts. |
| **Orchestration** | **Docker & Docker Compose** | Multi-container deployment for all 7 services. |

---

## Quickstart with Docker Compose

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Launch All Services
```bash
docker-compose up --build
```

### 3. Access Services
- **Next.js Frontend:** [http://localhost:3000](http://localhost:3000)
- **FastAPI API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Neo4j Browser:** [http://localhost:7474](http://localhost:7474) (Auth: `neo4j` / `bis_neo4j_password`)
- **Elasticsearch:** [http://localhost:9200](http://localhost:9200)
- **Qdrant Dashboard:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)
- **Ollama:** [http://localhost:11434](http://localhost:11434)

---

## 23-Step End-to-End Automated Pipeline Test

Run the comprehensive validation test verifying all 23 pipeline stages:

```bash
cd backend
python test_end_to_end.py
```

This validates:
1. Backend service health & knowledge stores.
2. PostgreSQL, Elasticsearch, Qdrant, and Neo4j seed population.
3. IndicBERT multilingual query understanding (English, Hindi, Tamil).
4. Hybrid retrieval fusion across ES, Qdrant, and Neo4j.
5. RDA Engine reasoning and evidence-only answering.
6. Evidence verification engine (clause, page, and version grounding).
7. Negative test: Grounded refusal (`"Insufficient verified BIS evidence was found..."`) for unsupported queries.
