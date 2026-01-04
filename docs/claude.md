# Claude & LLM Integration Guide

## Overview

This document explains how Large Language Models (LLMs) are integrated into the Neuro Patient Tracker system, including support for both cloud-based (OpenAI/Claude) and local (Llama 3.2) models.

## Table of Contents

- [LLM Architecture](#llm-architecture)
- [Supported Models](#supported-models)
- [Configuration](#configuration)
- [Agent System Prompts](#agent-system-prompts)
- [Message Flow](#message-flow)
- [Best Practices](#best-practices)
- [Performance Optimization](#performance-optimization)

## LLM Architecture

### Multi-Agent Framework

The system uses **Microsoft AutoGen** to orchestrate multiple AI agents, each powered by an LLM:

```
User Query
    ↓
Orchestrator (NeuroCrew)
    ↓
RoundRobinGroupChat
    ↓
Agent 1 → LLM → Response
Agent 2 → LLM → Response
Agent 3 → LLM → Response
    ...
    ↓
Aggregated Response
```

### Agent Types

Each agent has a specialized system prompt that guides its behavior:

| Agent | LLM Role | Specialization |
|-------|----------|---------------|
| **Neurologist** | Clinical Expert | Case review, diagnosis, medical assessment |
| **Prognosis Analyst** | Data Scientist | Trend analysis, predictions, trajectories |
| **Treatment Advisor** | Pharmacologist | Medication recommendations, treatment plans |
| **Report Generator** | Technical Writer | Comprehensive clinical summaries |
| **QA Validator** | Quality Assurance | Data validation, logic checking |
| **Clinical Architect** | System Designer | HIPAA compliance, data modeling |

## Supported Models

### 1. OpenAI GPT Models

**Primary Model:** `gpt-4o-mini`

**Features:**
- 128K token context window
- Fast response times
- High quality medical reasoning
- Cost: ~$0.15 per 1M input tokens

**Configuration:**
```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Use Cases:**
- Production deployments
- Critical medical analysis
- Large context requirements
- Best quality outputs

### 2. Local Llama 3.2

**Supported Variants:**
- `llama-3.2-1b-instruct` - Fast, basic quality
- `llama-3.2-3b-instruct` - **Recommended** - Good balance
- `llama-3.2-8b-instruct` - Best quality, slower

**Features:**
- 100% local execution
- Zero API costs
- Complete privacy
- 4K-8K context window

**Configuration:**
```bash
# .env
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=llama-3.2-3b-instruct
LOCAL_LLM_API_KEY=not-needed
```

**Use Cases:**
- Development and testing
- Privacy-sensitive data
- Offline operation
- Cost-free experimentation

### 3. Anthropic Claude (Future Support)

**Note:** Claude API support can be added by extending the model client factory.

**Potential Configuration:**
```python
# Future implementation
if settings.LLM_PROVIDER == "anthropic":
    from anthropic import Anthropic
    client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
```

## Configuration

### Model Client Factory

Location: `src/orchestrator.py:31`

```python
def get_model_client() -> OpenAIChatCompletionClient:
    """
    Create model client based on LLM_PROVIDER setting.
    """
    if settings.LLM_PROVIDER == "local":
        # Local LLM with OpenAI-compatible endpoint
        return OpenAIChatCompletionClient(
            model=settings.LOCAL_LLM_MODEL,
            api_key=settings.LOCAL_LLM_API_KEY,
            base_url=settings.LOCAL_LLM_BASE_URL,
        )
    else:
        # OpenAI Cloud API
        return OpenAIChatCompletionClient(
            model=settings.OPENAI_MODEL,
            api_key=settings.OPENAI_API_KEY,
        )
```

### Environment Variables

All LLM configuration is managed through environment variables:

```bash
# Provider selection
LLM_PROVIDER=local  # or "openai"

# OpenAI settings
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Local LLM settings
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=llama-3.2-3b-instruct
LOCAL_LLM_API_KEY=not-needed
```

## Agent System Prompts

### Example: Neurologist Agent

Location: `src/agents/neurologist.py`

```python
system_message = """
You are an expert neurologist with 20+ years of clinical experience.

Your role:
1. Review patient clinical data and symptoms
2. Identify key neurological findings
3. Provide differential diagnoses
4. Suggest appropriate workup and testing

Guidelines:
- Base recommendations on current medical evidence
- Consider patient history and comorbidities
- Be specific about exam findings
- Note any red flags or urgent concerns

Format: Clear, clinical language appropriate for medical professionals.
"""
```

### Key Prompt Engineering Techniques

1. **Role Definition**: Clear expertise statement
2. **Structured Tasks**: Numbered responsibilities
3. **Guidelines**: Specific behavior expectations
4. **Output Format**: Expected response structure

### Temperature Settings

Different agents use different temperature settings:

```python
# Clinical accuracy (lower temperature)
neurologist_temp = 0.7

# Creative analysis (higher temperature)
prognosis_temp = 0.8

# Fact-checking (lowest temperature)
qa_validator_temp = 0.5
```

## Message Flow

### Multi-Agent Conversation

```python
# 1. User submits query
query = "Analyze this Parkinson's patient..."

# 2. Orchestrator initializes conversation
crew = NeuroCrew()
await crew.run_prognosis_analysis(patient_data)

# 3. RoundRobinGroupChat manages turns
# Each agent gets a turn to contribute

# 4. Agents process messages
for message in conversation:
    agent.process(message)  # → LLM call
    response = await llm.generate()
    conversation.append(response)

# 5. Termination condition checked
if max_messages or "TERMINATE" in message:
    break

# 6. Results returned to user
```

### Single Agent Consultation

```python
# Simpler flow for direct queries
chat = SingleAgentChat()
await chat.consult_neurologist("What is...")

# Creates temporary team with one agent
# Runs for 3 turns maximum
# Returns direct response
```

## Best Practices

### 1. Prompt Engineering

**DO:**
- ✅ Be specific about role and expertise
- ✅ Provide clear task structure
- ✅ Include examples when possible
- ✅ Specify output format
- ✅ Add safety guidelines for medical context

**DON'T:**
- ❌ Use vague instructions
- ❌ Mix multiple unrelated tasks
- ❌ Rely on implicit knowledge
- ❌ Ignore ethical considerations

### 2. Context Management

```python
# Keep context focused
task = f"""
Analyze THIS specific aspect:
{specific_data}

Ignore:
- Historical data from other patients
- Unrelated conditions
"""
```

### 3. Error Handling

```python
try:
    response = await agent.generate()
except RateLimitError:
    # Handle API limits
    await asyncio.sleep(60)
except InvalidRequestError:
    # Handle malformed requests
    logger.error("Invalid LLM request")
```

### 4. Cost Control

```python
# Monitor token usage
from src.logging import get_telemetry

telemetry = get_telemetry()
telemetry.track_llm_call(
    model=model_name,
    input_tokens=prompt_tokens,
    output_tokens=completion_tokens,
    cost=calculated_cost
)
```

## Performance Optimization

### 1. Reduce Token Usage

```python
# Concise system prompts
system_message = """Expert neurologist. Analyze symptoms.
Provide: 1) Diagnosis 2) Tests 3) Treatment."""

# vs verbose prompts (costs more)
```

### 2. Parallel Agent Calls

```python
# Sequential (slow)
result1 = await agent1.process()
result2 = await agent2.process()

# Parallel (fast)
results = await asyncio.gather(
    agent1.process(),
    agent2.process(),
)
```

### 3. Caching Strategies

```python
# Cache static agent prompts
@lru_cache(maxsize=128)
def get_agent_prompt(agent_type: str) -> str:
    return AGENT_PROMPTS[agent_type]
```

### 4. Model Selection

Choose appropriate model for task complexity:

| Task Complexity | OpenAI | Local Llama |
|----------------|--------|-------------|
| Simple queries | gpt-4o-mini | llama-3.2-1b |
| Standard medical | gpt-4o-mini | llama-3.2-3b |
| Complex analysis | gpt-4o | llama-3.2-8b |

### 5. Batch Processing

```python
# Process multiple patients in batch
async def analyze_batch(patients: list):
    tasks = [crew.analyze(p) for p in patients]
    return await asyncio.gather(*tasks)
```

## Token Limits

### Context Windows

| Model | Context Size | Recommended Use |
|-------|-------------|-----------------|
| gpt-4o-mini | 128K tokens | Large patient histories |
| llama-3.2-1b | 4K tokens | Short consultations |
| llama-3.2-3b | 8K tokens | Standard cases |
| llama-3.2-8b | 8K tokens | Complex analysis |

### Staying Within Limits

```python
def truncate_context(text: str, max_tokens: int = 4000) -> str:
    """Truncate text to fit within token limit."""
    import tiktoken

    encoder = tiktoken.encoding_for_model("gpt-4")
    tokens = encoder.encode(text)

    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
        text = encoder.decode(tokens)

    return text
```

## Monitoring & Logging

### LLM Telemetry

Location: `src/logging/telemetry.py`

```python
# Automatic tracking of:
- Model used
- Input/output tokens
- Cost per call
- Response time
- Success/failure rate

# Access session report:
telemetry.print_cost_summary()
telemetry.save_session_report()
```

### Audit Logging

All LLM interactions are logged for:
- HIPAA compliance
- Quality assurance
- Cost analysis
- Performance monitoring

```python
logger.log_agent_message(
    agent_name="Neurologist",
    message_type="response",
    content_preview=response[:500],
    correlation_id=session_id
)
```

## Switching Between Models

### Runtime Switching

```python
# Change in .env
LLM_PROVIDER=local  # or openai

# Restart application
# No code changes needed!
```

### Per-Agent Model Selection

Future enhancement to use different models for different agents:

```python
# Concept (not yet implemented)
class NeurologistAgent:
    model = "gpt-4o"  # Best quality for diagnosis

class QAValidatorAgent:
    model = "llama-3.2-3b"  # Sufficient for validation
```

## Testing with Different Models

### Test Script

```bash
# Test local LLM
python test_local_llm.py

# Test OpenAI (requires API key)
LLM_PROVIDER=openai python test_local_llm.py
```

### Unit Tests

```python
# Mock LLM for testing
from unittest.mock import Mock

def test_agent_response():
    mock_llm = Mock()
    mock_llm.generate.return_value = "Test response"

    agent = NeurologistAgent(llm_client=mock_llm)
    response = agent.process("Test query")

    assert response == "Test response"
```

## Future Enhancements

### Planned Features

1. **Multi-Model Routing**
   - Route simple queries to fast models
   - Use powerful models for complex cases

2. **Fine-Tuned Models**
   - Train specialized neurology model
   - Better domain-specific performance

3. **Retrieval-Augmented Generation (RAG)**
   - Add medical knowledge base
   - Ground responses in clinical literature

4. **Streaming Responses**
   - Real-time token streaming
   - Better UX for long responses

5. **Model A/B Testing**
   - Compare model performance
   - Optimize cost vs quality

## Resources

### Documentation
- [AutoGen Docs](https://microsoft.github.io/autogen/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Llama Documentation](https://llama.meta.com/)

### Code References
- Model client: `src/orchestrator.py:31`
- Agent definitions: `src/agents/`
- Configuration: `src/config/settings.py`
- Telemetry: `src/logging/telemetry.py`

### Configuration Files
- Environment: `.env`
- Agent prompts: `src/agents/*.py`
- Test cases: `tests/test_*.py`

---

**Note:** This system is designed for medical professional use and educational purposes. All LLM outputs should be reviewed by qualified healthcare providers before clinical application.
