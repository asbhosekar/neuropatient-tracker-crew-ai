"""
Tests for data models and schemas.
"""
import pytest
from datetime import date, datetime
from src.models.schemas import (
    Patient,
    PatientCreate,
    Gender,
    NeurologicalCondition,
    Visit,
    VisitCreate,
    VitalSigns,
    NeurologicalAssessment,
    MedicationRecord,
    PrognosisAnalysis,
    PrognosisTrend,
    SeverityLevel,
)


class TestPatientModels:
    """Test Patient data models."""

    def test_patient_create(self):
        """Test creating a patient."""
        patient = PatientCreate(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1960, 5, 15),
            gender=Gender.MALE,
            email="john.doe@example.com",
            phone="555-0123",
            primary_condition=NeurologicalCondition.PARKINSONS,
        )

        assert patient.first_name == "John"
        assert patient.last_name == "Doe"
        assert patient.gender == Gender.MALE
        assert patient.primary_condition == NeurologicalCondition.PARKINSONS

    def test_patient_full_model(self):
        """Test full Patient model with metadata."""
        patient = Patient(
            id="PT-001",
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1975, 3, 20),
            gender=Gender.FEMALE,
            primary_condition=NeurologicalCondition.EPILEPSY,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True,
        )

        assert patient.id == "PT-001"
        assert patient.is_active is True
        assert patient.primary_condition == NeurologicalCondition.EPILEPSY


class TestVisitModels:
    """Test Visit data models."""

    def test_vital_signs(self):
        """Test VitalSigns model."""
        vitals = VitalSigns(
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            heart_rate=72,
            temperature=98.6,
            weight_kg=75.5,
        )

        assert vitals.blood_pressure_systolic == 120
        assert vitals.heart_rate == 72

    def test_neurological_assessment(self):
        """Test NeurologicalAssessment model."""
        assessment = NeurologicalAssessment(
            mmse_score=28,
            moca_score=26,
            motor_function_score=85,
            symptom_severity=3,
            seizure_frequency=2,
            notes="Stable cognitive function",
        )

        assert assessment.mmse_score == 28
        assert assessment.motor_function_score == 85

    def test_neurological_assessment_score_validation(self):
        """Test score validation in NeurologicalAssessment."""
        # Valid scores
        assessment = NeurologicalAssessment(
            mmse_score=30,  # Max valid
            moca_score=0,   # Min valid
        )
        assert assessment.mmse_score == 30

        # Invalid scores should raise validation error
        with pytest.raises(ValueError):
            NeurologicalAssessment(mmse_score=31)  # Above max

        with pytest.raises(ValueError):
            NeurologicalAssessment(motor_function_score=101)  # Above max

    def test_medication_record(self):
        """Test MedicationRecord model."""
        med = MedicationRecord(
            name="Levetiracetam",
            dosage="500mg",
            frequency="BID",
            start_date=date(2024, 1, 1),
            is_active=True,
        )

        assert med.name == "Levetiracetam"
        assert med.is_active is True

    def test_visit_create(self):
        """Test creating a visit."""
        visit = VisitCreate(
            patient_id="PT-001",
            chief_complaint="Follow-up for Parkinson's management",
            vitals=VitalSigns(heart_rate=75),
            assessment=NeurologicalAssessment(mmse_score=27),
            medications=[
                MedicationRecord(
                    name="Carbidopa/Levodopa",
                    dosage="25/100mg",
                    frequency="TID",
                    start_date=date(2024, 1, 1),
                )
            ],
        )

        assert visit.patient_id == "PT-001"
        assert len(visit.medications) == 1


class TestPrognosisModels:
    """Test Prognosis data models."""

    def test_prognosis_analysis(self):
        """Test PrognosisAnalysis model."""
        prognosis = PrognosisAnalysis(
            patient_id="PT-001",
            condition=NeurologicalCondition.PARKINSONS,
            overall_trend=PrognosisTrend.STABLE,
            cognitive_trend=PrognosisTrend.IMPROVING,
            motor_trend=PrognosisTrend.DECLINING,
            current_severity=SeverityLevel.MODERATE,
            predicted_severity_3mo=SeverityLevel.MODERATE,
            predicted_severity_6mo=SeverityLevel.SEVERE,
            summary="Patient showing mixed trends with cognitive improvement but motor decline.",
            recommendations=[
                "Consider medication adjustment",
                "Increase physical therapy frequency",
            ],
            risk_factors=["Age", "Disease progression"],
            confidence_score=0.82,
        )

        assert prognosis.patient_id == "PT-001"
        assert prognosis.overall_trend == PrognosisTrend.STABLE
        assert prognosis.confidence_score == 0.82
        assert len(prognosis.recommendations) == 2

    def test_prognosis_confidence_validation(self):
        """Test confidence score validation."""
        # Valid confidence
        prognosis = PrognosisAnalysis(
            patient_id="PT-001",
            condition=NeurologicalCondition.EPILEPSY,
            overall_trend=PrognosisTrend.IMPROVING,
            current_severity=SeverityLevel.MILD,
            summary="Test summary",
            confidence_score=1.0,  # Max valid
        )
        assert prognosis.confidence_score == 1.0

        # Invalid confidence should raise error
        with pytest.raises(ValueError):
            PrognosisAnalysis(
                patient_id="PT-001",
                condition=NeurologicalCondition.EPILEPSY,
                overall_trend=PrognosisTrend.IMPROVING,
                current_severity=SeverityLevel.MILD,
                summary="Test",
                confidence_score=1.5,  # Above max
            )


class TestEnums:
    """Test enum values."""

    def test_gender_enum(self):
        """Test Gender enum."""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.OTHER.value == "other"

    def test_condition_enum(self):
        """Test NeurologicalCondition enum."""
        assert NeurologicalCondition.PARKINSONS.value == "parkinsons"
        assert NeurologicalCondition.EPILEPSY.value == "epilepsy"
        assert NeurologicalCondition.ALZHEIMERS.value == "alzheimers"

    def test_trend_enum(self):
        """Test PrognosisTrend enum."""
        assert PrognosisTrend.IMPROVING.value == "improving"
        assert PrognosisTrend.STABLE.value == "stable"
        assert PrognosisTrend.DECLINING.value == "declining"

    def test_severity_enum(self):
        """Test SeverityLevel enum."""
        assert SeverityLevel.MILD.value == "mild"
        assert SeverityLevel.MODERATE.value == "moderate"
        assert SeverityLevel.SEVERE.value == "severe"
        assert SeverityLevel.CRITICAL.value == "critical"
