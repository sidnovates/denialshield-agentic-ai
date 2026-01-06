"""
Llama-3-8B Extractor Model via Groq API.
Handles document classification and structured field extraction.
"""
from groq import Groq
from config import settings
import json
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)


class ExtractorLLM:
    """LLM-8B for document classification and structured extraction."""
    
    def __init__(self):
        self.client = client
        self.model = settings.EXTRACTOR_MODEL
    
    def classify_document(self, ocr_text: str) -> str:
        """
        Classify a document based on its OCR text.
        
        Args:
            ocr_text: Raw OCR extracted text
            
        Returns:
            Document type: medical_bill, eob, denial_letter, doctor_note, unknown
        """
        prompt = f"""You are a document classifier. Categorize the following medical document into one of these categories:
["medical_bill", "eob", "denial_letter", "doctor_note", "unknown"]

Return ONLY valid JSON in this exact format:
{{"type": "..."}}

Do not include any explanations or additional text.

Document text:
{ocr_text[:2000]}
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise document classifier. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=100
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info(f"Classification result: {result_text}")
            
            # Robust JSON cleanup
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            result = json.loads(result_text)
            doc_type = result.get("type", "unknown")
            
            return doc_type
            
        except Exception as e:
            logger.error(f"Error classifying document: {str(e)}")
            return "unknown"
    
    def extract_fields(self, ocr_text: str, doc_type: str) -> Dict[str, Any]:
        """
        Extract structured fields from document based on its type.
        
        Args:
            ocr_text: Raw OCR text
            doc_type: Document type (from classification)
            
        Returns:
            Dictionary of extracted fields
        """
        # Define extraction schema based on document type
        schemas = {
            "doctor_note": {
                "diagnosis": "string",
                "icd_code": "string",
                "symptoms": "string",
                "recommended_procedure": "string",
                "cpt_code": "string",
                "conservative_treatments": "string",
                "dates": "string",
                "patient_name": "string"
            },
            "medical_bill": {
                "cpt_code": "string",
                "procedure_name": "string",
                "amount_charged": "string",
                "provider": "string",
                "date_of_service": "string",
                "patient_name": "string"
            },
            "eob": {
                "amount_billed": "string",
                "allowed_amount": "string",
                "paid_amount": "string",
                "adjustment_code": "string",
                "patient_responsibility": "string",
                "date_of_service": "string",
                "patient_name": "string"
            },
            "denial_letter": {
                "patient_name": "string",
                "denial_reason": "string",
                "denial_code": "string",
                "policy_excerpt": "string",
                "missing_documentation": "string",
                "appeal_deadline": "string",
                "date_of_service": "string",
                "procedure": "string",
                "cpt_code": "string"
            }
        }
        
        schema = schemas.get(doc_type, {})
        
        if not schema:
            return {}
        
        # Build extraction prompt
        schema_str = json.dumps(schema, indent=2)
        prompt = f"""You are an information extraction model for medical documents.
Extract all relevant fields from the document text below.

Expected fields (return as JSON):
{schema_str}

Return ONLY valid JSON with the extracted values. If a field is not found, use empty string "".
Do not include any explanations.

Document text:
{ocr_text[:3000]}
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a precise medical information extractor. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info(f"Extraction complete for {doc_type}")
            
            # Robust JSON cleanup
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            extracted_fields = json.loads(result_text)
            print(f"DEBUG: Extracted Fields for {doc_type}: {json.dumps(extracted_fields, indent=2)}")
            return extracted_fields
            
        except Exception as e:
            logger.error(f"Error extracting fields: {str(e)}")
            return {}


# Global extractor instance
extractor_llm = ExtractorLLM()
