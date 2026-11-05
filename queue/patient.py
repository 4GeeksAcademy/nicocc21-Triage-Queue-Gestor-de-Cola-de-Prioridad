"""
Patient module for the Triage Queue system.

Represents a patient with name, triage level, and arrival timestamp.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Patient:
    """Represents a patient in the triage queue."""

    VALID_LEVELS = {1, 2, 3}

    name: str
    triage_level: int
    arrived_at: datetime
    patient_id: int

    def __post_init__(self) -> None:
        """Validate the patient data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Patient name cannot be empty.")

        if self.triage_level not in self.VALID_LEVELS:
            raise ValueError(
                f"Invalid triage level: {self.triage_level}. "
                f"Must be one of {sorted(self.VALID_LEVELS)}."
            )

        self.name = self.name.strip()

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        level_labels = {1: "CRÍTICO", 2: "URGENTE", 3: "ESTÁNDAR"}
        label = level_labels.get(self.triage_level, "DESCONOCIDO")
        arrived = self.arrived_at.strftime("%H:%M:%S")
        return (
            f"[{self.patient_id}] {self.name} — "
            f"Nivel {self.triage_level} ({label}) · llegó {arrived}"
        )