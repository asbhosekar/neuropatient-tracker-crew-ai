"""
Neuro Patient Tracker - Streamlit Web Interface

Interactive web UI for the neurology patient tracking system.
"""
import streamlit as st
import asyncio
from datetime import datetime, date
from src.orchestrator import NeuroCrew, SingleAgentChat
from src.models.schemas import (
    Gender,
    NeurologicalCondition,
    SeverityLevel,
)
from src.config import settings
from autogen_agentchat.agents import AssistantAgent
import os


# Page configuration
st.set_page_config(
    page_title="Neuro Patient Tracker",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def check_llm_config():
    """Check if LLM is properly configured."""
    if settings.LLM_PROVIDER == "openai":
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "your_openai_api_key_here":
            st.error("❌ OPENAI_API_KEY not configured!")
            st.info("Please set your API key in .env file or as an environment variable.")
            st.stop()
    elif settings.LLM_PROVIDER == "local":
        st.success(f"🖥️ Using Local LLM: {settings.LOCAL_LLM_MODEL}")
        st.info(f"📡 Endpoint: {settings.LOCAL_LLM_BASE_URL}")
        with st.expander("ℹ️ Local LLM Setup"):
            st.markdown("""
            Make sure your local LLM server is running:
            - **LM Studio**: Start the local server on port 1234
            - **Ollama**: Run `ollama serve`
            - **llama.cpp**: Start with `--port 1234`

            Default model: `llama-3.2-3b-instruct`
            """)
    return True


def main():
    """Main Streamlit app."""

    # Check LLM configuration
    check_llm_config()

    # Header
    st.title("🧠 Neuro Patient Tracker")
    st.markdown("**AI-powered Patient Tracking System for Neurologists**")
    st.divider()

    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page:",
            ["🏠 Home", "👤 Patient Analysis", "🩺 Single Agent Consultation", "📊 About"],
            label_visibility="collapsed"
        )

        st.divider()
        st.markdown("### System Info")
        if settings.LLM_PROVIDER == "local":
            st.caption(f"🖥️ Local: {settings.LOCAL_LLM_MODEL}")
        else:
            st.caption(f"☁️ OpenAI: {settings.OPENAI_MODEL}")
        st.caption("AutoGen Multi-Agent System")

    # Page routing
    if page == "🏠 Home":
        show_home_page()
    elif page == "👤 Patient Analysis":
        show_patient_analysis_page()
    elif page == "🩺 Single Agent Consultation":
        show_single_agent_page()
    elif page == "📊 About":
        show_about_page()


def show_home_page():
    """Display home page."""
    st.header("Welcome to Neuro Patient Tracker")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 Key Features")
        st.markdown("""
        - **Multi-Agent Analysis**: Collaborative AI specialists
        - **Prognosis Tracking**: Trend analysis and predictions
        - **Clinical Insights**: Evidence-based recommendations
        - **HIPAA Compliance**: Audit logging and security
        """)

    with col2:
        st.subheader("🤖 AI Agents")
        agents = [
            ("Neurologist", "Clinical case review and assessment"),
            ("Prognosis Analyst", "Trend analysis and predictions"),
            ("Treatment Advisor", "Medication and treatment planning"),
            ("Report Generator", "Clinical summary reports"),
            ("QA Validator", "Data quality assurance"),
        ]
        for name, desc in agents:
            st.markdown(f"**{name}**: {desc}")

    st.divider()
    st.info("👈 Use the sidebar to navigate to different sections.")


def show_patient_analysis_page():
    """Patient prognosis analysis page."""
    st.header("👤 Patient Prognosis Analysis")
    st.markdown("Run multi-agent analysis on patient data")

    # Sample patient data option
    use_sample = st.checkbox("Use sample patient data", value=True)

    if use_sample:
        # Pre-filled sample data
        patient_id = st.text_input("Patient ID", value="PT-2024-001", disabled=True)
        condition = st.selectbox(
            "Primary Condition",
            options=[c.value for c in NeurologicalCondition],
            index=2,  # Parkinson's
            disabled=True
        )

        clinical_summary = st.text_area(
            "Clinical Summary",
            value="""Patient: 68-year-old male
Diagnosis: Parkinson's Disease (diagnosed 3 years ago)

Recent Visit History:
- Visit 1 (6 months ago): UPDRS Motor Score: 28, Stable tremor
- Visit 2 (5 months ago): UPDRS Motor Score: 30, Mild bradykinesia increase
- Visit 3 (4 months ago): UPDRS Motor Score: 32, Started Pramipexole
- Visit 4 (3 months ago): UPDRS Motor Score: 29, Improved with medication
- Visit 5 (2 months ago): UPDRS Motor Score: 31, Some wearing-off noted
- Visit 6 (current): UPDRS Motor Score: 34, Increased OFF time (~3 hrs/day)

Current Medications:
- Carbidopa/Levodopa 25/100mg TID
- Pramipexole 0.5mg TID

Concerns:
- Motor fluctuations increasing
- Reports ~3 hours of OFF time daily
- Sleep disturbances
- Mild cognitive complaints (MoCA: 24/30)""",
            height=300,
            disabled=True
        )
        visit_count = 6
    else:
        # Custom patient input
        patient_id = st.text_input("Patient ID", value="PT-2024-002")
        condition = st.selectbox(
            "Primary Condition",
            options=[c.value for c in NeurologicalCondition],
        )
        clinical_summary = st.text_area(
            "Clinical Summary",
            placeholder="Enter patient clinical data, visit history, medications, etc.",
            height=300
        )
        visit_count = st.number_input("Number of Visits", min_value=1, value=1)

    st.divider()

    if st.button("🚀 Run Multi-Agent Analysis", type="primary", use_container_width=True):
        if not clinical_summary.strip():
            st.error("Please provide clinical summary.")
            return

        # Prepare patient data
        patient_data = {
            "id": patient_id,
            "condition": condition,
            "visit_count": visit_count,
            "clinical_summary": clinical_summary,
        }

        # Create placeholder for streaming output
        analysis_placeholder = st.empty()
        log_placeholder = st.empty()  # For logging
        response_texts = []
        log_messages = []

        def log(msg):
            """Add log message and update display."""
            import datetime
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            log_messages.append(f"`{timestamp}` {msg}")
            log_placeholder.markdown("**📋 Event Log:**\n" + "\n".join(log_messages[-10:]))  # Show last 10
            print(f"[LOG {timestamp}] {msg}")  # Also print to terminal

        # Run analysis
        with st.spinner("Running multi-agent analysis... This may take a moment."):
            try:
                # Import nest_asyncio to allow nested event loops in Streamlit
                import nest_asyncio
                nest_asyncio.apply()

                async def run_analysis():
                    """Run multi-agent analysis and capture responses."""
                    log("🚀 Starting multi-agent analysis...")
                    
                    log("📦 Creating NeuroCrew...")
                    crew = NeuroCrew()
                    
                    # Use fewer messages for faster local LLM testing
                    log("👥 Setting up team with 6 agents (max 6 messages for speed)...")
                    crew.setup_team(max_messages=6)
                    log(f"✅ Team ready: {', '.join(crew.get_agent_names())}")

                    # Prepare task
                    task = f"""
Perform a comprehensive prognosis analysis for this patient:

Patient ID: {patient_data['id']}
Condition: {patient_data['condition']}
Recent Visits: {patient_data['visit_count']}

Clinical Data:
{patient_data['clinical_summary']}

Each specialist should contribute:
1. Neurologist: Review case, identify key clinical findings
2. Prognosis Analyst: Analyze trends and trajectory
3. Treatment Advisor: Suggest any treatment adjustments
4. QA Validator: Verify data accuracy
5. Report Generator: Summarize findings

Collaborate to provide a comprehensive assessment. When all specialists have contributed, end the discussion.
"""
                    log(f"📝 Task prepared ({len(task)} chars)")
                    log("🔄 Starting run_stream - waiting for LLM responses...")

                    # Stream the conversation
                    message_count = 0
                    async for message in crew._team.run_stream(task=task):
                        message_count += 1
                        msg_type = type(message).__name__
                        log(f"📨 Message #{message_count}: {msg_type}")
                        
                        if hasattr(message, 'content') and message.content:
                            agent_name = getattr(message, 'source', 'System')
                            log(f"   └─ From: {agent_name} ({len(str(message.content))} chars)")
                            response_texts.append(f"**{agent_name}:**\n\n{message.content}")
                            # Update display in real-time
                            analysis_placeholder.markdown("### Analysis Output\n\n" + "\n\n---\n\n".join(response_texts))
                        else:
                            log(f"   └─ No content (may be TaskResult)")
                    
                    log(f"✅ Stream complete. Total messages: {message_count}")

                # Run the analysis
                log("⏳ Calling asyncio.run()...")
                asyncio.run(run_analysis())

                st.success("✅ Analysis complete!")

            except Exception as e:
                log(f"❌ Error: {str(e)}")
                st.error(f"Error running analysis: {str(e)}")
                st.exception(e)


def show_single_agent_page():
    """Single agent consultation page."""
    st.header("🩺 Single Agent Consultation")
    st.markdown("Consult with a specific AI agent")

    # Agent selection
    agent_type = st.selectbox(
        "Select Agent",
        ["Neurologist", "Prognosis Analyst", "Treatment Advisor"],
    )

    # Agent-specific prompts
    if agent_type == "Neurologist":
        st.subheader("Neurologist Consultation")
        default_query = """A 45-year-old female presents with:
- Recurrent headaches, 4-5 per week for past 2 months
- Throbbing, unilateral, moderate-severe intensity
- Associated nausea and photophobia
- Duration: 4-12 hours
- Some relief with OTC ibuprofen but incomplete

What is your assessment and recommended workup?"""

    elif agent_type == "Prognosis Analyst":
        st.subheader("Prognosis Analysis")
        default_query = """Patient: 72-year-old male with Alzheimer's Disease
Duration: Diagnosed 2 years ago

MMSE Scores over time:
- 24 months ago: 24/30
- 18 months ago: 22/30
- 12 months ago: 21/30
- 6 months ago: 19/30
- Current: 17/30

Currently on Donepezil 10mg daily."""

    else:  # Treatment Advisor
        st.subheader("Treatment Recommendations")
        default_query = """Patient with epilepsy (focal seizures with impaired awareness)
- Current: Levetiracetam 1000mg BID
- Seizure frequency: 2-3 per month (previously 4-5/month)
- Side effects: Mild irritability, otherwise tolerating well
- Goal: Better seizure control

Should we adjust the treatment?"""

    query = st.text_area(
        "Your Question",
        value=default_query,
        height=200
    )

    if st.button("💬 Consult Agent", type="primary", use_container_width=True):
        if not query.strip():
            st.error("Please enter a question.")
            return

        # Create a placeholder for streaming output
        response_placeholder = st.empty()

        with st.spinner(f"Consulting {agent_type}..."):
            try:
                # Import nest_asyncio to allow nested event loops
                import nest_asyncio
                nest_asyncio.apply()

                # Create consultation
                chat = SingleAgentChat()

                # Run the appropriate consultation
                response_text = []

                async def run_consultation():
                    """Run consultation and collect responses."""
                    from autogen_agentchat.messages import TextMessage

                    # Create team
                    if agent_type == "Neurologist":
                        from src.agents import NeurologistAgent
                        agent = AssistantAgent(
                            name="Neurologist",
                            model_client=chat.model_client,
                            system_message=NeurologistAgent().system_message,
                        )
                    elif agent_type == "Prognosis Analyst":
                        from src.agents import PrognosisAnalystAgent
                        agent = AssistantAgent(
                            name="PrognosisAnalyst",
                            model_client=chat.model_client,
                            system_message=PrognosisAnalystAgent().system_message,
                        )
                    else:
                        from src.agents import TreatmentAdvisorAgent
                        agent = AssistantAgent(
                            name="TreatmentAdvisor",
                            model_client=chat.model_client,
                            system_message=TreatmentAdvisorAgent().system_message,
                        )

                    from autogen_agentchat.teams import RoundRobinGroupChat
                    from autogen_agentchat.conditions import MaxMessageTermination

                    termination = MaxMessageTermination(3)
                    team = RoundRobinGroupChat(
                        participants=[agent],
                        termination_condition=termination
                    )

                    # Stream messages
                    async for message in team.run_stream(task=query):
                        if hasattr(message, 'content') and message.content:
                            response_text.append(str(message.content))
                            # Update display in real-time
                            response_placeholder.markdown("### Response\n\n" + "\n\n---\n\n".join(response_text))

                # Run the consultation
                asyncio.run(run_consultation())

                st.success("✅ Consultation complete!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)


def show_about_page():
    """About page."""
    st.header("📊 About Neuro Patient Tracker")

    st.markdown("""
    ### Overview

    The Neuro Patient Tracker is an AI-powered system designed to assist neurologists
    with patient tracking, prognosis analysis, and clinical decision support.

    ### Technology Stack

    - **Framework**: Microsoft AutoGen (Multi-Agent AI)
    - **LLM**: OpenAI GPT-4o-mini
    - **UI**: Streamlit
    - **Backend**: FastAPI
    - **Database**: SQLAlchemy + SQLite
    - **Validation**: Pydantic v2

    ### Multi-Agent Architecture

    The system uses multiple specialized AI agents that collaborate to analyze patient data:

    1. **Clinical Architect**: Designs data models and ensures HIPAA compliance
    2. **Neurologist**: Reviews clinical cases and provides assessments
    3. **Prognosis Analyst**: Analyzes trends and predicts disease trajectories
    4. **Treatment Advisor**: Suggests treatment plans and adjustments
    5. **QA Validator**: Validates data quality and medical logic
    6. **Report Generator**: Creates comprehensive clinical reports

    ### Features

    - 📊 **Longitudinal Analysis**: Track patient progress over time
    - 🎯 **Prognosis Prediction**: AI-powered trajectory forecasting
    - 💊 **Treatment Optimization**: Evidence-based recommendations
    - 🔒 **HIPAA Compliance**: Audit logging and secure data handling
    - 📈 **Trend Visualization**: Clinical metric tracking

    ### Supported Conditions

    - Epilepsy
    - Migraines
    - Parkinson's Disease
    - Multiple Sclerosis
    - Alzheimer's Disease
    - Stroke
    - Neuropathy

    ### Version

    **v0.1.0** - Initial Release

    ---

    *Built with AI-powered multi-agent collaboration*
    """)


if __name__ == "__main__":
    main()
