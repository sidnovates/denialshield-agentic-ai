"""
Legal Agent: Insurance Appeals Specialist.
Converts policy + medical findings into appeal-ready legal arguments.
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

class LegalArgument(BaseModel):
    title: str
    argument_text: str = Field(description="The core argument paragraph")
    citation: str = Field(description="Policy section or legal precedent if applicable")

class LegalAnalysis(BaseModel):
    statutory_basis: str = Field(description="Relevant laws (e.g., ERISA, ACA)")
    arguments: List[LegalArgument]
    procedural_errors: List[str] = Field(description="Did the insurer miss deadlines?")

def run_legal_agent(state: ClaimState) -> dict:
    logger.info("--- Legal Agent Running ---")
    
    policy_analysis = state.get("policy_analysis", {})
    medical_analysis = state.get("medical_analysis", {})
    ocr_data = state.get("ocr_data", {})
    
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )
    
    parser = PydanticOutputParser(pydantic_object=LegalAnalysis)
    
    template = """
    You are an Attorney specializing in Healthcare Denials.
    Frame the legal arguments for an appeal based on the medical and policy analysis.
    
    MEDICAL EVIDENCE:
    {medical_analysis}
    
    POLICY ANALYSIS:
    {policy_analysis}
    
    DENIAL INFO:
    {denial_info}
    
    Task:
    1. Frame the argument using professional, firm legal language.
    2. Cite "Standard of Care" obligations.
    3. If denial was "Medical Necessity", argue that the insurer is interfering with clinical judgment.
    
    Return JSON:
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["medical_analysis", "policy_analysis", "denial_info"],
        partial_variables={"format_instructions": parser.get_format_instructions()}
    )
    
    chain = prompt | llm | parser
    
    try:
        denial = ocr_data.get("denial", {}).get("structured", {})
        
        result = chain.invoke({
            "medical_analysis": str(medical_analysis),
            "policy_analysis": str(policy_analysis),
            "denial_info": str(denial)
        })
        
        return {"legal_analysis": result.dict()}
        
    except Exception as e:
        logger.error(f"Legal Agent error: {e}")
        return {"legal_analysis": None}
