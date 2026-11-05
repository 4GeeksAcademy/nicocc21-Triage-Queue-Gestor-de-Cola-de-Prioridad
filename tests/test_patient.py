"""Tests for the Patient class."""

from datetime import datetime

import pytest

from queue.patient import Patient


def make_patient(name="Ana", level=1, pid=1, arrived=None):
    """Helper to create a patient with a fixed or now timestamp."""
    return Patient(
        name=name,
        triage_level=level,
        arrived_at=arrived or datetime.now(),
        patient_id=pid,
    )


def test_create_valid_patient():
    """Creating a patient with valid data should work."""
    patient = make_patient()

    assert patient.name == "Ana"
    assert patient.triage_level == 1
    assert patient.patient_id == 1
    assert isinstance(patient.arrived_at, datetime)


def test_name_is_stripped():
    """Leading and trailing whitespace in name should be removed."""
    patient = make_patient(name="  Pedro Pérez  ", level=2)

    assert patient.name == "Pedro Pérez"


def test_invalid_triage_level_raises():
    """Invalid triage levels should raise ValueError."""
    for invalid_level in (0, 4, -1, 10, "abc", None):
        with pytest.raises(ValueError):
            make_patient(level=invalid_level)


def test_empty_name_raises():
    """Empty or whitespace-only names should raise ValueError."""
    for invalid_name in ("", "   ", "\t"):
        with pytest.raises(ValueError):
            make_patient(name=invalid_name)


def test_str_representation():
    """String representation should include name and level."""
    patient = make_patient(name="María", level=3)

    text = str(patient)
    assert "María" in text
    assert "3" in text
    assert "ESTÁNDAR" in text


def test_repr_representation():
    """Repr (dataclass) should include all fields."""
    patient = make_patient(name="Luis", level=2, pid=7)

    text = repr(patient)
    assert "Luis" in text
    assert "2" in text
    assert "7" in text


def test_arrived_at_preserved():
    """The arrived_at timestamp should be preserved as given."""
    ts = datetime(2026, 11, 5, 9, 30, 0)
    patient = make_patient(arrived=ts)

    assert patient.arrived_at == ts