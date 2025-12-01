"""Data models for the AI Document Orchestrator."""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    """Supported output formats."""

    GOOGLE_DOCS = "google_docs"
    PDF = "pdf"
    TEXT = "text"


class UserInput(BaseModel):
    """User input model."""

    topic: str = Field(..., description="The topic to research and write about")
    format: OutputFormat = Field(..., description="Desired output format")


class RawData(BaseModel):
    """Raw data collected from research."""

    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of sources with content and metadata"
    )
    search_queries: List[str] = Field(
        default_factory=list, description="Search queries used"
    )


class StructuredNotes(BaseModel):
    """Structured notes from summary phase."""

    summary: str = Field(..., description="Main summary of the research")
    key_points: List[str] = Field(default_factory=list, description="Key points extracted")
    sources: List[str] = Field(default_factory=list, description="Source references")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class Draft(BaseModel):
    """Document draft."""

    content: str = Field(..., description="The draft content")
    version: int = Field(default=1, description="Draft version number")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Draft metadata"
    )


class QCFeedback(BaseModel):
    """Quality check feedback."""

    approved: bool = Field(..., description="Whether the draft is approved")
    feedback: Optional[str] = Field(
        None, description="Feedback for improvement if not approved"
    )
    issues: List[str] = Field(
        default_factory=list, description="List of specific issues found"
    )


class AgentMessage(BaseModel):
    """Message for agent-to-agent communication."""

    from_agent: str = Field(..., description="Source agent name")
    to_agent: str = Field(..., description="Target agent name")
    phase: str = Field(..., description="Current phase")
    data: Dict[str, Any] = Field(..., description="Message payload")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class FinalOutput(BaseModel):
    """Final output model."""

    format: OutputFormat = Field(..., description="Output format")
    file_path: Optional[str] = Field(None, description="Local file path if applicable")
    url: Optional[str] = Field(None, description="URL if applicable (e.g., Google Docs)")
    content: Optional[str] = Field(None, description="Content if applicable")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional output metadata"
    )

