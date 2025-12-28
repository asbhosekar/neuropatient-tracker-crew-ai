"""
Neuro Patient Tracker - Treatment Advisor Agent

Responsible for suggesting treatment adjustments based on patient
trends, medication efficacy, and clinical guidelines.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


TREATMENT_ADVISOR_PROMPT = """You are the Treatment Advisor Agent for a Neurology Patient Tracking System.

Your responsibilities:
1. Analyze treatment effectiveness based on patient outcomes
2. Suggest medication adjustments when indicated
3. Recommend non-pharmacological interventions
4. Identify when treatment escalation may be needed
5. Flag potential drug interactions and contraindications
6. Provide evidence-based treatment recommendations

Treatment domains:

**Epilepsy Management:**
- First-line: Levetiracetam, Lamotrigine, Valproate
- Seizure frequency targets and adjustment triggers
- When to consider surgery referral
- Lifestyle modifications (sleep, stress, triggers)

**Parkinson's Disease:**
- Levodopa optimization and wearing-off management
- Dopamine agonist considerations
- Non-motor symptom management
- Physical therapy and exercise recommendations

**Migraine Management:**
- Acute treatment: Triptans, NSAIDs, antiemetics
- Preventive therapy indications (≥4 headache days/month)
- Preventive options: Topiramate, Propranolol, CGRP inhibitors
- Trigger identification and lifestyle modifications

**Dementia/Alzheimer's:**
- Cholinesterase inhibitors (Donepezil, Rivastigmine)
- NMDA antagonists (Memantine)
- Non-pharmacological cognitive interventions
- Caregiver support recommendations

**Multiple Sclerosis:**
- Disease-modifying therapy selection
- Relapse management with steroids
- Symptom management (fatigue, spasticity)
- Rehabilitation referrals

Treatment recommendation format:
1. Current treatment assessment
2. Indication for change (if any)
3. Specific recommendation with rationale
4. Expected outcomes and monitoring plan
5. Alternative options if primary fails
6. Contraindications and precautions

Guidelines:
- Base recommendations on trend data and clinical evidence
- Consider patient-specific factors (age, comorbidities)
- Always note this is decision support, not a prescription
- Recommend specialist consultation for complex cases
- Include monitoring parameters for any changes

DISCLAIMER: All recommendations are for clinical decision support only.
Final treatment decisions must be made by the treating physician.
"""


class TreatmentAdvisorAgent(BaseAgent):
    """
    Treatment Advisor Agent for clinical decision support.
    
    Provides evidence-based treatment recommendations based on
    patient trends and clinical guidelines for neurological conditions.
    """
    
    def __init__(self, llm_config: Optional[dict] = None):
        """Initialize the Treatment Advisor Agent."""
        super().__init__(
            name="TreatmentAdvisor",
            system_message=TREATMENT_ADVISOR_PROMPT,
            llm_config=llm_config,
        )
    
    def create_agent(self) -> AssistantAgent:
        """Create the AutoGen AssistantAgent instance."""
        return AssistantAgent(
            name=self.name,
            description=self.system_message,
        )
    
    def get_first_line_treatments(self, condition: str) -> dict:
        """
        Get first-line treatment options for a condition.
        
        Args:
            condition: Neurological condition
            
        Returns:
            Dictionary with treatment options
        """
        treatments = {
            "epilepsy": {
                "focal_seizures": [
                    {"name": "Levetiracetam", "typical_dose": "500-1500mg BID", "notes": "Well-tolerated, few interactions"},
                    {"name": "Lamotrigine", "typical_dose": "100-200mg BID", "notes": "Requires slow titration"},
                    {"name": "Carbamazepine", "typical_dose": "200-600mg BID", "notes": "Many drug interactions"},
                ],
                "generalized_seizures": [
                    {"name": "Valproate", "typical_dose": "500-1000mg BID", "notes": "Avoid in women of childbearing age"},
                    {"name": "Levetiracetam", "typical_dose": "500-1500mg BID", "notes": "Broad spectrum"},
                    {"name": "Lamotrigine", "typical_dose": "100-200mg BID", "notes": "Good for absence seizures"},
                ],
            },
            "migraine": {
                "acute": [
                    {"name": "Sumatriptan", "typical_dose": "50-100mg PRN", "notes": "Triptan class, max 200mg/day"},
                    {"name": "Ibuprofen", "typical_dose": "400-800mg PRN", "notes": "First-line for mild-moderate"},
                    {"name": "Metoclopramide", "typical_dose": "10mg PRN", "notes": "For nausea, enhances absorption"},
                ],
                "preventive": [
                    {"name": "Topiramate", "typical_dose": "50-100mg daily", "notes": "Weight loss side effect"},
                    {"name": "Propranolol", "typical_dose": "40-160mg daily", "notes": "Avoid in asthma"},
                    {"name": "Amitriptyline", "typical_dose": "10-50mg nightly", "notes": "Good for tension component"},
                ],
            },
            "parkinsons": {
                "early_stage": [
                    {"name": "Levodopa/Carbidopa", "typical_dose": "100/25mg TID", "notes": "Most effective, may start early"},
                    {"name": "Pramipexole", "typical_dose": "0.5-1.5mg TID", "notes": "Dopamine agonist, younger patients"},
                    {"name": "Rasagiline", "typical_dose": "1mg daily", "notes": "MAO-B inhibitor, mild effect"},
                ],
                "motor_fluctuations": [
                    {"name": "Add Entacapone", "typical_dose": "200mg with each levodopa dose", "notes": "COMT inhibitor"},
                    {"name": "Increase levodopa frequency", "typical_dose": "Smaller doses more often", "notes": "Smooth out effect"},
                    {"name": "Add Amantadine", "typical_dose": "100mg BID", "notes": "For dyskinesia"},
                ],
            },
            "alzheimers": {
                "mild_moderate": [
                    {"name": "Donepezil", "typical_dose": "5-10mg daily", "notes": "Start low, increase after 4-6 weeks"},
                    {"name": "Rivastigmine", "typical_dose": "Patch 4.6-13.3mg/24hr", "notes": "Patch reduces GI side effects"},
                    {"name": "Galantamine", "typical_dose": "8-24mg daily", "notes": "Extended release available"},
                ],
                "moderate_severe": [
                    {"name": "Memantine", "typical_dose": "10mg BID", "notes": "Add to cholinesterase inhibitor"},
                    {"name": "Donepezil 23mg", "typical_dose": "23mg daily", "notes": "Higher dose for advanced disease"},
                ],
            },
            "multiple_sclerosis": {
                "relapsing": [
                    {"name": "Dimethyl fumarate", "typical_dose": "240mg BID", "notes": "Oral, flushing common initially"},
                    {"name": "Fingolimod", "typical_dose": "0.5mg daily", "notes": "First-dose cardiac monitoring"},
                    {"name": "Ocrelizumab", "typical_dose": "IV q6months", "notes": "High efficacy"},
                ],
                "acute_relapse": [
                    {"name": "Methylprednisolone", "typical_dose": "1g IV daily x 3-5 days", "notes": "Speeds recovery"},
                    {"name": "Prednisone taper", "typical_dose": "Oral taper over 2 weeks", "notes": "Alternative to IV"},
                ],
            },
        }
        return treatments.get(condition.lower(), {})
    
    def evaluate_treatment_response(
        self, 
        baseline_score: float, 
        current_score: float, 
        metric_type: str
    ) -> dict:
        """
        Evaluate treatment response based on score changes.
        
        Args:
            baseline_score: Score at treatment start
            current_score: Current score
            metric_type: Type of metric (higher_better or lower_better)
            
        Returns:
            Treatment response evaluation
        """
        if baseline_score == 0:
            return {
                "response": "Unable to evaluate",
                "change_percent": 0,
                "recommendation": "Insufficient baseline data",
            }
        
        change_pct = ((current_score - baseline_score) / baseline_score) * 100
        
        # For scores where higher is better (cognitive, motor function)
        if metric_type == "higher_better":
            if change_pct >= 10:
                response = "Good response"
                recommendation = "Continue current treatment"
            elif change_pct >= 0:
                response = "Stable"
                recommendation = "Monitor, consider optimization"
            elif change_pct >= -10:
                response = "Minimal decline"
                recommendation = "Review treatment, consider adjustment"
            else:
                response = "Poor response"
                recommendation = "Treatment modification recommended"
        
        # For scores where lower is better (symptom severity, seizure frequency)
        else:  # lower_better
            if change_pct <= -50:
                response = "Excellent response"
                recommendation = "Continue current treatment"
            elif change_pct <= -25:
                response = "Good response"
                recommendation = "Continue, monitor for further improvement"
            elif change_pct <= 0:
                response = "Partial response"
                recommendation = "Consider treatment optimization"
            else:
                response = "Poor response"
                recommendation = "Treatment modification recommended"
        
        return {
            "response": response,
            "change_percent": round(change_pct, 1),
            "recommendation": recommendation,
        }
    
    def check_escalation_criteria(self, condition: str, metrics: dict) -> dict:
        """
        Check if treatment escalation criteria are met.
        
        Args:
            condition: Neurological condition
            metrics: Dictionary of relevant clinical metrics
            
        Returns:
            Escalation assessment
        """
        escalation_criteria = {
            "epilepsy": {
                "criteria": [
                    "≥1 seizure per month despite medication",
                    "Intolerable side effects",
                    "Two or more AED failures",
                ],
                "escalation_options": [
                    "Add second antiepileptic drug",
                    "Switch to alternative AED",
                    "Consider epilepsy surgery evaluation",
                    "VNS therapy evaluation",
                ],
            },
            "migraine": {
                "criteria": [
                    "≥4 headache days per month",
                    "Significant disability (MIDAS >10)",
                    "Acute medication overuse",
                    "Failed 2+ preventive medications",
                ],
                "escalation_options": [
                    "Initiate preventive therapy",
                    "Switch preventive class",
                    "Consider CGRP monoclonal antibody",
                    "Refer to headache specialist",
                ],
            },
            "parkinsons": {
                "criteria": [
                    "Motor fluctuations >2 hours/day",
                    "Troublesome dyskinesia",
                    "Significant OFF time",
                    "Declining function despite optimization",
                ],
                "escalation_options": [
                    "Add COMT inhibitor",
                    "Add MAO-B inhibitor",
                    "Consider extended-release formulations",
                    "Refer for DBS evaluation",
                ],
            },
        }
        
        condition_info = escalation_criteria.get(condition.lower(), {})
        
        return {
            "condition": condition,
            "escalation_criteria": condition_info.get("criteria", []),
            "escalation_options": condition_info.get("escalation_options", []),
            "metrics_provided": metrics,
            "note": "Evaluate if patient meets any escalation criteria based on provided metrics",
        }
    
    def get_non_pharmacological_recommendations(self, condition: str) -> list[str]:
        """
        Get non-pharmacological treatment recommendations.
        
        Args:
            condition: Neurological condition
            
        Returns:
            List of non-pharmacological recommendations
        """
        recommendations = {
            "epilepsy": [
                "Maintain regular sleep schedule (7-9 hours)",
                "Avoid alcohol and recreational drugs",
                "Stress management techniques",
                "Seizure diary to identify triggers",
                "Medical alert bracelet",
                "Safety precautions (driving, swimming, heights)",
            ],
            "migraine": [
                "Regular sleep schedule",
                "Stay hydrated (8+ glasses water/day)",
                "Regular meals - avoid skipping",
                "Identify and avoid triggers (food diary)",
                "Regular aerobic exercise (30 min, 5x/week)",
                "Stress management and relaxation techniques",
                "Limit caffeine to <200mg/day",
            ],
            "parkinsons": [
                "Regular exercise program (walking, cycling, swimming)",
                "Physical therapy for gait and balance",
                "Speech therapy if speech affected",
                "Occupational therapy for daily activities",
                "Tai Chi or yoga for balance",
                "High-fiber diet for constipation",
                "Fall prevention strategies",
            ],
            "alzheimers": [
                "Cognitive stimulation activities",
                "Regular physical exercise",
                "Social engagement and activities",
                "Structured daily routine",
                "Memory aids (calendars, lists, labels)",
                "Safe, simplified environment",
                "Caregiver education and support",
            ],
            "multiple_sclerosis": [
                "Regular exercise within tolerance",
                "Physical therapy for mobility",
                "Cooling strategies for heat sensitivity",
                "Fatigue management techniques",
                "Bladder management strategies",
                "Stress reduction practices",
                "Vitamin D supplementation (discuss with physician)",
            ],
        }
        return recommendations.get(condition.lower(), [
            "Regular exercise appropriate for condition",
            "Healthy sleep habits",
            "Stress management",
            "Balanced nutrition",
        ])
