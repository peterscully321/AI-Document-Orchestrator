"""Example usage of the AI Document Orchestrator."""

import asyncio
import os

from ai_doc_orchestrator.models import OutputFormat, UserInput
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator


async def example():
    """Example of using the orchestrator."""
    # Check for required API keys
    if not os.getenv("GOOGLE_GEMINI_API_KEY"):
        print("Error: GOOGLE_GEMINI_API_KEY environment variable is required")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        return

    if not os.getenv("TAVILY_API_KEY"):
        print("Warning: TAVILY_API_KEY not set. Web search may not work.")
        print("Get your API key at: https://tavily.com")

    # Initialize orchestrator
    orchestrator = DocumentOrchestrator()

    # Example 1: Generate a text document
    print("Example 1: Generating a text document about 'Python Programming'")
    user_input = UserInput(
        topic="Python Programming Basics",
        format=OutputFormat.TEXT,
    )
    
    try:
        result = await orchestrator.process(user_input)
        print(f"\n✅ Generated document (format: {result.format})")
        if result.content:
            print(f"Content preview: {result.content[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Generate a PDF
    print("\n\nExample 2: Generating a PDF about 'Machine Learning'")
    user_input = UserInput(
        topic="Introduction to Machine Learning",
        format=OutputFormat.PDF,
    )
    
    try:
        result = await orchestrator.process(user_input)
        print(f"\n✅ Generated PDF: {result.file_path}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Generate with local files
    print("\n\nExample 3: Generating with local files")
    user_input = UserInput(
        topic="Data Analysis Techniques",
        format=OutputFormat.TEXT,
    )
    
    # Note: Make sure these files exist or adjust paths
    local_files = []  # Add file paths here if needed
    
    try:
        result = await orchestrator.process(user_input, local_files=local_files)
        print(f"\n✅ Generated document with local files")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(example())

