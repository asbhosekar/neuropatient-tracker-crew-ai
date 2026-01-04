# Quick Start - Local Llama 3.2

## ⚡ 3-Step Setup

### Step 1: Configure `.env`
```bash
# Copy the example
copy .env.example .env

# Your .env should have:
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://localhost:1234/v1
LOCAL_LLM_MODEL=llama-3.2-3b-instruct
```

### Step 2: Start Local LLM Server

**Using LM Studio** (Easiest for Windows):
1. Download from https://lmstudio.ai/
2. Download model: "llama-3.2-3b-instruct"
3. Go to "Local Server" tab
4. Click "Start Server" (port 1234)

**Using Ollama**:
```bash
ollama pull llama3.2
ollama serve
```
Then update `.env`: `LOCAL_LLM_BASE_URL=http://localhost:11434/v1`

### Step 3: Run the App

**Test Connection**:
```bash
python test_local_llm.py
```

**CLI Interface**:
```bash
python -m src.main
```

**Web Interface** (Recommended):
```bash
streamlit run app.py
```

## 🎯 What You Get

### In Streamlit Web UI:
1. **Home** - Overview and agent info
2. **Patient Analysis** - Multi-agent prognosis analysis
3. **Single Agent** - Consult specific AI agents
4. **About** - System info

### Sample Data Included:
- Parkinson's Disease case with 6 visits
- Pre-filled queries for each agent
- Clinical assessments and medications

## 🔍 Quick Test

1. Open Streamlit: `streamlit run app.py`
2. Check banner shows: "🖥️ Using Local LLM: llama-3.2-3b-instruct"
3. Go to "Single Agent Consultation"
4. Click "Consult Agent" (uses pre-filled example)
5. Watch your local Llama respond!

## 🐛 Troubleshooting

**Can't connect?**
- Check LM Studio/Ollama is running
- Verify port 1234 (or 11434 for Ollama)
- Run: `curl http://localhost:1234/v1/models`

**Slow responses?**
- Use smaller model: llama-3.2-1b-instruct
- Increase GPU layers in LM Studio
- Close other GPU applications

**Need OpenAI instead?**
```bash
# In .env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
```

## 📖 Full Documentation

- **[LOCAL_LLM_SETUP.md](LOCAL_LLM_SETUP.md)** - Complete setup guide
- **[STREAMLIT_GUIDE.md](STREAMLIT_GUIDE.md)** - Web UI features
- **[README.md](README.md)** - Full project documentation

## 💡 Tips

1. **For best results**: Use llama-3.2-3b or larger
2. **For privacy**: Local LLM keeps all data on your machine
3. **For cost**: Local = free, OpenAI = paid per token
4. **For speed**: Depends on your GPU (RTX 3060+ recommended)

---

Ready in 3 minutes! 🚀
