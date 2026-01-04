# Local LLM Setup Guide - Llama 3.2

This guide explains how to connect the Neuro Patient Tracker to your local Llama 3.2 model.

## Quick Setup

### 1. Configure Environment Variables

Edit your `.env` file:

```bash
# Set provider to local
LLM_PROVIDER=local

# Local LLM Configuration
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=llama-3.2-3b-instruct
LOCAL_LLM_API_KEY=not-needed
```

### 2. Start Your Local LLM Server

Choose one of the following methods:

#### Option A: LM Studio (Recommended for Windows)

1. **Download LM Studio** from https://lmstudio.ai/
2. **Download Llama 3.2** model:
   - Open LM Studio
   - Search for "llama-3.2-3b-instruct"
   - Download the model
3. **Start the Server**:
   - Go to "Local Server" tab
   - Select your Llama 3.2 model
   - Click "Start Server"
   - Default port: 1234

#### Option B: Ollama

1. **Install Ollama**:
   ```bash
   # Windows (PowerShell as Admin)
   winget install Ollama.Ollama

   # Or download from https://ollama.ai/
   ```

2. **Download Llama 3.2**:
   ```bash
   ollama pull llama3.2
   ```

3. **Start Server**:
   ```bash
   ollama serve
   ```

4. **Update .env** for Ollama:
   ```bash
   LOCAL_LLM_BASE_URL=http://localhost:11434/v1
   LOCAL_LLM_MODEL=llama3.2
   ```

#### Option C: llama.cpp Server

1. **Download llama.cpp**:
   ```bash
   git clone https://github.com/ggerganov/llama.cpp
   cd llama.cpp
   make
   ```

2. **Download Model** (GGUF format):
   - Get Llama 3.2 GGUF from Hugging Face
   - Place in `models/` directory

3. **Start Server**:
   ```bash
   ./server -m models/llama-3.2-3b-instruct.gguf --port 1234
   ```

### 3. Verify Connection

Test that your local LLM is accessible:

```bash
# Test with curl
curl http://localhost:1234/v1/models

# Or use Python
python -c "import requests; print(requests.get('http://localhost:1234/v1/models').json())"
```

## Running the Application

### Command Line Interface

```bash
python -m src.main
```

You should see:
```
🖥️  Using Local LLM: llama-3.2-3b-instruct
📡 Endpoint: http://localhost:1234/v1
   Make sure your local LLM server is running!
```

### Streamlit Web Interface

```bash
streamlit run app.py
```

The app will show:
- ✅ Green banner: "Using Local LLM: llama-3.2-3b-instruct"
- 📡 Endpoint information
- ℹ️ Setup instructions (expandable)

## Configuration Options

### Different Port

If your local server uses a different port:

```bash
# .env
LOCAL_LLM_BASE_URL=http://localhost:8080/v1
```

### Different Model

To use a different Llama variant:

```bash
# .env
LOCAL_LLM_MODEL=llama-3.2-1b-instruct  # Smaller, faster
# or
LOCAL_LLM_MODEL=llama-3.2-8b-instruct  # Larger, more capable
```

### Switch Back to OpenAI

To use OpenAI instead of local LLM:

```bash
# .env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-actual-api-key
OPENAI_MODEL=gpt-4o-mini
```

## Performance Optimization

### LM Studio Settings

For better performance in LM Studio:
1. **GPU Offload**: Set layers based on your GPU
   - RTX 3060 (6GB): ~20-25 layers
   - RTX 3080 (10GB): ~30-35 layers
   - RTX 4090 (24GB): All layers
2. **Context Length**: 4096 or 8192 tokens
3. **Temperature**: 0.7 (medical tasks prefer consistency)

### Model Selection

Choose based on your hardware:

| Model | RAM | VRAM | Speed | Quality |
|-------|-----|------|-------|---------|
| Llama 3.2 1B | 2GB | 2GB | Fast | Good |
| Llama 3.2 3B | 4GB | 4GB | Medium | Better |
| Llama 3.2 8B | 8GB | 8GB | Slow | Best |

For medical applications, we recommend **3B** as the minimum for reasonable quality.

## Troubleshooting

### Connection Refused

```
Error: Connection refused to http://localhost:1234
```

**Solution**:
1. Check if server is running
2. Verify port number in `.env`
3. Check firewall settings

### Model Not Loaded

```
Error: No model loaded
```

**Solution**:
- In LM Studio: Select and load a model before starting server
- In Ollama: Run `ollama pull llama3.2` first

### Slow Responses

**Solutions**:
1. Use smaller model (1B or 3B instead of 8B)
2. Reduce context length
3. Increase GPU offload layers
4. Close other applications using GPU

### Out of Memory

```
Error: CUDA out of memory
```

**Solutions**:
1. Use smaller model
2. Reduce GPU layers
3. Reduce context length
4. Use CPU-only mode (slower but works)

## API Compatibility

The local LLM server must support OpenAI-compatible API endpoints:
- `/v1/models` - List available models
- `/v1/chat/completions` - Chat completions
- `/v1/completions` - Text completions

Most modern local LLM servers (LM Studio, Ollama, llama.cpp) support this by default.

## Testing the Setup

### Quick Test

```python
from src.orchestrator import get_model_client

# This will print which LLM is being used
client = get_model_client()
print("LLM client created successfully!")
```

### Full Test - Single Agent

```bash
# Run the demo
python -m src.main

# Choose option 2 (Single agent demo - Neurologist)
```

### Streamlit Test

1. Start Streamlit: `streamlit run app.py`
2. Go to "Single Agent Consultation"
3. Select "Neurologist"
4. Click "Consult Agent"
5. Should see response from your local Llama model

## Model Comparison

### Llama 3.2 vs GPT-4o-mini

| Aspect | Llama 3.2 (Local) | GPT-4o-mini (OpenAI) |
|--------|-------------------|----------------------|
| Cost | Free | ~$0.15/1M tokens |
| Privacy | 100% local | Cloud-based |
| Speed | Depends on hardware | Fast |
| Quality | Good | Excellent |
| Context | 4K-8K tokens | 128K tokens |

### Recommended Use Cases

**Use Local Llama 3.2 for**:
- Development and testing
- Privacy-sensitive data
- Offline operation
- Cost-free experimentation

**Use OpenAI GPT-4o-mini for**:
- Production deployment
- Best quality responses
- Large context needs
- Fastest response times

## Environment Variables Reference

```bash
# Provider Selection
LLM_PROVIDER=local              # "local" or "openai"

# Local LLM Settings
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=llama-3.2-3b-instruct
LOCAL_LLM_API_KEY=not-needed    # Some servers might need this

# OpenAI Settings (when LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## Next Steps

1. ✅ Configure `.env` file
2. ✅ Start local LLM server
3. ✅ Test connection
4. ✅ Run the application
5. 📊 Monitor performance
6. 🎯 Optimize settings based on your hardware

For issues or questions, check the main README.md or STREAMLIT_GUIDE.md.
