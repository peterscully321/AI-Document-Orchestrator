"""Main entry point for the AI Document Orchestrator."""

import asyncio
import sys

from ai_doc_orchestrator.models import OutputFormat
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator


async def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python -m ai_doc_orchestrator.main <topic> [format] [local_files...]")
        print("\nFormats: text, pdf, google_docs")
        print("\nExample:")
        print("  python -m ai_doc_orchestrator.main 'Machine Learning Basics' pdf")
        sys.exit(1)

    topic = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "text"
    local_files = sys.argv[3:] if len(sys.argv) > 3 else None

    try:
        # Initialize orchestrator
        orchestrator = DocumentOrchestrator()

        # Run the workflow
        print(f"\n🚀 Starting document generation for topic: '{topic}'")
        print(f"📄 Output format: {output_format}\n")

        result = await orchestrator.run(
            topic=topic,
            output_format=output_format,
            local_files=local_files,
        )

        # Display results
        print("\n✅ Document generation completed!")
        print("\nResults:")
        print(f"  Format: {result['format']}")
        
        if result.get("file_path"):
            print(f"  File: {result['file_path']}")
        if result.get("url"):
            print(f"  URL: {result['url']}")
        if result.get("content"):
            content_preview = result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"]
            print(f"  Content preview: {content_preview}")

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

