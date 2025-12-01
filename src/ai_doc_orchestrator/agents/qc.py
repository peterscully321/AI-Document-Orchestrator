"""Quality Check Agent - Phase 3: Iteration."""

from typing import Any, Dict

from ai_doc_orchestrator.base_agent import BaseAgent
from ai_doc_orchestrator.models import AgentMessage, Draft, QCFeedback


class QCAgent(BaseAgent):
    """Agent responsible for quality checking drafts."""

    def __init__(self, gemini_api_key=None, model: str = "gemini-2.5-flash"):
        """Initialize the QC Agent."""
        super().__init__("QCAgent", gemini_api_key, model)
        self.max_iterations = 3

    async def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process draft and provide quality check feedback.

        Args:
            message: Message containing draft

        Returns:
            Dictionary with QC feedback
        """
        draft_dict = message.data.get("draft", {})
        draft = Draft(**draft_dict)
        topic = message.data.get("topic", "")
        format_type = message.data.get("format", "")

        # Quality check prompt
        system_prompt = """You are a quality assurance expert for document review. Evaluate documents 
        for clarity, completeness, accuracy, structure, and adherence to the topic. Provide constructive 
        feedback for improvement."""
        
        user_prompt = f"""Topic: {topic}
Target Format: {format_type}
Draft Version: {draft.version}

Draft Content:
{draft.content}

Evaluate this draft and determine:
1. Is it approved for final formatting? (yes/no)
2. If not approved, what specific issues need to be addressed?
3. Provide constructive feedback for improvement.

Format your response as:
APPROVED: yes/no
ISSUES:
- [list specific issues]
FEEDBACK:
[detailed feedback]"""

        qc_response = self._call_llm(system_prompt, user_prompt, temperature=0.3)

        # Parse the response
        approved = "APPROVED: yes" in qc_response.lower() or "approved: yes" in qc_response.lower()
        
        # Extract issues
        issues = []
        if "ISSUES:" in qc_response:
            issues_section = qc_response.split("ISSUES:")[1].split("FEEDBACK:")[0]
            issues = [i.strip().lstrip("- ") for i in issues_section.split("\n") if i.strip()]

        # Extract feedback
        feedback = ""
        if "FEEDBACK:" in qc_response:
            feedback = qc_response.split("FEEDBACK:")[1].strip()
        elif not approved:
            feedback = qc_response

        # Check iteration limit
        if draft.version >= self.max_iterations:
            approved = True
            feedback = "Maximum iterations reached. Approving current draft."

        qc_feedback = QCFeedback(
            approved=approved,
            feedback=feedback if not approved else None,
            issues=issues,
        )

        return {
            "phase": "qc",
            "qc_feedback": qc_feedback.dict(),
            "status": "completed",
        }

