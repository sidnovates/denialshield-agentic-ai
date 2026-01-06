from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db, AnalysisSession
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple in-memory storage for the active policy context 
# In a real app, this would be tied to a specific session_id or user_id
# For this single-user Hackathon demo, a global var or file-based store is fine.
# But passing it via DB is better if we want persistence across server restarts.
# Let's use a simple file-based approach or DB. 
# Since we already have AnalysisSession table, we can mostly reuse logic, 
# but simply storing the "current_policy" in a file is easiest for "session persistence" 
# that survives server restarts without complex user auth.
# Actually, let's use a simple JSON file for "user_session_state.json" in UserData.

from config import settings
import json
import os

SESSION_FILE = settings.UPLOAD_FOLDER / "user_session_state.json"

class PolicyUpdate(BaseModel):
    policy_id: str

@router.post("/session/policy")
async def save_policy(data: PolicyUpdate):
    """Save the user's selected policy."""
    try:
        # Ensure directory exists
        if not settings.UPLOAD_FOLDER.exists():
            settings.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

        state = {}
        if SESSION_FILE.exists():
            try:
                with open(SESSION_FILE, 'r') as f:
                    state = json.load(f)
            except json.JSONDecodeError:
                state = {}
        
        state['selected_policy'] = data.policy_id
        
        with open(SESSION_FILE, 'w') as f:
            json.dump(state, f)
            
        logger.info(f"Saved policy preference: {data.policy_id}")
        return {"success": True, "policy_id": data.policy_id}
    except Exception as e:
        logger.error(f"Error saving policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/policy")
async def get_policy():
    """Get the user's saved policy."""
    try:
        if not SESSION_FILE.exists():
            return {"success": True, "policy_id": None}
            
        with open(SESSION_FILE, 'r') as f:
            state = json.load(f)
            
        return {"success": True, "policy_id": state.get('selected_policy')}
    except Exception as e:
        logger.error(f"Error retrieving policy: {e}")
        return {"success": False, "policy_id": None}
