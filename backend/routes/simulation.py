"""
Claim Outcome Simulation Endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
import json
import logging
import asyncio

from database import get_db, UploadedDocument
from ocr.mock_ocr_data import mock_ocr_data
from agents.orchestrator import run_appeal_workflow
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

class SimulationRequest(BaseModel):
    document_ids: List[int]
    insurance_plan: Optional[str] = None

@router.post("/simulation/run")
async def run_claim_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Run the Claim Outcome Simulator.
    Returns counterfactual analysis and approval probabilities.
    """
    try:
        # 1. Retrieve & Prepare Data (Similar to appeal generation)
        documents = db.query(UploadedDocument).filter(
            UploadedDocument.id.in_(request.document_ids)
        ).all()
        
        if not documents:
             raise HTTPException(status_code=400, detail="No documents found")

        # Aggregate data
        combined_ocr_data = {}
        for doc in documents:
            # Use mock data if real OCR is not available/reliable for this demo
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

        # 3. RUN AGENTS
        logger.info(f"Running Claim Simulation...")
        
        final_state = await asyncio.to_thread(
            run_appeal_workflow, 
            combined_ocr_data, 
            insurance_rules
        )
        
        simulation_result = final_state.get("simulation_result", {})
        
        # If simulation didn't run or failed, provide fallback or info
        if not simulation_result:
            return {
                "status": "warning",
                "message": "Simulation ran but returned no results. Check if Medical Agent succeeded.",
                "data": {}
            }
            
        return {
            "status": "success",
            "data": simulation_result
        }

    except Exception as e:
        logger.error(f"Error running simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
