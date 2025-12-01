"""Base agent class for all agents in the system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from ai_doc_orchestrator.models import AgentMessage


class BaseAgent(ABC):
    """Base class for all agents."""

    def __init__(
        self,
        name: str,
        gemini_api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
    ):
        """Initialize the agent.

        Args:
            name: Agent name
            gemini_api_key: Google Gemini API key (creates new client if None)
            model: Model to use for LLM calls (default: gemini-pro)
        """
        if genai is None:
            raise ImportError(
                "google-generativeai is required. Install with: pip install google-generativeai"
            )
        
        self.name = name
        self.model = model
        
        # Configure Gemini API
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
        else:
            import os
            api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
            if not api_key:
                raise ValueError("Google Gemini API key is required. Set GOOGLE_GEMINI_API_KEY env var or pass gemini_api_key parameter.")
            genai.configure(api_key=api_key)
        
        self.tools: Dict[str, Any] = {}

    def register_tool(self, name: str, tool: Any):
        """Register a tool for this agent to use.

        Args:
            name: Tool name
            tool: Tool instance
        """
        self.tools[name] = tool

    def send_message(
        self, to_agent: str, phase: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        """Send a message to another agent (A2A handoff).

        Args:
            to_agent: Target agent name
            phase: Current phase
            data: Message payload
            metadata: Optional metadata

        Returns:
            AgentMessage instance
        """
        return AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            phase=phase,
            data=data,
            metadata=metadata or {},
        )

    @abstractmethod
    async def process(self, message: AgentMessage) -> Dict[str, Any]:
        """Process a message and return results.

        Args:
            message: Incoming agent message

        Returns:
            Dictionary with processing results
        """
        pass

    def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
    ) -> str:
        """Call the LLM with given prompts.

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature for generation

        Returns:
            LLM response text
        """
        # Combine system and user prompts for Gemini
        # Gemini doesn't have separate system messages, so we combine them
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        # Create the model instance (use full model name if not already prefixed)
        model_name = self.model if self.model.startswith("models/") else f"models/{self.model}"
        model = genai.GenerativeModel(model_name)
        
        # Generate content with temperature
        generation_config = {
            "temperature": temperature,
        }
        
        response = model.generate_content(
            full_prompt,
            generation_config=generation_config,
        )
        
        return response.text or ""

