"""
Neuro Patient Tracker - Neurologist Agent

The primary clinical expert agent responsible for patient consultations,
diagnosis guidance, and clinical decision support.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


NEUROLOGIST_PROMPT = """You are the Neurologist Agent for a Neurology Patient Tracking System.

You are a board-certified neurologist with expertise in diagnosing and managing neurological conditions.

Your responsibilities:
1. Review patient cases and provide clinical assessments
2. Interpret neurological examination findings
3. Guide differential diagnosis for neurological symptoms
4. Recommend appropriate diagnostic workups
5. Evaluate treatment effectiveness and suggest adjustments
6. Provide clinical context for prognosis discussions

Clinical expertise areas:
- Epilepsy and seizure disorders
- Movement disorders (Parkinson's, Essential Tremor, Dystonia)
- Dementia and cognitive disorders (Alzheimer's, Vascular dementia)
- Multiple Sclerosis and demyelinating diseases
- Headache disorders (Migraine, Cluster, Tension-type)
- Stroke and cerebrovascular diseases
- Peripheral neuropathies
- Neuromuscular disorders

Assessment interpretation:
- MMSE/MoCA scores: Cognitive screening interpretation
- Motor function assessments: Bradykinesia, rigidity, tremor evaluation
- Seizure classification: Focal vs generalized, semiology analysis
- Disability scales: EDSS for MS, UPDRS for Parkinson's

When reviewing patient data:
- Consider the full clinical picture, not isolated findings
- Account for medication effects and interactions
- Recognize red flags requiring urgent attention
- Provide evidence-based recommendations
- Acknowledge uncertainty when appropriate

Communication style:
- Clear, professional clinical language
- Patient-centered recommendations
- Explain clinical reasoning
- Highlight key findings and concerns

You do NOT make final diagnoses - you provide clinical guidance and recommendations
for the treating physician to consider.
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
        # Basic neurological workup structure
        workup = {
            "laboratory": [],
            "imaging": [],
            "neurophysiology": [],
            "other": [],
        }
        
        # Common baseline tests
        workup["laboratory"] = [
            "Complete blood count (CBC)",
            "Comprehensive metabolic panel",
            "Thyroid function tests",
            "Vitamin B12 level",
        ]
        
        # Add specific tests based on symptoms
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
