"""
NeuroCrew AI - Main Entry Point

Run the multi-agent neurology patient tracking system.
Includes LLM telemetry for cost and performance tracking.
"""
import asyncio
import sys
import os
import atexit

from src.orchestrator import NeuroCrew, SingleAgentChat, run_async
from src.config import settings
from src.logging import init_logging, get_logger, init_telemetry, get_telemetry


# Initialize logging at module load
_logger = None
_telemetry = None


def _shutdown():
    """Clean shutdown of logging and telemetry systems."""
    global _telemetry
    
    # Print and save session cost report
    if _telemetry:
        print("\n" + "=" * 60)
        print("📊 LLM Session Cost Report")
        print("=" * 60)
        _telemetry.print_cost_summary()
        
        # Save session report to file
        _telemetry.save_session_report()
    
    # Log system stop
    if _logger:
        _logger.log_system_stop()


async def run_demo():
    """Run a demonstration with sample patient data."""
    print("\n" + "=" * 60)
    print("🧠 NeuroCrew AI - Demo Mode")
    print("=" * 60)
    
    # Sample patient for demonstration
    sample_patient = {
        "id": "PT-2024-001",
        "condition": "Parkinson's Disease",
        "visit_count": 6,
        "clinical_summary": """
Patient: 68-year-old male
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
- Mild cognitive complaints (MoCA: 24/30)
"""
    }
    
    print("\n📋 Running prognosis analysis for sample patient...")
    print(f"   Patient ID: {sample_patient['id']}")
    print(f"   Condition: {sample_patient['condition']}")
    print("\n" + "-" * 60 + "\n")
    
    crew = NeuroCrew()
    await crew.run_prognosis_analysis(sample_patient)


async def run_single_agent_demo(agent_type: str = "neurologist"):
    """
    Run a simple single-agent consultation demo.
    
    Args:
        agent_type: Type of agent to consult (neurologist, prognosis, treatment)
    """
    chat = SingleAgentChat()
    
    if agent_type == "neurologist":
        question = """
A 45-year-old female presents with:
- Recurrent headaches, 4-5 per week for past 2 months
- Throbbing, unilateral, moderate-severe intensity
- Associated nausea and photophobia
- Duration: 4-12 hours
- Some relief with OTC ibuprofen but incomplete

What is your assessment and recommended workup?
"""
        print("\n🩺 Consulting Neurologist Agent...")
        await chat.consult_neurologist(question)
    
    elif agent_type == "prognosis":
        summary = """
Patient: 72-year-old male with Alzheimer's Disease
Duration: Diagnosed 2 years ago

MMSE Scores over time:
- 24 months ago: 24/30
- 18 months ago: 22/30
- 12 months ago: 21/30
- 6 months ago: 19/30
- Current: 17/30

Currently on Donepezil 10mg daily.
"""
        print("\n📊 Running Prognosis Analysis...")
        await chat.consult_prognosis(summary)
    
    elif agent_type == "treatment":
        case = """
Patient with epilepsy (focal seizures with impaired awareness)
- Current: Levetiracetam 1000mg BID
- Seizure frequency: 2-3 per month (previously 4-5/month before medication)
- Side effects: Mild irritability, otherwise tolerating well
- Goal: Better seizure control

Should we adjust the treatment?
"""
        print("\n💊 Getting Treatment Recommendations...")
        await chat.consult_treatment(case)


def main():
    """Main entry point."""
    global _logger, _telemetry
    
    # Initialize logging system
    _logger = init_logging()
    
    # Initialize telemetry for LLM cost tracking
    _telemetry = init_telemetry()
    
    # Register cleanup on exit
    atexit.register(_shutdown)
    
    # Check LLM configuration based on provider
    if settings.LLM_PROVIDER == "openai":
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key == "your_openai_api_key_here":
            _logger.log_error("OPENAI_API_KEY not configured")
            print("\n❌ Error: OPENAI_API_KEY not configured!")
            print("   Please set your API key:")
            print("   - In .env file, OR")
            print("   - As global environment variable")
            sys.exit(1)
    elif settings.LLM_PROVIDER == "local":
        print(f"\n🖥️  Using Local LLM: {settings.LOCAL_LLM_MODEL}")
        print(f"📡 Endpoint: {settings.LOCAL_LLM_BASE_URL}")
        print("   Make sure your local LLM server is running!")
    else:
        print(f"\n⚠️  Warning: Unknown LLM_PROVIDER: {settings.LLM_PROVIDER}")
        print("   Defaulting to local LLM...")
    
    print("\n🧠 NeuroCrew AI")
    print("-" * 40)
    print(f"📊 Telemetry: Session {_telemetry._session_id[:8]}... started")
    print("-" * 40)
    print("Select mode:")
    print("  1. Demo with sample patient (multi-agent)")
    print("  2. Single agent demo (Neurologist)")
    print("  3. Single agent demo (Prognosis)")
    print("  4. Single agent demo (Treatment)")
    print("  5. Show cost summary")
    print("  0. Exit")
    
    try:
        choice = input("\nEnter choice (1-5, 0 to exit): ").strip()
        
        if choice == "1":
            asyncio.run(run_demo())
        elif choice == "2":
            asyncio.run(run_single_agent_demo("neurologist"))
        elif choice == "3":
            asyncio.run(run_single_agent_demo("prognosis"))
        elif choice == "4":
            asyncio.run(run_single_agent_demo("treatment"))
        elif choice == "5":
            _telemetry.print_cost_summary()
        elif choice == "0":
            print("👋 Goodbye!")
        else:
            print("Invalid choice. Running demo mode...")
            asyncio.run(run_demo())
            
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        _logger.log_error(f"Application error: {str(e)}", exception=e)
        raise


if __name__ == "__main__":
    main()
