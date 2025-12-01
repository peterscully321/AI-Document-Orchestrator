"""Main orchestrator for coordinating all agents and phases."""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from ai_doc_orchestrator.agents.formatting import FormattingAgent
from ai_doc_orchestrator.agents.qc import QCAgent
from ai_doc_orchestrator.agents.research import ResearchAgent
from ai_doc_orchestrator.agents.summary import SummaryAgent
from ai_doc_orchestrator.agents.writer import WriterAgent
from ai_doc_orchestrator.models import (
    AgentMessage,
    FinalOutput,
    OutputFormat,
    UserInput,
)
from ai_doc_orchestrator.tools.google_docs import GoogleDocsTool
from ai_doc_orchestrator.tools.mcp_filesystem import MCPFileSystemTool
from ai_doc_orchestrator.tools.pdf_generator import PDFGeneratorTool
from ai_doc_orchestrator.tools.search import SearchTool

# Load environment variables
load_dotenv()


class DocumentOrchestrator:
    """Orchestrator that coordinates all agents through the document generation workflow."""

    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        tavily_api_key: Optional[str] = None,
        google_credentials_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        """Initialize the orchestrator.

        Args:
            gemini_api_key: Google Gemini API key (defaults to GOOGLE_GEMINI_API_KEY env var)
            model: Model to use for LLM calls (default: gemini-pro)
            tavily_api_key: Tavily API key (defaults to TAVILY_API_KEY env var)
            google_credentials_path: Path to Google service account JSON
            output_dir: Directory for output files
        """
        # Get Gemini API key (strip quotes if present)
        api_key = gemini_api_key or os.getenv("GOOGLE_GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Google Gemini API key is required. Set GOOGLE_GEMINI_API_KEY env var or pass gemini_api_key parameter.")
        api_key = api_key.strip('"\'')  # Remove quotes if present
        self.model = model

        # Initialize agents with Gemini API key
        self.research_agent = ResearchAgent(gemini_api_key=api_key, model=model)
        self.summary_agent = SummaryAgent(gemini_api_key=api_key, model=model)
        self.writer_agent = WriterAgent(gemini_api_key=api_key, model=model)
        self.qc_agent = QCAgent(gemini_api_key=api_key, model=model)
        self.formatting_agent = FormattingAgent(gemini_api_key=api_key, model=model)

        # Initialize tools
        tavily_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        if tavily_key:
            tavily_key = tavily_key.strip('"\'')  # Remove quotes if present
        search_tool = SearchTool(api_key=tavily_key, provider="tavily")
        self.research_agent.set_search_tool(search_tool)

        fs_tool = MCPFileSystemTool()
        self.summary_agent.set_filesystem_tool(fs_tool)

        # Setup formatting tools
        google_creds = google_credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")
        if google_creds:
            try:
                google_docs_tool = GoogleDocsTool(credentials_path=google_creds)
                self.formatting_agent.set_google_docs_tool(google_docs_tool)
            except Exception as e:
                print(f"Warning: Could not initialize Google Docs tool: {e}")

        pdf_tool = PDFGeneratorTool(output_dir=output_dir)
        self.formatting_agent.set_pdf_tool(pdf_tool)

    async def process(self, user_input: UserInput, local_files: Optional[list] = None) -> FinalOutput:
        """Process user input through all phases.

        Args:
            user_input: User input with topic and format
            local_files: Optional list of local file paths to include

        Returns:
            FinalOutput with the generated document
        """
        # Phase 1: Information Gathering
        print("Phase 1: Information Gathering...")
        research_message = AgentMessage(
            from_agent="Orchestrator",
            to_agent="ResearchAgent",
            phase="research",
            data={
                "topic": user_input.topic,
                "format": user_input.format.value,
            },
        )
        research_result = await self.research_agent.process(research_message)
        raw_data = research_result["raw_data"]

        # Phase 2: Processing
        print("Phase 2: Processing...")
        summary_message = AgentMessage(
            from_agent="ResearchAgent",
            to_agent="SummaryAgent",
            phase="summary",
            data={
                "raw_data": raw_data,
                "local_files": local_files or [],
            },
        )
        summary_result = await self.summary_agent.process(summary_message)
        structured_notes = summary_result["structured_notes"]

        # Phase 3: Creation & Iteration (The Loop)
        print("Phase 3: Creation & Iteration...")
        draft_version = 1
        max_iterations = 3
        qc_feedback_text = ""

        while draft_version <= max_iterations:
            # Writer creates/revises draft
            writer_message = AgentMessage(
                from_agent="SummaryAgent" if draft_version == 1 else "QCAgent",
                to_agent="WriterAgent",
                phase="writing",
                data={
                    "structured_notes": structured_notes,
                    "topic": user_input.topic,
                    "format": user_input.format.value,
                    "version": draft_version,
                    "feedback": qc_feedback_text if draft_version > 1 else "",
                },
            )
            writer_result = await self.writer_agent.process(writer_message)
            draft = writer_result["draft"]

            # QC checks the draft
            qc_message = AgentMessage(
                from_agent="WriterAgent",
                to_agent="QCAgent",
                phase="qc",
                data={
                    "draft": draft,
                    "topic": user_input.topic,
                    "format": user_input.format.value,
                },
            )
            qc_result = await self.qc_agent.process(qc_message)
            qc_feedback = qc_result["qc_feedback"]

            if qc_feedback["approved"]:
                print(f"Draft approved after {draft_version} iteration(s)")
                break

            print(f"Draft version {draft_version} needs improvement. Iterating...")
            qc_feedback_text = qc_feedback.get("feedback", "")
            draft_version += 1

        # If max iterations reached, use the last draft
        if draft_version > max_iterations:
            print(f"Maximum iterations ({max_iterations}) reached. Using current draft.")

        # Phase 4: Output
        print("Phase 4: Output...")
        formatting_message = AgentMessage(
            from_agent="QCAgent",
            to_agent="FormattingAgent",
            phase="formatting",
            data={
                "draft": draft,
                "topic": user_input.topic,
                "format": user_input.format.value,
            },
        )
        formatting_result = await self.formatting_agent.process(formatting_message)
        final_output_dict = formatting_result["final_output"]

        return FinalOutput(**final_output_dict)

    async def run(
        self,
        topic: str,
        output_format: str = "text",
        local_files: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Convenience method to run the orchestrator.

        Args:
            topic: Topic to research and write about
            output_format: Output format ('text', 'pdf', or 'google_docs')
            local_files: Optional list of local file paths to include

        Returns:
            Dictionary with final output information
        """
        try:
            format_enum = OutputFormat(output_format.lower())
        except ValueError:
            format_enum = OutputFormat.TEXT

        user_input = UserInput(topic=topic, format=format_enum)
        final_output = await self.process(user_input, local_files)

        return final_output.dict()

