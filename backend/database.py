"""
Database models and session management using SQLAlchemy.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


class UploadedDocument(Base):
    """Model for storing uploaded document information."""
    __tablename__ = "uploaded_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)  # pdf, jpg, png
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    ocr_text = Column(Text)  # Extracted OCR text
    ocr_completed = Column(Integer, default=0)  # 0 = pending, 1 = completed


class AnalysisSession(Base):
    """Model for storing analysis session data."""
    __tablename__ = "analysis_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    insurance_plan = Column(String)
    analysis_type = Column(String)  # pre_claim, denial_explanation, appeal_letter
    document_ids = Column(JSON)  # List of document IDs used


class ExtractedData(Base):
    """Model for storing extracted structured data from documents."""
    __tablename__ = "extracted_data"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    session_id = Column(String, nullable=False)
    document_type = Column(String)  # medical_bill, eob, denial_letter, doctor_note, unknown
    extracted_fields = Column(JSON)  # Structured extracted data
    extraction_timestamp = Column(DateTime, default=datetime.utcnow)


class GeneratedAppeal(Base):
    """Model for storing generated appeal letters."""
    __tablename__ = "generated_appeals"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    appeal_text = Column(Text)
    pdf_path = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)
    denial_risk_score = Column(Float)  # 0-100 percentage


class ReasoningResult(Base):
    """Model for storing LLM reasoning outputs."""
    __tablename__ = "reasoning_results"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=False)
    reasoning_type = Column(String)  # pre_claim, denial_explanation, appeal
    input_data = Column(JSON)
    output_data = Column(JSON)
    denial_risk_score = Column(Float)
    missing_requirements = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
