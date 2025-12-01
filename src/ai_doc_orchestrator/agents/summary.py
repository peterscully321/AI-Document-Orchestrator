"""Summary Agent - Phase 2: Processing."""

from typing import Any, Dict, Optional

from ai_doc_orchestrator.base_agent import BaseAgent
from ai_doc_orchestrator.models import AgentMessage, RawData, StructuredNotes
from ai_doc_orchestrator.tools.mcp_filesystem import MCPFileSystemTool


class SummaryAgent(BaseAgent):
    """Agent responsible for summarizing raw data into structured notes."""

    def __init__(self, gemini_api_key=None, model: str = "gemini-2.5-flash"):
        """Initialize the Summary Agent."""
        super().__init__("SummaryAgent", gemini_api_key, model)
        self.fs_tool: Optional[MCPFileSystemTool] = None

    def set_filesystem_tool(self, fs_tool: MCPFileSystemTool):
        """Set the file system tool to use.

        Args:
            fs_tool: MCPFileSystemTool instance
        """
        self.fs_tool = fs_tool
        self.register_tool("read_file", fs_tool)

    async def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process raw data and create structured notes.

        Args:
            message: Message containing raw data

        Returns:
            Dictionary with structured notes
        """
        raw_data_dict = message.data.get("raw_data", {})
        raw_data = RawData(**raw_data_dict)

        # Collect all content from sources
        all_content = []
        sources_list = []
        for source in raw_data.sources:
            content = source.get("content", "")
            title = source.get("title", "")
            url = source.get("url", "")
            if content:
                all_content.append(f"Source: {title}\nURL: {url}\n\n{content}\n")
                sources_list.append(url)

        combined_content = "\n---\n\n".join(all_content)

        # Check if there are any local file references to include
        local_content = ""
        if self.fs_tool and message.data.get("local_files"):
            for file_path in message.data.get("local_files", []):
                try:
                    file_data = self.fs_tool.read_file(file_path)
                    if not file_data.get("is_binary"):
                        local_content += f"\n\nLocal File: {file_path}\n{file_data['content']}\n"
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")

        # Create structured summary
        system_prompt = """You are a summarization expert. Analyze the provided research content and create 
        a comprehensive structured summary. Extract key points and organize the information clearly. 
        Return a well-structured summary with main points and insights."""
        user_prompt = f"""Research Content:
{combined_content}
{local_content}

Create a structured summary with:
1. A comprehensive summary paragraph
2. Key points (as a bulleted list)
3. Important insights and findings"""

        summary_text = self._call_llm(system_prompt, user_prompt, temperature=0.5)

        # Extract key points using LLM
        key_points_prompt = f"""From the following summary, extract the key points as a simple list, 
        one point per line:

{summary_text}

Key points:"""
        key_points_text = self._call_llm(
            "Extract key points from text. Return only the points, one per line.",
            key_points_prompt,
            temperature=0.3,
        )
        key_points = [kp.strip() for kp in key_points_text.split("\n") if kp.strip()]

        # Create StructuredNotes
        structured_notes = StructuredNotes(
            summary=summary_text,
            key_points=key_points,
            sources=sources_list,
            metadata={
                "num_sources": len(sources_list),
                "search_queries": raw_data.search_queries,
            },
        )

        return {
            "phase": "summary",
            "structured_notes": structured_notes.dict(),
            "status": "completed",
        }

