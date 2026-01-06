"""
Policy Agent: Insurance Compliance Expert.
Analyzes extracted claim data against insurance policy rules.
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

# Define Output Structure
class PolicyFinding(BaseModel):
    issue: str = Field(description="The specific policy issue (e.g., Missing Prior Auth)")
    status: str = Field(description="VIOLATION, COMPLIANT, or WARNING")
    details: str = Field(description="Explanation of the finding")

class PolicyAnalysis(BaseModel):
    findings: List[PolicyFinding]
    prior_auth_required: bool
    policy_limit_issues: bool

def run_policy_agent(state: ClaimState) -> dict:
    """
    Run the Policy Agent to analyze compliance.
    """
    logger.info("--- Policy Agent Running ---")
    
    ocr_data = state.get("ocr_data", {})
    rules = state.get("insurance_rules", {})
    
    # Initialize LLM
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile" # Use 70B for complex rule checking
    )
    
    parser = PydanticOutputParser(pydantic_object=PolicyAnalysis)
    
    template = """
    You are an expert Insurance Policy Compliance Analyst.
    Your job is to check if a medical claim adheres to the insurance policy rules.
    
    INSURANCE RULES:
    {rules}
    
    CLAIM DATA:
    {claim_data}
    
    Analyze the claim for:
    1. Prior authorization requirements (Was it required? Was it obtained?)
    2. Policy exclusions or limits
    3. Missing documentation
    
    Return the analysis in valid JSON format matching this schema:
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["rules", "claim_data"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        # Flatten OCR data for the prompt
        claim_summary = str(ocr_data)
        rules_summary = str(rules)
        
        result = chain.invoke({
            "rules": rules_summary,
            "claim_data": claim_summary
        })
        
        logger.info(f"Policy Agent Findings: {len(result.findings)}")
        return {"policy_analysis": result.dict()}
        
    except Exception as e:
        logger.error(f"Policy Agent encountered an error: {e}")
        # Fallback empty analysis
        return {"policy_analysis": {"findings": [], "prior_auth_required": False, "policy_limit_issues": False}}
