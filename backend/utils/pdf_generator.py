from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

def create_appeal_pdf(llm_content, user_details, output_path):
    """
    Generate a strictly formatted Appeal Letter PDF.
    
    Args:
        llm_content (dict): {'subject': str, 'body': str}
        user_details (dict): {'senderName':..., 'recipientName':...}
        output_path (str): The full path to save the PDF.
    """
    try:
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                                rightMargin=inch, leftMargin=inch,
                                topMargin=inch, bottomMargin=inch)
        
        styles = getSampleStyleSheet()
        # Custom Styles - Removed spaceBefore/spaceAfter to control manually with Spacer
        # Use 'AppealTitle' to avoid collision with default 'Title'
        styles.add(ParagraphStyle(name='AppealTitle', fontName='Helvetica-Bold', fontSize=14, leading=18, alignment=TA_CENTER, spaceAfter=12))
        styles.add(ParagraphStyle(name='HeaderBlock', fontName='Helvetica', fontSize=10, leading=12, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='RecipientBlock', fontName='Helvetica', fontSize=10, leading=12, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='DateBlock', fontName='Helvetica', fontSize=10, leading=12, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='SubjectLine', fontName='Helvetica-Bold', fontSize=11, leading=13, alignment=TA_LEFT))
        styles.add(ParagraphStyle(name='BodyJustify', fontName='Helvetica', fontSize=11, leading=13, alignment=TA_JUSTIFY))
        styles.add(ParagraphStyle(name='SignatureBlock', fontName='Helvetica', fontSize=11, leading=13, alignment=TA_LEFT))

        flowables = []
        
        # --- 0. TITLE ---
        flowables.append(Paragraph("Appeal Letter", styles['AppealTitle']))
        # Space handled by spaceAfter in title, or we can add spacer. Title usually needs more separation? 
        # User said "leave only one line between...". Let's stick to consistent 1 line.
        # But Title usually stands out. I'll leave title space as 12 (one line) effectively via Title style or manual spacer.
        # Adjusted Title spaceAfter to 12 above.
        
        # --- 1. SENDER DETAILS (Top Left) ---
        sender_lines = []
        if user_details.get('senderName'): sender_lines.append(user_details['senderName'])
        if user_details.get('senderAddress'): sender_lines.append(user_details['senderAddress'])
        if user_details.get('senderCityStateZip'): sender_lines.append(user_details['senderCityStateZip'])
        if user_details.get('senderEmail'): sender_lines.append(user_details['senderEmail'])
        if user_details.get('senderPhone'): sender_lines.append(user_details['senderPhone'])
        
        if sender_lines:
            flowables.append(Paragraph("<br/>".join(sender_lines), styles['HeaderBlock']))
            flowables.append(Spacer(1, 12))
        
        # --- 2. DATE ---
        current_date = datetime.now().strftime("%B %d, %Y")
        flowables.append(Paragraph(current_date, styles['DateBlock']))
        flowables.append(Spacer(1, 12))
        
        # --- 3. RECIPIENT DETAILS ---
        recipient_lines = []
        if user_details.get('recipientName'): recipient_lines.append(user_details['recipientName'])
        if user_details.get('recipientTitle'): recipient_lines.append(user_details['recipientTitle'])
        if user_details.get('recipientOrg'): recipient_lines.append(user_details['recipientOrg'])
        if user_details.get('recipientAddress'): recipient_lines.append(user_details['recipientAddress'])
        
        # Fallback if empty
        if not recipient_lines:
            recipient_lines = ["Insurance Company Appeals Department", "[Address Unknown]"]
            
        flowables.append(Paragraph("<br/>".join(recipient_lines), styles['RecipientBlock']))
        flowables.append(Spacer(1, 12))
        
        # --- 4. SUBJECT ---
        subject_text = llm_content.get('subject', 'Appeal Against Benefit Denial')
        if not subject_text.lower().startswith('subject:'):
            subject_text = f"Subject: {subject_text}"
        flowables.append(Paragraph(subject_text, styles['SubjectLine']))
        flowables.append(Spacer(1, 12))
        
        # --- 5. BODY (Structured) ---
        # Robust handling for structured keys from LLM
        body_keys = ['salutation', 'paragraph1', 'paragraph2', 'paragraph3', 'paragraph4', 'closing']
        
        # Check if llm_content has these keys or just 'body' (fallback)
        if 'paragraph1' in llm_content:
            for key in body_keys:
                text = llm_content.get(key, '')
                if text:
                    # Render text with Justify alignment
                    flowables.append(Paragraph(text, styles['BodyJustify']))
                    # "leave a line" -> Add Spacer
                    flowables.append(Spacer(1, 12))
        else:
            # Fallback for old 'body' format or error case
            body_text = llm_content.get('body', '')
            paragraphs = body_text.split('\n\n')
            for p in paragraphs:
                if p.strip():
                    if p.startswith("Dear") or p.endswith(":"):
                         flowables.append(Paragraph(p.strip(), styles['BodyJustify']))
                    else:
                         flowables.append(Paragraph(p.replace('\n', ' '), styles['BodyJustify']))
                    flowables.append(Spacer(1, 12))
        
        # --- 6. SIGNATURE ---
        # "Sincerely ,(in next line only name, phone and email)"
        # Removing the empty string that created the gap
        signature_lines = ["Sincerely,", user_details.get('senderName', '[Your Name]')]
        if user_details.get('senderPhone'): signature_lines.append(user_details['senderPhone'])
        if user_details.get('senderEmail'): signature_lines.append(user_details['senderEmail'])
        
        flowables.append(Paragraph("<br/>".join(signature_lines), styles['SignatureBlock']))
        
        # Build PDF
        doc.build(flowables)
        return True, None
        
    except Exception as e:
        return False, str(e)
