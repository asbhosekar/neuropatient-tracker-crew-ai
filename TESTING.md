# Testing Guide

## Overview

This guide covers all testing procedures for the Neuro Patient Tracker system, including unit tests, integration tests, and system verification.

## Table of Contents

- [Quick Test](#quick-test)
- [Unit Tests](#unit-tests)
- [Integration Tests](#integration-tests)
- [System Tests](#system-tests)
- [LLM Testing](#llm-testing)
- [Performance Testing](#performance-testing)
- [Manual Testing](#manual-testing)

## Quick Test

### 1. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check installed packages
pip list | grep -E "streamlit|pytest|pydantic|autogen"
```

### 2. Run All Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Expected output: 16 tests passed
```

### 3. Test Local LLM Connection

```bash
# Make sure local LLM server is running first!
python test_local_llm.py
```

### 4. Test Streamlit App

```bash
# Launch app
streamlit run app.py

# Check:
# - App loads without errors
# - LLM status shown correctly
# - All pages accessible
```

## Unit Tests

### Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Shared fixtures
├── test_models.py        # Data model tests
└── test_config.py        # Configuration tests
```

### Running Unit Tests

```bash
# Run all unit tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run specific test class
pytest tests/test_models.py::TestPatientModels -v

# Run specific test
pytest tests/test_models.py::TestPatientModels::test_patient_create -v
```

### Test Coverage

```bash
# Generate coverage report
pytest tests/ --cov=src --cov-report=html

# View report
# Open htmlcov/index.html in browser

# Coverage summary
pytest tests/ --cov=src --cov-report=term
```

### Test Categories

#### 1. Data Model Tests (`test_models.py`)

Tests for Pydantic models:

```bash
# Patient models
pytest tests/test_models.py::TestPatientModels -v

# Visit models
pytest tests/test_models.py::TestVisitModels -v

# Prognosis models
pytest tests/test_models.py::TestPrognosisModels -v

# Enumerations
pytest tests/test_models.py::TestEnums -v
```

**What's Tested:**
- Model creation and validation
- Field constraints (min/max values)
- Required vs optional fields
- Enum values
- Type coercion

#### 2. Configuration Tests (`test_config.py`)

Tests for settings:

```bash
pytest tests/test_config.py -v
```

**What's Tested:**
- Default configuration values
- Environment variable loading
- Data types
- Directory settings

### Writing New Tests

#### Example Test

```python
# tests/test_example.py
import pytest
from src.models.schemas import Patient, Gender, NeurologicalCondition
from datetime import date

class TestExample:
    """Example test class."""

    def test_patient_creation(self):
        """Test creating a patient."""
        patient = Patient(
            id="TEST-001",
            first_name="Test",
            last_name="Patient",
            date_of_birth=date(1980, 1, 1),
            gender=Gender.MALE,
            primary_condition=NeurologicalCondition.EPILEPSY
        )

        assert patient.id == "TEST-001"
        assert patient.first_name == "Test"
        assert patient.is_active is True

    def test_patient_validation_error(self):
        """Test patient validation."""
        with pytest.raises(ValueError):
            # Invalid date format should raise error
            Patient(
                id="TEST-001",
                first_name="",  # Empty name - should fail
                last_name="Test",
                date_of_birth=date(1980, 1, 1),
                gender=Gender.MALE,
                primary_condition=NeurologicalCondition.EPILEPSY
            )
```

#### Using Fixtures

```python
def test_with_fixture(sample_patient):
    """Use predefined fixture from conftest.py."""
    assert sample_patient.id == "PT-TEST-001"
    assert sample_patient.is_active is True
```

## Integration Tests

### Agent Integration Tests

Test agent initialization and basic functionality:

```python
# tests/test_agents_integration.py
import pytest
from src.agents import NeurologistAgent

@pytest.mark.asyncio
async def test_neurologist_initialization():
    """Test neurologist agent creation."""
    agent = NeurologistAgent()

    assert agent.system_message is not None
    assert "neurologist" in agent.system_message.lower()
    assert len(agent.system_message) > 100
```

### Orchestrator Integration Tests

Test multi-agent coordination:

```python
# tests/test_orchestrator_integration.py
import pytest
from src.orchestrator import NeuroCrew

@pytest.mark.asyncio
async def test_crew_initialization():
    """Test NeuroCrew initialization."""
    crew = NeuroCrew()

    agents = crew.get_agents()
    assert len(agents) == 6

    agent_names = crew.get_agent_names()
    assert "Neurologist" in agent_names
    assert "PrognosisAnalyst" in agent_names
```

## System Tests

### End-to-End Test

```bash
# Create test script
# tests/test_e2e.py
```

```python
import pytest
import asyncio
from src.orchestrator import NeuroCrew, SingleAgentChat

@pytest.mark.asyncio
async def test_single_agent_consultation():
    """Test single agent consultation workflow."""
    chat = SingleAgentChat()

    # This will actually call the LLM
    # Skip in CI/CD if no LLM available
    if not os.getenv("RUN_LLM_TESTS"):
        pytest.skip("LLM tests disabled")

    await chat.consult_neurologist("Test question")
    # If we get here, test passed (no exceptions)

@pytest.mark.asyncio
async def test_multi_agent_workflow():
    """Test multi-agent prognosis analysis."""
    crew = NeuroCrew()

    patient_data = {
        "id": "TEST-001",
        "condition": "parkinsons",
        "visit_count": 3,
        "clinical_summary": "Test patient data"
    }

    if not os.getenv("RUN_LLM_TESTS"):
        pytest.skip("LLM tests disabled")

    await crew.run_prognosis_analysis(patient_data)
```

### Run System Tests

```bash
# Enable LLM tests
export RUN_LLM_TESTS=1  # Linux/Mac
set RUN_LLM_TESTS=1     # Windows

# Run system tests
pytest tests/test_e2e.py -v -s
```

## LLM Testing

### Test Local LLM Connection

Use the provided test script:

```bash
# Ensure local LLM server is running
# Then run:
python test_local_llm.py
```

**Expected Output:**
```
🧠 Neuro Patient Tracker - Local LLM Test

🔧 Current Configuration
==================================================
Provider: local
🖥️  Local LLM Model: llama-3.2-3b-instruct
📡 Base URL: http://localhost:1234/v1
==================================================

🔌 Testing Model Client Connection...
✅ Model client created successfully!

💬 Testing Simple Query...
[Agent responses displayed]

✅ Query test successful!

🎉 All tests passed!
```

### Test OpenAI Connection

```bash
# Set environment
export LLM_PROVIDER=openai
export OPENAI_API_KEY=sk-your-key

# Run test
python test_local_llm.py
```

### Mock LLM for Unit Tests

```python
from unittest.mock import Mock, AsyncMock

def test_agent_with_mock_llm():
    """Test agent without calling real LLM."""
    mock_client = Mock()
    mock_client.generate = AsyncMock(return_value="Mock response")

    # Use mock in tests
    # This avoids API costs during testing
```

## Performance Testing

### Measure Response Times

```python
# tests/test_performance.py
import time
import pytest
from src.orchestrator import SingleAgentChat

@pytest.mark.asyncio
async def test_response_time():
    """Measure agent response time."""
    chat = SingleAgentChat()

    start = time.time()
    await chat.consult_neurologist("Quick test question")
    duration = time.time() - start

    # Should respond within reasonable time
    assert duration < 30  # 30 seconds max

    print(f"Response time: {duration:.2f}s")
```

### Load Testing

```python
import asyncio
from src.orchestrator import SingleAgentChat

async def load_test(num_requests=10):
    """Test system under load."""
    chat = SingleAgentChat()

    tasks = []
    for i in range(num_requests):
        task = chat.consult_neurologist(f"Test question {i}")
        tasks.append(task)

    start = time.time()
    await asyncio.gather(*tasks)
    duration = time.time() - start

    print(f"Processed {num_requests} requests in {duration:.2f}s")
    print(f"Average: {duration/num_requests:.2f}s per request")
```

## Manual Testing

### Streamlit App Testing Checklist

#### Home Page
- [ ] Page loads without errors
- [ ] LLM status displayed correctly
- [ ] Agent list shows all 6 agents
- [ ] Navigation sidebar works

#### Patient Analysis Page
- [ ] Sample data loads correctly
- [ ] Custom input accepted
- [ ] Analysis runs successfully
- [ ] Output displayed properly
- [ ] Errors handled gracefully

#### Single Agent Consultation Page
- [ ] All agent types selectable
- [ ] Pre-filled examples work
- [ ] Custom queries accepted
- [ ] Responses displayed
- [ ] Agent switching works

#### About Page
- [ ] System info accurate
- [ ] Tech stack listed
- [ ] Features described
- [ ] Links work

### CLI Testing Checklist

```bash
# Run main CLI
python -m src.main
```

Test each menu option:
- [ ] Demo mode (option 1)
- [ ] Neurologist consultation (option 2)
- [ ] Prognosis analysis (option 3)
- [ ] Treatment advice (option 4)
- [ ] Cost summary (option 5)
- [ ] Exit (option 0)

### Configuration Testing

Test different configurations:

#### Local LLM
```bash
# .env
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
```
- [ ] Connects successfully
- [ ] Displays local model name
- [ ] Responses generated

#### OpenAI
```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
```
- [ ] Connects successfully
- [ ] Displays OpenAI model name
- [ ] Responses generated
- [ ] Costs tracked

## Continuous Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -e ".[dev]"

    - name: Run unit tests
      run: |
        pytest tests/ -v --cov=src

    - name: Upload coverage
      run: |
        bash <(curl -s https://codecov.io/bash)
```

## Test Automation

### Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
pytest tests/test_models.py tests/test_config.py -v
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### Make Test Commands

```makefile
# Makefile
.PHONY: test test-unit test-integration test-coverage

test:
	pytest tests/ -v

test-unit:
	pytest tests/test_models.py tests/test_config.py -v

test-integration:
	pytest tests/test_e2e.py -v -s

test-coverage:
	pytest tests/ --cov=src --cov-report=html
	open htmlcov/index.html
```

## Troubleshooting Tests

### Common Issues

#### Import Errors
```bash
# Fix: Add src to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}/src"
```

#### Fixture Not Found
```bash
# Fix: Check conftest.py is in tests/ directory
ls tests/conftest.py
```

#### Async Test Errors
```python
# Fix: Add @pytest.mark.asyncio decorator
@pytest.mark.asyncio
async def test_async_function():
    await some_async_function()
```

#### LLM Connection Failures
```bash
# Fix: Check server is running
curl http://localhost:1234/v1/models

# Fix: Check environment variables
echo $LLM_PROVIDER
echo $LOCAL_LLM_BASE_URL
```

## Test Reports

### Generate HTML Report

```bash
pytest tests/ --html=report.html --self-contained-html
```

### Generate JUnit XML

```bash
pytest tests/ --junitxml=report.xml
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Fast Tests**: Unit tests should run quickly
3. **Meaningful Names**: Use descriptive test names
4. **Arrange-Act-Assert**: Follow AAA pattern
5. **Mock External Services**: Don't depend on LLM for unit tests
6. **Test Edge Cases**: Include boundary conditions
7. **Document Tests**: Add docstrings to test functions

## Next Steps

After testing:
1. Review coverage report
2. Add tests for uncovered code
3. Set up CI/CD pipeline
4. Configure automated testing
5. Monitor test results

---

**For more information:**
- pytest Documentation: https://docs.pytest.org/
- Test examples in `tests/` directory
- AutoGen testing guide: https://microsoft.github.io/autogen/
