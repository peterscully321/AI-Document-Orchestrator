"""PDF generator tool."""

import os
import re
from pathlib import Path
from typing import Any, Dict, Optional
from xml.sax.saxutils import escape

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except ImportError:
    letter = None
    getSampleStyleSheet = None
    SimpleDocTemplate = None


def _format_inline_markup(text: str) -> str:
    """Convert common Markdown and simple inline LaTeX into ReportLab markup."""
    parts = re.split(r"(\$[^$\n]+\$)", text)
    formatted_parts = []
    for part in parts:
        if part.startswith("$") and part.endswith("$"):
            expression = part[1:-1].strip()
            expression = re.sub(
                r"\\(?:text|mathrm|mathbf)\{([^{}]*)\}", r"\1", expression
            )
            expression = (
                expression.replace(r"\times", "×")
                .replace(r"\cdot", "·")
                .replace(r"\le", "≤")
                .replace(r"\ge", "≥")
                .replace(r"\approx", "≈")
                .replace(r"\in", "∈")
            )
            expression = escape(expression)
            expression = re.sub(
                r"\^\{?([A-Za-z0-9+\-=]+)\}?",
                r"<super>\1</super>",
                expression,
            )
            expression = re.sub(
                r"_\{?([A-Za-z0-9+\-=]+)\}?",
                r"<sub>\1</sub>",
                expression,
            )
            formatted_parts.append(expression)
        else:
            formatted_parts.append(escape(part))

    formatted = "".join(formatted_parts).replace("`", "")
    formatted = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", formatted)
    formatted = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<i>\1</i>", formatted)
    return formatted


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
            story.append(Paragraph(escape(title), title_style))
            story.append(Spacer(1, 0.2 * inch))

        # Render common Markdown structure as document elements, escaping text
        # so characters such as '&' and '<' cannot break ReportLab's parser.
        for block in re.split(r"\n\s*\n", content.strip()):
            lines = [
                line.strip()
                for line in block.splitlines()
                if line.strip() and not re.fullmatch(r"(?:-{3,}|\*{3,}|_{3,})", line.strip())
            ]
            if not lines:
                continue
            prose_lines = []

            def flush_prose():
                if prose_lines:
                    story.append(Paragraph("<br/>".join(prose_lines), styles["Normal"]))
                    prose_lines.clear()

            for line in lines:
                heading = re.match(r"^#{1,6}\s+(.+)$", line)
                bullet = re.match(r"^[-*]\s+(.+)$", line)
                numbered = re.match(r"^(\d+)[.)]\s+(.+)$", line)
                if heading:
                    flush_prose()
                    story.append(
                        Paragraph(_format_inline_markup(heading.group(1)), styles["Heading2"])
                    )
                elif bullet or numbered:
                    flush_prose()
                    text = bullet.group(1) if bullet else numbered.group(2)
                    marker = "•" if bullet else f"{numbered.group(1)}."
                    story.append(
                        Paragraph(_format_inline_markup(text), styles["Normal"], bulletText=marker)
                    )
                else:
                    prose_lines.append(_format_inline_markup(line))
            flush_prose()
            story.append(Spacer(1, 0.1 * inch))

        # Build PDF
        doc.build(story)

        return {
            "file_path": str(file_path),
            "filename": filename,
            "size": file_path.stat().st_size,
        }

