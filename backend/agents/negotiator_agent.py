"""
Negotiator Agent: Primary Appeal Author.
Synthesizes all outputs into a cohesive appeal letter.
"""
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import logging

from config import settings
from agents.state import ClaimState

logger = logging.getLogger(__name__)

def run_negotiator_agent(state: ClaimState) -> dict:
    logger.info("--- Negotiator Agent Running ---")
    
    medical = state.get("medical_analysis", {})
    legal = state.get("legal_analysis", {})
    ocr_data = state.get("ocr_data", {})
    feedback = state.get("audit_feedback", [])
    
    llm = ChatGroq(
        api_key=settings.GROQ_API_KEY,
        model_name="llama-3.3-70b-versatile"
    )
    
    template = """
    You are the Lead Negotiator for Medical Appeals.
    Write a final, high-impact appeal letter.
    
    CONTEXT:
    - Patient Name: {patient_name}
    - Denial Reason: {denial_reason}
    
    MEDICAL ARGUMENTS:
    {medical_args}
    
    LEGAL ARGUMENTS:
    {legal_args}
    
    AUDITOR FEEDBACK (Address these weaknesses if present):
    {feedback}
    
    INSTRUCTIONS:
    - Write a formal 1-2 page appeal letter.
    - Use a professional tone (Firm but polite).
    - Structure: Header, Case Summary, Medical Necessity (Detailed), Legal/Policy Basis, Conclusion.
    - Do NOT include placeholders like [Date] or [Address] - use real data or leave blank if unknown.
    
    OUTPUT:
    Return ONLY the full text of the letter.
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["patient_name", "denial_reason", "medical_args", "legal_args", "feedback"]
    )
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        denial = ocr_data.get("denial", {}).get("structured", {})
        patient = denial.get("patient_name", "Valued Member")
        reason = denial.get("denial_reason", "Unspecified")
        
        appeal_text = chain.invoke({
            "patient_name": patient,
            "denial_reason": reason,
            "medical_args": str(medical),
            "legal_args": str(legal),
            "feedback": str(feedback)
        })
        
        return {"appeal_draft": appeal_text, "iteration_count": state.get("iteration_count", 0) + 1}
        
    except Exception as e:
        logger.error(f"Negotiator Agent error: {e}")
        return {"appeal_draft": "Error generating appeal."}
