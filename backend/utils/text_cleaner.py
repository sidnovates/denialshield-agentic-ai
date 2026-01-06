"""
Text cleaning and normalization utilities for OCR output.
"""
import re
from typing import List, Dict


class TextCleaner:
    """Utilities for cleaning and normalizing OCR text."""
    
    @staticmethod
    def clean_ocr_text(text: str) -> str:
        """
        Clean OCR text by removing artifacts and normalizing spacing.
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that are OCR artifacts
        text = re.sub(r'[|╔╗╚╝═║]', '', text)
        
        # Fix common OCR mistakes
        text = text.replace('$', 'S')  # Sometimes $ is confused with S
        
        # Normalize line breaks
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        return text.strip()
    
    @staticmethod
    def extract_cpt_codes(text: str) -> List[str]:
        """
        Extract CPT codes from text.
        CPT codes are typically 5-digit numbers.
        
        Args:
            text: Text containing CPT codes
            
        Returns:
            List of found CPT codes
        """
        # CPT codes are 5-digit numbers, often preceded by "CPT" or similar
        pattern = r'\b\d{5}\b'
        codes = re.findall(pattern, text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_codes = []
        for code in codes:
            if code not in seen:
                seen.add(code)
                unique_codes.append(code)
        
        return unique_codes
    
    @staticmethod
    def extract_icd_codes(text: str) -> List[str]:
        """
        Extract ICD-10 codes from text.
        ICD-10 codes follow pattern: Letter + 2 digits + optional decimal + more digits
        
        Args:
            text: Text containing ICD codes
            
        Returns:
            List of found ICD codes
        """
        # ICD-10 pattern: A00-Z99 with optional decimal point and digits
        pattern = r'\b[A-Z]\d{2}(?:\.\d{1,4})?\b'
        codes = re.findall(pattern, text)
        
        # Remove duplicates
        return list(set(codes))
    
    @staticmethod
    def extract_denial_codes(text: str) -> List[str]:
        """
        Extract common denial codes (CO-##, PR-##, OA-##).
        
        Args:
            text: Text containing denial codes
            
        Returns:
            List of found denial codes
        """
        # Common denial code patterns
        pattern = r'\b(?:CO|PR|OA|CR|PI|MA)-?\s*\d{1,3}\b'
        codes = re.findall(pattern, text, re.IGNORECASE)
        
        # Normalize format (uppercase, with hyphen)
        normalized = []
        for code in codes:
            code = code.upper().replace(' ', '')
            if '-' not in code:
                # Add hyphen if missing
                code = re.sub(r'([A-Z]+)(\d+)', r'\1-\2', code)
            normalized.append(code)
        
        return list(set(normalized))
    
    @staticmethod
    def extract_currency_amounts(text: str) -> List[str]:
        """
        Extract currency amounts from text.
        
        Args:
            text: Text containing dollar amounts
            
        Returns:
            List of found amounts
        """
        # Pattern for currency: $1,234.56 or 1,234.56 or $1234.56
        pattern = r'\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        amounts = re.findall(pattern, text)
        
        # Clean up amounts
        cleaned = []
        for amount in amounts:
            amount = amount.strip().replace(' ', '')
            if amount:
                cleaned.append(amount)
        
        return cleaned
    
    @staticmethod
    def extract_dates(text: str) -> List[str]:
        """
        Extract dates from text in various formats.
        
        Args:
            text: Text containing dates
            
        Returns:
            List of found dates
        """
        # Common date patterns
        patterns = [
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # MM/DD/YYYY or M/D/YY
            r'\b\d{1,2}-\d{1,2}-\d{2,4}\b',  # MM-DD-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
        ]
        
        dates = []
        for pattern in patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(found)
        
        return list(set(dates))


# Global text cleaner instance
text_cleaner = TextCleaner()
