# 🧠 Neuro Patient Tracker

**AI-powered Patient Tracking System for Neurologists with Prognosis Analysis**

Built using Microsoft AutoGen multi-agent framework.

## 🎯 Overview

A comprehensive patient tracking system designed for neurologists to:
- Track patient visits and neurological assessments over time
- Monitor conditions: Epilepsy, Migraines, Parkinson's, MS, etc.
- Generate prognosis reports with trend analysis
- Predict condition trajectories based on historical data

## 🤖 Agent Architecture

| Agent | Role |
|-------|------|
| **Clinical Architect** | Designs data models, ensures HIPAA compliance |
| **Backend Developer** | Builds FastAPI services, database layer |
| **Prognosis Analyst** | Analyzes trends, predicts trajectories |
| **QA Validator** | Tests code, validates medical logic |
| **Report Generator** | Creates prognosis reports, summaries |
| **Documentation Agent** | Generates API docs, user guides |

## 📁 Project Structure

```
neuro-patient-tracker/
├── src/
│   ├── agents/           # AutoGen agent definitions
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic
│   ├── api/              # FastAPI endpoints
│   └── config/           # Configuration
├── tests/                # Unit & integration tests
├── output/               # Generated artifacts
└── docs/                 # Documentation
```

## 🚀 Quick Start

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install -e ".[dev]"

# Set up environment
copy .env.example .env
# Edit .env - Choose your LLM provider:
# - For Local Llama 3.2: Set LLM_PROVIDER=local (default)
# - For OpenAI: Set LLM_PROVIDER=openai and add OPENAI_API_KEY

# Run with CLI
python -m src.main

# OR Run with Streamlit Web UI
streamlit run app.py
```

## 📊 Key Features

- **Patient Management**: CRUD operations for patient records
- **Visit Tracking**: Log appointments with neurological assessments
- **Prognosis Engine**: Longitudinal analysis of patient condition
- **Trend Analysis**: Track symptom severity, medication efficacy
- **Report Generation**: Clinical summaries and prognosis reports

## 🔧 Tech Stack

- **Framework**: Microsoft AutoGen
- **LLM**: OpenAI GPT-4o-mini OR Local Llama 3.2 (your choice!)
- **UI**: Streamlit (Web Interface)
- **API**: FastAPI
- **Database**: SQLAlchemy + SQLite
- **Validation**: Pydantic v2

## 🚀 New Features

### Local LLM Support (Llama 3.2)
- ✅ Run 100% locally with your own Llama 3.2 model
- ✅ No API costs, complete privacy
- ✅ Works with LM Studio, Ollama, or llama.cpp
- 📖 See [LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md) for setup guide

### Streamlit Web Interface
- ✅ Beautiful web UI for easy interaction
- ✅ Multi-agent analysis with real-time output
- ✅ Single agent consultations
- ✅ Pre-filled sample cases for testing
- 📖 See [STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md) for usage

### Testing
- ✅ Comprehensive test suite with pytest
- ✅ 16 passing tests for models and configuration
- 🧪 Run: `pytest tests/ -v`

## 📚 Documentation

- **[STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)** - Web UI setup and usage
- **[LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md)** - Local Llama 3.2 configuration
- **[test_local_llm.py](test_local_llm.py)** - Quick test script for local LLM

---
*Built with AI-powered multi-agent collaboration*
