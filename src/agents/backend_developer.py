"""
Neuro Patient Tracker - Backend Developer Agent

Responsible for building FastAPI services, database layer,
and REST API endpoints for the patient tracking system.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


BACKEND_DEVELOPER_PROMPT = """You are the Backend Developer Agent for a Neurology Patient Tracking System.

Your responsibilities:
1. Build FastAPI REST API endpoints for patient management
2. Implement database models and SQLAlchemy ORM layer
3. Create CRUD operations for patients, visits, and prognosis records
4. Implement data validation and error handling
5. Design efficient database queries for longitudinal data

Technical stack:
- Framework: FastAPI
- ORM: SQLAlchemy 2.0
- Database: SQLite (dev) / PostgreSQL (prod)
- Validation: Pydantic v2
- Authentication: OAuth2 / JWT (future)

API endpoints to implement:
- POST /patients - Create new patient
- GET /patients/{id} - Get patient details
- GET /patients/{id}/visits - Get patient visit history
- POST /visits - Record new visit
- GET /patients/{id}/prognosis - Get prognosis analysis
- GET /analytics/trends - Get aggregate trend data

Best practices:
- Use async/await for database operations
- Implement proper exception handling
- Add request/response logging
- Follow REST conventions
- Write type hints for all functions

Output production-ready Python code with proper error handling.
"""


class BackendDeveloperAgent(BaseAgent):
    """
    Backend Developer Agent for API and database implementation.
    
    Builds FastAPI services and SQLAlchemy database layer
    for the patient tracking system.
    """
    
    def __init__(self, llm_config: Optional[dict] = None):
        """Initialize the Backend Developer Agent."""
        super().__init__(
            name="BackendDeveloper",
            system_message=BACKEND_DEVELOPER_PROMPT,
            llm_config=llm_config,
        )
    
    def create_agent(self) -> AssistantAgent:
        """Create the AutoGen AssistantAgent instance."""
        return AssistantAgent(
            name=self.name,
            description=self.system_message,
        )
    
    def get_api_routes(self) -> list[dict]:
        """
        Return list of API routes to implement.
        
        Returns:
            List of route specifications
        """
        return [
            {"method": "POST", "path": "/patients", "description": "Create patient"},
            {"method": "GET", "path": "/patients/{id}", "description": "Get patient"},
            {"method": "PUT", "path": "/patients/{id}", "description": "Update patient"},
            {"method": "DELETE", "path": "/patients/{id}", "description": "Delete patient"},
            {"method": "GET", "path": "/patients/{id}/visits", "description": "Get visits"},
            {"method": "POST", "path": "/visits", "description": "Create visit"},
            {"method": "GET", "path": "/patients/{id}/prognosis", "description": "Get prognosis"},
        ]
    
    def generate_crud_template(self, model_name: str) -> str:
        """
        Generate CRUD operations template for a model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Template code string
        """
        # TODO: Implement template generation
        # This is a skeleton for future implementation
        return f"# CRUD operations for {model_name}"
