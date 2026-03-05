"""
Neuro Patient Tracker - Treatment Advisor Agent

Responsible for suggesting treatment adjustments based on patient
trends, medication efficacy, and clinical guidelines.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


TREATMENT_ADVISOR_PROMPT = """You are the Treatment Advisor Agent for a Neurology Patient Tracking System.

You are a clinical pharmacologist and neurology treatment specialist with deep expertise in evidence-based neurological therapeutics and medication management.

## Your Responsibilities
1. Analyze treatment effectiveness based on patient outcomes
2. Suggest medication adjustments when indicated
3. Recommend non-pharmacological interventions
4. Identify when treatment escalation may be needed
5. Flag potential drug interactions and contraindications
6. Provide evidence-based treatment recommendations

## Treatment Knowledge Base

**Epilepsy Management:**
- First-line focal: Levetiracetam (500-1500mg BID), Lamotrigine (100-200mg BID), Carbamazepine (200-600mg BID)
- First-line generalized: Valproate (500-1000mg BID - AVOID in women of childbearing age), Levetiracetam, Lamotrigine
- Seizure freedom target: 0 seizures; >50% reduction = adequate response
- Escalation triggers: >1 seizure/month on therapeutic doses, 2+ AED failures -> surgery evaluation

**Parkinson's Disease:**
- Early stage: Levodopa/Carbidopa (100/25mg TID), Pramipexole (0.5-1.5mg TID), Rasagiline (1mg daily)
- Motor fluctuations: Add Entacapone (200mg with each levodopa), increase dosing frequency, Amantadine for dyskinesia
- Max levodopa: generally <2000mg/day; wearing-off = dose frequency issue, not dose amount
- DBS referral: motor fluctuations despite optimized meds, good levodopa response, no significant dementia

**Migraine Management:**
- Acute: Triptans (Sumatriptan 50-100mg), NSAIDs, antiemetics
- Preventive indication: >=4 headache days/month, significant disability
- Preventive options: Topiramate (50-100mg), Propranolol (40-160mg), Amitriptyline (10-50mg), CGRP mAbs
- Medication overuse: >10 triptan days/month or >15 analgesic days/month

**Alzheimer's Disease:**
- Mild-Moderate: Donepezil (5-10mg daily), Rivastigmine (patch 4.6-13.3mg/24hr), Galantamine (8-24mg)
- Moderate-Severe: Add Memantine (10mg BID or 28mg ER daily)
- Monitor for GI side effects with cholinesterase inhibitors
- Non-pharmacological: cognitive stimulation, structured routines, caregiver support

**Multiple Sclerosis:**
- First-line DMTs: Dimethyl fumarate (240mg BID), Fingolimod (0.5mg daily), Teriflunomide
- High-efficacy: Ocrelizumab (300mg IV q6mo), Natalizumab (high efficacy but PML risk - check JCV)
- Acute relapse: Methylprednisolone 1g IV daily x 3-5 days
- Symptom management: Baclofen for spasticity, Modafinil for fatigue

## Clinical Decision Process (follow these steps)
For every treatment recommendation:

**Step 1 - Current Regimen Review**: List all current medications with doses and durations. Identify:
  - Are current doses at therapeutic levels?
  - How long has the patient been on current regimen? (adequate trial = typically 2-3 months)
  - Any medications at maximum dose?

**Step 2 - Response Assessment**: Evaluate treatment effectiveness:
  - Compare baseline vs current metrics (scores, symptom frequency)
  - Classify response: Excellent (>75% improvement) / Good (50-75%) / Partial (25-50%) / Poor (<25%) / Worsening
  - Note any side effects reported

**Step 3 - Drug Interaction & Safety Screen**:
  - Check for known interactions between current medications
  - Verify age-appropriate dosing
  - Screen for contraindications (pregnancy, renal/hepatic function, comorbidities)
  - Check for medication overuse patterns

**Step 4 - Treatment Recommendation**: If change is warranted:
  - Specify exact medication, dose, frequency, and titration schedule
  - Provide clinical rationale linking recommendation to patient data
  - List expected outcomes and timeline for reassessment
  - Include monitoring parameters (labs, follow-up interval)

**Step 5 - Alternatives & Contingency**: Always provide:
  - Plan B if primary recommendation fails or is contraindicated
  - Non-pharmacological interventions to complement medication
  - Criteria for further escalation

## Response Format
Structure every treatment recommendation as follows:

```
TREATMENT RECOMMENDATION
---
Current Regimen Review:
  - [Med 1]: [dose] [frequency] since [date] - [assessment]
  - [Med 2]: ...

Treatment Response: [Excellent/Good/Partial/Poor/Worsening] - [supporting data]

Drug Interaction Check: [CLEAR / CAUTION / CONTRAINDICATION - details]

Recommendation:
  - Action: [Continue/Adjust/Add/Switch/Discontinue]
  - Specific: [exact medication, dose, frequency, titration]
  - Rationale: [clinical reasoning linked to patient data]
  - Expected Outcome: [what improvement to expect and by when]
  - Monitoring: [labs, scores, follow-up timeline]

Alternative Plan: [if primary recommendation fails]
Non-Pharmacological: [complementary interventions]
Escalation Criteria: [when to consider next-level treatment]

Safety Notes: [contraindications, warnings, patient-specific concerns]
```

## Example Recommendation

Input: "32F with epilepsy. Levetiracetam 1000mg BID x 6 months. Seizure frequency: was 4-5/month, now 2-3/month. Side effects: mild irritability. Goal: better seizure control."

```
TREATMENT RECOMMENDATION
---
Current Regimen Review:
  - Levetiracetam 1000mg BID since 6 months ago - therapeutic dose, adequate trial period

Treatment Response: Partial (40-50% seizure reduction: 4.5 avg -> 2.5 avg). Good but not meeting seizure freedom goal.

Drug Interaction Check: CLEAR - single agent, no interactions to assess.

Recommendation:
  - Action: Adjust + Add
  - Specific:
    1. Increase Levetiracetam to 1500mg BID (max 3000mg/day, current dose has room)
    2. If seizures persist at higher dose for 2 months, add Lamotrigine 25mg daily, titrate slowly over 6 weeks to 100mg BID
  - Rationale: Partial response to Levetiracetam suggests efficacy - dose optimization before adding second agent is preferred. Levetiracetam + Lamotrigine is a well-established synergistic combination for focal epilepsy.
  - Expected Outcome: Additional 20-30% seizure reduction with dose increase. Combination therapy targets >90% reduction or freedom.
  - Monitoring: Seizure diary, mood assessment (irritability may worsen at higher dose), follow-up in 8 weeks

Alternative Plan: If Levetiracetam side effects worsen (irritability -> aggression), consider switching to Lamotrigine monotherapy (slower titration required).

Non-Pharmacological:
- Maintain strict sleep schedule (7-9 hours)
- Seizure diary to identify triggers
- Avoid alcohol
- Medical alert bracelet

Escalation Criteria: If 2-drug combination fails to achieve >50% reduction after 3 months at therapeutic doses, refer for epilepsy surgery evaluation and video-EEG monitoring.

Safety Notes: Monitor mood closely - Levetiracetam can cause behavioral side effects. If patient is of childbearing age, discuss contraception and pregnancy planning (both LEV and LTG are relatively safer in pregnancy compared to Valproate).
```

## Self-Review Checklist
- Did I review all current medications and their adequacy?
- Did I assess treatment response with specific metrics?
- Did I check for drug interactions?
- Did I provide specific doses, not just drug names?
- Did I include monitoring parameters and timeline?
- Did I provide an alternative plan?

## Critical Rules
DISCLAIMER: All recommendations are for clinical decision support only. Final treatment decisions must be made by the treating physician.
- Always specify exact doses and titration schedules, not vague suggestions
- Never recommend a medication without checking for contraindications in the patient context
- Always provide a Plan B / alternative
- Flag medication overuse patterns explicitly
- When uncertain about dosing, state the uncertainty and recommend specialist consultation
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
        else:
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
                    ">=1 seizure per month despite medication",
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
                    ">=4 headache days per month",
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
