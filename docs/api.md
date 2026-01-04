# API Documentation

## Overview

This document describes the APIs and interfaces available in the Neuro Patient Tracker system.

## Table of Contents

- [Python API](#python-api)
- [Data Models](#data-models)
- [Orchestrator API](#orchestrator-api)
- [Configuration API](#configuration-api)
- [Logging & Telemetry](#logging--telemetry)

## Python API

### Core Classes

#### NeuroCrew

Main orchestrator for multi-agent system.

**Location:** `src/orchestrator.py`

```python
from src.orchestrator import NeuroCrew

crew = NeuroCrew()
```

**Methods:**

##### `setup_team(max_messages: int = 12) -> RoundRobinGroupChat`

Set up the multi-agent team.

**Parameters:**
- `max_messages` (int): Maximum messages before termination

**Returns:**
- `RoundRobinGroupChat`: Configured team instance

**Example:**
```python
team = crew.setup_team(max_messages=15)
```

##### `async run_conversation(task: str, patient_id: Optional[str] = None) -> None`

Run a multi-agent conversation.

**Parameters:**
- `task` (str): The initial task or query
- `patient_id` (Optional[str]): Patient ID for audit logging

**Example:**
```python
await crew.run_conversation(
    task="Analyze this patient case...",
    patient_id="PT-001"
)
```

##### `async run_prognosis_analysis(patient_data: dict) -> None`

Run a prognosis analysis workflow.

**Parameters:**
- `patient_data` (dict): Patient information dictionary
  - `id` (str): Patient ID
  - `condition` (str): Primary neurological condition
  - `visit_count` (int): Number of visits
  - `clinical_summary` (str): Clinical data and history

**Example:**
```python
await crew.run_prognosis_analysis({
    "id": "PT-001",
    "condition": "Parkinson's Disease",
    "visit_count": 6,
    "clinical_summary": "..."
})
```

##### `get_agents() -> list[AssistantAgent]`

Get all clinical agents.

**Returns:**
- `list[AssistantAgent]`: List of all agent instances

##### `get_agent_names() -> list[str]`

Get names of all agents.

**Returns:**
- `list[str]`: List of agent names

---

#### SingleAgentChat

Simple single-agent consultation.

**Location:** `src/orchestrator.py`

```python
from src.orchestrator import SingleAgentChat

chat = SingleAgentChat()
```

**Methods:**

##### `async consult_neurologist(question: str) -> None`

Direct consultation with Neurologist agent.

**Parameters:**
- `question` (str): Clinical question or scenario

**Example:**
```python
await chat.consult_neurologist("""
Patient presents with headaches.
What is your assessment?
""")
```

##### `async consult_prognosis(patient_summary: str) -> None`

Direct prognosis analysis request.

**Parameters:**
- `patient_summary` (str): Patient clinical summary

**Example:**
```python
await chat.consult_prognosis("""
Patient: 72-year-old with Alzheimer's
MMSE scores declining over 2 years
Current: 17/30
""")
```

##### `async consult_treatment(case_details: str) -> None`

Get treatment recommendations.

**Parameters:**
- `case_details` (str): Case information for treatment advice

**Example:**
```python
await chat.consult_treatment("""
Patient with epilepsy on Levetiracetam
Seizure frequency: 2-3/month
Should we adjust?
""")
```

---

## Data Models

All data models use Pydantic for validation.

**Location:** `src/models/schemas.py`

### Patient Models

#### PatientCreate

Create a new patient.

```python
from src.models.schemas import PatientCreate, Gender, NeurologicalCondition
from datetime import date

patient = PatientCreate(
    first_name="John",
    last_name="Doe",
    date_of_birth=date(1960, 5, 15),
    gender=Gender.MALE,
    email="john.doe@example.com",
    phone="555-0123",
    primary_condition=NeurologicalCondition.PARKINSONS
)
```

**Fields:**
- `first_name` (str): First name (1-100 chars)
- `last_name` (str): Last name (1-100 chars)
- `date_of_birth` (date): Date of birth
- `gender` (Gender): Gender enum
- `email` (Optional[str]): Email address
- `phone` (Optional[str]): Phone number
- `primary_condition` (NeurologicalCondition): Primary condition enum

#### Patient

Full patient model with metadata.

```python
from src.models.schemas import Patient

patient = Patient(
    id="PT-001",
    first_name="John",
    last_name="Doe",
    # ... other fields
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow(),
    is_active=True
)
```

**Additional Fields:**
- `id` (str): Unique patient identifier
- `created_at` (datetime): Creation timestamp
- `updated_at` (datetime): Last update timestamp
- `is_active` (bool): Active status

### Visit Models

#### VitalSigns

Patient vital signs.

```python
from src.models.schemas import VitalSigns

vitals = VitalSigns(
    blood_pressure_systolic=120,
    blood_pressure_diastolic=80,
    heart_rate=72,
    temperature=98.6,
    weight_kg=75.5
)
```

#### NeurologicalAssessment

Neurological examination results.

```python
from src.models.schemas import NeurologicalAssessment

assessment = NeurologicalAssessment(
    mmse_score=28,           # 0-30
    moca_score=26,           # 0-30
    motor_function_score=85, # 0-100
    symptom_severity=3,      # 0-10
    seizure_frequency=2,     # episodes/month
    notes="Stable condition"
)
```

#### MedicationRecord

Medication information.

```python
from src.models.schemas import MedicationRecord
from datetime import date

med = MedicationRecord(
    name="Levetiracetam",
    dosage="500mg",
    frequency="BID",
    start_date=date(2024, 1, 1),
    end_date=None,
    is_active=True,
    side_effects="Mild irritability"
)
```

#### VisitCreate

Create a new visit.

```python
from src.models.schemas import VisitCreate

visit = VisitCreate(
    patient_id="PT-001",
    chief_complaint="Follow-up",
    vitals=vitals,
    assessment=assessment,
    medications=[med],
    diagnosis_notes="Stable",
    treatment_plan="Continue current medications"
)
```

### Prognosis Models

#### PrognosisAnalysis

Prognosis analysis results.

```python
from src.models.schemas import (
    PrognosisAnalysis,
    PrognosisTrend,
    SeverityLevel,
    NeurologicalCondition
)

prognosis = PrognosisAnalysis(
    patient_id="PT-001",
    condition=NeurologicalCondition.PARKINSONS,
    overall_trend=PrognosisTrend.STABLE,
    cognitive_trend=PrognosisTrend.IMPROVING,
    motor_trend=PrognosisTrend.DECLINING,
    current_severity=SeverityLevel.MODERATE,
    predicted_severity_3mo=SeverityLevel.MODERATE,
    predicted_severity_6mo=SeverityLevel.SEVERE,
    summary="Mixed trends observed",
    recommendations=[
        "Adjust medication",
        "Increase PT frequency"
    ],
    risk_factors=["Age", "Disease duration"],
    confidence_score=0.82  # 0.0-1.0
)
```

### Enumerations

#### Gender

```python
from src.models.schemas import Gender

Gender.MALE
Gender.FEMALE
Gender.OTHER
```

#### NeurologicalCondition

```python
from src.models.schemas import NeurologicalCondition

NeurologicalCondition.EPILEPSY
NeurologicalCondition.MIGRAINE
NeurologicalCondition.PARKINSONS
NeurologicalCondition.MULTIPLE_SCLEROSIS
NeurologicalCondition.ALZHEIMERS
NeurologicalCondition.STROKE
NeurologicalCondition.NEUROPATHY
NeurologicalCondition.OTHER
```

#### PrognosisTrend

```python
from src.models.schemas import PrognosisTrend

PrognosisTrend.IMPROVING
PrognosisTrend.STABLE
PrognosisTrend.DECLINING
PrognosisTrend.UNKNOWN
```

#### SeverityLevel

```python
from src.models.schemas import SeverityLevel

SeverityLevel.MILD
SeverityLevel.MODERATE
SeverityLevel.SEVERE
SeverityLevel.CRITICAL
```

---

## Configuration API

### Settings

**Location:** `src/config/settings.py`

```python
from src.config import settings

# LLM Configuration
provider = settings.LLM_PROVIDER  # "local" or "openai"
model = settings.OPENAI_MODEL
local_url = settings.LOCAL_LLM_BASE_URL

# Database
db_url = settings.DATABASE_URL

# Application
debug = settings.DEBUG
log_level = settings.LOG_LEVEL

# Directories
output_dir = settings.OUTPUT_DIR
logs_dir = settings.LOGS_DIR
```

**Settings Properties:**
- `LLM_PROVIDER`: "openai" or "local"
- `OPENAI_API_KEY`: OpenAI API key
- `OPENAI_MODEL`: OpenAI model name
- `LOCAL_LLM_BASE_URL`: Local LLM endpoint
- `LOCAL_LLM_MODEL`: Local model name
- `LOCAL_LLM_API_KEY`: Local API key (if needed)
- `DATABASE_URL`: Database connection string
- `DEBUG`: Debug mode (bool)
- `LOG_LEVEL`: Logging level
- `OUTPUT_DIR`: Output directory path
- `LOGS_DIR`: Logs directory path

---

## Logging & Telemetry

### Audit Logger

**Location:** `src/logging/audit_logger.py`

```python
from src.logging import get_logger

logger = get_logger()

# Log system events
logger.log_system_start()
logger.log_system_stop()

# Log agent events
logger.log_agent_initialized("Neurologist")
logger.log_agent_message(
    agent_name="Neurologist",
    message_type="response",
    content_preview="Analysis complete",
    correlation_id="abc123"
)

# Log conversations
correlation_id = logger.new_correlation_id()
logger.log_conversation_start(
    correlation_id=correlation_id,
    task_summary="Patient analysis",
    agents_involved=["Neurologist", "PrognosisAnalyst"]
)

# Log PHI access (HIPAA)
logger.log_phi_access(
    patient_id="PT-001",
    access_type="read",
    data_fields=["clinical_summary", "medications"],
    reason="Prognosis analysis"
)

# Log prognosis
logger.log_prognosis_generated(
    patient_id="PT-001",
    correlation_id=correlation_id,
    trend="stable",
    confidence=0.85
)

# Log errors
logger.log_error(
    "Error message",
    exception=exc,
    correlation_id=correlation_id
)
```

### Telemetry

**Location:** `src/logging/telemetry.py`

```python
from src.logging import get_telemetry

telemetry = get_telemetry()

# Print cost summary
telemetry.print_cost_summary()

# Save session report
telemetry.save_session_report()

# Get session ID
session_id = telemetry._session_id
```

**Tracked Metrics:**
- LLM model used
- Input/output tokens
- Cost per call
- Response time
- Success/failure rate
- Session totals

---

## Helper Functions

### get_model_client

Create LLM model client.

**Location:** `src/orchestrator.py`

```python
from src.orchestrator import get_model_client

client = get_model_client()
# Returns OpenAIChatCompletionClient configured for current provider
```

### run_async

Run async coroutine synchronously.

```python
from src.orchestrator import run_async

result = run_async(async_function())
```

---

## Error Handling

### Common Exceptions

```python
from openai import RateLimitError, InvalidRequestError

try:
    await crew.run_conversation(task)
except RateLimitError:
    # Handle rate limits
    print("Rate limit exceeded")
except InvalidRequestError:
    # Handle invalid requests
    print("Invalid request")
except Exception as e:
    # Handle other errors
    print(f"Error: {e}")
```

---

## Examples

### Complete Workflow Example

```python
import asyncio
from src.orchestrator import NeuroCrew
from src.logging import init_logging, init_telemetry

async def main():
    # Initialize
    logger = init_logging()
    telemetry = init_telemetry()

    # Create crew
    crew = NeuroCrew()

    # Run analysis
    await crew.run_prognosis_analysis({
        "id": "PT-001",
        "condition": "parkinsons",
        "visit_count": 6,
        "clinical_summary": "Patient data..."
    })

    # Print costs
    telemetry.print_cost_summary()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## API Reference Links

- **AutoGen API**: https://microsoft.github.io/autogen/
- **Pydantic Models**: https://docs.pydantic.dev/
- **OpenAI API**: https://platform.openai.com/docs

---

For more information, see:
- [Architecture Documentation](architecture.html)
- [Agent Documentation](agents.md)
- [Claude/LLM Integration](claude.md)
