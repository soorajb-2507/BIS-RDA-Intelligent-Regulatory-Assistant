from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .connection import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    role = Column(String(50), default="officer")  # officer, auditor, public
    created_at = Column(DateTime, default=datetime.utcnow)

class BISDocument(Base):
    __tablename__ = "bis_documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    standard_number = Column(String(100), index=True, nullable=False)
    doc_type = Column(String(100), default="Standard")  # Standard, Scheme, Guideline, Lab, Update
    version = Column(String(50), default="1.0")
    file_path = Column(String(500), nullable=False)
    page_count = Column(Integer, default=0)
    is_scanned = Column(Boolean, default=False)
    processing_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    doc_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    clauses = relationship("BISClause", back_populates="document", cascade="all, delete-orphan")

class BISClause(Base):
    __tablename__ = "bis_clauses"
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("bis_documents.id"))
    clause_number = Column(String(100), index=True, nullable=False)
    page_number = Column(Integer, nullable=False)
    clause_title = Column(String(255))
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("BISDocument", back_populates="clauses")

class CertificationScheme(Base):
    __tablename__ = "certification_schemes"
    id = Column(Integer, primary_key=True, index=True)
    scheme_code = Column(String(100), unique=True, index=True)  # e.g., Scheme-I (ISI Mark), Scheme-II (CRS)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    applicable_products = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

class BISLaboratory(Base):
    __tablename__ = "bis_laboratories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    accreditation_number = Column(String(100), index=True)
    tested_standards = Column(JSON, default=list)  # List of IS standards covered
    contact_info = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

class StandardUpdate(Base):
    __tablename__ = "standard_updates"
    id = Column(Integer, primary_key=True, index=True)
    standard_number = Column(String(100), index=True, nullable=False)
    old_version = Column(String(50))
    new_version = Column(String(50), nullable=False)
    effective_date = Column(DateTime)
    summary_of_changes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryAudit(Base):
    __tablename__ = "query_audits"
    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    language = Column(String(10), default="en")
    intent = Column(String(100))
    entities = Column(JSON, default=list)
    verified = Column(Boolean, default=False)
    confidence_score = Column(Float, default=0.0)
    response_json = Column(JSON, default=dict)
    verification_info = Column(JSON, default=dict)
    user_feedback = Column(String(50), nullable=True)  # helpful, unhelpful, incorrect
    created_at = Column(DateTime, default=datetime.utcnow)
