"""PDF generator tool."""

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except ImportError:
    letter = None
    getSampleStyleSheet = None
    SimpleDocTemplate = None


class PDFGeneratorTool:
    """Tool for generating PDF files."""

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the PDF generator.

        Args:
            output_dir: Directory to save PDFs (defaults to current directory)
        """
        if SimpleDocTemplate is None:
            raise ImportError(
                "reportlab is required. Install with: pip install reportlab"
            )

        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_pdf(
        self,
        content: str,
        filename: str,
        title: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate a PDF file from content.

        Args:
            content: Text content to convert to PDF
            filename: Output filename (without .pdf extension)
            title: Optional document title

        Returns:
            Dictionary with file path and metadata
        """
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        file_path = self.output_dir / filename

        # Create PDF
        doc = SimpleDocTemplate(
            str(file_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Container for the 'Flowable' objects
        story = []
        styles = getSampleStyleSheet()

        # Add title if provided
        if title:
            title_style = styles["Heading1"]
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2 * inch))

        # Split content into paragraphs and add to story
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            if para.strip():
                # Clean up the paragraph text
                para_text = para.strip().replace("\n", "<br/>")
                story.append(Paragraph(para_text, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(story)

        return {
            "file_path": str(file_path),
            "filename": filename,
            "size": file_path.stat().st_size,
        }

