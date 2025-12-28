"""
NeuroCrew AI - Agent Orchestrator

Core AutoGen multi-agent conversation orchestration.
Sets up GroupChat for collaborative agent interactions.
"""
import autogen
from typing import Optional

from src.agents import (
    NeurologistAgent,
    ClinicalArchitectAgent,
    PrognosisAnalystAgent,
    ReportGeneratorAgent,
    QAValidatorAgent,
    TreatmentAdvisorAgent,
)
from src.config import settings


class NeuroCrew:
    """
    Main orchestrator for the NeuroCrew multi-agent system.
    
    Manages agent creation, group chat setup, and conversation flow.
    """
    
    def __init__(self, llm_config: Optional[dict] = None):
        """
        Initialize the NeuroCrew orchestrator.
        
        Args:
            llm_config: Optional LLM configuration override
        """
        self.llm_config = llm_config or self._default_llm_config()
        
        # Initialize agent wrappers
        self._neurologist = NeurologistAgent(self.llm_config)
        self._clinical_architect = ClinicalArchitectAgent(self.llm_config)
        self._prognosis_analyst = PrognosisAnalystAgent(self.llm_config)
        self._report_generator = ReportGeneratorAgent(self.llm_config)
        self._qa_validator = QAValidatorAgent(self.llm_config)
        self._treatment_advisor = TreatmentAdvisorAgent(self.llm_config)
        
        # AutoGen agents (created lazily)
        self._agents: list[autogen.AssistantAgent] = []
        self._user_proxy: Optional[autogen.UserProxyAgent] = None
        self._group_chat: Optional[autogen.GroupChat] = None
        self._manager: Optional[autogen.GroupChatManager] = None
    
    def _default_llm_config(self) -> dict:
        """Return default LLM configuration."""
        return {
            "config_list": [
                {
                    "model": settings.OPENAI_MODEL,
                    "api_key": settings.OPENAI_API_KEY,
                }
            ],
            "temperature": 0.7,
            "timeout": 120,
        }
    
    def _create_user_proxy(self) -> autogen.UserProxyAgent:
        """Create the human user proxy agent."""
        return autogen.UserProxyAgent(
            name="HumanUser",
            human_input_mode="TERMINATE",  # Request input only when TERMINATE is received
            max_consecutive_auto_reply=10,
            is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
            code_execution_config=False,  # Disable code execution for safety
            system_message="""You are a neurologist or clinical staff member using the NeuroCrew AI system.
You can ask questions about patients, request prognosis analyses, or ask for clinical recommendations.
Type 'exit' or 'quit' to end the conversation.""",
        )
    
    def _create_agents(self) -> list[autogen.AssistantAgent]:
        """Create all AutoGen assistant agents."""
        return [
            self._neurologist.agent,
            self._clinical_architect.agent,
            self._prognosis_analyst.agent,
            self._report_generator.agent,
            self._qa_validator.agent,
            self._treatment_advisor.agent,
        ]
    
    def setup_group_chat(self, max_round: int = 20) -> autogen.GroupChatManager:
        """
        Set up the multi-agent group chat.
        
        Args:
            max_round: Maximum conversation rounds
            
        Returns:
            GroupChatManager instance
        """
        # Create user proxy
        self._user_proxy = self._create_user_proxy()
        
        # Create all agents
        self._agents = self._create_agents()
        
        # Create group chat with all agents + user proxy
        all_participants = [self._user_proxy] + self._agents
        
        self._group_chat = autogen.GroupChat(
            agents=all_participants,
            messages=[],
            max_round=max_round,
            speaker_selection_method="auto",  # Let LLM decide who speaks next
            allow_repeat_speaker=False,
        )
        
        # Create manager to orchestrate the group chat
        self._manager = autogen.GroupChatManager(
            groupchat=self._group_chat,
            llm_config=self.llm_config,
        )
        
        return self._manager
    
    def start_conversation(self, initial_message: str) -> None:
        """
        Start a multi-agent conversation.
        
        Args:
            initial_message: The initial query or task
        """
        if self._manager is None:
            self.setup_group_chat()
        
        # Initiate chat from user proxy
        self._user_proxy.initiate_chat(
            self._manager,
            message=initial_message,
        )
    
    def run_prognosis_analysis(self, patient_data: dict) -> None:
        """
        Run a prognosis analysis workflow.
        
        Args:
            patient_data: Patient information dictionary
        """
        message = f"""
Please perform a comprehensive prognosis analysis for the following patient:

Patient ID: {patient_data.get('id', 'Unknown')}
Condition: {patient_data.get('condition', 'Unknown')}
Recent Visits: {patient_data.get('visit_count', 0)}

Clinical Data:
{patient_data.get('clinical_summary', 'No clinical data provided')}

I need:
1. Neurologist to review the case
2. Prognosis Analyst to analyze trends
3. Treatment Advisor to suggest any adjustments
4. QA Validator to verify data accuracy
5. Report Generator to create a summary report

Please collaborate to provide a comprehensive assessment.
"""
        self.start_conversation(message)
    
    def consult(self, question: str) -> None:
        """
        Start a clinical consultation conversation.
        
        Args:
            question: Clinical question or scenario
        """
        message = f"""
Clinical Consultation Request:

{question}

Please have the appropriate specialists collaborate to address this question.
"""
        self.start_conversation(message)


class TwoAgentChat:
    """
    Simple two-agent conversation setup.
    
    Useful for direct consultations between specific agents.
    """
    
    def __init__(self, llm_config: Optional[dict] = None):
        self.llm_config = llm_config or {
            "config_list": [
                {
                    "model": settings.OPENAI_MODEL,
                    "api_key": settings.OPENAI_API_KEY,
                }
            ],
            "temperature": 0.7,
        }
    
    def neurologist_consult(self, question: str) -> None:
        """Direct consultation with the Neurologist agent."""
        user = autogen.UserProxyAgent(
            name="Clinician",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
        
        neurologist = NeurologistAgent(self.llm_config).agent
        
        user.initiate_chat(
            neurologist,
            message=question,
        )
    
    def prognosis_analysis(self, patient_summary: str) -> None:
        """Direct prognosis analysis request."""
        user = autogen.UserProxyAgent(
            name="Clinician",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
        
        analyst = PrognosisAnalystAgent(self.llm_config).agent
        
        user.initiate_chat(
            analyst,
            message=f"Analyze the prognosis for this patient:\n\n{patient_summary}",
        )
    
    def treatment_recommendation(self, case_details: str) -> None:
        """Get treatment recommendations."""
        user = autogen.UserProxyAgent(
            name="Clinician",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=0,
            code_execution_config=False,
        )
        
        advisor = TreatmentAdvisorAgent(self.llm_config).agent
        
        user.initiate_chat(
            advisor,
            message=f"Provide treatment recommendations for:\n\n{case_details}",
        )
