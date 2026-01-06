"""
Medical Agent: Clinical Reasoning Expert.
Establishes medical necessity using clinical evidence.
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

class ClinicalPoint(BaseModel):
    evidence: str = Field(description="Clinical fact from the notes")
    relevance: str = Field(description="Why this supports medical necessity")

class MedicalAnalysis(BaseModel):
    medical_necessity_found: bool
    clinical_justification: str = Field(description="Comprehensive narrative justification")
    key_evidence: List[ClinicalPoint]
    guideline_alignment: str = Field(description="How this aligns with standard of care")

def run_medical_agent(state: ClaimState) -> dict:
    """
    Run the Medical Agent to establish necessity.
    """
    logger.info("--- Medical Agent Running ---")
    
    ocr_data = state.get("ocr_data", {})
    
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )
    
    parser = PydanticOutputParser(pydantic_object=MedicalAnalysis)
    
    template = """
    You are a Senior Medical Appeals Specialist.
    Your goal is to prove MEDICAL NECESSITY for the denied service.
    
    Evaluate the clinical documentation provided.
    
    PATIENT DOCUMENTATION:
    {documentation}
    
    DENIAL REASON (if known):
    {denial_reason}
    
    Task:
    1. Identify the patient's condition and symptoms (Subjective/Objective).
    2. Explain why the procedure was standard of care and necessary.
    3. specificlly address why conservative treatment failed or wasn't appropriate if related to the denial.
    
    Return the analysis in valid JSON format matching this schema:
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["documentation", "denial_reason"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        # Extract relevant docs
        docs = ocr_data.get("doctor", {}).get("structured", {})
        denial = ocr_data.get("denial", {}).get("structured", {})
        
        result = chain.invoke({
            "documentation": str(docs),
            "denial_reason": denial.get("denial_reason", "Not specified")
        })
        
        logger.info(f"Medical Agent Justification: {result.medical_necessity_found}")
        return {"medical_analysis": result.dict()}
        
    except Exception as e:
        logger.error(f"Medical Agent error: {e}")
        return {"medical_analysis": None}
