"""Formatting Agent - Phase 4: Output."""

from typing import Any, Dict, Optional

from ai_doc_orchestrator.base_agent import BaseAgent
from ai_doc_orchestrator.models import AgentMessage, Draft, FinalOutput, OutputFormat
from ai_doc_orchestrator.tools.google_docs import GoogleDocsTool
from ai_doc_orchestrator.tools.pdf_generator import PDFGeneratorTool


class FormattingAgent(BaseAgent):
    """Agent responsible for formatting approved drafts into final outputs."""

    def __init__(self, gemini_api_key=None, model: str = "gemini-2.5-flash"):
        """Initialize the Formatting Agent."""
        super().__init__("FormattingAgent", gemini_api_key, model)
        self.google_docs_tool: Optional[GoogleDocsTool] = None
        self.pdf_tool: Optional[PDFGeneratorTool] = None

    def set_google_docs_tool(self, tool: GoogleDocsTool):
        """Set the Google Docs tool.

        Args:
            tool: GoogleDocsTool instance
        """
        self.google_docs_tool = tool
        self.register_tool("google_docs", tool)

    def set_pdf_tool(self, tool: PDFGeneratorTool):
        """Set the PDF generator tool.

        Args:
            tool: PDFGeneratorTool instance
        """
        self.pdf_tool = tool
        self.register_tool("pdf_generator", tool)

    async def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process approved draft and create final output.

        Args:
            message: Message containing approved draft

        Returns:
            Dictionary with final output information
        """
        draft_dict = message.data.get("draft", {})
        draft = Draft(**draft_dict)
        topic = message.data.get("topic", "")
        format_type_str = message.data.get("format", "text")
        
        try:
            format_type = OutputFormat(format_type_str)
        except ValueError:
            format_type = OutputFormat.TEXT

        # Format the content based on output type
        if format_type == OutputFormat.GOOGLE_DOCS:
            if not self.google_docs_tool:
                raise ValueError("Google Docs tool not set. Call set_google_docs_tool() first.")
            
            result = self.google_docs_tool.create_document(
                title=topic or "Document",
                content=draft.content,
            )
            
            final_output = FinalOutput(
                format=format_type,
                url=result.get("url"),
                metadata={
                    "document_id": result.get("document_id"),
                    "title": result.get("title"),
                },
            )

        elif format_type == OutputFormat.PDF:
            if not self.pdf_tool:
                raise ValueError("PDF tool not set. Call set_pdf_tool() first.")
            
            # Generate filename from topic
            filename = topic.lower().replace(" ", "_").replace("/", "_")[:50]
            result = self.pdf_tool.generate_pdf(
                content=draft.content,
                filename=filename,
                title=topic,
            )
            
            final_output = FinalOutput(
                format=format_type,
                file_path=result.get("file_path"),
                metadata={
                    "filename": result.get("filename"),
                    "size": result.get("size"),
                },
            )

        else:  # TEXT format
            final_output = FinalOutput(
                format=OutputFormat.TEXT,
                content=draft.content,
                metadata={
                    "topic": topic,
                    "version": draft.version,
                },
            )

        return {
            "phase": "formatting",
            "final_output": final_output.dict(),
            "status": "completed",
        }

