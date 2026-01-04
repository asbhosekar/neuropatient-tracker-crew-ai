"""
Pytest configuration and shared fixtures.
"""
import pytest
from datetime import date, datetime
from src.models.schemas import (
    Patient,
    PatientCreate,
    Gender,
    NeurologicalCondition,
    Visit,
    VitalSigns,
    NeurologicalAssessment,
    MedicationRecord,
)


@pytest.fixture
def sample_patient():
    """Fixture providing a sample patient."""
    return Patient(
        id="PT-TEST-001",
        first_name="John",
        last_name="Doe",
        date_of_birth=date(1960, 5, 15),
        gender=Gender.MALE,
        email="john.doe@test.com",
        phone="555-0123",
        primary_condition=NeurologicalCondition.PARKINSONS,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True,
    )


@pytest.fixture
def sample_patient_create():
    """Fixture providing a sample patient creation request."""
    return PatientCreate(
        first_name="Jane",
        last_name="Smith",
        date_of_birth=date(1975, 3, 20),
        gender=Gender.FEMALE,
        primary_condition=NeurologicalCondition.EPILEPSY,
    )


@pytest.fixture
def sample_vitals():
    """Fixture providing sample vital signs."""
    return VitalSigns(
        blood_pressure_systolic=120,
        blood_pressure_diastolic=80,
        heart_rate=72,
        temperature=98.6,
        weight_kg=70.0,
    )


@pytest.fixture
def sample_assessment():
    """Fixture providing a sample neurological assessment."""
    return NeurologicalAssessment(
        mmse_score=28,
        moca_score=26,
        motor_function_score=85,
        symptom_severity=3,
        seizure_frequency=2,
        notes="Stable condition",
    )


@pytest.fixture
def sample_medication():
    """Fixture providing a sample medication record."""
    return MedicationRecord(
        name="Levetiracetam",
        dosage="500mg",
        frequency="BID",
        start_date=date(2024, 1, 1),
        is_active=True,
    )
