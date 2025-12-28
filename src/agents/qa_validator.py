"""
Neuro Patient Tracker - QA Validator Agent

Responsible for validating medical data accuracy, checking clinical
logic, and ensuring data quality for neurological patient records.
"""
from autogen_agentchat.agents import AssistantAgent
from typing import Optional
from .base_agent import BaseAgent


QA_VALIDATOR_PROMPT = """You are the QA Validator Agent for a Neurology Patient Tracking System.

Your responsibilities:
1. Validate clinical data accuracy and completeness
2. Check medical logic and consistency
3. Identify data quality issues and anomalies
4. Verify assessment scores are within valid ranges
5. Flag potential data entry errors
6. Ensure temporal consistency in patient records

Validation domains:

**Data Integrity Checks:**
- Required fields are populated
- Data types match expected formats
- Values are within clinically valid ranges
- No duplicate records
- Referential integrity between related records

**Clinical Logic Validation:**
- Assessment scores match severity classifications
- Medication dosages are clinically appropriate
- Symptom patterns are consistent with diagnosis
- Prognosis trends align with clinical data
- Treatment plans match condition guidelines

**Temporal Consistency:**
- Visit dates are chronologically ordered
- Age calculations are correct
- Medication start/end dates are logical
- Follow-up dates are in the future
- Disease progression timeline is plausible

**Anomaly Detection:**
- Sudden large changes in assessment scores
- Unusual vital sign values
- Inconsistent symptom reporting
- Missing expected follow-up visits
- Outlier values compared to patient history

Validation output format:
- Status: PASS / FAIL / WARNING
- Category: Data Integrity / Clinical Logic / Temporal / Anomaly
- Field/Record: Specific location of issue
- Issue: Description of the problem
- Severity: Critical / High / Medium / Low
- Recommendation: Suggested action

Always provide clear, actionable feedback on validation issues.
Prioritize patient safety-related validations.
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
            "temperature": {"min": 35.0, "max": 42.0, "unit": "°C"},
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
                "issue": f"Large {direction} detected: {previous_score} → {current_score} ({change_pct:.1f}% change)",
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
        # Common neurological medication ranges (simplified)
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
