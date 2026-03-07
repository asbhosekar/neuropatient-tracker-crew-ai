# Neuro Patient Tracker

**AI-powered Clinical Decision Support System for Neurology**

Multi-agent AI system built on Microsoft AutoGen 0.4+ with 6 specialized clinical agents that collaborate to analyze patient data, generate prognoses, and recommend treatments.

## Overview

- **6 AI Agents**: Neurologist, Prognosis Analyst, Treatment Advisor, QA Validator, Report Generator, Clinical Architect
- **7 Neurological Conditions**: Epilepsy, Migraine, Parkinson's, MS, Alzheimer's, Stroke, Neuropathy
- **Dual LLM Support**: OpenAI GPT-4o-mini or local models via Ollama (Phi-3, Llama 3.2)
- **Professional UI**: Streamlit web interface with clinical dark theme
- **HIPAA-Aware Logging**: PHI hashing (SHA256), audit trails, 7-year retention
- **Advanced Prompt Engineering**: Chain-of-Thought, Few-Shot, Self-Review, Confidence Calibration

## Quick Start

```bash
# Clone and setup
git clone https://github.com/asbhosekar/neuropatient-tracker-crew-ai.git
cd neuropatient-tracker-crew-ai
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -e ".[dev]"

# Configure LLM provider in .env
# Option A: Local (default) - requires Ollama running
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:11434/v1
LOCAL_LLM_MODEL=phi3:mini-128k

# Option B: OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here

# Run Streamlit UI
streamlit run app.py --server.port 8503

# Or run CLI
python -m src.main

# Run tests
pytest tests/ -v
```

## Architecture

```
User (Streamlit/CLI) -> NeuroCrew Orchestrator -> RoundRobinGroupChat -> 6 Agents -> LLM -> Report
```

### AI Agents

| Agent | Role | Techniques |
|-------|------|------------|
| **Neurologist** | 5-step clinical reasoning, differential diagnosis, red flag screening | CoT, Few-Shot, Self-Review |
| **Prognosis Analyst** | Trend calculation, trajectory projection, condition benchmarks | CoT, Benchmarks, Confidence 0-1 |
| **Treatment Advisor** | Medication optimization, drug interaction screening, dose titration | CoT, Drug DB, Guardrails |
| **Report Generator** | Integrated synthesis, executive summary, follow-up planning | Template, Integration |
| **QA Validator** | 6-step validation, score range checks, anomaly detection | Ref Tables, Quality Score |
| **Clinical Architect** | HIPAA 18-identifier audit, data model review | HIPAA Audit, Compliance |

## Project Structure

```
neuro-patient-tracker/
    app.py                      -- Streamlit web UI (clinical dark theme)
    pyproject.toml              -- Dependencies and project config
    .env                        -- LLM provider and environment config
    src/
        main.py                 -- CLI entry point
        orchestrator.py         -- NeuroCrew + SingleAgentChat
        agents/
            base_agent.py       -- BaseNeurologistAgent (abstract)
            neurologist.py      -- Clinical expert (5-step CoT)
            prognosis_analyst.py -- Trend analysis (benchmarks)
            treatment_advisor.py -- Medication planning (drug DB)
            qa_validator.py     -- Data quality (6-step validation)
            report_generator.py -- Clinical documentation
            clinical_architect.py -- HIPAA compliance
        models/
            schemas.py          -- Pydantic v2 data models
        config/
            settings.py         -- Environment-based config
        logging/
            audit_logger.py     -- HIPAA audit (SHA256 hashing)
            telemetry.py        -- LLM token/cost tracking
    data/
        test_patients.json      -- 12 test patient records
    tests/                      -- pytest test suite
    docs/
        architecture.html       -- Interactive architecture visualization
        architecture-onepage.html -- Compact one-page architecture (landscape)
        code-review.html        -- Code review report with findings
```

## Tech Stack

- **Framework**: Microsoft AutoGen 0.4+ (multi-agent orchestration)
- **LLM**: OpenAI GPT-4o-mini / Ollama (Phi-3, Llama 3.2)
- **UI**: Streamlit with custom clinical CSS
- **Data Models**: Pydantic v2 with strict validation
- **Logging**: HIPAA-compliant audit logging with SHA256 PHI hashing
- **Telemetry**: LLM token/cost tracking per session
- **Testing**: pytest

## Documentation

- [Architecture (Interactive)](docs/architecture.html) -- Full system visualization with animations
- [Architecture (One Page)](docs/architecture-onepage.html) -- Compact landscape overview
- [Code Review Report](docs/code-review.html) -- Security, quality, and architecture findings

## Test Data

12 diverse patient records in `data/test_patients.json` covering all 7 neurological conditions with full visit history, vitals, assessments, medications, and diagnosis notes.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `local` | LLM backend: "openai" or "local" |
| `OPENAI_API_KEY` | -- | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `LOCAL_LLM_BASE_URL` | `http://localhost:11434/v1` | Ollama/LM Studio endpoint |
| `LOCAL_LLM_MODEL` | `phi3:mini-128k` | Local model name |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

---

*Built with AI-powered multi-agent collaboration*
