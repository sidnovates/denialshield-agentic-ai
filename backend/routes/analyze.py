"""
Analysis endpoint for document classification, extraction, and reasoning.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
import json
import logging

from database import get_db, UploadedDocument, AnalysisSession, ExtractedData, ReasoningResult
from llm.extract_llm8b import extractor_llm
from llm.reasoning_llm70b import reasoning_llm
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request model for analysis endpoint."""
    document_ids: List[int]
    insurance_plan: Optional[str] = None
    analysis_type: str  # pre_claim, denial_explanation, appeal_letter


@router.post("/analyze")
async def analyze_documents(
    request: AnalyzeRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze uploaded documents using LLMs.
    
    1. Classify documents (LLM-8B)
    2. Extract structured fields (LLM-8B)
    3. Perform reasoning (LLM-70B)
    
    Args:
        request: Analysis request with document IDs and parameters
        db: Database session
        
    Returns:
        Analysis results with extracted data and reasoning
    """
    try:
        # Create new analysis session
        session_id = str(uuid.uuid4())
        
        # Retrieve documents from database
        documents = db.query(UploadedDocument).filter(
            UploadedDocument.id.in_(request.document_ids)
        ).all()
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found with provided IDs")
        
        # Step 1 & 2: Classify and extract fields from each document
        extracted_documents = []
        
        for doc in documents:
            if not doc.ocr_text:
                logger.warning(f"Document {doc.id} has no OCR text")
                continue
            
            # Classification Logic
            # Optimization: If file is in 'Denial' folder, force type to 'denial_letter'
            # Check for path separators specifically to avoid partial matches
            file_path_str = str(doc.file_path)
            # Standardize separators for Windows/Linux compatibility check
            norm_path = file_path_str.replace("\\", "/")
            
            if "/Denial/" in norm_path or "/UserData/Denial" in norm_path:
                doc_type = "denial_letter"
                logger.info(f"Optimization: Document {doc.id} forced as 'denial_letter' based on folder location.")
                print(f"DEBUG: Document {doc.id} ({doc.filename}) forced as: denial_letter (Location Based)")
            else:
                # LLM Classification fallback
                doc_type = extractor_llm.classify_document(doc.ocr_text)
                logger.info(f"DEBUG: Document {doc.id} ({doc.filename}) classified as: {doc_type}")
                print(f"DEBUG: Document {doc.id} ({doc.filename}) classified as: {doc_type}")
            
            # Extract fields based on type
            extracted_fields = extractor_llm.extract_fields(doc.ocr_text, doc_type)
            
            # Store extracted data
            extracted_data_record = ExtractedData(
                document_id=doc.id,
                session_id=session_id,
                document_type=doc_type,
                extracted_fields=extracted_fields
            )
            db.add(extracted_data_record)
            
            extracted_documents.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "type": doc_type,
                "fields": extracted_fields
            })
        
        db.commit()
        
        # Load insurance rules if plan is specified
        insurance_rules = None
        if request.insurance_plan:
            rules_file = settings.INSURANCE_RULES_DIR / f"{request.insurance_plan.lower().replace(' ', '_')}.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    insurance_rules = json.load(f)
                logger.info(f"Loaded insurance rules: {request.insurance_plan}")
        
        # Step 3: Reasoning based on analysis type
        reasoning_result = None
        denial_risk_score = 0
        missing_requirements = []
        
        if request.analysis_type == "pre_claim":
            # Pre-claim analysis
            reasoning_result = reasoning_llm.analyze_pre_claim(
                extracted_documents,
                insurance_rules
            )
            denial_risk_score = reasoning_result.get("denial_risk_score", 0)
            missing_requirements = reasoning_result.get("missing_requirements", [])
            
        elif request.analysis_type == "denial_explanation":
            # Find denial letter in extracted documents
            denial_doc = next(
                (d for d in extracted_documents if d["type"] == "denial_letter"),
                None
            )
            
            if not denial_doc:
                raise HTTPException(
                    status_code=400,
                    detail="No denial letter found in uploaded documents"
                )
            
            # Get supporting documents
            supporting_docs = [d for d in extracted_documents if d["type"] != "denial_letter"]
            
            print(f"DEBUG: Found Denial Letter. Extracted Fields: {json.dumps(denial_doc['fields'], indent=2)}")
            print(f"DEBUG: Sending to Reasoning Model with {len(supporting_docs)} supporting docs.")
            
            reasoning_result = reasoning_llm.explain_denial(
                denial_doc["fields"],
                supporting_docs
            )
        
        # Store reasoning result
        reasoning_record = ReasoningResult(
            session_id=session_id,
            reasoning_type=request.analysis_type,
            input_data={"documents": extracted_documents, "insurance_plan": request.insurance_plan},
            output_data=reasoning_result,
            denial_risk_score=denial_risk_score,
            missing_requirements=missing_requirements
        )
        db.add(reasoning_record)
        
        # Create analysis session record
        analysis_session = AnalysisSession(
            session_id=session_id,
            insurance_plan=request.insurance_plan,
            analysis_type=request.analysis_type,
            document_ids=request.document_ids
        )
        db.add(analysis_session)
        db.commit()
        
        logger.info(f"Analysis complete for session: {session_id}")
        
        return {
            "success": True,
            "session_id": session_id,
            "analysis_type": request.analysis_type,
            "extracted_documents": extracted_documents,
            "reasoning_result": reasoning_result,
            "denial_risk_score": denial_risk_score,
            "missing_requirements": missing_requirements
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

