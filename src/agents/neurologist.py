"""
Neuro Patient Tracker - Neurologist Agent

The primary clinical expert agent responsible for patient consultations,
diagnosis guidance, and clinical decision support.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


NEUROLOGIST_PROMPT = """You are the Neurologist Agent for a Neurology Patient Tracking System.

You are a board-certified neurologist with 20+ years of expertise in diagnosing and managing neurological conditions.

## Your Responsibilities
1. Review patient cases and provide clinical assessments
2. Interpret neurological examination findings
3. Guide differential diagnosis for neurological symptoms
4. Recommend appropriate diagnostic workups
5. Evaluate treatment effectiveness and suggest adjustments
6. Provide clinical context for prognosis discussions

## Clinical Expertise Areas
- Epilepsy and seizure disorders
- Movement disorders (Parkinson's, Essential Tremor, Dystonia)
- Dementia and cognitive disorders (Alzheimer's, Vascular dementia)
- Multiple Sclerosis and demyelinating diseases
- Headache disorders (Migraine, Cluster, Tension-type)
- Stroke and cerebrovascular diseases
- Peripheral neuropathies
- Neuromuscular disorders

## Assessment Interpretation Reference
- MMSE: 24-30 normal, 19-23 mild impairment, 10-18 moderate dementia, 0-9 severe
- MoCA: 26-30 normal, 18-25 mild impairment, 10-17 moderate, 0-9 severe
- Motor function (0-100): higher = better functional capacity
- Symptom severity (0-10): lower = better symptom control
- EDSS (0-10): MS disability scale, higher = more disability
- UPDRS: Parkinson's rating, higher = more impaired

## Clinical Reasoning Process (follow these steps for every case)
When reviewing any patient case, think through each step systematically:

**Step 1 - Identify Key Findings**: List the most clinically significant data points from the patient record (scores, symptoms, vital signs, medication history).

**Step 2 - Pattern Recognition**: Match findings against known neurological patterns. Consider:
  - Does the symptom constellation fit a recognized syndrome?
  - Are there features atypical for the stated diagnosis?
  - What is the temporal progression pattern?

**Step 3 - Red Flag Check**: Explicitly screen for urgent/emergent findings:
  - Acute change in mental status or new focal deficits
  - Rapid symptom progression inconsistent with diagnosis
  - Signs of increased intracranial pressure
  - Status epilepticus risk factors

**Step 4 - Differential Considerations**: List the primary diagnosis and 2-3 alternative considerations, especially if findings are atypical.

**Step 5 - Assessment & Recommendations**: Provide evidence-based recommendations with clear clinical rationale.

## Response Format
Structure every clinical assessment as follows:

```
CLINICAL ASSESSMENT
---
Key Findings: [bullet list of significant clinical data]
Clinical Impression: [primary assessment with reasoning]
Differential Considerations: [alternative diagnoses to consider]
Red Flags: [any urgent findings, or "None identified"]
Recommended Workup: [diagnostic tests if indicated]
Clinical Recommendations: [evidence-based suggestions]
Confidence Level: [High/Moderate/Low with brief justification]
```

## Example Assessment

Input: "68M, Parkinson's diagnosed 3 years ago. UPDRS Motor: 34 (was 28 six months ago). MoCA: 24/30. Carbidopa/Levodopa 25/100 TID + Pramipexole 0.5mg TID. Reports 3 hrs OFF time daily. Sleep disturbances."

```
CLINICAL ASSESSMENT
---
Key Findings:
- UPDRS Motor Score trending up: 28 -> 34 over 6 months (21% worsening)
- MoCA 24/30: borderline mild cognitive impairment (cutoff 26)
- Significant OFF time: ~3 hours/day indicating motor fluctuations
- Sleep disturbances: could indicate RBD or medication effect
- Current regimen: Levodopa TID + Pramipexole - suboptimal frequency for wearing-off

Clinical Impression: Parkinson's disease with emerging motor fluctuations and possible early cognitive involvement. The 21% UPDRS increase over 6 months exceeds typical annual progression rate (~3-5 points/year), suggesting either disease acceleration or suboptimal medication coverage.

Differential Considerations:
1. PD with wearing-off motor fluctuations (most likely)
2. Atypical parkinsonism if response to levodopa is waning disproportionately
3. Medication-related cognitive effects (pramipexole can cause cognitive fog)

Red Flags: MoCA decline warrants monitoring - could signal PD dementia trajectory.

Recommended Workup:
- Formal neuropsychological testing given MoCA borderline score
- Sleep study if RBD symptoms present

Clinical Recommendations:
1. Address wearing-off: increase levodopa frequency (QID) or add COMT inhibitor (entacapone)
2. Monitor cognition closely - repeat MoCA in 3 months
3. Evaluate sleep with validated RBD screening questionnaire
4. Consider physical therapy referral for gait and balance

Confidence Level: High - classic PD motor fluctuation pattern with clear data trajectory.
```

## Self-Review Checklist (verify before submitting your response)
- Did I follow the step-by-step clinical reasoning process?
- Did I explicitly check for red flags?
- Did I provide differential considerations, not just one diagnosis?
- Did I state my confidence level with justification?
- Are my recommendations evidence-based and actionable?
- Did I acknowledge any data gaps or limitations?

## Critical Rules
- You do NOT make final diagnoses - you provide clinical guidance for the treating physician
- Always state your confidence level and acknowledge uncertainty when data is limited
- Prioritize patient safety - flag any urgent findings prominently
- Base all recommendations on available clinical evidence
- When other agents provide input, integrate their perspectives into your clinical reasoning
"""


class NeurologistAgent(BaseAgent):
    """
    Neurologist Agent for clinical consultations and guidance.

    Provides expert neurological assessment, interpretation of
    clinical findings, and evidence-based recommendations.
    """

    def __init__(self, llm_config: Optional[dict] = None):
        """Initialize the Neurologist Agent."""
        super().__init__(
            name="Neurologist",
            system_message=NEUROLOGIST_PROMPT,
            llm_config=llm_config,
        )

    def create_agent(self) -> AssistantAgent:
        """Create the AutoGen AssistantAgent instance."""
        return AssistantAgent(
            name=self.name,
            description=self.system_message,
        )

    def get_red_flags(self, condition: str) -> list[str]:
        """
        Get red flag symptoms requiring urgent attention.

        Args:
            condition: Neurological condition being evaluated

        Returns:
            List of red flag symptoms
        """
        red_flags = {
            "epilepsy": [
                "Status epilepticus (prolonged seizure >5 min)",
                "New focal neurological deficit post-ictal",
                "First seizure in adult >40 years",
                "Seizure with fever in adult",
                "Significant change in seizure pattern",
            ],
            "headache": [
                "Thunderclap headache (sudden severe onset)",
                "New headache >50 years old",
                "Headache with fever and neck stiffness",
                "Progressive worsening headache",
                "Headache with papilledema",
                "Headache after head trauma",
            ],
            "parkinsons": [
                "Rapid symptom progression",
                "Early falls within first year",
                "Poor response to levodopa",
                "Early severe autonomic dysfunction",
                "Prominent hallucinations without medication",
            ],
            "stroke": [
                "Acute onset focal weakness",
                "Sudden speech difficulty",
                "Acute vision loss",
                "Severe sudden headache",
                "Rapid deterioration in consciousness",
            ],
            "multiple_sclerosis": [
                "Rapid vision loss (optic neuritis)",
                "Acute transverse myelitis symptoms",
                "Brainstem symptoms (diplopia, vertigo)",
                "Severe relapse with functional impairment",
                "Signs of disease progression",
            ],
        }
        return red_flags.get(condition.lower(), [
            "Acute change in mental status",
            "New focal neurological deficit",
            "Severe uncontrolled symptoms",
        ])

    def get_workup_recommendations(self, symptoms: list[str]) -> dict:
        """
        Recommend diagnostic workup based on presenting symptoms.

        Args:
            symptoms: List of presenting symptoms

        Returns:
            Dictionary with recommended tests and imaging
        """
        workup = {
            "laboratory": [],
            "imaging": [],
            "neurophysiology": [],
            "other": [],
        }

        workup["laboratory"] = [
            "Complete blood count (CBC)",
            "Comprehensive metabolic panel",
            "Thyroid function tests",
            "Vitamin B12 level",
        ]

        symptom_lower = [s.lower() for s in symptoms]

        if any("seizure" in s or "epilepsy" in s for s in symptom_lower):
            workup["imaging"].append("MRI Brain with epilepsy protocol")
            workup["neurophysiology"].append("EEG (routine and/or prolonged)")
            workup["laboratory"].extend(["Antiepileptic drug levels", "Prolactin (post-ictal)"])

        if any("headache" in s or "migraine" in s for s in symptom_lower):
            workup["imaging"].append("MRI Brain with/without contrast")
            workup["other"].append("Headache diary review")

        if any("tremor" in s or "parkinson" in s for s in symptom_lower):
            workup["imaging"].append("MRI Brain")
            workup["imaging"].append("DaTscan (if diagnostic uncertainty)")

        if any("memory" in s or "cognitive" in s or "dementia" in s for s in symptom_lower):
            workup["imaging"].append("MRI Brain with volumetric analysis")
            workup["neurophysiology"].append("Neuropsychological testing")
            workup["laboratory"].extend(["RPR/VDRL", "HIV testing"])

        if any("weakness" in s or "numbness" in s or "neuropathy" in s for s in symptom_lower):
            workup["neurophysiology"].append("EMG/Nerve conduction studies")
            workup["laboratory"].extend(["HbA1c", "SPEP/UPEP"])

        return workup

    def interpret_cognitive_score(self, test: str, score: int) -> dict:
        """
        Interpret cognitive assessment scores.

        Args:
            test: Name of cognitive test (MMSE, MoCA)
            score: Test score

        Returns:
            Interpretation with severity and recommendations
        """
        interpretations = {
            "mmse": {
                "ranges": [
                    (24, 30, "Normal", "No significant cognitive impairment"),
                    (19, 23, "Mild", "Mild cognitive impairment - further evaluation recommended"),
                    (10, 18, "Moderate", "Moderate dementia - consider specialist referral"),
                    (0, 9, "Severe", "Severe dementia - comprehensive care planning needed"),
                ],
                "max_score": 30,
            },
            "moca": {
                "ranges": [
                    (26, 30, "Normal", "No significant cognitive impairment"),
                    (18, 25, "Mild", "Mild cognitive impairment detected"),
                    (10, 17, "Moderate", "Moderate cognitive impairment"),
                    (0, 9, "Severe", "Severe cognitive impairment"),
                ],
                "max_score": 30,
            },
        }

        test_lower = test.lower()
        if test_lower not in interpretations:
            return {"error": f"Unknown test: {test}"}

        test_info = interpretations[test_lower]
        for min_score, max_score, severity, interpretation in test_info["ranges"]:
            if min_score <= score <= max_score:
                return {
                    "test": test.upper(),
                    "score": score,
                    "max_score": test_info["max_score"],
                    "severity": severity,
                    "interpretation": interpretation,
                }

        return {"error": "Score out of range"}
