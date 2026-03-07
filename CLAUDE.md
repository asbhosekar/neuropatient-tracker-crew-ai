# Neuro Patient Tracker - CLAUDE.md

## Project Overview
Multi-agent AI system for neurology patient tracking and prognosis, built on Microsoft AutoGen. 6 specialized clinical AI agents collaborate via round-robin group chat to analyze patient data, generate prognoses, and recommend treatments.

## Tech Stack
- **Framework**: Microsoft AutoGen (multi-agent orchestration)
- **Models**: Pydantic v2 (data validation)
- **UI**: Streamlit (web interface)
- **LLM**: OpenAI GPT-4o-mini or local models via Ollama (Phi-3, Llama 3.2)
- **Logging**: HIPAA-compliant audit logging with SHA256 PHI hashing
- **Telemetry**: LLM token/cost tracking per session
- **Backend**: FastAPI + SQLAlchemy 2.0 (planned)
- **Testing**: pytest

## Architecture
```
User (CLI/Streamlit) -> Orchestrator (NeuroCrew) -> RoundRobinGroupChat -> 6 Agents -> LLM Provider
```

### Agents (src/agents/)
| Agent | Role | Key Methods |
|-------|------|-------------|
| Neurologist | Primary clinical expert | get_red_flags(), get_workup_recommendations() |
| Clinical Architect | HIPAA data compliance | validate_data_model() |
| Prognosis Analyst | Longitudinal trend analysis | calculate_trend(), get_risk_factors() |
| Treatment Advisor | Medication planning | get_first_line_treatments(), check_escalation_criteria() |
| QA Validator | Data quality checks | validate_assessment_score(), validate_vital_signs() |
| Report Generator | Clinical documentation | get_report_template(), format_trend_summary() |

### Key Files
- `app.py` - Streamlit web UI (professional clinical dark theme with custom CSS)
- `src/main.py` - CLI entry point
- `src/orchestrator.py` - NeuroCrew orchestrator + RoundRobinGroupChat
- `src/agents/base_agent.py` - BaseNeurologistAgent (shared interface)
- `src/models/schemas.py` - Pydantic v2 data models (Patient, Visit, Prognosis)
- `src/config/settings.py` - Environment config (.env based)
- `src/logging/audit_logger.py` - HIPAA audit logging (singleton)
- `src/logging/telemetry.py` - LLM runtime telemetry (singleton)
- `tests/` - pytest test suite
- `data/test_patients.json` - 12 sample patient records for testing/demo

### Documentation (docs/)
- `architecture.html` - Interactive architecture visualization (animated)
- `architecture-onepage.html` - Compact one-page landscape architecture
- `code-review.html` - Full code review report with findings

## Commands
```bash
# Run CLI
python -m src.main

# Run Streamlit UI
streamlit run app.py

# Run tests
pytest tests/ -v

# Test local LLM connectivity
python test_local_llm.py
```

## Configuration
Set via `.env` file or environment variables:
- `LLM_PROVIDER`: "openai" or "local" (default: "local")
- `OPENAI_API_KEY`: API key (when using openai)
- `OPENAI_MODEL`: Model name (default: "gpt-4o-mini")
- `LOCAL_LLM_BASE_URL`: Local endpoint (default: "http://localhost:11434/v1")
- `LOCAL_LLM_MODEL`: Local model (default: "phi3:mini-128k")
- `LOG_LEVEL`: Logging verbosity (default: "INFO")

## Conventions
- All agents extend `BaseNeurologistAgent` in `src/agents/base_agent.py`
- Orchestrator uses `MaxMessageTermination(12)` and `TextMentionTermination("TERMINATE")`
- PHI (Protected Health Information) is never logged in plaintext - always SHA256 hashed
- Log files: `logs/` directory (app.log, audit.log, agents.log, phi_access.log)
- Telemetry output: `logs/` directory (llm_telemetry.jsonl, session reports)
- Data models use Pydantic v2 with strict field validation
- Enums: Gender, NeurologicalCondition, PrognosisTrend, SeverityLevel

## Neurological Conditions Supported
epilepsy, migraine, parkinsons, multiple_sclerosis, alzheimers, stroke, neuropathy, other
