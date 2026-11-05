"""
TriageQueue module for the Triage Queue system.

Manages the triage priority queue internally using three FIFO queues
(collections.deque), one per triage level.
"""

from collections import deque
from datetime import datetime
from typing import Optional

from queue.patient import Patient


class QueueEmptyError(Exception):
    """Raised when trying to dequeue or peek from an empty queue."""


class TriageQueue:
    """
    A priority queue for hospital triage.

    Level 1 (critical) has the highest priority, followed by level 2 (urgent)
    and level 3 (standard). Within the same level, patients are attended in
    strict arrival order (FIFO).

    Internally this uses three separate FIFO queues (one per level), so a
    critical patient arriving late simply appends to the level-1 queue without
    reordering anything.
    """

    def __init__(self) -> None:
        """Initialize an empty triage queue."""
        self._queues: dict[int, deque[Patient]] = {
            1: deque(),
            2: deque(),
            3: deque(),
        }
        self._counter = 0

    def enqueue(self, patient: Patient) -> None:
        """
        Add a patient to the queue.

        The patient keeps the arrival time set at creation and is appended
        to the end of their triage level queue.

        Args:
            patient: The Patient to enqueue.
        """
        self._queues[patient.triage_level].append(patient)

    def dequeue(self) -> Patient:
        """
        Remove and return the next patient to attend.

        Returns:
            The highest-priority waiting Patient.

        Raises:
            QueueEmptyError: If the queue is empty.
        """
        patient = self._pop_next()
        if patient is None:
            raise QueueEmptyError("Cannot dequeue: the queue is empty.")
        return patient

    def peek(self) -> Optional[Patient]:
        """
        Return the next patient to attend without removing them.

        Returns:
            The highest-priority waiting Patient, or None if the queue is empty.
        """
        for level in (1, 2, 3):
            if self._queues[level]:
                return self._queues[level][0]
        return None

    def list_queue(self) -> list[Patient]:
        """
        Return all waiting patients in order of attention.

        Patients are ordered by triage level (1 → 2 → 3) and FIFO within
        each level.

        Returns:
            A flat list of all waiting patients in attention order.
        """
        result: list[Patient] = []
        for level in (1, 2, 3):
            result.extend(self._queues[level])
        return result

    def stats(self) -> dict[str, int]:
        """
        Return statistics about waiting patients.

        Returns:
            A dict with keys 'level_1', 'level_2', 'level_3', and 'total'.
        """
        counts = {
            f"level_{level}": len(self._queues[level]) for level in (1, 2, 3)
        }
        counts["total"] = sum(counts.values())
        return counts

    # --- Helpers ---

    def _pop_next(self) -> Optional[Patient]:
        """Pop the highest-priority patient, or None if empty."""
        for level in (1, 2, 3):
            if self._queues[level]:
                return self._queues[level].popleft()
        return None

    # --- Factory ---

    @staticmethod
    def make_patient(name: str, triage_level: int, patient_id: int) -> Patient:
        """
        Factory helper to create a Patient.

        This keeps Patient creation out of the CLI to preserve a clean
        separation of responsibilities.

        Args:
            name: Patient's name.
            triage_level: Triage level (1=critical, 2=urgent, 3=standard).
            patient_id: Unique identifier.

        Returns:
            A new Patient with the current timestamp.
        """
        return Patient(
            name=name,
            triage_level=triage_level,
            arrived_at=datetime.now(),
            patient_id=patient_id,
        )