"""
Claim Outcome Simulator Agent.
Uses counterfactual reasoning to estimate approval probabilities.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Optional
import logging

from config import settings
from agents.state import ClaimState

logger = logging.getLogger(__name__)

class Scenario(BaseModel):
    description: str = Field(description="Description of the change (e.g., 'Add PT notes')")
    estimated_probability: int = Field(description="New approval probability (0-100)")
    reasoning: str = Field(description="Why this change improves the outcome")

class SimulationOutput(BaseModel):
    current_approval_probability: int = Field(description="Probability based on current evidence (0-100)")
    missing_evidence: List[str] = Field(description="List of critical missing documents or information")
    scenarios: List[Scenario] = Field(description="3 counterfactual scenarios improving the claim")

def run_simulator_agent(state: ClaimState) -> dict:
    """
    Run the Simulator Agent to estimate approval chances and generate improvement scenarios.
    """
    logger.info("--- Simulator Agent Running ---")
    
    ocr_data = state.get("ocr_data", {})
    medical_analysis = state.get("medical_analysis", {})
    
    # If medical analysis failed, we can't really simulate effectively, but we'll try with raw data
    medical_context = medical_analysis if medical_analysis else "Medical analysis pending or failed."
    
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )
    
    parser = PydanticOutputParser(pydantic_object=SimulationOutput)
    
    template = """
    You are a Strategic Insurance Claim Adjuster (The 'Simulator').
    Your goal is to perform COUNTERFACTUAL ANALYSIS on this denied claim.
    
    1. Estimate the CURRENT probability of approval (0-100%) based on existing evidence.
    2. Identify KEY MISSING EVIDENCE that would flip the decision.
    3. Generate 3 specific "What-If" scenarios. For example:
       - "If Physical Therapy notes from last 6 weeks were included -> 80%"
       - "If MRI report confirming stenosis is added -> 95%"
    
    CURRENT CLAIM CONTEXT:
    OCR Data: {ocr_data}
    Medical Analysis: {medical_context}
    
    Be realistic. Insurers are strict. 
    
    Return analysis in valid JSON matching this schema:
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["ocr_data", "medical_context"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        # Simplify OCR data for context window if needed, but sending full str usually works for reasonable size
        result = chain.invoke({
            "ocr_data": str(ocr_data),
            "medical_context": str(medical_context)
        })
        
        logger.info(f"Simulation Complete. Current Prob: {result.current_approval_probability}%")
        
        return {
            "simulation_result": result.dict()
        }
        
    except Exception as e:
        logger.error(f"Simulator Agent error: {e}")
        # Return empty structure on failure
        return {
            "simulation_result": {
                "current_approval_probability": 0,
                "missing_evidence": [],
                "scenarios": []
            }
        }
