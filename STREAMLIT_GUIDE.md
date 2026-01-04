# Streamlit Web Interface Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install Streamlit (if not already installed)
pip install streamlit

# Or install all project dependencies
pip install -e .
```

### 2. Configure API Key

Make sure your OpenAI API key is configured:

```bash
# Copy the example .env file
copy .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=your-actual-api-key-here
```

### 3. Run the Streamlit App

```bash
streamlit run app.py
```

The app will automatically open in your default browser at `http://localhost:8501`

## Features

### 🏠 Home Page
- Overview of the system capabilities
- List of AI agents and their roles
- Quick navigation guide

### 👤 Patient Analysis
- **Multi-Agent Analysis**: Run collaborative AI analysis on patient data
- **Sample Data**: Pre-filled patient case for quick testing
- **Custom Input**: Enter your own patient data
- Includes sample Parkinson's Disease case with:
  - Visit history and UPDRS scores
  - Medication tracking
  - Clinical concerns and cognitive assessments

### 🩺 Single Agent Consultation
- Consult with specific AI agents:
  - **Neurologist**: Clinical case review and diagnosis
  - **Prognosis Analyst**: Trend analysis and predictions
  - **Treatment Advisor**: Medication recommendations
- Pre-filled examples for each agent type
- Custom query support

### 📊 About
- System information
- Technology stack details
- Supported neurological conditions
- Multi-agent architecture overview

## Usage Examples

### Running Multi-Agent Analysis

1. Navigate to "Patient Analysis" page
2. Use the sample data (default) or enter custom patient info
3. Click "Run Multi-Agent Analysis"
4. View the collaborative analysis from all AI agents

### Consulting a Specific Agent

1. Navigate to "Single Agent Consultation"
2. Select the agent (Neurologist, Prognosis Analyst, or Treatment Advisor)
3. Review the pre-filled example or enter your own query
4. Click "Consult Agent"
5. View the agent's response

## Testing

Run the test suite to verify everything is working:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### API Key Not Found
- Error: "OPENAI_API_KEY not configured!"
- Solution: Check your `.env` file and ensure the API key is set correctly

### Import Errors
- Error: Module not found
- Solution: Make sure all dependencies are installed:
  ```bash
  pip install -r requirements.txt
  # or
  pip install streamlit pyautogen openai pydantic
  ```

### Port Already in Use
- Error: Port 8501 is already in use
- Solution: Use a different port:
  ```bash
  streamlit run app.py --server.port 8502
  ```

## Advanced Configuration

### Streamlit Configuration

Create a `.streamlit/config.toml` file for custom settings:

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
headless = true
```

### Environment Variables

Additional environment variables you can configure in `.env`:

```bash
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./neuro_tracker.db
DEBUG=false
LOG_LEVEL=INFO
```

## Architecture

The Streamlit app integrates with the existing AutoGen multi-agent system:

```
app.py (Streamlit UI)
    ↓
src/orchestrator.py (NeuroCrew, SingleAgentChat)
    ↓
src/agents/ (Individual AI Agents)
    ↓
OpenAI API (GPT-4o-mini)
```

## Next Steps

- Customize the UI theme in `.streamlit/config.toml`
- Add more agent consultation types
- Implement patient data persistence
- Add visualization for prognosis trends
- Create export functionality for reports

## Support

For issues or questions:
- Check the main README.md
- Review test files in `tests/` for usage examples
- Check AutoGen documentation: https://microsoft.github.io/autogen/
