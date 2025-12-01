# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository status

- This repository currently contains only high-level design documentation in `README.md` and no implementation code or tooling configuration yet.
- The target implementation language for this project is **Python**; agent and tool interfaces are expected to be defined in a Python package structure once implementation begins.

## Architecture overview (from README)

The project is an AI multi-agent orchestration system that takes a **user input topic and output format**, performs web research, organizes the information, and generates high-quality documents (e.g., Google Docs and PDFs) through an iterative quality loop.

High-level flow (phases):

1. **Phase 1 – Information Gathering**
   - The **Orchestrator Agent** receives the user's topic and target format and hands off to a **Research Agent** (A2A handoff).
   - The Research Agent uses external search tools (e.g., Google Search / Tavily) to gather **raw data**.

2. **Phase 2 – Processing**
   - A **Summary Agent** digests the raw data into concise summaries.
   - The Summary Agent can use an MCP file-system read tool to incorporate local references.
   - Output of this phase is a set of **structured notes** that serve as the canonical internal representation.

3. **Phase 3 – Creation & Iteration**
   - A **Writer Agent** transforms structured notes into an initial long-form draft.
   - A **Quality Check (QC) Agent** reviews drafts and either:
     - Sends feedback back to the Writer for another iteration, or
     - Approves the draft for final formatting.

4. **Phase 4 – Output**
   - A **Formatting Agent** converts approved drafts into final user-facing deliverables.
   - Planned integrations:
     - Google Docs API for collaborative documents.
     - A PDF generator for downloadable files.

The system is thus organized around clear agent responsibilities and tool integrations, with the Orchestrator coordinating agent-to-agent handoffs and the QC loop ensuring quality before final output.

## Commands and development workflow

At the time this file was written:

- There is **no implementation code** (no Python modules or packages) and **no build/test/lint tooling** configured yet (no `pyproject.toml`, `requirements.txt`, `Makefile`, etc.).
- As a result, there are **no concrete commands yet** for building, linting, or running tests.

When the Python implementation is added, future Warp agents should:

1. **Discover Python tooling**
   - Inspect the repo for Python tooling files (e.g., `pyproject.toml`, `requirements.txt`, `Pipfile`, `setup.cfg`, `Makefile`, `Dockerfile`, CI configs) and update this section with the actual build, lint, and test commands.

2. **Document core commands here** (examples of what to capture once they exist):
   - How to run the main orchestrator/service (e.g., the primary `python -m` entrypoint or CLI script).
   - How to run the full Python test suite (e.g., `pytest`, `unittest`, or other) and a single test.
   - How to run linting/formatting and type checks (e.g., `ruff`, `flake8`, `black`, `isort`, `mypy`, or project-specific tools).

## Guidance for future Warp updates

When this repository gains a concrete Python implementation:

- **Update the Architecture section** with:
  - The Python stack used (e.g., standard library + specific orchestration/LLM libraries) and any framework choices.
  - How agents are represented in code (e.g., Python classes or functions in modules such as `orchestrator`, `agents.research`, `agents.summary`, `agents.writer`, `agents.qc`, `agents.formatting`) and how A2A handoffs are implemented.
  - Where tool integrations live (e.g., modules implementing Google Search/Tavily, MCP FS read, Google Docs API, and PDF generation).
- **Add a "File/Module layout" subsection** only for the top-level structure, for example:
  - `src/ai_doc_orchestrator/` (or similar package root)
    - `orchestrator/`
    - `agents/` (`research`, `summary`, `writer`, `qc`, `formatting`)
    - `tools/` (search, MCP FS, Google Docs, PDF)
  - `tests/` (organized to mirror the package structure).
- **Fill in concrete Python commands** for build, lint, tests, and running the orchestrator once these are standardized in the project.

This WARP.md is intentionally minimal and should be treated as a living document: keep it in sync with the evolving Python architecture and tooling of the AI Document Orchestrator.
