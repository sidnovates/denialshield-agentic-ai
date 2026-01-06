"""
Enhanced Mock OCR results for testing/development.
Returns structured dictionaries to simulate intelligent extraction.
"""

MOCK_OCR_DATA = {
    "bill": {
        "doc_type": "medical_bill",
        "raw_text": """Medical Bill
        Patient Name: Emily Davis
        Provider: Valley Care Clinic
        Date of Service: 2024-08-31
        Procedure: CT Abdomen
        CPT Code: 74160
        Amount Charged: $1775
        Billing ID: BL-314225
        Patient Insurance: BlueCross PPO
        Member ID: BCB123456789""",
        "structured": {
            "patient_name": "Emily Davis",
            "provider": "Valley Care Clinic",
            "date_of_service": "2024-08-31",
            "procedure_name": "CT Abdomen",
            "cpt_code": "74160",
            "amount_charged": "$1775.00",
            "diagnosis_code": "R10.31", 
            "doc_type": "medical_bill"
        }
    },
    
    "doctor": {
        "doc_type": "doctor_note",
        "raw_text": """VALLEY CARE CLINIC... (Full text hidden for brevity)""",
        "structured": {
            "patient_name": "Emily Davis",
            "date": "2024-08-31",
            "chief_complaint": "Severe abdominal pain, 8/10",
            "diagnosis": "Acute Appendicitis (suspected)",
            "icd_code": "K35.80",
            "history": "Pain started 24 hours ago, worsening. Nausea present.",
            "physical_exam": "Tenderness in RLQ (McBurney's point). Guarding present.",
            "plan": "CT Abdomen required to rule out appendicitis vs ovarian cyst.",
            "physician": "Dr. Sarah Johnson, MD",
            "doc_type": "doctor_note"
        }
    },
    
    "denial": {
        "doc_type": "denial_letter",
        "raw_text": """...Denial Letter Content...""",
        "structured": {
            "patient_name": "Emily Davis",
            "denial_reason": "The requested procedure (CT Abdomen) is not medically necessary according to clinical guidelines. Conservative treatment should be attempted first.",
            "denial_code": "CO-50",
            "appeal_deadline": "60 days",
            "insurer": "BlueCross BlueShield",
            "doc_type": "denial_letter",
            "procedure": "CT Abdomen",
            "date_of_service": "2024-08-31"
        }
    },
    
    "insurance": {
        "doc_type": "insurance_card",
        "raw_text": "...",
        "structured": {
           "patient_name": "Emily Davis",
           "plan": "PPO Plus",
           "group_number": "GRP-5544",
           "doc_type": "insurance_card"
        }
    }
}

def mock_ocr_data(filename: str) -> dict:
    """
    Get mock structured data based on filename.
    Returns dictionary with 'structured' key expected by agents.
    """
    filename_lower = filename.lower()
    
    if "bill" in filename_lower:
        return MOCK_OCR_DATA["bill"]
    elif "doctor" in filename_lower or "note" in filename_lower:
        return MOCK_OCR_DATA["doctor"]
    elif "denial" in filename_lower:
        return MOCK_OCR_DATA["denial"]
    elif "insurance" in filename_lower:
        return MOCK_OCR_DATA["insurance"]
    
    # Default fallback
    return MOCK_OCR_DATA["bill"]
