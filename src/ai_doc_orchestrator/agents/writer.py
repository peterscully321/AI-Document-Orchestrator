"""Writer Agent - Phase 3: Creation."""

from typing import Any, Dict

from ai_doc_orchestrator.base_agent import BaseAgent
from ai_doc_orchestrator.models import AgentMessage, Draft, StructuredNotes


class WriterAgent(BaseAgent):
    """Agent responsible for writing drafts from structured notes."""

    def __init__(self, gemini_api_key=None, model: str = "gemini-2.5-flash"):
        """Initialize the Writer Agent."""
        super().__init__("WriterAgent", gemini_api_key, model)

    async def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process structured notes and create a draft.

        Args:
            message: Message containing structured notes and optional feedback

        Returns:
            Dictionary with draft content
        """
        structured_notes_dict = message.data.get("structured_notes", {})
        structured_notes = StructuredNotes(**structured_notes_dict)
        topic = message.data.get("topic", "")
        format_type = message.data.get("format", "")
        feedback = message.data.get("feedback", "")
        version = message.data.get("version", 1)
        blog_instructions = message.data.get("blog_instructions", "")

        # Build the writing prompt
        if blog_instructions:
            # Blog writing mode
            system_prompt = """You are an expert blog writer. Create engaging, well-structured blog posts 
            based on research notes. Write in an engaging style with proper formatting, headings, and 
            organization suitable for blog readers."""
        else:
            # Document writing mode
            system_prompt = """You are an expert technical writer. Create well-structured, comprehensive 
            documents based on research notes. Write in a clear, professional style with proper formatting, 
            headings, and organization."""
        
        user_prompt = f"""Topic: {topic}
Target Format: {format_type}

Structured Notes:
Summary: {structured_notes.summary}

Key Points:
{chr(10).join(f'- {kp}' for kp in structured_notes.key_points)}

Sources: {', '.join(structured_notes.sources[:5])}
"""

        if blog_instructions:
            user_prompt += f"\n\n{blog_instructions}"
        
        if feedback:
            user_prompt += f"\n\nPrevious Feedback (for revision):\n{feedback}\n\nPlease revise the draft addressing this feedback."

        # Generate the draft
        draft_content = self._call_llm(system_prompt, user_prompt, temperature=0.7)

        # Create Draft object
        draft = Draft(
            content=draft_content,
            version=version,
            metadata={
                "topic": topic,
                "format": format_type,
                "num_key_points": len(structured_notes.key_points),
            },
        )

        return {
            "phase": "writing",
            "draft": draft.dict(),
            "status": "completed",
        }

