"""Vercel serverless API for the AI Document Orchestrator.

The Streamlit app remains available for local use. Vercel serves the static
frontend from ``public/`` and invokes this module for the API routes.
"""

import asyncio
import base64
import json
import os
import sys
import tempfile
import time
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from ai_doc_orchestrator.models import AgentMessage, FinalOutput, OutputFormat  # noqa: E402
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator  # noqa: E402

load_dotenv(PROJECT_ROOT / ".env")


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(body)


def _run(coroutine):
    """Run an async agent workflow inside a short-lived serverless request."""
    return asyncio.run(coroutine)


def _orchestrator(output_dir: str) -> DocumentOrchestrator:
    if not os.getenv("GOOGLE_GEMINI_API_KEY"):
        raise ValueError("GOOGLE_GEMINI_API_KEY is not configured in Vercel project settings.")
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is not configured in Vercel project settings.")
    credentials_path = None
    credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if credentials_json:
        credentials_path = Path(output_dir) / "google-credentials.json"
        credentials_path.write_text(credentials_json, encoding="utf-8")
    return DocumentOrchestrator(
        output_dir=output_dir,
        google_credentials_path=str(credentials_path) if credentials_path else None,
    )


def _serialize_output(result) -> Dict[str, Any]:
    """Return a browser-friendly representation of a FinalOutput."""
    payload: Dict[str, Any] = {
        "format": result.format.value,
        "url": result.url,
        "content": result.content,
        "metadata": result.metadata,
    }

    if result.file_path:
        file_path = Path(result.file_path)
        if file_path.exists():
            payload.update(
                {
                    "filename": file_path.name,
                    "mime_type": "application/pdf",
                    "file_data": base64.b64encode(file_path.read_bytes()).decode("ascii"),
                }
            )
    return payload


async def _generate(payload: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    topic = str(payload.get("topic", "")).strip()
    output_format = str(payload.get("format", "text")).lower()
    if not topic:
        raise ValueError("Please provide a topic.")
    if len(topic) > 240:
        raise ValueError("Topic must be 240 characters or fewer.")
    if output_format not in {item.value for item in OutputFormat}:
        raise ValueError("Format must be text, pdf, or google_docs.")

    # The full local workflow makes several sequential Gemini calls (query
    # generation, two summary calls, writing, and QC). On a Vercel request
    # that leaves the browser waiting for a long time. Keep the web path lean:
    # one Tavily search, one Gemini writing call, then local formatting.
    orchestrator = _orchestrator(output_dir)
    started_at = time.perf_counter()
    print("[generate] Research search started")
    try:
        sources = orchestrator.research_agent.search_tool.search(topic, max_results=5)
    except Exception as exc:  # noqa: BLE001 - still let the writer help if search is unavailable
        elapsed = time.perf_counter() - started_at
        print(f"[generate] Research search failed after {elapsed:.1f}s: {exc}")
        sources = []
    elapsed = time.perf_counter() - started_at
    print(f"[generate] Research search finished in {elapsed:.1f}s ({len(sources)} sources)")

    source_notes = []
    source_urls = []
    for source in sources:
        title = str(source.get("title", "")).strip()
        url = str(source.get("url", "")).strip()
        content = str(source.get("content", "")).strip()
        if title or content:
            source_notes.append(f"Source: {title}\nURL: {url}\n{content[:1400]}")
        if url:
            source_urls.append(url)

    structured_notes = {
        "summary": "\n\n".join(source_notes)
        or "No web search results were available. Use reliable general knowledge and clearly avoid inventing specific facts or citations.",
        "key_points": [str(source.get("title", "Research result")) for source in sources if source.get("title")],
        "sources": source_urls[:5],
        "metadata": {"num_sources": len(sources)},
    }
    print("[generate] Document writing started")
    writing_started_at = time.perf_counter()
    writer_result = await orchestrator.writer_agent.process(
        AgentMessage(
            from_agent="SummaryAgent",
            to_agent="WriterAgent",
            phase="writing",
            data={
                "structured_notes": structured_notes,
                "topic": topic,
                "format": output_format,
                "version": 1,
                "max_output_tokens": 2048,
            },
        )
    )
    print(f"[generate] Document writing finished in {time.perf_counter() - writing_started_at:.1f}s")

    formatting_result = await orchestrator.formatting_agent.process(
        AgentMessage(
            from_agent="WriterAgent",
            to_agent="FormattingAgent",
            phase="formatting",
            data={"draft": writer_result["draft"], "topic": topic, "format": output_format},
        )
    )
    return _serialize_output(FinalOutput(**formatting_result["final_output"]))


async def _summarize(payload: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    orchestrator = _orchestrator(output_dir)
    topic = str(payload.get("topic", "")).strip()
    content = str(payload.get("content", "")).strip()

    if not topic and not content:
        raise ValueError("Provide a research topic or content to summarize.")

    if content:
        raw_data = {
            "sources": [{"title": "Pasted content", "url": "", "content": content}],
            "search_queries": [],
        }
    else:
        research_message = AgentMessage(
            from_agent="User",
            to_agent="ResearchAgent",
            phase="research",
            data={"topic": topic, "format": "text"},
        )
        research_result = await orchestrator.research_agent.process(research_message)
        raw_data = research_result["raw_data"]

    summary_message = AgentMessage(
        from_agent="User",
        to_agent="SummaryAgent",
        phase="summary",
        data={"raw_data": raw_data, "local_files": []},
    )
    summary_result = await orchestrator.summary_agent.process(summary_message)
    return summary_result["structured_notes"]


async def _blog(payload: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    topic = str(payload.get("topic", "")).strip()
    if not topic:
        raise ValueError("Please provide a blog topic.")

    tone = str(payload.get("tone", "Professional"))
    target_length = int(payload.get("target_length", 1000))
    include_intro = bool(payload.get("include_intro", True))
    include_conclusion = bool(payload.get("include_conclusion", True))
    target_length = max(500, min(target_length, 3000))

    orchestrator = _orchestrator(output_dir)
    research_message = AgentMessage(
        from_agent="User",
        to_agent="ResearchAgent",
        phase="research",
        data={"topic": f"{topic} (Tone: {tone}, Length: {target_length} words)", "format": "text"},
    )
    research_result = await orchestrator.research_agent.process(research_message)
    summary_message = AgentMessage(
        from_agent="ResearchAgent",
        to_agent="SummaryAgent",
        phase="summary",
        data={"raw_data": research_result["raw_data"], "local_files": []},
    )
    summary_result = await orchestrator.summary_agent.process(summary_message)
    instructions = (
        f"Write a blog post about: {topic}\n"
        f"Tone: {tone}\nTarget length: {target_length} words\n"
        f"Include introduction: {include_intro}\nInclude conclusion: {include_conclusion}\n"
        "Make it engaging, well-structured, and suitable for a blog audience."
    )
    writer_message = AgentMessage(
        from_agent="SummaryAgent",
        to_agent="WriterAgent",
        phase="writing",
        data={
            "structured_notes": summary_result["structured_notes"],
            "topic": topic,
            "format": "text",
            "version": 1,
            "blog_instructions": instructions,
        },
    )
    writer_result = await orchestrator.writer_agent.process(writer_message)
    return writer_result["draft"]


class handler(BaseHTTPRequestHandler):
    """Vercel-compatible HTTP handler."""

    def _api_route(self) -> str:
        parsed = urlparse(self.path)
        route = parse_qs(parsed.query).get("route", [""])[0].strip("/")
        if route:
            return route
        return parsed.path.rstrip("/").rsplit("/", 1)[-1]

    def do_OPTIONS(self):
        _json_response(self, 204, {})

    def do_GET(self):
        if self._api_route() == "health":
            _json_response(self, 200, {"ok": True, "service": "ai-document-orchestrator"})
            return
        _json_response(self, 404, {"error": "Not found"})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            route = self._api_route()

            with tempfile.TemporaryDirectory(prefix="ai-doc-") as output_dir:
                if route == "generate":
                    result = _run(_generate(payload, output_dir))
                elif route == "summarize":
                    result = _run(_summarize(payload, output_dir))
                elif route == "blog":
                    result = _run(_blog(payload, output_dir))
                else:
                    _json_response(self, 404, {"error": "Not found"})
                    return

            _json_response(self, 200, {"ok": True, "result": result})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            _json_response(self, 400, {"ok": False, "error": str(exc)})
        except Exception as exc:  # noqa: BLE001 - return a safe user-facing API error
            _json_response(self, 500, {"ok": False, "error": str(exc)})

    def log_message(self, format: str, *args) -> None:
        """Keep Vercel logs focused on useful application output."""
        return
