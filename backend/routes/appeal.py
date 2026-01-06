"""
Appeal letter generation endpoint.
Uses the new Multi-Agent Orchestrator.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import uuid
import json
import logging
import asyncio

from database import get_db, UploadedDocument, GeneratedAppeal
from ocr.mock_ocr_data import mock_ocr_data
from agents.orchestrator import run_appeal_workflow
from utils.pdf_generator import create_appeal_pdf
from config import settings
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
class AppealRequest(BaseModel):
    """Request model for appeal letter generation."""
    document_ids: List[int]
    insurance_plan: Optional[str] = None
    user_details: Optional[dict] = None

@router.post("/appeal-letter")
async def generate_appeal_letter(
    request: AppealRequest,
    db: Session = Depends(get_db)
):
    """
    Generate an appeal letter using Multi-Agent AI System.
    """
    try:
        session_id = str(uuid.uuid4())
        
        # 1. Retrieve & Prepare Data
        documents = db.query(UploadedDocument).filter(
            UploadedDocument.id.in_(request.document_ids)
        ).all()
        
        if not documents:
             raise HTTPException(status_code=400, detail="No documents found")

        # Aggregate data for the agents
        combined_ocr_data = {}
        for doc in documents:
            mock_data = mock_ocr_data(doc.filename)
            doc_type = mock_data.get("doc_type", "unknown")
            if "bill" in doc_type:
                combined_ocr_data["bill"] = mock_data
            elif "doctor" in doc_type:
                combined_ocr_data["doctor"] = mock_data
            elif "denial" in doc_type:
                combined_ocr_data["denial"] = mock_data
            else:
                combined_ocr_data[doc.filename] = mock_data

        # 2. Load Rules
        insurance_rules = {}
        if request.insurance_plan:
            rules_file = settings.INSURANCE_RULES_DIR / f"{request.insurance_plan.lower().replace(' ', '_')}.json"
            if rules_file.exists():
                with open(rules_file, 'r') as f:
                    insurance_rules = json.load(f)

        # 3. RUN MULTI-AGENT WORKFLOW
        # Running synchronously because LangGraph in this setup is sync, but wrapping in async handler.
        
        logger.info(f"Starting Multi-Agent Appeal for Session {session_id}")
        
        appeal_text = await asyncio.to_thread(
            run_appeal_workflow, 
            combined_ocr_data, 
            insurance_rules
        )
        
        # 4. Generate PDF (Formal Formatting)
        pdf_filename = f"appeal_letter_{session_id}.pdf"
        pdf_path = settings.UPLOAD_FOLDER / "Appeal"
        pdf_path.mkdir(parents=True, exist_ok=True)
        final_pdf_path = pdf_path / pdf_filename
        
        # Map input for pdf_generator
        # It expects {'body': text, 'subject': ...} or structured paragraphs.
        # Since agents return full text, we pass it as body.
        llm_content = {
            "subject": f"Appeal for Claim - {combined_ocr_data.get('denial', {}).get('structured', {}).get('patient_name', 'Patient')}",
            "body": appeal_text
        }
        
        # Use user details from request, or empty dict if None
        user_info = request.user_details or {}
        
        # Generate using the advanced formatter
        success, error = create_appeal_pdf(llm_content, user_info, str(final_pdf_path))
        
        if not success:
            raise Exception(f"PDF Generation Failed: {error}")
        
        # 5. Store & Return
        generated_appeal = GeneratedAppeal(
            session_id=session_id,
            appeal_text=appeal_text,
            pdf_path=str(final_pdf_path),
            denial_risk_score=0 
        )
        db.add(generated_appeal)
        db.commit()
        
        return FileResponse(
            path=str(final_pdf_path),
            filename=f"Appeal_Letter_{session_id[:8]}.pdf",
            media_type="application/pdf"
        )
            
    except Exception as e:
        logger.error(f"Error generating appeal: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
