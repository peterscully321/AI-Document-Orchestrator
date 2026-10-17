"""Writer Agent - Phase 3: Creation."""

from typing import Any, Dict

from ai_doc_orchestrator.base_agent import BaseAgent
from ai_doc_orchestrator.models import AgentMessage, Draft, StructuredNotes


def _is_typesetting_source(text: str) -> bool:
    """Detect when the model returned a layout language instead of document prose."""
    lowered = text.lower()
    markers = (
        "```typst",
        "#set page(",
        "#set text(",
        "#set par(",
        "#show heading",
        "locate(top",
    )
    return "```typst" in lowered or sum(marker in lowered for marker in markers[1:]) >= 2


class WriterAgent(BaseAgent):
    """Agent responsible for writing drafts from structured notes."""

    def __init__(self, gemini_api_key=None, model: str = "gemini-3.8-flash"):
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
        max_output_tokens = message.data.get("max_output_tokens")

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

        if format_type == "pdf":
            user_prompt += """

PDF OUTPUT RULES:
- Write the finished document itself in readable prose.
- Use plain text headings and simple bullets where useful.
- Never output Typst, LaTeX, HTML, PDF layout/configuration code, or code fences.
"""

        if blog_instructions:
            user_prompt += f"\n\n{blog_instructions}"
        
        if feedback:
            user_prompt += f"\n\nPrevious Feedback (for revision):\n{feedback}\n\nPlease revise the draft addressing this feedback."

        # Generate the draft
        draft_content = self._call_llm(
            system_prompt,
            user_prompt,
            temperature=0.7,
            max_output_tokens=max_output_tokens,
        )
        if format_type == "pdf" and _is_typesetting_source(draft_content):
            draft_content = self._call_llm(
                "You are an editor. Convert document-layout source into a polished, readable document.",
                f"Rewrite this as the finished document about {topic}. Keep its useful facts, but do not include source code, markup, or code fences.\n\n{draft_content}",
                temperature=0.2,
                max_output_tokens=max_output_tokens,
            )
            if _is_typesetting_source(draft_content):
                raise RuntimeError(
                    "Gemini returned PDF layout code instead of document text. Please retry once."
                )
        if not draft_content.strip():
            raise RuntimeError("Gemini returned an empty draft. Please try again with a shorter topic.")

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

