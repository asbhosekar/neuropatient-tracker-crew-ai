"""
NeuroCrew AI - Agent Orchestrator

Core AutoGen multi-agent conversation orchestration using AutoGen 0.4+ API.
Sets up RoundRobinGroupChat for collaborative agent interactions.
"""
import asyncio
import os
from typing import Optional

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from src.agents import (
    NeurologistAgent,
    ClinicalArchitectAgent,
    PrognosisAnalystAgent,
    ReportGeneratorAgent,
    QAValidatorAgent,
    TreatmentAdvisorAgent,
)
from src.config import settings


def get_model_client() -> OpenAIChatCompletionClient:
    """Create OpenAI model client."""
    api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")
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
        self.model_client = get_model_client()
        
        # Create agents with model client
        self._neurologist = self._create_agent("Neurologist", NeurologistAgent().system_message)
        self._prognosis_analyst = self._create_agent("PrognosisAnalyst", PrognosisAnalystAgent().system_message)
        self._treatment_advisor = self._create_agent("TreatmentAdvisor", TreatmentAdvisorAgent().system_message)
        self._report_generator = self._create_agent("ReportGenerator", ReportGeneratorAgent().system_message)
        self._qa_validator = self._create_agent("QAValidator", QAValidatorAgent().system_message)
        self._clinical_architect = self._create_agent("ClinicalArchitect", ClinicalArchitectAgent().system_message)
        
        self._team: Optional[RoundRobinGroupChat] = None
    
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
    
    async def run_conversation(self, task: str) -> None:
        """
        Run a multi-agent conversation.
        
        Args:
            task: The initial task or query
        """
        if self._team is None:
            self.setup_team()
        
        await Console(self._team.run_stream(task=task))
    
    async def run_prognosis_analysis(self, patient_data: dict) -> None:
        """
        Run a prognosis analysis workflow.
        
        Args:
            patient_data: Patient information dictionary
        """
        task = f"""
Perform a comprehensive prognosis analysis for this patient:

Patient ID: {patient_data.get('id', 'Unknown')}
Condition: {patient_data.get('condition', 'Unknown')}
Recent Visits: {patient_data.get('visit_count', 0)}

Clinical Data:
{patient_data.get('clinical_summary', 'No clinical data provided')}

Each specialist should contribute:
1. Neurologist: Review case, identify key clinical findings
2. Prognosis Analyst: Analyze trends and trajectory
3. Treatment Advisor: Suggest any treatment adjustments
4. QA Validator: Verify data accuracy
5. Report Generator: Summarize findings

Collaborate to provide a comprehensive assessment. End with TERMINATE when complete.
"""
        await self.run_conversation(task)
    
    async def consult(self, question: str) -> None:
        """
        Start a clinical consultation conversation.
        
        Args:
            question: Clinical question or scenario
        """
        task = f"""
Clinical Consultation Request:

{question}

Please have the appropriate specialists collaborate to address this question.
When finished, say TERMINATE.
"""
        await self.run_conversation(task)


class SingleAgentChat:
    """
    Simple single-agent consultation.
    
    Useful for direct consultations with a specific agent.
    """
    
    def __init__(self):
        self.model_client = get_model_client()
    
    async def consult_neurologist(self, question: str) -> None:
        """Direct consultation with the Neurologist agent."""
        agent = AssistantAgent(
            name="Neurologist",
            model_client=self.model_client,
            system_message=NeurologistAgent().system_message,
        )
        
        termination = MaxMessageTermination(3)
        team = RoundRobinGroupChat(participants=[agent], termination_condition=termination)
        
        await Console(team.run_stream(task=question))
    
    async def consult_prognosis(self, patient_summary: str) -> None:
        """Direct prognosis analysis request."""
        agent = AssistantAgent(
            name="PrognosisAnalyst",
            model_client=self.model_client,
            system_message=PrognosisAnalystAgent().system_message,
        )
        
        termination = MaxMessageTermination(3)
        team = RoundRobinGroupChat(participants=[agent], termination_condition=termination)
        
        task = f"Analyze the prognosis for this patient:\n\n{patient_summary}"
        await Console(team.run_stream(task=task))
    
    async def consult_treatment(self, case_details: str) -> None:
        """Get treatment recommendations."""
        agent = AssistantAgent(
            name="TreatmentAdvisor",
            model_client=self.model_client,
            system_message=TreatmentAdvisorAgent().system_message,
        )
        
        termination = MaxMessageTermination(3)
        team = RoundRobinGroupChat(participants=[agent], termination_condition=termination)
        
        task = f"Provide treatment recommendations for:\n\n{case_details}"
        await Console(team.run_stream(task=task))


# Helper function for synchronous usage
def run_async(coro):
    """Run an async coroutine synchronously."""
    return asyncio.run(coro)
