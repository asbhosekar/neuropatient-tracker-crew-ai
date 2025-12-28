"""
Neuro Patient Tracker - Base Agent

Abstract base class for all AutoGen agents in the system.
"""
from abc import ABC, abstractmethod
from typing import Any, Optional
from autogen_agentchat.agents import AssistantAgent


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Neuro Patient Tracker.
    
    Provides common functionality and interface for AutoGen agents.
    """
    
    def __init__(
        self,
        name: str,
        system_message: str,
        llm_config: Optional[dict] = None,
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name identifier
            system_message: System prompt defining agent behavior
            llm_config: LLM configuration dictionary
        """
        self.name = name
        self.system_message = system_message
        self.llm_config = llm_config or self._default_llm_config()
        self._agent: Optional[AssistantAgent] = None
    
    def _default_llm_config(self) -> dict:
        """Return default LLM configuration."""
        from src.config import settings
        return {
            "config_list": [
                {
                    "model": settings.OPENAI_MODEL,
                    "api_key": settings.OPENAI_API_KEY,
                }
            ],
            "temperature": 0.7,
        }
    
    @abstractmethod
    def create_agent(self) -> AssistantAgent:
        """
        Create and return the AutoGen agent instance.
        
        Must be implemented by subclasses.
        """
        pass
    
    @property
    def agent(self) -> AssistantAgent:
        """Get or create the agent instance."""
        if self._agent is None:
            self._agent = self.create_agent()
        return self._agent
    
    def get_system_message(self) -> str:
        """Return the agent's system message."""
        return self.system_message
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
