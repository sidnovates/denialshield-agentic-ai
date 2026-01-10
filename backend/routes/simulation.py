"""
Simulation endpoint for running counterfactual claim analysis.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import logging

from database import get_db, UploadedDocument
from ocr.mock_ocr_data import mock_ocr_data
from agents.simulator_agent import run_simulator_agent
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class SimulationRequest(BaseModel):
    """Request model for simulation."""
    document_ids: List[int]
    insurance_plan: str = None

@router.post("/simulation/run")
async def run_simulation(
    request: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Run claim outcome simulation with counterfactual analysis.
    """
    try:
        # 1. Retrieve & Prepare Data
        documents = db.query(UploadedDocument).filter(
            UploadedDocument.id.in_(request.document_ids)
        ).all()
        
        if not documents:
            raise HTTPException(status_code=400, detail="No documents found")

        # Aggregate data
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

        # 2. Run Simulator Agent
        logger.info("Running Simulator Agent for counterfactual analysis")
        
        # Create minimal state for simulator
        state = {
            "ocr_data": combined_ocr_data,
            "medical_analysis": {}  # Simulator can work with basic OCR data
        }
        
        # Run simulator
        result = run_simulator_agent(state)
        
        if not result or "simulation_result" not in result:
            raise HTTPException(
                status_code=500, 
                detail="Simulation failed to produce results"
            )

        # 3. Return Results
        return {
            "status": "success",
            "data": result["simulation_result"]
        }
            
    except Exception as e:
        logger.error(f"Error running simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
