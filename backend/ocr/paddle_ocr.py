"""
PaddleOCR integration for extracting text from PDFs and images.
"""
from paddleocr import PaddleOCR
from pathlib import Path
from typing import List, Dict, Optional
import logging
import os
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize PaddleOCR
# use_angle_cls=True enables angle classification for rotated text
# lang='en' sets English as the language
ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')


class OCRProcessor:
    """Handles OCR processing for documents."""
    
    def __init__(self):
        self.ocr = ocr_engine
    
    def process_document(self, file_path: str) -> str:
        """
        Process a document (PDF or image) and extract text.
        Uses mock data if USE_MOCK_OCR is enabled.
        
        Args:
            file_path: Path to document
            
        Returns:
            Extracted text
        """
        from config import settings
        
        # Check if mock OCR is enabled
        if settings.USE_MOCK_OCR:
            from ocr.mock_ocr_data import mock_ocr_data
            filename = Path(file_path).name
            logger.info(f"🚀 USING MOCK OCR for {filename}")
            
            # Simulate processing delay
            # time.sleep(2)
            
            return mock_ocr_data(filename)
        
        # Otherwise use real OCR
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return self.extract_text_from_image(file_path)
        else:
            logger.error(f"Unsupported file type: {extension}")
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from a single image file.
        
        Args:
            image_path: Path to image file (jpg, png, etc.)
            
        Returns:
            Extracted text as a single string
        """
        try:
            start_time = time.time()
            logger.info(f"Processing image: {image_path}")
            result = self.ocr.ocr(image_path)
            
            # Debug: Print raw result to understand what is being detected
            print(f"DEBUG: Raw OCR result for {os.path.basename(image_path)}: {result}")
            
            if not result or result[0] is None:
                logger.warning(f"No text found in {image_path}")
                return ""
            
            # Extract text from OCR result
            text_lines = []
            
            # Check for new PaddleOCR/PaddleX format (list of dicts)
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                # The log shows 'rec_texts' key contains the text lines
                if 'rec_texts' in result[0]:
                    text_lines = result[0]['rec_texts']
                    logger.info(f"Detected PaddleX format. Found {len(text_lines)} lines.")
            
            # Fallback for standard PaddleOCR format: [[[bbox], (text, confidence)], ...]
            elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                for line in result[0]:
                    if len(line) >= 2:
                        text = line[1][0]  # Get text from (text, confidence) tuple
                        text_lines.append(text)
            
            full_text = "\n".join(text_lines)
            elapsed = time.time() - start_time
            logger.info(f"[TIMING] Image OCR took {elapsed:.2f}s, extracted {len(text_lines)} lines from {image_path}")
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF by converting to images first.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text from all pages
        """
        total_start = time.time()
        try:
            from pdf2image import convert_from_path
            import tempfile
            import os
            
            logger.info(f"Processing PDF: {pdf_path}")
            
            # Convert PDF to images
            convert_start = time.time()
            with tempfile.TemporaryDirectory() as tmp_dir:
                logger.info(f"[TIMING] Converting PDF to images...")
                images = convert_from_path(pdf_path, output_folder=tmp_dir)
                convert_elapsed = time.time() - convert_start
                logger.info(f"[TIMING] PDF conversion took {convert_elapsed:.2f}s, generated {len(images)} image(s)")
                
                all_text = []
                for i, image in enumerate(images):
                    page_start = time.time()
                    # Save image temporarily
                    img_path = os.path.join(tmp_dir, f"page_{i}.jpg")
                    image.save(img_path, 'JPEG')
                    
                    # Extract text from image
                    page_text = self.extract_text_from_image(img_path)
                    page_elapsed = time.time() - page_start
                    logger.info(f"[TIMING] Page {i+1} processing took {page_elapsed:.2f}s")
                    
                    if page_text:
                        all_text.append(f"--- Page {i+1} ---\n{page_text}")
                
                full_text = "\n\n".join(all_text)
                total_elapsed = time.time() - total_start
                logger.info(f"[TIMING] Total PDF processing took {total_elapsed:.2f}s for {len(images)} page(s)")
                return full_text
                
        except Exception as e:
            error_msg = f"Error processing PDF {pdf_path}: {str(e)}"
            logger.error(error_msg)
            return ""


# Global OCR processor instance
ocr_processor = OCRProcessor()
