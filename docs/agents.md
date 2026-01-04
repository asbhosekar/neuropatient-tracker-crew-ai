# AI Agents Documentation

## Overview

The Neuro Patient Tracker uses a multi-agent architecture where specialized AI agents collaborate to provide comprehensive neurological patient analysis. Each agent has a specific role and expertise.

## Agent Architecture

### Base Agent

All agents inherit from `BaseAgent` which provides:
- Standard initialization
- System message management
- Configuration handling
- Logging capabilities

**Location:** `src/agents/base_agent.py`

## Agent Catalog

### 1. Neurologist Agent 👨‍⚕️

**Location:** `src/agents/neurologist.py`

**Role:** Clinical case review and medical assessment

**Capabilities:**
- Reviews patient clinical data and symptoms
- Identifies key neurological findings
- Provides differential diagnoses
- Suggests appropriate workup and testing
- Interprets neurological exam results

**System Prompt Highlights:**
- 20+ years clinical experience persona
- Evidence-based recommendations
- Considers patient history and comorbidities
- Notes red flags and urgent concerns

**Best Used For:**
- Initial patient assessment
- Symptom analysis
- Diagnostic workup planning
- Clinical case review

**Example Usage:**
```python
from src.orchestrator import SingleAgentChat

chat = SingleAgentChat()
await chat.consult_neurologist("""
A 45-year-old female presents with:
- Recurrent headaches, 4-5 per week
- Throbbing, unilateral pain
- Associated nausea and photophobia
What is your assessment?
""")
```

---

### 2. Prognosis Analyst Agent 📊

**Location:** `src/agents/prognosis_analyst.py`

**Role:** Longitudinal analysis and trajectory prediction

**Capabilities:**
- Analyzes patient trends over time
- Identifies patterns in clinical metrics
- Predicts disease trajectories
- Assesses treatment efficacy
- Provides confidence scores

**System Prompt Highlights:**
- Data science and medical analytics expertise
- Statistical trend analysis
- Predictive modeling
- Risk factor identification

**Best Used For:**
- Long-term patient monitoring
- Treatment effectiveness evaluation
- Disease progression prediction
- Risk stratification

**Example Usage:**
```python
await chat.consult_prognosis("""
Patient with Parkinson's Disease:
- Month 0: UPDRS 28
- Month 3: UPDRS 32
- Month 6: UPDRS 34
- Started medication at month 2
Analyze progression and predict next 6 months.
""")
```

---

### 3. Treatment Advisor Agent 💊

**Location:** `src/agents/treatment_advisor.py`

**Role:** Medication and treatment planning

**Capabilities:**
- Reviews current medications
- Identifies drug interactions
- Suggests dosage adjustments
- Recommends alternative treatments
- Considers side effect profiles

**System Prompt Highlights:**
- Pharmacology expertise
- Evidence-based medicine approach
- Patient safety focus
- Personalized treatment plans

**Best Used For:**
- Medication optimization
- Treatment plan development
- Side effect management
- Therapy adjustments

**Example Usage:**
```python
await chat.consult_treatment("""
Patient with epilepsy on Levetiracetam 1000mg BID:
- Current seizure frequency: 2-3/month
- Side effects: Mild irritability
- Goal: Better control
Should we adjust treatment?
""")
```

---

### 4. Report Generator Agent 📄

**Location:** `src/agents/report_generator.py`

**Role:** Clinical documentation and summaries

**Capabilities:**
- Creates comprehensive clinical reports
- Summarizes multi-agent analyses
- Structures information clearly
- Generates patient-friendly summaries
- Documents recommendations

**System Prompt Highlights:**
- Medical writing expertise
- Clear, structured documentation
- HIPAA-compliant language
- Professional formatting

**Best Used For:**
- Prognosis reports
- Clinical summaries
- Patient documentation
- Multi-agent synthesis

**Example Usage:**
```python
# Usually called automatically after multi-agent analysis
crew = NeuroCrew()
await crew.run_prognosis_analysis(patient_data)
# Report Generator synthesizes all agent inputs
```

---

### 5. QA Validator Agent ✅

**Location:** `src/agents/qa_validator.py`

**Role:** Quality assurance and data validation

**Capabilities:**
- Validates data accuracy
- Checks medical logic
- Identifies inconsistencies
- Ensures recommendation quality
- Flags potential errors

**System Prompt Highlights:**
- Quality assurance expertise
- Medical safety focus
- Critical analysis
- Error detection

**Best Used For:**
- Data quality checks
- Logic validation
- Safety verification
- Consistency checking

**Example Usage:**
```python
# Usually runs automatically in multi-agent workflow
# Validates outputs from other agents
# Ensures clinical recommendations are sound
```

---

### 6. Clinical Architect Agent 🏗️

**Location:** `src/agents/clinical_architect.py`

**Role:** System design and HIPAA compliance

**Capabilities:**
- Designs data models
- Ensures HIPAA compliance
- Plans system architecture
- Manages data security
- Defines workflows

**System Prompt Highlights:**
- Healthcare IT expertise
- HIPAA/compliance knowledge
- System architecture
- Data security focus

**Best Used For:**
- System design decisions
- Compliance verification
- Data model design
- Architecture planning

---

## Multi-Agent Workflows

### Prognosis Analysis Workflow

```
User Request
    ↓
1. Neurologist: Reviews clinical data
    ↓
2. Prognosis Analyst: Analyzes trends
    ↓
3. Treatment Advisor: Suggests adjustments
    ↓
4. QA Validator: Checks analysis quality
    ↓
5. Report Generator: Creates summary
    ↓
Result to User
```

**Implementation:**
```python
crew = NeuroCrew()
await crew.run_prognosis_analysis({
    "id": "PT-001",
    "condition": "parkinsons",
    "clinical_summary": "...",
})
```

### Single Consultation Workflow

```
User Question
    ↓
Single Agent (e.g., Neurologist)
    ↓
Direct Response
```

**Implementation:**
```python
chat = SingleAgentChat()
await chat.consult_neurologist(question)
```

## Agent Communication

### Message Types

Agents communicate using AutoGen message types:

1. **TextMessage**: Standard conversation
2. **ToolCallMessage**: Function calls
3. **ToolCallResultMessage**: Function results
4. **TaskResult**: Final conversation outcome

### Conversation Flow

```python
# RoundRobinGroupChat manages turn-taking
team = RoundRobinGroupChat(
    participants=[agent1, agent2, agent3],
    termination_condition=MaxMessageTermination(12)
)

# Agents take turns responding
async for message in team.run_stream(task=question):
    # Process message
    print(message.content)
```

## Agent Configuration

### System Messages

Each agent has a carefully crafted system message that defines:
- **Identity**: Role and expertise level
- **Responsibilities**: What the agent should do
- **Guidelines**: How to approach tasks
- **Constraints**: What to avoid
- **Output Format**: Expected response structure

### Temperature Settings

Recommended temperature settings per agent:

```python
AGENT_TEMPERATURES = {
    "Neurologist": 0.7,      # Clinical precision
    "PrognosisAnalyst": 0.8,  # Analytical creativity
    "TreatmentAdvisor": 0.7,  # Balanced recommendations
    "ReportGenerator": 0.6,   # Structured output
    "QAValidator": 0.5,       # Fact-checking accuracy
    "ClinicalArchitect": 0.6, # Design clarity
}
```

## Adding New Agents

### Step 1: Create Agent Class

```python
# src/agents/new_agent.py
from .base_agent import BaseAgent

class NewAgent(BaseAgent):
    """Description of new agent."""

    @property
    def system_message(self) -> str:
        return """
        You are an expert in [domain].

        Your role:
        1. [Responsibility 1]
        2. [Responsibility 2]

        Guidelines:
        - [Guideline 1]
        - [Guideline 2]
        """
```

### Step 2: Register in __init__.py

```python
# src/agents/__init__.py
from .new_agent import NewAgent

__all__ = [
    # ... existing agents
    "NewAgent",
]
```

### Step 3: Add to Orchestrator

```python
# src/orchestrator.py
class NeuroCrew:
    def __init__(self):
        # ... existing agents
        self._new_agent = self._create_agent(
            "NewAgent",
            NewAgent().system_message
        )
```

## Agent Testing

### Unit Testing

```python
# tests/test_agents.py
def test_neurologist_agent():
    agent = NeurologistAgent()

    assert "neurologist" in agent.system_message.lower()
    assert len(agent.system_message) > 100
```

### Integration Testing

```python
async def test_multi_agent_workflow():
    crew = NeuroCrew()
    result = await crew.run_prognosis_analysis(sample_patient)

    assert result is not None
    # Verify all agents participated
```

## Best Practices

### 1. System Prompt Design

**DO:**
- ✅ Be specific about expertise level
- ✅ Provide clear task structure
- ✅ Include examples when helpful
- ✅ Define output format
- ✅ Add ethical guidelines

**DON'T:**
- ❌ Use vague role descriptions
- ❌ Mix unrelated responsibilities
- ❌ Create overly long prompts
- ❌ Ignore safety considerations

### 2. Agent Scope

Keep agents focused:
- One primary expertise area
- Clear boundaries of responsibility
- Well-defined inputs/outputs
- Specific use cases

### 3. Error Handling

```python
try:
    response = await agent.process(message)
except LLMError as e:
    logger.error(f"Agent {agent.name} error: {e}")
    # Graceful degradation
```

### 4. Performance

Optimize agent performance:
- Keep system prompts concise
- Use appropriate temperature
- Limit conversation length
- Cache static content

## Agent Metrics

### Tracked Metrics

For each agent, we track:
- Number of invocations
- Average response time
- Token usage
- Success/failure rate
- Cost per invocation

### Accessing Metrics

```python
from src.logging import get_telemetry

telemetry = get_telemetry()
telemetry.print_cost_summary()
# Shows per-agent statistics
```

## Troubleshooting

### Agent Not Responding

**Check:**
1. LLM connection is active
2. System message is valid
3. Input message is well-formed
4. Token limits not exceeded

### Poor Quality Responses

**Solutions:**
1. Refine system prompt
2. Adjust temperature
3. Provide more context
4. Use more capable model

### Agent Conflicts

If agents provide conflicting advice:
1. QA Validator should catch this
2. Report Generator synthesizes
3. Human review recommended

## Future Enhancements

### Planned Agent Features

1. **Specialist Agents**
   - Epilepsy specialist
   - Movement disorder specialist
   - Stroke specialist

2. **Support Agents**
   - Research assistant (literature search)
   - Clinical trial matcher
   - Insurance pre-authorization

3. **Patient-Facing Agents**
   - Patient educator
   - Symptom tracker
   - Medication reminder

4. **Administrative Agents**
   - Appointment scheduler
   - Follow-up coordinator
   - Documentation assistant

---

## References

- AutoGen Documentation: https://microsoft.github.io/autogen/
- Agent Definitions: `src/agents/`
- Orchestrator: `src/orchestrator.py`
- Configuration: `src/config/settings.py`
