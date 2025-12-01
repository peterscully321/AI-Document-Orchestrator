# Quick Start Guide

## 🚀 Get Running in 3 Steps

### Step 1: Get API Keys

**Required APIs (you need both):**

1. **Google Gemini API Key**
   - 🔗 https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Click "Create API Key" or "Get API Key"
   - Copy the key

2. **Tavily API Key**
   - 🔗 https://tavily.com
   - Sign up (free tier available)
   - Copy your API key from dashboard

### Step 2: Create `.env` File

Create a file named `.env` in the project root:

```env
GOOGLE_GEMINI_API_KEY=AIzaSy-your-key-here
TAVILY_API_KEY=tvly-your-key-here
```

### Step 3: Install & Run

```bash
# Install dependencies
pip install -r requirements.txt

# Run it!
python -m ai_doc_orchestrator.main "Your Topic Here" pdf
```

---

## 📝 Example Commands

```bash
# Generate text output
python -m ai_doc_orchestrator.main "Python Programming" text

# Generate PDF
python -m ai_doc_orchestrator.main "Machine Learning Basics" pdf

# Generate Google Docs (requires additional setup - see API_SETUP.md)
python -m ai_doc_orchestrator.main "Data Science" google_docs
```

---

## ⚙️ Where APIs Are Used

| Phase | Agent | API Used | Required? |
|-------|-------|----------|----------|
| Phase 1 | Research | Tavily | ✅ Yes |
| Phase 2 | Summary | Google Gemini | ✅ Yes |
| Phase 3 | Writer | Google Gemini | ✅ Yes |
| Phase 3 | QC | Google Gemini | ✅ Yes |
| Phase 4 | Formatting | Google Gemini | ✅ Yes |
| Phase 4 | Formatting | Google Docs API | ⚪ Only for Google Docs output |

---

## 🔧 Configuration Files

- **`.env`** - Your API keys (create this file)
- **`src/ai_doc_orchestrator/orchestrator/orchestrator.py`** - Where APIs are loaded (lines 50, 64, 72)

---

## ❓ Need More Help?

See **[API_SETUP.md](API_SETUP.md)** for detailed setup instructions with screenshots and troubleshooting.

