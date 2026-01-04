# Documentation Index

## Welcome to Neuro Patient Tracker Documentation

This directory contains comprehensive documentation for the Neuro Patient Tracker system.

### 📂 Documentation Files

#### Core Documentation

- **[index.html](index.html)** - Main documentation homepage (open in browser)
- **[architecture.html](architecture.html)** - Interactive architecture diagram
- **[agents.md](agents.md)** - AI agents comprehensive guide
- **[claude.md](claude.md)** - LLM integration and configuration
- **[api.md](api.md)** - Complete API reference

### 🌐 How to View

#### Option 1: Open HTML Files in Browser

```bash
# Windows
start docs/index.html

# macOS
open docs/index.html

# Linux
xdg-open docs/index.html
```

#### Option 2: View Markdown Files

All `.md` files can be viewed in:
- VS Code (with Markdown Preview)
- GitHub
- Any text editor

### 📖 Documentation Structure

```
docs/
├── index.html              # Main documentation hub
├── architecture.html       # System architecture (interactive)
├── agents.md              # AI agents guide
├── claude.md              # LLM integration
├── api.md                 # API reference
├── images/                # Documentation images
└── README.md              # This file
```

### 🚀 Quick Links

#### Getting Started
- [Quick Start Guide](../QUICK_START.md)
- [Local LLM Setup](../LOCAL_LLM_SETUP.md)
- [Streamlit Guide](../STREAMLIT_GUIDE.md)

#### Architecture
- [Architecture Diagram](architecture.html) - Visual system overview
- [Data Flow](architecture.html#data-flow) - How data moves through system
- [Tech Stack](architecture.html#tech-stack) - Technologies used

#### AI Agents
- [Agent Overview](agents.md#overview) - What agents do
- [Agent Catalog](agents.md#agent-catalog) - All 6 agents detailed
- [Multi-Agent Workflows](agents.md#multi-agent-workflows) - How agents collaborate

#### LLM Integration
- [LLM Architecture](claude.md#llm-architecture) - How LLMs are integrated
- [Supported Models](claude.md#supported-models) - OpenAI & Llama 3.2
- [Configuration](claude.md#configuration) - Setup and customization
- [Best Practices](claude.md#best-practices) - Optimization tips

#### API Reference
- [Python API](api.md#python-api) - Core classes and methods
- [Data Models](api.md#data-models) - Pydantic models
- [Configuration](api.md#configuration-api) - Settings and environment
- [Logging](api.md#logging--telemetry) - Audit and telemetry

### 🎯 Documentation by Role

#### For Developers
1. Start with [Architecture](architecture.html)
2. Read [API Reference](api.md)
3. Check [Agents Guide](agents.md)
4. Review code in `src/`

#### For AI/ML Engineers
1. Read [Claude & LLM Integration](claude.md)
2. Study [Agent System Prompts](agents.md#system-prompts)
3. Check [Performance Optimization](claude.md#performance-optimization)

#### For Medical Professionals
1. Review [Agent Capabilities](agents.md#agent-catalog)
2. See [Multi-Agent Workflows](agents.md#multi-agent-workflows)
3. Check [Data Models](api.md#data-models) for medical records

#### For System Administrators
1. Check [Configuration Guide](claude.md#configuration)
2. Read [Local LLM Setup](../LOCAL_LLM_SETUP.md)
3. Review [Logging & Audit](api.md#logging--telemetry)

### 📚 Additional Resources

#### Project Root Documentation
- [README.md](../README.md) - Project overview
- [QUICK_START.md](../QUICK_START.md) - 3-minute setup
- [LOCAL_LLM_SETUP.md](../LOCAL_LLM_SETUP.md) - Llama 3.2 guide
- [STREAMLIT_GUIDE.md](../STREAMLIT_GUIDE.md) - Web UI guide

#### Code Examples
- [test_local_llm.py](../test_local_llm.py) - LLM connection test
- [tests/](../tests/) - Comprehensive test suite
- [src/main.py](../src/main.py) - CLI entry point
- [app.py](../app.py) - Streamlit application

### 🔧 Documentation Standards

#### Writing Style
- Clear and concise
- Code examples included
- Screenshots where helpful
- Professional medical tone

#### Code Examples
All code examples use:
- Python 3.10+ syntax
- Type hints
- Docstrings
- Error handling

#### Updates
Documentation is updated with:
- Each major feature
- API changes
- Configuration updates
- New agents or capabilities

### 📝 Contributing to Documentation

To update documentation:

1. Edit relevant `.md` or `.html` file
2. Follow existing formatting
3. Add code examples
4. Update index if adding new pages
5. Test all links

### 🐛 Issues

Found a documentation issue?
- Check existing issues
- Create detailed bug report
- Include page/section reference

### 📊 Documentation Metrics

Current documentation includes:
- 4 main documentation files
- 1 interactive HTML diagram
- 100+ code examples
- Complete API reference
- 6 agent guides

### 🎓 Learning Path

**Beginner Path:**
1. Read [Quick Start](../QUICK_START.md)
2. View [Architecture Diagram](architecture.html)
3. Try [Streamlit UI](../STREAMLIT_GUIDE.md)

**Intermediate Path:**
1. Study [Agents Guide](agents.md)
2. Read [LLM Integration](claude.md)
3. Review [API Reference](api.md)

**Advanced Path:**
1. Deep dive into code in `src/`
2. Study [AutoGen Framework](https://microsoft.github.io/autogen/)
3. Customize agents and prompts

### 🌟 Best Practices

When using documentation:
- Start with architecture overview
- Reference API docs while coding
- Check examples before implementing
- Test configurations incrementally

### 📞 Support

For help:
- Check [Troubleshooting](../LOCAL_LLM_SETUP.md#troubleshooting)
- Review test files for examples
- Check AutoGen documentation
- Review code comments

---

**Last Updated:** 2024
**Version:** 0.1.0
**Maintained by:** Development Team
