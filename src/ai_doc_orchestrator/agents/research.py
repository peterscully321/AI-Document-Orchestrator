"""Research Agent - Phase 1: Information Gathering."""

from typing import Any, Dict

from ai_doc_orchestrator.base_agent import BaseAgent
from ai_doc_orchestrator.models import AgentMessage, RawData
from ai_doc_orchestrator.tools.search import SearchTool


class ResearchAgent(BaseAgent):
    """Agent responsible for gathering raw data through web search."""

    def __init__(self, gemini_api_key=None, model: str = "gemini-2.5-flash"):
        """Initialize the Research Agent."""
        super().__init__("ResearchAgent", gemini_api_key, model)
        self.search_tool: SearchTool = None

    def set_search_tool(self, search_tool: SearchTool):
        """Set the search tool to use.

        Args:
            search_tool: SearchTool instance
        """
        self.search_tool = search_tool
        self.register_tool("search", search_tool)

    async def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process research request.

        Args:
            message: Message containing topic and format

        Returns:
            Dictionary with raw data collected
        """
        topic = message.data.get("topic", "")
        format_type = message.data.get("format", "")

        if not self.search_tool:
            raise ValueError("Search tool not set. Call set_search_tool() first.")

        # Generate search queries based on topic
        system_prompt = """You are a research assistant. Given a topic, generate effective search queries 
        to gather comprehensive information. Return only a list of 3-5 search queries, one per line."""
        user_prompt = f"Topic: {topic}\n\nGenerate search queries:"

        queries_text = self._call_llm(system_prompt, user_prompt, temperature=0.7)
        queries = [q.strip() for q in queries_text.split("\n") if q.strip()][:5]

        # Perform searches
        all_results = []
        for query in queries:
            try:
                results = self.search_tool.search(query, max_results=3)
                all_results.extend(results)
            except Exception as e:
                print(f"Error searching for '{query}': {e}")

        # Create RawData object
        raw_data = RawData(
            sources=all_results,
            search_queries=queries,
        )

        return {
            "phase": "research",
            "raw_data": raw_data.dict(),
            "status": "completed",
        }

