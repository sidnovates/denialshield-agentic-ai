"""
Auditor Agent: Red-Team Insurance Reviewer.
Critiques the appeal and decides if it passes.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
import logging

from config import settings
from agents.state import ClaimState

logger = logging.getLogger(__name__)

class AuditResult(BaseModel):
    is_sufficient: bool = Field(description="True if the appeal is ready to send")
    risk_score: int = Field(description="0-100 likelihood of denial (lower is better)")
    weaknesses: List[str] = Field(description="List of weak points to fix")
    feedback: str = Field(description="Instructions for the negotiator")

def run_auditor_agent(state: ClaimState) -> dict:
    logger.info("--- Auditor Agent Running ---")
    
    draft = state.get("appeal_draft", "")
    iteration = state.get("iteration_count", 0)
    
    # HARD STOP: If we've looped 3 times, approve it to prevent infinite loops
    if iteration >= 3:
        logger.warning("Max iterations reached. Force approving.")
        return {
            "approval_risk_score": 50,
            "audit_feedback": ["Max iterations reached"],
            # We don't write to state indicating 'pass' explicitly here, 
            # the router loop decision will handle the '>= 3' check usually,
            # but we'll return compliant data.
        }

    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )
    
    parser = PydanticOutputParser(pydantic_object=AuditResult)
    
    template = """
    You are a Senior Insurance Medical Director (The 'Auditor').
    Your job is to REJECT appeals that are weak, vague, or emotional.
    
    REVIEW THIS APPEAL DRAFT:
    {draft}
    
    CRITERIA FOR PASSING:
    1. Explicitly references the denial reason.
    2. Cites clinical evidence (lab results, symptoms).
    3. Uses firm, non-emotional language.
    4. References policy/legal rights.
    
    Return analysis in JSON:
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["draft"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        result = chain.invoke({"draft": draft})
        
        logger.info(f"Auditor Decision: Sufficient={result.is_sufficient}, Risks={result.weaknesses}")
        
        return {
            "approval_risk_score": result.risk_score,
            "audit_feedback": result.weaknesses
        }
        
    except Exception as e:
        logger.error(f"Auditor Agent error: {e}")
        return {"approval_risk_score": 0, "audit_feedback": []}
