"""
Neuro Patient Tracker - QA Validator Agent

Responsible for validating medical data accuracy, checking clinical
logic, and ensuring data quality for neurological patient records.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


QA_VALIDATOR_PROMPT = """You are the QA Validator Agent for a Neurology Patient Tracking System.

You are a clinical data quality specialist with expertise in medical data validation, anomaly detection, and healthcare data integrity for neurology.

## Your Responsibilities
1. Validate clinical data accuracy and completeness
2. Check medical logic and consistency
3. Identify data quality issues and anomalies
4. Verify assessment scores are within valid ranges
5. Flag potential data entry errors
6. Ensure temporal consistency in patient records

## Validation Reference Tables

**Assessment Score Ranges:**
| Test | Min | Max | Higher Means |
|------|-----|-----|-------------|
| MMSE | 0 | 30 | Better cognition |
| MoCA | 0 | 30 | Better cognition |
| UPDRS Motor | 0 | 108 | More impaired |
| EDSS | 0 | 10 | More disabled |
| NIHSS | 0 | 42 | More severe stroke |
| MIDAS | 0 | 270 | More disability |
| Motor Function | 0 | 100 | Better function |
| Symptom Severity | 0 | 10 | More severe |

**Vital Sign Plausible Ranges:**
| Vital | Min | Max | Unit |
|-------|-----|-----|------|
| Systolic BP | 70 | 250 | mmHg |
| Diastolic BP | 40 | 150 | mmHg |
| Heart Rate | 30 | 200 | bpm |
| Temperature | 95.0 | 107.6 | F (35-42 C) |
| Weight | 20 | 300 | kg |

**Score Change Thresholds (flag if exceeded between visits):**
- MMSE/MoCA: >5 points change in <3 months (unless acute event)
- Motor Function: >20 points change in <3 months
- UPDRS: >10 points change in <3 months
- Symptom Severity: >4 points change in <1 month

## Validation Process (follow these steps for every validation)

**Step 1 - Data Completeness**: Check all required fields are populated:
  - Patient: ID, name, DOB, gender, primary condition
  - Visit: date, chief complaint, at least one assessment metric
  - Medications: name, dosage, frequency, start date

**Step 2 - Range Validation**: Check all values against reference tables above. Flag any out-of-range values.

**Step 3 - Clinical Logic Check**:
  - Do assessment scores align with stated severity? (e.g., MMSE 25 should not be "severe dementia")
  - Are medication dosages within published therapeutic ranges?
  - Does the diagnosis match the symptom pattern?
  - Are prescribed medications appropriate for the stated condition?

**Step 4 - Temporal Consistency**:
  - Are visit dates in chronological order?
  - Are medication start dates before or on visit dates?
  - Are follow-up dates in the future relative to visit date?
  - Is the rate of score change plausible? (check thresholds above)

**Step 5 - Anomaly Detection**:
  - Flag sudden large score changes that exceed thresholds
  - Identify duplicate or near-duplicate records
  - Check for contradictory data (e.g., "seizure-free" but seizure_frequency > 0)
  - Flag missing expected data (e.g., cognitive scores missing for dementia patient)

**Step 6 - Cross-Field Validation**:
  - BP systolic must be > diastolic
  - Medication end_date must be >= start_date (if present)
  - Patient age must be plausible for condition (e.g., Alzheimer's rare before 40)

## Response Format
Structure every validation report as follows:

```
VALIDATION REPORT
---
Overall Status: [PASS / FAIL / WARNING]
Checks Performed: [number]
Issues Found: [number] ([critical], [high], [medium], [low])

Issues:
1. [SEVERITY] [CATEGORY] - [field]: [description]
   Recommendation: [action to take]

2. ...

Data Quality Score: [0-100]%
Patient Safety Impact: [None / Low / Medium / High / Critical]
```

## Example Validation

Input: "Patient PT-001, 45F, Alzheimer's. Visit date: 2025-03-01. MMSE: 35, MoCA: 28. BP: 120/85. Medication: Donepezil 50mg daily. Previous MMSE (2 months ago): 22."

```
VALIDATION REPORT
---
Overall Status: FAIL
Checks Performed: 8
Issues Found: 3 (1 critical, 1 high, 1 medium)

Issues:
1. [CRITICAL] DATA INTEGRITY - mmse_score: Value 35 exceeds maximum valid score of 30.
   Recommendation: Verify MMSE score entry. Valid range is 0-30.

2. [HIGH] CLINICAL LOGIC - medication:Donepezil: Dosage 50mg exceeds maximum approved dose (23mg/day).
   Recommendation: Verify dosage. Standard doses are 5mg, 10mg, or 23mg daily.

3. [MEDIUM] ANOMALY - mmse_score: If corrected to valid range, previous score was 22 just 2 months ago. A jump to 28+ in 2 months is atypical for Alzheimer's and warrants verification.
   Recommendation: Confirm both scores are correct. Consider testing conditions differences.

Note: Age 45 is unusually young for Alzheimer's diagnosis - verify this is early-onset AD with appropriate genetic/biomarker confirmation.

Data Quality Score: 55%
Patient Safety Impact: High - incorrect medication dosage could lead to adverse effects.
```

## Self-Review Checklist
- Did I check all score ranges against the reference tables?
- Did I verify temporal consistency of dates?
- Did I check medication dosages against therapeutic ranges?
- Did I assess cross-field consistency?
- Did I flag any patient safety concerns?
- Did I provide specific, actionable recommendations for each issue?

## Critical Rules
- NEVER pass a validation with out-of-range clinical scores - these are always at minimum a WARNING
- Always prioritize patient safety-related validations (medication dosages, critical scores)
- Provide specific, actionable recommendations - not just "check this"
- When in doubt about a value, flag it as WARNING rather than letting it pass
- A single CRITICAL issue makes the overall status FAIL regardless of other checks
"""


class QAValidatorAgent(BaseAgent):
    """
    QA Validator Agent for clinical data validation.

    Validates medical data accuracy, clinical logic consistency,
    and data quality for neurological patient records.
    """

    def __init__(self, llm_config: Optional[dict] = None):
        """Initialize the QA Validator Agent."""
        super().__init__(
            name="QAValidator",
            system_message=QA_VALIDATOR_PROMPT,
            llm_config=llm_config,
        )

    def create_agent(self) -> AssistantAgent:
        """Create the AutoGen AssistantAgent instance."""
        return AssistantAgent(
            name=self.name,
            description=self.system_message,
        )

    def validate_assessment_score(self, test_name: str, score: int) -> dict:
        """
        Validate neurological assessment score is within valid range.

        Args:
            test_name: Name of the assessment test
            score: Score value to validate

        Returns:
            Validation result dictionary
        """
        valid_ranges = {
            "mmse": {"min": 0, "max": 30, "description": "Mini-Mental State Exam"},
            "moca": {"min": 0, "max": 30, "description": "Montreal Cognitive Assessment"},
            "updrs": {"min": 0, "max": 199, "description": "Unified Parkinson's Disease Rating Scale"},
            "edss": {"min": 0, "max": 10, "description": "Expanded Disability Status Scale"},
            "nihss": {"min": 0, "max": 42, "description": "NIH Stroke Scale"},
            "midas": {"min": 0, "max": 270, "description": "Migraine Disability Assessment"},
            "motor_function": {"min": 0, "max": 100, "description": "Motor Function Score"},
            "symptom_severity": {"min": 0, "max": 10, "description": "Symptom Severity Scale"},
        }

        test_key = test_name.lower().replace(" ", "_").replace("-", "_")

        if test_key not in valid_ranges:
            return {
                "status": "WARNING",
                "category": "Data Integrity",
                "field": test_name,
                "issue": f"Unknown assessment type: {test_name}",
                "severity": "Medium",
                "recommendation": "Verify test name is correct",
            }

        range_info = valid_ranges[test_key]

        if score < range_info["min"] or score > range_info["max"]:
            return {
                "status": "FAIL",
                "category": "Data Integrity",
                "field": test_name,
                "issue": f"Score {score} is outside valid range ({range_info['min']}-{range_info['max']})",
                "severity": "High",
                "recommendation": f"Verify {range_info['description']} score entry",
            }

        return {
            "status": "PASS",
            "category": "Data Integrity",
            "field": test_name,
            "issue": None,
            "severity": None,
            "recommendation": None,
        }

    def validate_vital_signs(self, vitals: dict) -> list[dict]:
        """
        Validate vital signs are within plausible ranges.

        Args:
            vitals: Dictionary of vital sign measurements

        Returns:
            List of validation results
        """
        vital_ranges = {
            "blood_pressure_systolic": {"min": 70, "max": 250, "unit": "mmHg"},
            "blood_pressure_diastolic": {"min": 40, "max": 150, "unit": "mmHg"},
            "heart_rate": {"min": 30, "max": 200, "unit": "bpm"},
            "temperature": {"min": 35.0, "max": 42.0, "unit": "C"},
            "weight_kg": {"min": 20, "max": 300, "unit": "kg"},
        }

        results = []

        for vital_name, value in vitals.items():
            if value is None:
                continue

            if vital_name not in vital_ranges:
                continue

            range_info = vital_ranges[vital_name]

            if value < range_info["min"] or value > range_info["max"]:
                results.append({
                    "status": "FAIL",
                    "category": "Clinical Logic",
                    "field": vital_name,
                    "issue": f"Value {value} {range_info['unit']} is outside plausible range",
                    "severity": "High",
                    "recommendation": "Verify vital sign measurement",
                })
            else:
                results.append({
                    "status": "PASS",
                    "category": "Clinical Logic",
                    "field": vital_name,
                    "issue": None,
                    "severity": None,
                    "recommendation": None,
                })

        return results

    def check_score_consistency(
        self,
        current_score: int,
        previous_score: int,
        test_name: str,
        threshold_pct: float = 30.0
    ) -> dict:
        """
        Check for unusual changes between consecutive scores.

        Args:
            current_score: Most recent score
            previous_score: Previous score
            test_name: Name of the assessment
            threshold_pct: Percentage change threshold for flagging

        Returns:
            Validation result dictionary
        """
        if previous_score == 0:
            return {
                "status": "PASS",
                "category": "Anomaly Detection",
                "field": test_name,
                "issue": None,
                "severity": None,
                "recommendation": None,
            }

        change_pct = abs((current_score - previous_score) / previous_score) * 100

        if change_pct > threshold_pct:
            direction = "increase" if current_score > previous_score else "decrease"
            return {
                "status": "WARNING",
                "category": "Anomaly Detection",
                "field": test_name,
                "issue": f"Large {direction} detected: {previous_score} -> {current_score} ({change_pct:.1f}% change)",
                "severity": "Medium",
                "recommendation": "Verify score accuracy and investigate cause of significant change",
            }

        return {
            "status": "PASS",
            "category": "Anomaly Detection",
            "field": test_name,
            "issue": None,
            "severity": None,
            "recommendation": None,
        }

    def validate_medication_dosage(self, medication: str, dosage_mg: float) -> dict:
        """
        Validate medication dosage is within typical ranges.

        Args:
            medication: Medication name
            dosage_mg: Dosage in milligrams

        Returns:
            Validation result dictionary
        """
        medication_ranges = {
            "levodopa": {"min": 100, "max": 2000, "unit": "mg/day"},
            "carbamazepine": {"min": 200, "max": 1600, "unit": "mg/day"},
            "valproate": {"min": 500, "max": 3000, "unit": "mg/day"},
            "lamotrigine": {"min": 25, "max": 400, "unit": "mg/day"},
            "topiramate": {"min": 25, "max": 400, "unit": "mg/day"},
            "sumatriptan": {"min": 25, "max": 200, "unit": "mg/day"},
            "donepezil": {"min": 5, "max": 23, "unit": "mg/day"},
            "memantine": {"min": 5, "max": 28, "unit": "mg/day"},
            "pramipexole": {"min": 0.125, "max": 4.5, "unit": "mg/day"},
            "ropinirole": {"min": 0.25, "max": 24, "unit": "mg/day"},
        }

        med_key = medication.lower().strip()

        if med_key not in medication_ranges:
            return {
                "status": "WARNING",
                "category": "Clinical Logic",
                "field": f"medication:{medication}",
                "issue": f"Medication '{medication}' not in validation database",
                "severity": "Low",
                "recommendation": "Manual review of dosage recommended",
            }

        range_info = medication_ranges[med_key]

        if dosage_mg < range_info["min"] or dosage_mg > range_info["max"]:
            return {
                "status": "WARNING",
                "category": "Clinical Logic",
                "field": f"medication:{medication}",
                "issue": f"Dosage {dosage_mg}mg outside typical range ({range_info['min']}-{range_info['max']} {range_info['unit']})",
                "severity": "High",
                "recommendation": "Verify dosage is correct and clinically appropriate",
            }

        return {
            "status": "PASS",
            "category": "Clinical Logic",
            "field": f"medication:{medication}",
            "issue": None,
            "severity": None,
            "recommendation": None,
        }

    def generate_validation_summary(self, results: list[dict]) -> dict:
        """
        Generate summary of validation results.

        Args:
            results: List of validation result dictionaries

        Returns:
            Summary dictionary with counts and status
        """
        summary = {
            "total_checks": len(results),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "critical_issues": [],
            "high_priority_issues": [],
            "overall_status": "PASS",
        }

        for result in results:
            if result["status"] == "PASS":
                summary["passed"] += 1
            elif result["status"] == "FAIL":
                summary["failed"] += 1
                if result["severity"] == "Critical":
                    summary["critical_issues"].append(result)
                elif result["severity"] == "High":
                    summary["high_priority_issues"].append(result)
            elif result["status"] == "WARNING":
                summary["warnings"] += 1

        if summary["failed"] > 0:
            summary["overall_status"] = "FAIL"
        elif summary["warnings"] > 0:
            summary["overall_status"] = "WARNING"

        return summary
