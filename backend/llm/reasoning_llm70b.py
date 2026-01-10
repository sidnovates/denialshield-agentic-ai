"""
Llama-3-70B Reasoning Model via Groq API.
Handles complex reasoning tasks: denial risk analysis, denial explanation, and appeal letter generation.
"""
from groq import Groq
from config import settings
import json
import logging
from typing import Dict, Any, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Groq client
client = Groq(api_key=settings.GROQ_API_KEY)


class ReasoningLLM:
    """LLM-70B for complex reasoning and appeal generation."""
    
    def __init__(self):
        self.client = client
        self.model = settings.REASONING_MODEL
    
    def analyze_pre_claim(
        self, 
        extracted_documents: List[Dict[str, Any]], 
        insurance_rules: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Pre-claim denial risk analysis.
        
        Args:
            extracted_documents: List of documents with extracted fields
            insurance_rules: Insurance plan rules (if available)
            
        Returns:
            Analysis result with denial risk score and missing requirements
        """
        # Prepare input data
        docs_str = json.dumps(extracted_documents, indent=2)
        rules_str = json.dumps(insurance_rules, indent=2) if insurance_rules else "No insurance rules provided"
        
        prompt = f"""You are a medical insurance pre-authorization analyst.

Compare the extracted document fields with the insurance rule JSON (if available).
Identify:
1. Missing requirements or documentation
2. Medical necessity flags
3. Denial risk percentage (0-100)

Extracted Documents:
{docs_str}

Insurance Rules:
{rules_str}

Provide a comprehensive analysis in JSON format:
{{
  "denial_risk_score": <number 0-100>,
  "missing_requirements": [<list of missing items>],
  "found_evidence": [<list of evidence found>],
  "recommendation": "<plain English recommendation>",
  "explanation": "<detailed explanation for patient>"
}}

Return ONLY valid JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a medical insurance expert providing pre-claim risk analysis."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                lines = result_text.split("\n")
                # Remove first line with ``` and last line with ```
                result_text = "\n".join(lines[1:-1])
                # Remove 'json' if it's the language identifier
                if result_text.startswith("json"):
                    result_text = result_text[4:].strip()
            
            logger.info(f"Groq response (length: {len(result_text)}): {result_text[:200]}...")
            
            # Parse JSON response
            analysis = json.loads(result_text)
            logger.info("Pre-claim analysis complete ✅")
            return analysis
            
        except Exception as e:
            logger.error(f"Error in pre-claim analysis: {str(e)}")
            return {
                "denial_risk_score": 0,
                "missing_requirements": [],
                "found_evidence": [],
                "recommendation": "Error occurred during analysis",
                "explanation": str(e)
            }
    
    def explain_denial(self, denial_data: Dict[str, Any], supporting_docs: List[Dict[str, Any]] = None, historical_context: Optional[dict] = None) -> Dict[str, Any]:
        """
        Explain a denial letter in simple English.
        
        Args:
            denial_data: Extracted denial letter fields
            supporting_docs: Other documents (doctor notes, bills) if available
            historical_context: Information on similar past denials (Memory)
            
        Returns:
            Explanation with patient-friendly language
        """
        denial_str = json.dumps(denial_data, indent=2)
        supporting_str = json.dumps(supporting_docs, indent=2) if supporting_docs else "No supporting documents"
        
        # Format Memory Context
        memory_str = ""
        if historical_context and historical_context.get("found"):
            memory_str = f"""
            PAST AI MEMORY (For Context Only - Use to improve 'next_steps'):
            - This denial pattern has happened {historical_context.get('occurrence_count')} times before.
            - Successful resolution strategy from past: {historical_context.get('suggested_solution')}
            - Commonly missing docs: {historical_context.get('common_missing_docs')}
            """
        
        prompt = f"""You are a patient advocate explaining insurance denials in simple English.

Denial Letter Information:
{denial_str}

Supporting Documents:
{supporting_str}

{memory_str}

Provide a clear explanation in JSON format:
{{
  "simple_explanation": "<easy-to-understand explanation>",
  "denial_code_meaning": "<what the denial code means>",
  "insurer_reasoning": "<why the insurer denied it>",
  "missing_documentation_identified": [<list>],
  "next_steps": "<what the patient should do>"
}}

If PAST AI MEMORY is provided, specifically mention "We have seen similar denials X times" in the 'simple_explanation' or 'next_steps' to reassure the user.

Return ONLY valid JSON.
"""
        
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a compassionate patient advocate explaining medical insurance denials."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.4,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            logger.info("Denial explanation complete")
            
            # Robust JSON cleanup
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0].strip()
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0].strip()
            
            # Parse JSON response
            explanation = json.loads(result_text)
            return explanation
            
        except Exception as e:
            logger.error(f"Error explaining denial: {str(e)}")
            logger.error(f"Failed output: {result_text if 'result_text' in locals() else 'No output'}")
            return {
                "simple_explanation": "Error occurred during explanation",
                "denial_code_meaning": "",
                "insurer_reasoning": "",
                "missing_documentation_identified": [],
                "next_steps": str(e)
            }
    
    def generate_appeal_letter(
        self, 
        denial_data: Dict[str, Any], 
        doctor_note: Dict[str, Any], 
        bill_data: Dict[str, Any],
        insurance_rules: Optional[Dict[str, Any]] = None,
        user_details: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Generate appeal letter content (Subject and Body only).
        
        Args:
            denial_data: Extracted denial letter information
            doctor_note: Extracted doctor note with medical evidence
            bill_data: Medical bill information
            insurance_rules: Insurance plan rules
            user_details: User details (not used in prompt anymore, but kept for signature compatibility if needed)
            
        Returns:
            Dict with 'subject' and 'body' keys.
        """
        denial_str = json.dumps(denial_data, indent=2)
        doctor_str = json.dumps(doctor_note, indent=2)
        bill_str = json.dumps(bill_data, indent=2)
        rules_str = json.dumps(insurance_rules, indent=2) if insurance_rules else "No insurance rules available"
        
        prompt = f"""You are a professional medical appeal specialist. 
Your task is to draft the CONTENT for a formal appeal letter using the specific structure below.
DO NOT write the header, date, recipient address, or signature.

You must return a JSON object with strictly these keys:
1. "subject": Concise formal subject line (e.g., "Appeal Against Denial of [Procedure] - Claim #[Number]").
2. "salutation": Formal salutation (e.g., "Dear Appeals Committee," or "Dear [Name],").
3. "paragraph1": Introduction. State purpose, reference decision date, and claim number.
4. "paragraph2": Explanation & Justification. Explain why decision should be reconsidered. Be factual.
5. "paragraph3": Supporting Evidence. Cite Doctor's Note, clinical findings, and attached documents.
6. "paragraph4": Request. Specifically request review and reconsideration.
7. "closing": Professional closing sentence (e.g., "Thank you for your time...").

CONTENT TO USE:
Denial Information:
{denial_str}

Doctor's Note Analysis:
{doctor_str}

Medical Bill:
{bill_str}

Insurance Rules:
{rules_str}

INSTRUCTIONS:
- Return ONLY valid JSON.
- Tone: Professional, firm, factual.
- Do NOT include "Sincerely" or the name (that is handled separately).
"""
        
        try:
            print("DEBUG: Generating Appeal Content (JSON)...") # DEBUG
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that outputs strictly JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=settings.REASONING_MODEL,
                temperature=0.1, # Low temp for structure
                response_format={"type": "json_object"}
            )
            
            response_content = chat_completion.choices[0].message.content
            print(f"DEBUG: RAW LLM OUTPUT:\n{response_content}") # DEBUG
            
            # Clean and Parse
            try:
                # Remove markdown code blocks if present
                clean_content = response_content.replace('```json', '').replace('```', '').strip()
                data = json.loads(clean_content)
                return data
            except json.JSONDecodeError:
                print("ERROR: Failed to parse JSON. Returning fallback.")
                return {
                    "subject": "Appeal Regarding Denied Claim",
                    "body": response_content # Fallback: return whole text as body
                }

        except Exception as e:
            print(f"Error in generate_appeal_letter: {e}")
            return {
                "subject": "Appeal Error",
                "body": "An error occurred while generating the appeal content."
            }


# Global reasoning LLM instance
reasoning_llm = ReasoningLLM()
