"""
Neuro Patient Tracker - Report Generator Agent

Responsible for creating clinical prognosis reports, visit summaries,
and patient documentation for neurologists.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from datetime import datetime
from .base_agent import BaseAgent


REPORT_GENERATOR_PROMPT = """You are the Report Generator Agent for a Neurology Patient Tracking System.

Your responsibilities:
1. Generate comprehensive clinical prognosis reports
2. Create patient visit summaries
3. Produce trend analysis documentation
4. Format clinical findings for physician review
5. Generate patient-friendly condition summaries

Report types you create:
- **Prognosis Report**: Longitudinal analysis with trend predictions
- **Visit Summary**: Concise documentation of patient encounters
- **Progress Report**: Tracking condition changes over time
- **Clinical Dashboard Summary**: Key metrics at a glance
- **Referral Summary**: Information for specialist consultations

Report structure standards:
1. Patient identification (de-identified for privacy)
2. Chief complaint / Reason for report
3. Clinical history summary
4. Current assessment findings
5. Trend analysis with visualizable data
6. Prognosis assessment
7. Recommendations
8. Follow-up plan

Writing guidelines:
- Use clear, professional medical terminology
- Present data in structured, scannable format
- Highlight critical findings and red flags
- Include confidence levels for predictions
- Cite relevant assessment scores and metrics
- Use bullet points for recommendations

Data visualization suggestions:
- Trend charts for longitudinal metrics
- Severity indicators (color-coded)
- Timeline of key events
- Comparison tables for before/after

HIPAA compliance:
- Never include full patient identifiers in reports
- Use patient ID codes only
- Mark reports with appropriate confidentiality notices
- Include generation timestamp and agent attribution

Output well-structured, clinically accurate reports ready for physician review.
"""


class ReportGeneratorAgent(BaseAgent):
    """
    Report Generator Agent for clinical documentation.
    
    Creates prognosis reports, visit summaries, and clinical
    documentation for neurological patient tracking.
    """
    
    def __init__(self, llm_config: Optional[dict] = None):
        """Initialize the Report Generator Agent."""
        super().__init__(
            name="ReportGenerator",
            system_message=REPORT_GENERATOR_PROMPT,
            llm_config=llm_config,
        )
    
    def create_agent(self) -> AssistantAgent:
        """Create the AutoGen AssistantAgent instance."""
        return AssistantAgent(
            name=self.name,
            description=self.system_message,
        )
    
    def get_report_template(self, report_type: str) -> dict:
        """
        Get template structure for a specific report type.
        
        Args:
            report_type: Type of report to generate
            
        Returns:
            Template dictionary with sections
        """
        templates = {
            "prognosis": {
                "title": "Neurological Prognosis Report",
                "sections": [
                    "patient_summary",
                    "condition_overview",
                    "visit_history",
                    "assessment_trends",
                    "current_status",
                    "prognosis_analysis",
                    "risk_factors",
                    "recommendations",
                    "follow_up_plan",
                ],
                "required_data": [
                    "patient_id",
                    "condition",
                    "visits",
                    "assessments",
                ],
            },
            "visit_summary": {
                "title": "Visit Summary Report",
                "sections": [
                    "visit_info",
                    "chief_complaint",
                    "vitals",
                    "neurological_exam",
                    "assessment",
                    "plan",
                    "follow_up",
                ],
                "required_data": [
                    "patient_id",
                    "visit_date",
                    "chief_complaint",
                ],
            },
            "progress": {
                "title": "Progress Report",
                "sections": [
                    "patient_summary",
                    "reporting_period",
                    "baseline_status",
                    "current_status",
                    "changes_observed",
                    "treatment_response",
                    "goals_progress",
                    "next_steps",
                ],
                "required_data": [
                    "patient_id",
                    "start_date",
                    "end_date",
                    "visits",
                ],
            },
            "referral": {
                "title": "Referral Summary",
                "sections": [
                    "patient_demographics",
                    "reason_for_referral",
                    "clinical_history",
                    "current_medications",
                    "recent_findings",
                    "specific_questions",
                    "urgency_level",
                ],
                "required_data": [
                    "patient_id",
                    "referral_reason",
                    "referring_physician",
                ],
            },
        }
        return templates.get(report_type.lower(), templates["visit_summary"])
    
    def generate_report_header(self, patient_id: str, report_type: str) -> str:
        """
        Generate standardized report header.
        
        Args:
            patient_id: Patient identifier
            report_type: Type of report
            
        Returns:
            Formatted header string
        """
        template = self.get_report_template(report_type)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        
        header = f"""
{'='*60}
{template['title'].upper()}
{'='*60}

Patient ID: {patient_id}
Report Generated: {timestamp}
Generated By: ReportGeneratorAgent
Confidentiality: HIPAA Protected Health Information

{'='*60}
"""
        return header.strip()
    
    def format_trend_summary(self, trends: dict) -> str:
        """
        Format trend data into readable summary.
        
        Args:
            trends: Dictionary with trend information
            
        Returns:
            Formatted trend summary
        """
        trend_icons = {
            "improving": "↑ IMPROVING",
            "stable": "→ STABLE",
            "declining": "↓ DECLINING",
            "unknown": "? UNKNOWN",
        }
        
        lines = ["TREND ANALYSIS", "-" * 40]
        
        for metric, trend in trends.items():
            icon = trend_icons.get(trend.lower(), "? UNKNOWN")
            lines.append(f"  {metric}: {icon}")
        
        return "\n".join(lines)
    
    def get_severity_indicator(self, severity: str) -> str:
        """
        Get visual indicator for severity level.
        
        Args:
            severity: Severity level string
            
        Returns:
            Formatted severity indicator
        """
        indicators = {
            "mild": "🟢 MILD",
            "moderate": "🟡 MODERATE", 
            "severe": "🟠 SEVERE",
            "critical": "🔴 CRITICAL",
        }
        return indicators.get(severity.lower(), severity.upper())
    
    def generate_recommendations_section(self, recommendations: list[str]) -> str:
        """
        Format recommendations list.
        
        Args:
            recommendations: List of clinical recommendations
            
        Returns:
            Formatted recommendations section
        """
        if not recommendations:
            return "RECOMMENDATIONS\n" + "-" * 40 + "\n  No specific recommendations at this time."
        
        lines = ["RECOMMENDATIONS", "-" * 40]
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"  {i}. {rec}")
        
        return "\n".join(lines)
