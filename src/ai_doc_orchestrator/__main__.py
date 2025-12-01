"""Entry point for running the package as a module."""

from ai_doc_orchestrator.main import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

