"""
Neuro Patient Tracker - Streamlit Web Interface

Interactive web UI for the neurology patient tracking system.
Professional clinical-grade interface with custom styling.
"""
import streamlit as st
import asyncio
import json
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
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_clinical_css():
    """Inject professional clinical CSS styling."""
    st.markdown("""
    <style>
    /* ── Import clean medical font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1a2e 0%, #1a2744 100%);
        border-right: 2px solid #2a4a7f;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e8f0;
    }
    section[data-testid="stSidebar"] .stRadio label span {
        font-size: 0.95rem;
    }

    /* ── Main header banner ── */
    .clinical-banner {
        background: linear-gradient(135deg, #0d2137 0%, #1a3a5c 50%, #0d2137 100%);
        border: 1px solid #2a5a8f;
        border-radius: 8px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 1.2rem;
    }
    .clinical-banner .banner-icon {
        font-size: 2.5rem;
        line-height: 1;
    }
    .clinical-banner .banner-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .clinical-banner .banner-subtitle {
        font-size: 0.9rem;
        color: #8ab4e8;
        margin: 0.2rem 0 0 0;
        font-weight: 400;
    }

    /* ── Status badge (LLM config) ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .status-badge.online {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-badge.offline {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .status-dot {
        width: 7px; height: 7px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot.green { background: #4ade80; }
    .status-dot.red   { background: #f87171; }

    /* ── Card containers ── */
    .clinical-card {
        background: linear-gradient(135deg, #111b2e 0%, #162035 100%);
        border: 1px solid #253554;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .clinical-card:hover {
        border-color: #3b6cb5;
    }
    .clinical-card h3 {
        color: #8ab4e8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #253554;
    }
    .clinical-card p {
        color: #c8d8e8;
        font-size: 0.92rem;
        line-height: 1.6;
        margin: 0;
    }

    /* ── Agent cards ── */
    .agent-card {
        background: linear-gradient(135deg, #111b2e 0%, #162035 100%);
        border: 1px solid #253554;
        border-left: 3px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
        transition: all 0.2s;
    }
    .agent-card:hover {
        border-left-color: #60a5fa;
        background: linear-gradient(135deg, #142240 0%, #1a2a48 100%);
    }
    .agent-card .agent-name {
        font-weight: 600;
        color: #e0e8f5;
        font-size: 0.95rem;
    }
    .agent-card .agent-role {
        color: #8898b0;
        font-size: 0.82rem;
        margin-top: 0.15rem;
    }

    /* ── Patient card ── */
    .patient-header {
        background: linear-gradient(135deg, #0d1f35 0%, #15294a 100%);
        border: 1px solid #2a4a7f;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .patient-header .patient-name {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
    }
    .patient-header .patient-meta {
        color: #7a9ec5;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }

    /* ── Metric overrides ── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0f1c30 0%, #152240 100%);
        border: 1px solid #253554;
        border-radius: 8px;
        padding: 0.8rem 1rem;
    }
    [data-testid="stMetric"] label {
        color: #6b8cad !important;
        font-size: 0.75rem !important;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: #e0ecf5 !important;
        font-size: 1.2rem !important;
        font-weight: 600;
    }

    /* ── Buttons ── */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
        border: 1px solid #3b82f6;
        font-weight: 600;
        letter-spacing: 0.02em;
        padding: 0.6rem 1.5rem;
        border-radius: 8px;
        transition: all 0.2s;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        border-color: #60a5fa;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    /* ── Text areas and inputs ── */
    .stTextArea textarea, .stTextInput input {
        background: #0d1825 !important;
        border: 1px solid #253554 !important;
        border-radius: 6px !important;
        color: #c8d8e8 !important;
        font-family: 'Inter', monospace !important;
        font-size: 0.88rem !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: #0d1825 !important;
        border: 1px solid #253554 !important;
        border-radius: 6px !important;
    }

    /* ── Analysis output ── */
    .agent-response {
        background: linear-gradient(135deg, #0e1a2d 0%, #132038 100%);
        border: 1px solid #253554;
        border-left: 3px solid #3b82f6;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 1rem;
    }
    .agent-response .agent-label {
        color: #60a5fa;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 0.6rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #1e3050;
    }
    .agent-response .agent-content {
        color: #c8d8e8;
        font-size: 0.9rem;
        line-height: 1.7;
    }

    /* ── Event log ── */
    .event-log {
        background: #080e18;
        border: 1px solid #1a2840;
        border-radius: 6px;
        padding: 0.8rem 1rem;
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 0.78rem;
        color: #5a7a98;
        max-height: 200px;
        overflow-y: auto;
    }

    /* ── Feature list on home ── */
    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        padding: 0.7rem 0;
        border-bottom: 1px solid #1a2840;
    }
    .feature-item:last-child { border-bottom: none; }
    .feature-icon {
        width: 32px; height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.2);
    }
    .feature-title { font-weight: 600; color: #e0e8f5; font-size: 0.92rem; }
    .feature-desc { color: #7a94b0; font-size: 0.82rem; margin-top: 0.1rem; }

    /* ── Dividers ── */
    hr {
        border: none;
        border-top: 1px solid #1e3050;
        margin: 1.5rem 0;
    }

    /* ── Section headers ── */
    .section-header {
        color: #8ab4e8;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.8rem;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #1e3050;
    }

    /* ── About page tech stack ── */
    .tech-badge {
        display: inline-block;
        padding: 0.25rem 0.65rem;
        background: rgba(59, 130, 246, 0.1);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 4px;
        color: #8ab4e8;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
    }

    /* ── Condition badge ── */
    .condition-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        background: rgba(139, 92, 246, 0.15);
        color: #a78bfa;
        border: 1px solid rgba(139, 92, 246, 0.25);
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def check_llm_config():
    """Check if LLM is properly configured. Returns status for sidebar."""
    if settings.LLM_PROVIDER == "openai":
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "your_openai_api_key_here":
            st.error("OPENAI_API_KEY not configured!")
            st.info("Please set your API key in .env file or as an environment variable.")
            st.stop()
        return "openai", settings.OPENAI_MODEL
    elif settings.LLM_PROVIDER == "local":
        return "local", settings.LOCAL_LLM_MODEL
    return "unknown", "N/A"


def main():
    """Main Streamlit app."""
    inject_clinical_css()

    provider, model_name = check_llm_config()

    # Banner header
    st.markdown("""
    <div class="clinical-banner">
        <div class="banner-icon">+</div>
        <div>
            <div class="banner-title">Neuro Patient Tracker</div>
            <div class="banner-subtitle">AI-Powered Clinical Decision Support System for Neurology</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0 1rem 0;">
            <div style="font-size:1.6rem; font-weight:700; color:#e0ecf5; letter-spacing:-0.02em;">NeuroCrew AI</div>
            <div style="font-size:0.75rem; color:#5a7a98; margin-top:0.2rem;">Multi-Agent Clinical Platform</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        page = st.radio(
            "Select Page:",
            ["Dashboard", "Patient Analysis", "Agent Consultation", "System Info"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        # LLM Status
        st.markdown('<div class="section-header">LLM Status</div>', unsafe_allow_html=True)
        if provider == "local":
            st.markdown(f"""
            <div class="status-badge online">
                <span class="status-dot green"></span> Local LLM Active
            </div>
            <div style="color:#5a7a98; font-size:0.75rem; margin-top:0.5rem;">
                Model: {model_name}<br>
                Endpoint: {settings.LOCAL_LLM_BASE_URL}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="status-badge online">
                <span class="status-dot green"></span> OpenAI Active
            </div>
            <div style="color:#5a7a98; font-size:0.75rem; margin-top:0.5rem;">
                Model: {model_name}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown('<div class="section-header">Session</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="color:#5a7a98; font-size:0.75rem;">
            Date: {datetime.now().strftime('%Y-%m-%d')}<br>
            Engine: AutoGen 0.4+<br>
            Agents: 6 specialists
        </div>
        """, unsafe_allow_html=True)

    # Page routing
    if page == "Dashboard":
        show_home_page()
    elif page == "Patient Analysis":
        show_patient_analysis_page()
    elif page == "Agent Consultation":
        show_single_agent_page()
    elif page == "System Info":
        show_about_page()


def show_home_page():
    """Display dashboard home page."""

    # Quick stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("AI Agents", "6")
    with col2:
        st.metric("Conditions", "7")
    with col3:
        st.metric("Test Patients", "12")
    with col4:
        st.metric("LLM Provider", settings.LLM_PROVIDER.upper())

    st.markdown("---")

    # Two-column layout
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("""
        <div class="clinical-card">
            <h3>Platform Capabilities</h3>
            <div class="feature-item">
                <div class="feature-icon">MA</div>
                <div>
                    <div class="feature-title">Multi-Agent Analysis</div>
                    <div class="feature-desc">6 specialized AI agents collaborate on each case</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">PT</div>
                <div>
                    <div class="feature-title">Prognosis Tracking</div>
                    <div class="feature-desc">Longitudinal trend analysis with trajectory projection</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">TX</div>
                <div>
                    <div class="feature-title">Treatment Optimization</div>
                    <div class="feature-desc">Evidence-based medication and dosage recommendations</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">QA</div>
                <div>
                    <div class="feature-title">Data Validation</div>
                    <div class="feature-desc">Automated clinical data quality assurance checks</div>
                </div>
            </div>
            <div class="feature-item">
                <div class="feature-icon">HC</div>
                <div>
                    <div class="feature-title">HIPAA Compliance</div>
                    <div class="feature-desc">Full audit logging with PHI hashing and access control</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="clinical-card"><h3>Clinical AI Agents</h3>', unsafe_allow_html=True)

        agents = [
            ("Neurologist", "Clinical case review, differential diagnosis, red flag screening"),
            ("Prognosis Analyst", "Disease trajectory projection with confidence scoring"),
            ("Treatment Advisor", "Medication optimization with drug interaction checks"),
            ("Report Generator", "Integrated clinical report synthesis"),
            ("QA Validator", "Score range validation and anomaly detection"),
            ("Clinical Architect", "HIPAA compliance and data model review"),
        ]
        for name, desc in agents:
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-name">{name}</div>
                <div class="agent-role">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Supported conditions
    st.markdown('<div class="section-header">Supported Neurological Conditions</div>', unsafe_allow_html=True)
    conditions = ["Epilepsy", "Migraine", "Parkinson's Disease", "Multiple Sclerosis",
                   "Alzheimer's Disease", "Stroke", "Neuropathy"]
    badges = " ".join([f'<span class="condition-badge">{c}</span>' for c in conditions])
    st.markdown(badges, unsafe_allow_html=True)


def _load_test_patients():
    """Load test patients from JSON file."""
    try:
        with open("data/test_patients.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("patients", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _format_patient_summary(patient: dict) -> str:
    """Format a patient record into a clinical summary string."""
    dob = patient.get("date_of_birth", "Unknown")
    gender = patient.get("gender", "Unknown")
    condition = patient.get("primary_condition", "Unknown")
    visits = patient.get("visits", [])

    lines = [
        f"Patient: {patient['first_name']} {patient['last_name']}",
        f"DOB: {dob} | Gender: {gender}",
        f"Primary Condition: {condition}",
        "",
        f"Visit History ({len(visits)} visits):",
    ]

    for i, visit in enumerate(visits, 1):
        visit_date = visit.get("visit_date", "Unknown")[:10]
        complaint = visit.get("chief_complaint", "N/A")
        assessment = visit.get("assessment", {})
        scores = []
        if assessment.get("mmse_score") is not None:
            scores.append(f"MMSE: {assessment['mmse_score']}")
        if assessment.get("moca_score") is not None:
            scores.append(f"MoCA: {assessment['moca_score']}")
        if assessment.get("motor_function_score") is not None:
            scores.append(f"Motor: {assessment['motor_function_score']}")
        if assessment.get("symptom_severity") is not None:
            scores.append(f"Severity: {assessment['symptom_severity']}/10")
        score_str = ", ".join(scores) if scores else "No scores"
        notes = assessment.get("notes", "")
        lines.append(f"- Visit {i} ({visit_date}): {complaint}")
        lines.append(f"  Scores: {score_str}")
        if notes:
            lines.append(f"  Notes: {notes}")

    if visits:
        latest = visits[0]
        meds = latest.get("medications", [])
        if meds:
            lines.append("")
            lines.append("Current Medications:")
            for med in meds:
                if med.get("is_active", True):
                    lines.append(f"- {med['name']} {med.get('dosage', '')} {med.get('frequency', '')}")

        dx = latest.get("diagnosis_notes", "")
        if dx:
            lines.append("")
            lines.append(f"Diagnosis Notes: {dx}")

        plan = latest.get("treatment_plan", "")
        if plan:
            lines.append(f"Treatment Plan: {plan}")

    return "\n".join(lines)


def show_patient_analysis_page():
    """Patient prognosis analysis page."""
    st.markdown('<div class="section-header">Patient Prognosis Analysis</div>', unsafe_allow_html=True)

    test_patients = _load_test_patients()

    data_source = st.radio(
        "Patient Data Source:",
        ["Select from Test Patients", "Enter Custom Data"],
        horizontal=True,
    )

    if data_source == "Select from Test Patients" and test_patients:
        patient_options = {
            f"{p['id']} - {p['first_name']} {p['last_name']} ({p['primary_condition']})": p
            for p in test_patients
        }

        selected_label = st.selectbox(
            "Select Patient",
            options=list(patient_options.keys()),
        )

        selected_patient = patient_options[selected_label]
        patient_id = selected_patient["id"]
        condition = selected_patient["primary_condition"]
        visit_count = len(selected_patient.get("visits", []))
        dob = selected_patient.get("date_of_birth", "N/A")
        gender = selected_patient.get("gender", "N/A").capitalize()
        name = f"{selected_patient['first_name']} {selected_patient['last_name']}"
        clinical_summary = _format_patient_summary(selected_patient)

        # Patient header card
        st.markdown(f"""
        <div class="patient-header">
            <div class="patient-name">{name}</div>
            <div class="patient-meta">
                {patient_id} &nbsp;|&nbsp; DOB: {dob} &nbsp;|&nbsp; {gender} &nbsp;|&nbsp;
                <span class="condition-badge">{condition}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Patient ID", patient_id)
        with col2:
            st.metric("Condition", condition)
        with col3:
            st.metric("Total Visits", visit_count)
        with col4:
            if selected_patient.get("visits"):
                latest_date = selected_patient["visits"][0].get("visit_date", "")[:10]
                st.metric("Last Visit", latest_date)
            else:
                st.metric("Last Visit", "N/A")

        clinical_summary = st.text_area(
            "Clinical Summary",
            value=clinical_summary,
            height=350,
        )
    else:
        patient_id = st.text_input("Patient ID", value="PT-CUSTOM-001")
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

    st.markdown("---")

    if st.button("Run Multi-Agent Analysis", type="primary", use_container_width=True):
        if not clinical_summary.strip():
            st.error("Please provide clinical summary.")
            return

        patient_data = {
            "id": patient_id,
            "condition": condition,
            "visit_count": visit_count,
            "clinical_summary": clinical_summary,
        }

        analysis_placeholder = st.empty()
        log_placeholder = st.empty()
        response_texts = []
        log_messages = []

        def log(msg):
            """Add log message and update display."""
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_messages.append(f"`{timestamp}` {msg}")
            log_placeholder.markdown(
                '<div class="event-log">' +
                "<br>".join(log_messages[-10:]) +
                '</div>',
                unsafe_allow_html=True
            )
            try:
                print(f"[LOG {timestamp}] {msg}")
            except UnicodeEncodeError:
                print(f"[LOG {timestamp}] {msg.encode('ascii', errors='replace').decode()}")

        with st.spinner("Running multi-agent analysis... This may take a moment."):
            try:
                import nest_asyncio
                nest_asyncio.apply()

                async def run_analysis():
                    """Run multi-agent analysis and capture responses."""
                    log("Starting multi-agent analysis...")

                    log("Creating NeuroCrew...")
                    crew = NeuroCrew()

                    log("Setting up team with 6 agents (max 6 messages for speed)...")
                    crew.setup_team(max_messages=6)
                    log(f"Team ready: {', '.join(crew.get_agent_names())}")

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
                    log(f"Task prepared ({len(task)} chars)")
                    log("Starting run_stream - waiting for LLM responses...")

                    message_count = 0
                    async for message in crew._team.run_stream(task=task):
                        message_count += 1
                        msg_type = type(message).__name__
                        log(f"Message #{message_count}: {msg_type}")

                        if hasattr(message, 'content') and message.content:
                            agent_name = getattr(message, 'source', 'System')
                            log(f"   From: {agent_name} ({len(str(message.content))} chars)")
                            response_texts.append(
                                f'<div class="agent-response">'
                                f'<div class="agent-label">{agent_name}</div>'
                                f'<div class="agent-content">{message.content}</div>'
                                f'</div>'
                            )
                            analysis_placeholder.markdown(
                                "\n".join(response_texts),
                                unsafe_allow_html=True
                            )
                        else:
                            log(f"   No content (may be TaskResult)")

                    log(f"Stream complete. Total messages: {message_count}")

                log("Calling asyncio.run()...")
                asyncio.run(run_analysis())

                st.success("Analysis complete!")

            except Exception as e:
                log(f"Error: {str(e)}")
                st.error(f"Error running analysis: {str(e)}")
                st.exception(e)


def show_single_agent_page():
    """Single agent consultation page."""
    st.markdown('<div class="section-header">Agent Consultation</div>', unsafe_allow_html=True)

    col_select, col_info = st.columns([1, 2])

    with col_select:
        agent_type = st.selectbox(
            "Select Specialist",
            ["Neurologist", "Prognosis Analyst", "Treatment Advisor"],
        )

    with col_info:
        descriptions = {
            "Neurologist": "Board-certified neurologist with 20+ years experience. Clinical case review, differential diagnosis, and workup recommendations.",
            "Prognosis Analyst": "Senior data analyst specializing in disease trajectory modeling. Trend analysis with confidence scoring.",
            "Treatment Advisor": "Clinical pharmacology specialist. Medication optimization, interaction screening, and treatment planning.",
        }
        st.markdown(f"""
        <div class="agent-card" style="margin-top: 1.6rem;">
            <div class="agent-name">{agent_type}</div>
            <div class="agent-role">{descriptions[agent_type]}</div>
        </div>
        """, unsafe_allow_html=True)

    if agent_type == "Neurologist":
        default_query = """A 45-year-old female presents with:
- Recurrent headaches, 4-5 per week for past 2 months
- Throbbing, unilateral, moderate-severe intensity
- Associated nausea and photophobia
- Duration: 4-12 hours
- Some relief with OTC ibuprofen but incomplete

What is your assessment and recommended workup?"""

    elif agent_type == "Prognosis Analyst":
        default_query = """Patient: 72-year-old male with Alzheimer's Disease
Duration: Diagnosed 2 years ago

MMSE Scores over time:
- 24 months ago: 24/30
- 18 months ago: 22/30
- 12 months ago: 21/30
- 6 months ago: 19/30
- Current: 17/30

Currently on Donepezil 10mg daily."""

    else:
        default_query = """Patient with epilepsy (focal seizures with impaired awareness)
- Current: Levetiracetam 1000mg BID
- Seizure frequency: 2-3 per month (previously 4-5/month)
- Side effects: Mild irritability, otherwise tolerating well
- Goal: Better seizure control

Should we adjust the treatment?"""

    query = st.text_area(
        "Clinical Question",
        value=default_query,
        height=200
    )

    if st.button("Submit Consultation", type="primary", use_container_width=True):
        if not query.strip():
            st.error("Please enter a question.")
            return

        response_placeholder = st.empty()

        with st.spinner(f"Consulting {agent_type}..."):
            try:
                import nest_asyncio
                nest_asyncio.apply()

                chat = SingleAgentChat()
                response_text = []

                async def run_consultation():
                    """Run consultation and collect responses."""
                    from autogen_agentchat.messages import TextMessage

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

                    async for message in team.run_stream(task=query):
                        if hasattr(message, 'content') and message.content:
                            agent_name = getattr(message, 'source', agent_type)
                            response_text.append(
                                f'<div class="agent-response">'
                                f'<div class="agent-label">{agent_name}</div>'
                                f'<div class="agent-content">{message.content}</div>'
                                f'</div>'
                            )
                            response_placeholder.markdown(
                                "\n".join(response_text),
                                unsafe_allow_html=True
                            )

                asyncio.run(run_consultation())
                st.success("Consultation complete!")

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.exception(e)


def show_about_page():
    """System info / about page."""
    st.markdown('<div class="section-header">System Information</div>', unsafe_allow_html=True)

    # Tech stack badges
    st.markdown("""
    <div class="clinical-card">
        <h3>Technology Stack</h3>
        <p>
            <span class="tech-badge">Microsoft AutoGen 0.4+</span>
            <span class="tech-badge">Python 3.12</span>
            <span class="tech-badge">Streamlit</span>
            <span class="tech-badge">FastAPI</span>
            <span class="tech-badge">Pydantic v2</span>
            <span class="tech-badge">SQLAlchemy</span>
            <span class="tech-badge">SQLite</span>
            <span class="tech-badge">OpenAI API</span>
            <span class="tech-badge">Ollama</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    left, right = st.columns(2)

    with left:
        st.markdown("""
        <div class="clinical-card">
            <h3>Multi-Agent Architecture</h3>
            <p>The system uses 6 specialized AI agents in a RoundRobinGroupChat
            that collaborate sequentially on each patient case. Each agent follows
            structured Chain-of-Thought reasoning with self-review checklists
            and confidence calibration.</p>
        </div>
        """, unsafe_allow_html=True)

        agents = [
            ("Clinical Architect", "HIPAA compliance, data model review, 18-identifier audit"),
            ("Neurologist", "5-step clinical reasoning, differential diagnosis, red flag screening"),
            ("Prognosis Analyst", "Trend calculation, trajectory projection, condition benchmarks"),
            ("Treatment Advisor", "5-step clinical decision process, drug interaction screening"),
            ("QA Validator", "6-step validation with reference tables, anomaly detection"),
            ("Report Generator", "Integrated synthesis, executive summary, follow-up planning"),
        ]
        for name, desc in agents:
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-name">{name}</div>
                <div class="agent-role">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    with right:
        st.markdown("""
        <div class="clinical-card">
            <h3>Prompt Engineering</h3>
            <p>All agent prompts use advanced techniques for reliable clinical output:</p>
        </div>
        """, unsafe_allow_html=True)

        techniques = [
            ("Chain-of-Thought", "Numbered step-by-step reasoning processes per agent"),
            ("Few-Shot Examples", "Complete input/output examples in every agent prompt"),
            ("Structured Output", "Named templates (CLINICAL ASSESSMENT, PROGNOSIS ANALYSIS, etc.)"),
            ("Self-Review", "Verification checklists before submitting responses"),
            ("Confidence Calibration", "Required confidence levels (High/Moderate/Low or 0.0-1.0)"),
            ("Reference Grounding", "Score ranges, benchmarks, dosage tables in prompts"),
            ("Behavioral Guardrails", "Critical Rules sections with explicit safety boundaries"),
        ]
        for name, desc in techniques:
            st.markdown(f"""
            <div class="agent-card">
                <div class="agent-name">{name}</div>
                <div class="agent-role">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div class="clinical-card">
            <h3>Supported Conditions</h3>
            <p>
                <span class="condition-badge">Epilepsy</span>
                <span class="condition-badge">Migraine</span>
                <span class="condition-badge">Parkinson's</span>
                <span class="condition-badge">Multiple Sclerosis</span>
                <span class="condition-badge">Alzheimer's</span>
                <span class="condition-badge">Stroke</span>
                <span class="condition-badge">Neuropathy</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#5a7a98; font-size:0.8rem;">
        Neuro Patient Tracker v0.1.0 &nbsp;|&nbsp; Built with AI-powered multi-agent collaboration
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
