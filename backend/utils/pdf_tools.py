"""
PDF processing utilities.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AppealLetterPDF:
    """Generate professional appeal letter PDFs."""
    
    def __init__(self, output_path: str):
        """
        Initialize PDF generator.
        
        Args:
            output_path: Path where PDF will be saved
        """
        self.output_path = output_path
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        self.styles = getSampleStyleSheet()
        self.story = []
        
        # Create custom styles
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Create custom paragraph styles for the letter."""
        # Header style
        self.styles.add(ParagraphStyle(
            name='LetterHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor='#1a5490',
            spaceAfter=12,
            alignment=TA_CENTER
        ))
        
        # Date style
        self.styles.add(ParagraphStyle(
            name='DateStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_RIGHT
        ))
        
        # Body style
        self.styles.add(ParagraphStyle(
            name='AppealBodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Signature style
        self.styles.add(ParagraphStyle(
            name='SignatureStyle',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_LEFT
        ))
    
    def generate_appeal_letter(self, letter_content: str, patient_name: str = "Patient") -> str:
        """
        Generate PDF from appeal letter text.
        
        Args:
            letter_content: The appeal letter text
            patient_name: Patient name for the signature
            
        Returns:
            Path to generated PDF
        """
        try:
            # Add header
            header = Paragraph(
                "INSURANCE CLAIM APPEAL LETTER",
                self.styles['LetterHeader']
            )
            self.story.append(header)
            self.story.append(Spacer(1, 0.2 * inch))
            
            # Add date
            current_date = datetime.now().strftime("%B %d, %Y")
            date = Paragraph(current_date, self.styles['DateStyle'])
            self.story.append(date)
            self.story.append(Spacer(1, 0.3 * inch))
            
            # Process letter content into paragraphs
            paragraphs = letter_content.split('\n\n')
            
            for para_text in paragraphs:
                if para_text.strip():
                    # Clean up the text
                    clean_text = para_text.strip().replace('\n', ' ')
                    para = Paragraph(clean_text, self.styles['AppealBodyText'])
                    self.story.append(para)
                    self.story.append(Spacer(1, 0.1 * inch))
            
            # Add signature section
            self.story.append(Spacer(1, 0.3 * inch))
            signature_lines = [
                "Sincerely,",
                "",
                patient_name,
                "Patient/Authorized Representative"
            ]
            
            for line in signature_lines:
                sig = Paragraph(line, self.styles['SignatureStyle'])
                self.story.append(sig)
            
            # Build PDF
            self.doc.build(self.story)
            logger.info(f"Appeal letter PDF generated: {self.output_path}")
            
            return self.output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
