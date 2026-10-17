# 🤖 AI Document Orchestrator

> A powerful multi-agent system that transforms topics into professional documents through intelligent research, writing, and iterative quality checking.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/peterscully321/AI-Document-Orchestrator?style=social)](https://github.com/peterscully321/AI-Document-Orchestrator)
![Repo size](https://img.shields.io/github/repo-size/peterscully321/AI-Document-Orchestrator)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)

**📖 [Documentation](https://github.com/peterscully321/AI-Document-Orchestrator/wiki)** · **🚀 [Quick Start](#-quick-start)** · **📝 [API Setup](#-api-setup)** · **🐛 [Report Bug](https://github.com/peterscully321/AI-Document-Orchestrator/issues)**

---

## ✨ Features

- 🔍 **Intelligent Research** — Automated web search using Tavily
- 📝 **Smart Summarization** — Extract structured insights
- ✍️ **Content Writing** — Produces high-quality documents
- ✅ **Quality Assurance** — Iterative feedback loop
- 📄 **Multiple Formats** — PDF, Google Docs, or text
- 🎨 **Interactive UI** — Streamlit interface
- 🔄 **Agent Communication** — A2A protocol
- ⚡ **Async Processing** — Non-blocking operations
- 🔐 **Secure API Integration** — Environment variables only

---

## 🧭 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [🏗️ Architecture](#-architecture)
- [📦 Installation Details](#-installation-details)
- [🔑 API Setup](#-api-setup)
- [💻 Usage](#-usage)
- [🔄 Detailed Workflow](#-detailed-workflow)
- [🛠️ Development](#-development)
- [📖 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📝 License](#-license)
- [📞 Support](#-support)
- [🙏 Acknowledgments](#-acknowledgments)

---

## 🚀 Quick Start

### Prerequisites
- Python **3.10+**
- `pip`
- API keys: **Google Gemini** + **Tavily**

### Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/peterscully321/AI-Document-Orchestrator.git
cd AI-Document-Orchestrator

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Launch Interactive UI

```bash
# Windows
run_ui.bat

# Linux/Mac
./run_ui.sh

# Or directly
streamlit run app.py
```

Open: **[http://localhost:8501](http://localhost:8501)**

### Deploy the Vercel UI

Vercel cannot run Streamlit's long-lived server directly, so this repository includes a Vercel-ready web UI and Python serverless API. The original Streamlit app remains available for local use.

1. Push this repository to GitHub and import it into Vercel.
2. Add these Project Environment Variables in Vercel:

   ```env
   GOOGLE_GEMINI_API_KEY=your_key_here
   TAVILY_API_KEY=your_key_here
   # Optional: minified service-account JSON for the Google Docs output
   GOOGLE_CREDENTIALS_JSON={"type":"service_account", ...}
   ```

3. Deploy with the default project settings. Vercel serves `public/index.html` and routes `/api/generate`, `/api/summarize`, and `/api/blog` to the Python function in `api/index.py`.
4. Keep serverless dependencies scoped to `api/requirements.txt` (instead of root `requirements.txt`) so the Vercel Python function bundle stays under the 500 MB limit.

The PDF workflow returns the generated file directly to the browser, which keeps it compatible with Vercel's ephemeral serverless filesystem. Google Docs output requires the optional `GOOGLE_CREDENTIALS_JSON` service-account secret.

### Command Line Usage

```bash
python -m ai_doc_orchestrator.main "Machine Learning Basics" pdf
python -m ai_doc_orchestrator.main "AI Ethics" google_docs
python -m ai_doc_orchestrator.main "Your Topic Here" text
```

---

## 🏗️ Architecture

### High-Level Overview

```text
User Input → Research → Summarize → Write + QC → Format → Final Document
```

### Components

| Phase         | Agent             | Purpose                   | Tools                      |
| ------------- | ----------------- | ------------------------- | -------------------------- |
| 1️⃣ Research  | Research Agent    | Web data gathering        | Tavily API                 |
| 2️⃣ Summarize | Summary Agent     | Structure information     | MCP File System            |
| 3️⃣ Write/QC  | Writer + QC Agent | Generate & review content | Feedback loop              |
| 4️⃣ Format    | Formatting Agent  | PDF/Text/Google Docs      | ReportLab, Google Docs API |

---

## 📦 Installation Details

### Step 1 — Clone Repository

```bash
git clone https://github.com/peterscully321/AI-Document-Orchestrator.git
cd AI-Document-Orchestrator
```

### Step 2 — Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
```

### Step 3 — Install Requirements

```bash
pip install -r requirements.txt
```

### Step 4 — Environment Variables

Create a `.env` file:

```env
GOOGLE_GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Optional (Google Docs)
GOOGLE_CREDENTIALS_PATH=/path/to/service-account.json

OUTPUT_DIR=./output
```

---

## 🔑 API Setup

### Google Gemini API (Required)

Get your key:
[https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)

Add to `.env`:

```env
GOOGLE_GEMINI_API_KEY=your_key_here
```

### Tavily API (Required)

Get your key:
[https://tavily.com](https://tavily.com)

```env
TAVILY_API_KEY=your_key_here
```

### Google Docs API (Optional)

Requires Service Account JSON.

```env
GOOGLE_CREDENTIALS_PATH=C:\path\to\credentials.json
```

---

## 💻 Usage

### Web UI

```bash
run_ui.bat          # Windows
./run_ui.sh         # Linux/Mac
streamlit run app.py
```

### CLI

```bash
python -m ai_doc_orchestrator.main "Machine Learning Ethics" pdf
```

### Python API

```python
import asyncio
from ai_doc_orchestrator.models import UserInput, OutputFormat
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator

async def main():
    orchestrator = DocumentOrchestrator(
        gemini_api_key="your_key",
        tavily_api_key="your_key"
    )

    user_input = UserInput(topic="ML Basics", format=OutputFormat.PDF)

    result = await orchestrator.process(user_input)
    print("Generated:", result.file_path)

asyncio.run(main())
```

---

## 🔄 Detailed Workflow

1. **User Input** → Topic + format
2. **Research Agent** → Tavily search
3. **Summary Agent** → Extract structure
4. **Writer Agent** → Generate draft
5. **QC Agent** → Review & iterate
6. **Formatting Agent** → PDF/Text/Google Docs

---

## 🛠️ Development

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio black ruff mypy
```

### Tests

```bash
pytest -v
```

### Linting & Formatting

```bash
black src/
ruff check src/
mypy src/
```

---

## 📖 Documentation

- **Quick Start:** `QUICK_START.md`
- **API Setup:** `API_SETUP.md`
- **UI Guide:** `README_UI.md`
- **WARP Guide:** `WARP.md`

---

## 🤝 Contributing

1. Fork repo
2. Create branch
3. Commit changes
4. Push
5. Open PR

---

## 📝 License

MIT License — see `LICENSE`

---

## 📞 Support

- Issues: [https://github.com/peterscully321/AI-Document-Orchestrator/issues](https://github.com/peterscully321/AI-Document-Orchestrator/issues)
- Wiki: [https://github.com/peterscully321/AI-Document-Orchestrator/wiki](https://github.com/peterscully321/AI-Document-Orchestrator/wiki)

---

## 🙏 Acknowledgments

- Google Generative AI
- Tavily
- Streamlit
- Pydantic
- ReportLab
- Python

---

**⭐ If this project helps you, please give it a star!**

[🔝 Back to top](#-ai-document-orchestrator)
