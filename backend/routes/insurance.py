"""
Insurance plans endpoint.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
import json
import logging

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/insurance-plans")
async def get_insurance_plans():
    """
    Get list of available insurance plans.
    
    Returns:
        List of insurance plan names and their details
    """
    try:
        plans = []
        rules_dir = settings.INSURANCE_RULES_DIR
        
        # Check if directory exists
        if not rules_dir.exists():
            logger.warning(f"Insurance rules directory not found: {rules_dir}")
            return {"plans": []}
        
        # Read all JSON files in the insurance rules directory
        for rules_file in rules_dir.glob("*.json"):
            try:
                with open(rules_file, 'r') as f:
                    rules_data = json.load(f)
                    
                    plan_info = {
                        "id": rules_file.stem,  # filename without extension
                        "name": rules_data.get("insurance", rules_file.stem),
                        "procedure_count": len(rules_data.get("procedure_rules", {}))
                    }
                    plans.append(plan_info)
                    
            except Exception as e:
                logger.error(f"Error reading {rules_file}: {str(e)}")
                continue
        
        logger.info(f"Found {len(plans)} insurance plans")
        
        return {
            "success": True,
            "plans": plans
        }
        
    except Exception as e:
        logger.error(f"Error retrieving insurance plans: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
