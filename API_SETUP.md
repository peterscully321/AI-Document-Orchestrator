# API Setup Guide

This guide shows you exactly which APIs you need and where to configure them.

## Required APIs (Must Have)

### 1. Google Gemini API Key ⚠️ REQUIRED

**What it's for:** All LLM-powered agents (Research, Summary, Writer, QC, Formatting)

**Where to get it:**
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key" or "Get API Key"
4. Copy the key

**Where to configure:**
- **File:** `.env` (create this file in the project root)
- **Variable name:** `GOOGLE_GEMINI_API_KEY`
- **Code location:** `src/ai_doc_orchestrator/orchestrator/orchestrator.py` (line 50)

**Example:**
```env
GOOGLE_GEMINI_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

### 2. Tavily API Key ⚠️ REQUIRED

**What it's for:** Web search functionality (Research Agent - Phase 1)

**Where to get it:**
1. Go to https://tavily.com/
2. Sign up for a free account
3. Navigate to your dashboard
4. Copy your API key

**Where to configure:**
- **File:** `.env` (in project root)
- **Variable name:** `TAVILY_API_KEY`
- **Code location:** `src/ai_doc_orchestrator/orchestrator/orchestrator.py` (line 64)

**Note:** Tavily API key is still required for web search functionality.

**Example:**
```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## Optional APIs (Only if you need Google Docs output)

### 3. Google Service Account Credentials (Optional)

**What it's for:** Creating Google Docs files (Formatting Agent - Phase 4)

**When you need it:** Only if you want to generate Google Docs format output

**Where to get it:**
1. Go to https://console.cloud.google.com/
2. Create a new project or select existing one
3. Enable Google Docs API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Docs API"
   - Click "Enable"
4. Create Service Account:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Fill in details and create
5. Create Key:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file

**Where to configure:**
- **File:** `.env` (in project root)
- **Variable name:** `GOOGLE_CREDENTIALS_PATH`
- **Code location:** `src/ai_doc_orchestrator/orchestrator/orchestrator.py` (line 72)
- **File location:** Place the downloaded JSON file anywhere on your system

**Example:**
```env
GOOGLE_CREDENTIALS_PATH=C:\Users\hp\credentials\service-account.json
# Or on Linux/Mac:
# GOOGLE_CREDENTIALS_PATH=/home/user/credentials/service-account.json
```

---

## Quick Setup Steps

### Step 1: Create `.env` file

Create a file named `.env` in the project root directory (`C:\Users\hp\ai-doc-orchestrator\.env`):

```env
# Required
GOOGLE_GEMINI_API_KEY=your_gemini_key_here
TAVILY_API_KEY=your_tavily_key_here

# Optional (only for Google Docs output)
GOOGLE_CREDENTIALS_PATH=path/to/service-account.json

# Optional (for output files)
OUTPUT_DIR=./output
```

### Step 2: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Test it

```bash
# Test with text output (only needs OpenAI + Tavily)
python -m ai_doc_orchestrator.main "Python Programming" text

# Test with PDF output (only needs OpenAI + Tavily)
python -m ai_doc_orchestrator.main "Machine Learning" pdf

# Test with Google Docs (needs OpenAI + Tavily + Google credentials)
python -m ai_doc_orchestrator.main "Data Science" google_docs
```

---

## Configuration Summary

| API | Required? | Environment Variable | Used By | Cost |
|-----|-----------|---------------------|---------|------|
| **Google Gemini** | ✅ Yes | `GOOGLE_GEMINI_API_KEY` | All agents | Free tier available |
| **Tavily** | ✅ Yes | `TAVILY_API_KEY` | Research Agent | Free tier available |
| **Google Docs** | ❌ Optional | `GOOGLE_CREDENTIALS_PATH` | Formatting Agent | Free |

---

## Code Locations Reference

### Where APIs are loaded:

1. **Google Gemini API Key**
   - File: `src/ai_doc_orchestrator/orchestrator/orchestrator.py`
   - Line: 50
   - Code: `api_key = gemini_api_key or os.getenv("GOOGLE_GEMINI_API_KEY")`

2. **Tavily API Key**
   - File: `src/ai_doc_orchestrator/orchestrator/orchestrator.py`
   - Line: 64
   - Code: `tavily_key = tavily_api_key or os.getenv("TAVILY_API_KEY")`
   - Also used in: `src/ai_doc_orchestrator/tools/search.py` (line 23)

3. **Google Credentials**
   - File: `src/ai_doc_orchestrator/orchestrator/orchestrator.py`
   - Line: 72
   - Code: `google_creds = google_credentials_path or os.getenv("GOOGLE_CREDENTIALS_PATH")`
   - Also used in: `src/ai_doc_orchestrator/tools/google_docs.py` (line 45)

---

## Troubleshooting

### Error: "Google Gemini API key is required"
- **Solution:** Make sure `GOOGLE_GEMINI_API_KEY` is set in your `.env` file
- **Check:** The `.env` file is in the project root directory
- **Get key:** https://makersuite.google.com/app/apikey

### Error: "TAVILY_API_KEY environment variable is required"
- **Solution:** Get a Tavily API key from https://tavily.com and add it to `.env`
- **Alternative:** You can modify the code to use a different search provider

### Error: "Could not initialize Google Docs tool"
- **Solution:** This is only a warning if you're not using Google Docs output
- **If you need Google Docs:** Set up Google Service Account credentials (see above)

### Error: "Module not found" or import errors
- **Solution:** Run `pip install -r requirements.txt` to install all dependencies

---

## Alternative: Pass API Keys Directly in Code

If you prefer not to use `.env` file, you can pass API keys directly when creating the orchestrator:

```python
from ai_doc_orchestrator.orchestrator import DocumentOrchestrator

orchestrator = DocumentOrchestrator(
    gemini_api_key="AIzaSy...",
    tavily_api_key="tvly-...",
    google_credentials_path="path/to/service-account.json"
)
```

However, **using `.env` file is recommended** for security and convenience.

