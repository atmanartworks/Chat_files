from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

def generate_pdf_from_text(content: str, filename: str = None) -> str:
    """
    Generate a PDF file from text content.
    
    Args:
        content: The text content to convert to PDF
        filename: Optional filename. If not provided, generates a timestamped filename.
    
    Returns:
        str: Path to the generated PDF file
    """
    # Create output directory if it doesn't exist
    output_dir = "generated_pdfs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}.pdf"
    
    # Ensure .pdf extension
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    
    filepath = os.path.join(output_dir, filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1a1a1a',
        spaceAfter=30,
        alignment=TA_LEFT
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#333333',
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Split content into paragraphs
    paragraphs = content.split('\n\n')
    
    # Add title
    title = Paragraph("Generated Document", title_style)
    story.append(title)
    story.append(Spacer(1, 0.2*inch))
    
    # Add content
    for para in paragraphs:
        if para.strip():
            # Clean up the paragraph text
            para_text = para.strip()
            # Replace code blocks with plain text (remove markdown formatting)
            para_text = para_text.replace('```', '')
            # Escape special characters for ReportLab
            para_text = para_text.replace('&', '&amp;')
            para_text = para_text.replace('<', '&lt;')
            para_text = para_text.replace('>', '&gt;')
            
            p = Paragraph(para_text, body_style)
            story.append(p)
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    
    return filepath
