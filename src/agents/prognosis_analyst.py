"""
Neuro Patient Tracker - Prognosis Analyst Agent

Responsible for analyzing patient data trends, predicting
condition trajectories, and generating prognosis insights.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


PROGNOSIS_ANALYST_PROMPT = """You are the Prognosis Analyst Agent for a Neurology Patient Tracking System.

Your responsibilities:
1. Analyze longitudinal patient data for trends
2. Calculate condition trajectory predictions
3. Identify risk factors and warning signs
4. Generate evidence-based prognosis assessments
5. Provide clinical recommendations based on data patterns

Analysis capabilities:
- Trend detection: Improving, Stable, Declining
- Score analysis: MMSE, MoCA, motor function over time
- Symptom frequency tracking: Seizures, migraines
- Medication efficacy assessment
- Comparative analysis with condition baselines

Neurological metrics to track:
- Cognitive decline rates (dementia, Alzheimer's)
- Seizure frequency trends (epilepsy)
- Motor function deterioration (Parkinson's, MS)
- Migraine frequency and severity
- Stroke recovery progress

Output format:
- Overall trend classification
- Confidence score (0-1)
- Supporting data points
- Risk factors identified
- Clinical recommendations

Always base assessments on available data.
Clearly state confidence levels and limitations.
Do not make diagnoses - provide data-driven insights.
"""


class PrognosisAnalystAgent(BaseAgent):
    """
    Prognosis Analyst Agent for trend analysis and predictions.
    
    Analyzes longitudinal patient data to identify trends,
    predict trajectories, and provide clinical insights.
    """
    
    def __init__(self, llm_config: Optional[dict] = None):
        """Initialize the Prognosis Analyst Agent."""
        super().__init__(
            name="PrognosisAnalyst",
            system_message=PROGNOSIS_ANALYST_PROMPT,
            llm_config=llm_config,
        )
    
    def create_agent(self) -> AssistantAgent:
        """Create the AutoGen AssistantAgent instance."""
        return AssistantAgent(
            name=self.name,
            description=self.system_message,
        )
    
    def calculate_trend(self, data_points: list[float]) -> str:
        """
        Calculate trend from a series of data points.
        
        Args:
            data_points: List of numerical values over time
            
        Returns:
            Trend classification: improving, stable, declining
        """
        # TODO: Implement statistical trend analysis
        # This is a skeleton for future implementation
        if len(data_points) < 2:
            return "unknown"
        
        # Simple slope calculation
        first_half = sum(data_points[:len(data_points)//2]) / (len(data_points)//2)
        second_half = sum(data_points[len(data_points)//2:]) / (len(data_points) - len(data_points)//2)
        
        diff = second_half - first_half
        threshold = 0.1 * first_half if first_half != 0 else 0.1
        
        if diff > threshold:
            return "improving"
        elif diff < -threshold:
            return "declining"
        return "stable"
    
    def get_risk_factors(self, condition: str) -> list[str]:
        """
        Get common risk factors for a neurological condition.
        
        Args:
            condition: Neurological condition name
            
        Returns:
            List of risk factors
        """
        risk_factors = {
            "epilepsy": [
                "Medication non-compliance",
                "Sleep deprivation",
                "Alcohol consumption",
                "Stress",
                "Missed doses",
            ],
            "parkinsons": [
                "Age progression",
                "Medication wearing off",
                "Depression",
                "Sleep disorders",
                "Cognitive decline",
            ],
            "alzheimers": [
                "Age progression",
                "Cardiovascular risk factors",
                "Social isolation",
                "Depression",
                "Sleep disturbances",
            ],
            "migraine": [
                "Stress",
                "Hormonal changes",
                "Sleep irregularity",
                "Dietary triggers",
                "Medication overuse",
            ],
        }
        return risk_factors.get(condition.lower(), ["Unknown condition"])
