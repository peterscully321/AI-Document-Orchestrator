# 🤖 AI Document Orchestrator

> A powerful multi-agent system that transforms topics into professional documents through intelligent research, writing, and iterative quality checking.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/peterscully321/AI-Document-Orchestartor?style=social)](https://github.com/peterscully321/AI-Document-Orchestartor)

**[📖 Documentation](https://github.com/peterscully321/AI-Document-Orchestartor/wiki)** | **[🚀 Quick Start](#-quick-start)** | **[📝 API Docs](#-api-setup)** | **[🐛 Report Bug](https://github.com/peterscully321/AI-Document-Orchestartor/issues)**

---

## ✨ Features

- 🔍 **Intelligent Research** - Automated web search and data gathering using Tavily
- 📝 **Smart Summarization** - Extract key information and structure it intelligently
- ✍️ **Content Writing** - Generate high-quality, coherent document content
- ✅ **Quality Assurance** - Iterative feedback loop for continuous improvement
- 📄 **Multiple Formats** - Export as Text, PDF, or Google Docs
- 🎨 **Interactive UI** - Beautiful Streamlit web interface for easy access
- 🔄 **Agent Communication** - Seamless agent-to-agent handoffs using A2A protocol
- ⚡ **Async Processing** - Non-blocking asynchronous operations
- 🔐 **Secure API Integration** - Environment-based credential management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- `pip` package manager
- API keys: [Google Gemini](#google-gemini-api-required) + [Tavily](#tavily-api-required)

### Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/peterscully321/AI-Document-Orchestartor.git
cd AI-Document-Orchestartor

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Launch Interactive UI

```bash
# Windows
run_ui.bat

# Linux/Mac
./run_ui.sh

# Or directly with Streamlit
streamlit run app.py
```

Then open your browser to **`http://localhost:8501`**

### Command Line Usage

```bash
# Generate PDF document
python -m ai_doc_orchestrator.main "Machine Learning Basics" pdf

# Generate as Google Doc
python -m ai_doc_orchestrator.main "AI Ethics" google_docs

# Generate as text
python -m ai_doc_orchestrator.main "Your Topic Here" text
```

---

## 🏗️ Architecture

### High-Level Overview

```
User Input (Topic + Format)
           ↓
    ┌──────────────────────┐
    │  Phase 1: RESEARCH   │ → Uses Tavily to gather data
    └──────────────────────┘
           ↓
    ┌──────────────────────┐
    │  Phase 2: SUMMARIZE  │ → Processes and structures info
    └──────────────────────┘
           ↓
    ┌──────────────────────┐
    │ Phase 3: WRITE & QC  │ → Iterative improvement loop
    └──────────────────────┘
           ↓
    ┌──────────────────────┐
    │ Phase 4: FORMAT      │ → Creates final output (PDF/Docs/Text)
    └──────────────────────┘
           ↓
      Final Document
```

### Components

| Phase | Agent | Purpose | Tools |
|-------|-------|---------|-------|
| **1️⃣ Research** | Research Agent | Gather web data | [Tavily Search API](https://tavily.com/) |
| **2️⃣ Summarize** | Summary Agent | Process & structure data | MCP File System |
| **3️⃣ Write & QC** | Writer + QC Agent | Generate & validate content | Feedback Loop |
| **4️⃣ Format** | Formatting Agent | Create final output | [Google Docs API](https://developers.google.com/docs/api), [ReportLab](https://www.reportlab.com/) |

### Project Structure

```
src/ai_doc_orchestrator/
├── __init__.py
├── __main__.py
├── base_agent.py              # Base agent class with A2A support
├── models.py                  # Data models (Pydantic)
├── main.py                    # CLI entry point
├── agents/
│   ├── research.py            # Research Agent (Phase 1)
│   ├── summary.py             # Summary Agent (Phase 2)
│   ├── writer.py              # Writer Agent (Phase 3)
│   ├── qc.py                  # Quality Check Agent (Phase 3)
│   └── formatting.py          # Formatting Agent (Phase 4)
├── tools/
│   ├── search.py              # Tavily/Google Search
│   ├── mcp_filesystem.py      # MCP File System Read
│   ├── google_docs.py         # Google Docs API integration
│   └── pdf_generator.py       # PDF generation
└── orchestrator/
    └── orchestrator.py        # Main orchestrator
```

---

## 📦 Installation

### Step 1: Clone Repository

```bash
git clone https://github.com/peterscully321/AI-Document-Orchestartor.git
cd AI-Document-Orchestartor
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root with your API keys:

```env
# Required
GOOGLE_GEMINI_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here

# Optional (for Google Docs output)
GOOGLE_CREDENTIALS_PATH=/path/to/credentials.json

# Optional
OUTPUT_DIR=./output
```

📖 **[Detailed Setup Guide →](API_SETUP.md)**

---

## 🔑 API Setup

### Google Gemini API (Required) ✅

**Purpose:** Powers all LLM agents (Research, Summary, Writer, QC, Formatting)

**Get your free API key:**
1. Go to **[Google Makersuite](https://makersuite.google.com/app/apikey)**
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

**Add to `.env`:**
```env
GOOGLE_GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Documentation:** https://ai.google.dev/

**Pricing:** Free tier available with generous limits

---

### Tavily API (Required) ✅

**Purpose:** Web search for the Research Agent

**Get your free API key:**
1. Go to **[Tavily.com](https://tavily.com/)**
2. Sign up for free account
3. Navigate to Dashboard
4. Copy your API key

**Add to `.env`:**
```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Documentation:** https://docs.tavily.com/

**Pricing:** Free tier available

---

### Google Docs API (Optional) ⚪

**Purpose:** Create documents directly in Google Drive (only needed for `google_docs` format)

**Setup steps:**
1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Create a new project
3. Enable **Google Docs API** and **Google Drive API**
4. Create a Service Account:
   - APIs & Services → Credentials
   - Create Service Account
   - Generate JSON key
5. Download and save the JSON file

**Add to `.env`:**
```env
GOOGLE_CREDENTIALS_PATH=C:\path\to\service-account.json
```

**Documentation:** https://developers.google.com/docs/api

---

## 💻 Usage

### 🎨 Interactive Web UI (Recommended)

The easiest way to use AI Document Orchestrator:

```bash
# Windows
run_ui.bat

# Linux/Mac
./run_ui.sh

# Or directly
streamlit run app.py
```

**Access:** http://localhost:8501

**Features:**
- 📝 **Document Generator** - Full research + document generation workflow
- 📄 **Summarizer** - Quick content summarization
- ✍️ **Blog Writer** - Create engaging blog posts
- ⚙️ **Settings** - API configuration & system information

---

### 📱 Command Line Interface

```bash
# Generate PDF document
python -m ai_doc_orchestrator.main "Machine Learning Ethics" pdf

# Generate as Google Docs
python -m ai_doc_orchestrator.main "Python Programming Basics" google_docs

# Generate as plain text
python -m ai_doc_orchestrator.main "Data Science Trends" text
```

**Output files** are saved to the `output/` directory.

---

### 🐍 Python API

```python
import asyncio
from ai_doc_orchestrator.models import UserInput, OutputFormat
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator

async def main():
    # Create orchestrator instance
    orchestrator = DocumentOrchestrator(
        gemini_api_key="your_key_here",
        tavily_api_key="your_key_here"
    )
    
    # Define input
    user_input = UserInput(
        topic="Machine Learning Basics",
        format=OutputFormat.PDF
    )
    
    # Generate document
    result = await orchestrator.process(user_input)
    print(f"✅ Generated: {result.file_path}")
    print(f"📊 Stats: {result.stats}")

# Run
asyncio.run(main())
```

---

### 📚 Examples

See `example.py` for more comprehensive usage examples:

```bash
python example.py
```

---

## 🔄 Workflow Details

### Complete Process Flow

**1. 👤 User Input**
   - Provide topic (e.g., "Machine Learning Ethics")
   - Select output format (text, PDF, or google_docs)

**2. 🔍 Phase 1: Research**
   - Orchestrator initializes and hands off to Research Agent
   - Research Agent queries Tavily API for relevant articles
   - Collects raw data including URLs, summaries, and content
   - Returns structured research data

**3. 📋 Phase 2: Summary**
   - Summary Agent processes raw research data
   - Reads any local file context via MCP File System
   - Extracts key points and identifies themes
   - Creates structured notes with:
     - Executive summary
     - Key findings
     - Source citations
     - Related topics

**4. ✍️ Phase 3: Writing & Quality Check**
   - Writer Agent transforms structured notes into draft document
   - QC Agent reviews the draft for:
     - Accuracy and factuality
     - Coherence and flow
     - Completeness
     - Tone and style
   - If feedback needed:
     - QC sends feedback to Writer
     - Writer revises based on feedback
     - Loop continues (max 3 iterations)
   - Once approved, proceeds to Phase 4

**5. 📤 Phase 4: Formatting & Output**
   - Formatting Agent receives approved content
   - Creates final output in requested format:
     - **Text**: Returns as string
     - **PDF**: Generates using ReportLab with formatting
     - **Google Docs**: Creates via Google Docs API, returns shareable link

---

## 🔌 Agent Communication

Agents communicate using **A2A (Agent-to-Agent)** messages:

```python
@dataclass
class AgentMessage:
    source: str              # Sending agent
    target: str              # Receiving agent
    phase: str              # Workflow phase
    data: dict              # Payload
    metadata: dict          # Context
```

The orchestrator routes messages between agents, enabling:
- Sequential handoffs
- Parallel processing where applicable
- State management across phases
- Error handling and retries

---

## 🛠️ Development

### Development Setup

```bash
# Clone and setup
git clone https://github.com/peterscully321/AI-Document-Orchestartor.git
cd AI-Document-Orchestartor

# Create environment
python -m venv .venv
.venv\Scripts\activate

# Install with dev dependencies
pip install -r requirements.txt
pip install pytest pytest-asyncio black ruff mypy
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src/ai_doc_orchestrator
```

### Code Quality

```bash
# Format code with black
black src/

# Lint with ruff
ruff check src/

# Type checking with mypy
mypy src/
```

### Project Configuration

- **Black** - Code formatting (100 char line length)
- **Ruff** - Fast Python linter
- **Mypy** - Static type checker
- **Pytest** - Testing framework
- **Pydantic** - Data validation

---

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get running in 5 minutes
- **[API Setup Guide](API_SETUP.md)** - Detailed API configuration
- **[UI Guide](README_UI.md)** - Streamlit UI features and walkthrough
- **[WARP Documentation](WARP.md)** - Advanced configuration options

---

## 🤝 Contributing

Contributions welcome! Here's how:

1. **Fork** the repository on GitHub
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Commit** with clear message (`git commit -m 'Add amazing feature'`)
5. **Push** to branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

### Guidelines
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Add tests for new features
- Update documentation
- Use descriptive commit messages

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Community

- **GitHub Issues:** [Report a bug](https://github.com/peterscully321/AI-Document-Orchestartor/issues)
- **GitHub Discussions:** [Ask questions](https://github.com/peterscully321/AI-Document-Orchestartor/discussions)
- **Documentation:** [Full Wiki](https://github.com/peterscully321/AI-Document-Orchestartor/wiki)

---

## 🙏 Acknowledgments

Built with amazing technologies:

- **[Google Generative AI](https://ai.google.dev/)** - LLM capabilities
- **[Tavily](https://tavily.com/)** - Web search API
- **[Streamlit](https://streamlit.io/)** - Web UI framework
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation
- **[ReportLab](https://www.reportlab.com/)** - PDF generation
- **[Python](https://www.python.org/)** - Programming language

---

## 📊 Project Stats

[![GitHub followers](https://img.shields.io/github/followers/peterscully321?style=social)](https://github.com/peterscully321)
![Repository size](https://img.shields.io/github/repo-size/peterscully321/AI-Document-Orchestartor)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)
![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)

---

**⭐ If this project helps you, please give it a star!**

**[🔝 Back to top](#-ai-document-orchestrator)**
