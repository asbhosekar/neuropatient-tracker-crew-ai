"""
NeuroCrew AI - Agent Orchestrator

Core AutoGen multi-agent conversation orchestration using AutoGen 0.4+ API.
Sets up RoundRobinGroupChat for collaborative agent interactions.
Includes LLM telemetry for cost and performance tracking.
"""
import asyncio
import os
import time
from typing import Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_ext.models.openai._openai_client import ModelInfo

from src.agents import (
    NeurologistAgent,
    ClinicalArchitectAgent,
    PrognosisAnalystAgent,
    ReportGeneratorAgent,
    QAValidatorAgent,
    TreatmentAdvisorAgent,
)
from src.config import settings
from src.logging import get_logger, AuditEventType, get_telemetry


def get_model_client() -> OpenAIChatCompletionClient:
    """
    Create model client based on LLM_PROVIDER setting.

    Supports both OpenAI and local LLM (via OpenAI-compatible API).
    """
    if settings.LLM_PROVIDER == "local":
        # Use local LLM with OpenAI-compatible endpoint
        print(f"🖥️  Using local LLM: {settings.LOCAL_LLM_MODEL}")
        print(f"📡 Endpoint: {settings.LOCAL_LLM_BASE_URL}")

        # Define model info for local LLM
        local_model_info = ModelInfo(
            vision=False,
            function_calling=True,
            json_output=True,
            family="llama",
            context_window=8192,  # Llama 3.2 context window
            max_output_tokens=4096,
            input_price_per_million_tokens=0.0,  # Free for local
            output_price_per_million_tokens=0.0,  # Free for local
        )

        return OpenAIChatCompletionClient(
            model=settings.LOCAL_LLM_MODEL,
            api_key=settings.LOCAL_LLM_API_KEY,
            base_url=settings.LOCAL_LLM_BASE_URL,
            model_info=local_model_info,
        )
    else:
        # Use OpenAI
        api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
        print(f"☁️  Using OpenAI: {settings.OPENAI_MODEL}")
        return OpenAIChatCompletionClient(
            model=settings.OPENAI_MODEL,
            api_key=api_key,
        )


class NeuroCrew:
    """
    Main orchestrator for the NeuroCrew multi-agent system.
    
    Manages agent creation, group chat setup, and conversation flow
    using AutoGen 0.4+ RoundRobinGroupChat.
    """
    
    def __init__(self):
        """Initialize the NeuroCrew orchestrator."""
        self.logger = get_logger()
        self.telemetry = get_telemetry()
        self.model_client = get_model_client()
        
        # Create agents with model client
        self._neurologist = self._create_agent("Neurologist", NeurologistAgent().system_message)
        self._prognosis_analyst = self._create_agent("PrognosisAnalyst", PrognosisAnalystAgent().system_message)
        self._treatment_advisor = self._create_agent("TreatmentAdvisor", TreatmentAdvisorAgent().system_message)
        self._report_generator = self._create_agent("ReportGenerator", ReportGeneratorAgent().system_message)
        self._qa_validator = self._create_agent("QAValidator", QAValidatorAgent().system_message)
        self._clinical_architect = self._create_agent("ClinicalArchitect", ClinicalArchitectAgent().system_message)
        
        self._team: Optional[RoundRobinGroupChat] = None
        
        # Log agent initialization
        for agent_name in ["Neurologist", "PrognosisAnalyst", "TreatmentAdvisor", 
                          "ReportGenerator", "QAValidator", "ClinicalArchitect"]:
            self.logger.log_agent_initialized(agent_name)
    
    def _create_agent(self, name: str, system_message: str) -> AssistantAgent:
        """Create an AssistantAgent with the model client."""
        return AssistantAgent(
            name=name,
            model_client=self.model_client,
            system_message=system_message,
        )
    
    def get_agents(self) -> list[AssistantAgent]:
        """Get all clinical agents."""
        return [
            self._neurologist,
            self._prognosis_analyst,
            self._treatment_advisor,
            self._report_generator,
            self._qa_validator,
            self._clinical_architect,
        ]
    
    def get_agent_names(self) -> list[str]:
        """Get names of all agents."""
        return [a.name for a in self.get_agents()]
    
    def setup_team(self, max_messages: int = 12) -> RoundRobinGroupChat:
        """
        Set up the multi-agent team.
        
        Args:
            max_messages: Maximum messages before termination
            
        Returns:
            RoundRobinGroupChat team instance
        """
        termination = MaxMessageTermination(max_messages) | TextMentionTermination("TERMINATE")
        
        self._team = RoundRobinGroupChat(
            participants=self.get_agents(),
            termination_condition=termination,
        )
        
        return self._team
    
    async def run_conversation(self, task: str, patient_id: Optional[str] = None) -> None:
        """
        Run a multi-agent conversation.
        
        Args:
            task: The initial task or query
            patient_id: Optional patient ID for audit logging
        """
        if self._team is None:
            self.setup_team()
        
        # Generate correlation ID for this conversation
        correlation_id = self.logger.new_correlation_id()
        start_time = time.time()
        
        # Log conversation start
        self.logger.log_conversation_start(
            correlation_id=correlation_id,
            task_summary=task[:200],
            agents_involved=self.get_agent_names(),
        )
        
        # Log PHI access if patient data involved
        if patient_id:
            self.logger.log_phi_access(
                patient_id=patient_id,
                access_type="read",
                data_fields=["clinical_summary", "visit_history"],
                reason="Multi-agent prognosis analysis",
            )
        
        try:
            # Run conversation and capture messages for logging
            message_count = 0
            async for message in self._team.run_stream(task=task):
                message_count += 1
                
                # Log each agent message to clinical log
                if hasattr(message, 'source') and hasattr(message, 'content'):
                    self.logger.log_agent_message(
                        agent_name=str(message.source),
                        message_type=type(message).__name__,
                        content_preview=str(message.content)[:500] if message.content else "",
                        correlation_id=correlation_id,
                    )
                    
                    # Pretty print for user
                    print(f"\n---------- {type(message).__name__} ({message.source}) ----------")
                    print(message.content if message.content else str(message))
                else:
                    # Handle TaskResult or other message types
                    if hasattr(message, 'messages'):
                        print(f"\n{'='*60}")
                        print(f"Conversation complete. {len(message.messages)} messages.")
                    else:
                        print(message)
            
            # Log successful completion
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_conversation_end(
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                message_count=message_count,
                termination_reason="completed",
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            self.logger.log_error(
                f"Conversation failed: {str(e)}",
                exception=e,
                correlation_id=correlation_id,
            )
            self.logger.log_conversation_end(
                correlation_id=correlation_id,
                duration_ms=duration_ms,
                message_count=0,
                termination_reason=f"error: {str(e)}",
            )
            raise
    
    async def run_prognosis_analysis(self, patient_data: dict) -> None:
        """
        Run a prognosis analysis workflow.
        
        Args:
            patient_data: Patient information dictionary
        """
        patient_id = patient_data.get('id', 'Unknown')
        
        # Log PHI access for prognosis
        self.logger.log_phi_access(
            patient_id=patient_id,
            access_type="read",
            data_fields=["condition", "visit_history", "medications", "assessments"],
            reason="Prognosis analysis request",
        )
        
        task = f"""
## Multi-Agent Prognosis Analysis Request

**Patient ID:** {patient_id}
**Condition:** {patient_data.get('condition', 'Unknown')}
**Recent Visits:** {patient_data.get('visit_count', 0)}

### Clinical Data
{patient_data.get('clinical_summary', 'No clinical data provided')}

### Instructions for Each Specialist
Analyze this patient case sequentially. Each agent must follow their structured reasoning process and output format:

1. **Neurologist** (FIRST): Perform your 5-step clinical reasoning process. Identify key findings, check for red flags, provide differential considerations. Use your CLINICAL ASSESSMENT format.

2. **Prognosis Analyst** (SECOND): Using the Neurologist's findings, perform your analytical reasoning process. Calculate trends against condition benchmarks, project 3-month and 6-month trajectory. Use your PROGNOSIS ANALYSIS format with confidence score.

3. **Treatment Advisor** (THIRD): Review current medications and the trends identified. Follow your clinical decision process to assess treatment response and recommend specific adjustments with doses. Use your TREATMENT RECOMMENDATION format.

4. **QA Validator** (FOURTH): Validate all clinical data in this case. Check score ranges, medication dosages, temporal consistency. Use your VALIDATION REPORT format with data quality score.

5. **Report Generator** (FIFTH): Synthesize ALL findings from the team into a unified clinical report. Do not simply list each agent's output - integrate into a cohesive document. Use your standard report template.

### Collaboration Rules
- Build on previous agents' findings - reference and integrate, don't repeat
- If you disagree with a previous agent's assessment, state your reasoning
- Flag any data gaps that limit your analysis
- When all 5 specialists have contributed their structured analysis, say TERMINATE
"""
        await self.run_conversation(task, patient_id=patient_id)
        
        # Log prognosis generation
        self.logger.log_prognosis_generated(
            patient_id=patient_id,
            correlation_id=self.logger.new_correlation_id(),
            trend="analysis_completed",
            confidence=0.0,  # Will be populated by actual analysis
        )
    
    async def consult(self, question: str) -> None:
        """
        Start a clinical consultation conversation.
        
        Args:
            question: Clinical question or scenario
        """
        task = f"""
## Clinical Consultation Request

{question}

### Instructions
Each specialist should contribute their expertise using their structured response format:
- Follow your step-by-step reasoning process
- Use your designated output format
- Build on previous agents' analysis - integrate, don't repeat
- State your confidence level and any limitations
- When the team has provided a comprehensive answer, say TERMINATE
"""
        await self.run_conversation(task)


class SingleAgentChat:
    """
    Simple single-agent consultation.
    
    Useful for direct consultations with a specific agent.
    """
    
    def __init__(self):
        self.model_client = get_model_client()
        self.logger = get_logger()
    
    async def _run_with_logging(self, team: RoundRobinGroupChat, task: str, agent_name: str):
        """Run a team conversation with clinical logging."""
        correlation_id = self.logger.new_correlation_id()
        
        self.logger.log_conversation_start(
            correlation_id=correlation_id,
            task_summary=task[:200],
            agents_involved=[agent_name],
        )
        
        async for message in team.run_stream(task=task):
            # Log each message
            if hasattr(message, 'source') and hasattr(message, 'content'):
                self.logger.log_agent_message(
                    agent_name=str(message.source),
                    message_type=type(message).__name__,
                    content_preview=str(message.content)[:500] if message.content else "",
                    correlation_id=correlation_id,
                )
                # Pretty print
                print(f"\n---------- {type(message).__name__} ({message.source}) ----------")
                print(message.content if message.content else str(message))
            else:
                if hasattr(message, 'messages'):
                    print(f"\n{'='*60}")
                    print(f"Consultation complete.")
        
        self.logger.log_conversation_end(
            correlation_id=correlation_id,
            duration_ms=0,
            message_count=3,
            termination_reason="completed",
        )
    
    async def consult_neurologist(self, question: str) -> None:
        """Direct consultation with the Neurologist agent."""
        agent = AssistantAgent(
            name="Neurologist",
            model_client=self.model_client,
            system_message=NeurologistAgent().system_message,
        )
        
        termination = MaxMessageTermination(3)
        team = RoundRobinGroupChat(participants=[agent], termination_condition=termination)
        
        await self._run_with_logging(team, question, "Neurologist")
    
    async def consult_prognosis(self, patient_summary: str) -> None:
        """Direct prognosis analysis request."""
        agent = AssistantAgent(
            name="PrognosisAnalyst",
            model_client=self.model_client,
            system_message=PrognosisAnalystAgent().system_message,
        )
        
        termination = MaxMessageTermination(3)
        team = RoundRobinGroupChat(participants=[agent], termination_condition=termination)
        
        task = f"Analyze the prognosis for this patient. Follow your step-by-step analytical reasoning process and use your PROGNOSIS ANALYSIS response format. Include confidence score and benchmarks.\n\n{patient_summary}"
        await self._run_with_logging(team, task, "PrognosisAnalyst")
    
    async def consult_treatment(self, case_details: str) -> None:
        """Get treatment recommendations."""
        agent = AssistantAgent(
            name="TreatmentAdvisor",
            model_client=self.model_client,
            system_message=TreatmentAdvisorAgent().system_message,
        )
        
        termination = MaxMessageTermination(3)
        team = RoundRobinGroupChat(participants=[agent], termination_condition=termination)
        
        task = f"Provide treatment recommendations following your clinical decision process. Use your TREATMENT RECOMMENDATION response format with specific doses, rationale, alternatives, and monitoring plan.\n\n{case_details}"
        await self._run_with_logging(team, task, "TreatmentAdvisor")


# Helper function for synchronous usage
def run_async(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)
