"""
Shared state definition for the multi-agent appeal system.
"""
from typing import TypedDict, List, Dict, Any, Optional

class ClaimState(TypedDict):
    """
    Represents the state of the insurance appeal process.
    This state flows through the LangGraph nodes.
    """
    # Inputs
    ocr_data: Dict[str, Any]      # Structured data from OCR/Mock
    insurance_rules: Dict[str, Any] # Loaded insurance policy rules

    # Agent Outputs
    policy_analysis: Optional[Dict[str, Any]]
    medical_analysis: Optional[Dict[str, Any]]
    legal_analysis: Optional[Dict[str, Any]]
    simulation_result: Optional[Dict[str, Any]]

    # Negotiation
    appeal_draft: str

    # Feedback Loop
    audit_feedback: List[str]
    approval_risk_score: int  # 0-100

    # System Metadata
    iteration_count: int
    session_id: str