"""Tests for the TriageQueue class."""

from datetime import datetime

import pytest

from queue.patient import Patient
from queue.triage_queue import QueueEmptyError, TriageQueue


def make_patient(name: str, level: int, pid: int, ts=None) -> Patient:
    """Helper to create a patient for testing."""
    return Patient(
        name=name,
        triage_level=level,
        arrived_at=ts or datetime.now(),
        patient_id=pid,
    )


# --- enqueue / dequeue ---


def test_new_queue_is_empty():
    """A new queue should be empty."""
    q = TriageQueue()
    assert q.peek() is None
    assert q.list_queue() == []
    assert q.stats()["total"] == 0


def test_strict_priority_order():
    """Dequeue should respect strict priority: 1 before 2 before 3."""
    q = TriageQueue()
    p3 = make_patient("Std", 3, 1)
    p2 = make_patient("Urg", 2, 2)
    p1 = make_patient("Crit", 1, 3)

    q.enqueue(p3)
    q.enqueue(p2)
    q.enqueue(p1)

    assert q.dequeue() is p1
    assert q.dequeue() is p2
    assert q.dequeue() is p3


def test_fifo_within_same_level():
    """Patients of the same level should be served in arrival order."""
    q = TriageQueue()
    pa = make_patient("A", 2, 1)
    pb = make_patient("B", 2, 2)
    pc = make_patient("C", 2, 3)

    q.enqueue(pa)
    q.enqueue(pb)
    q.enqueue(pc)

    assert q.dequeue() is pa
    assert q.dequeue() is pb
    assert q.dequeue() is pc


def test_priority_with_late_arrival():
    """A critical patient arriving late should jump ahead of lower levels."""
    q = TriageQueue()
    p3a = make_patient("Std-A", 3, 1)
    p2a = make_patient("Urg-A", 2, 2)
    p3b = make_patient("Std-B", 3, 3)
    p1a = make_patient("Crit-A", 1, 4)

    q.enqueue(p3a)
    q.enqueue(p2a)
    q.enqueue(p3b)
    q.enqueue(p1a)

    assert q.dequeue() is p1a
    assert q.dequeue() is p2a
    assert q.dequeue() is p3a
    assert q.dequeue() is p3b


def test_fifo_within_same_level_late_critical():
    """A late critical (level 1) goes ahead of level 2/3 but behind earlier level 1."""
    q = TriageQueue()
    p1_early = make_patient("Crit-A", 1, 1)
    p2 = make_patient("Urg-A", 2, 2)
    p1_late = make_patient("Crit-B", 1, 3)

    q.enqueue(p1_early)
    q.enqueue(p2)
    q.enqueue(p1_late)

    # The late critical goes behind the earlier critical, but ahead of urgent
    assert q.dequeue() is p1_early
    assert q.dequeue() is p1_late
    assert q.dequeue() is p2


def test_dequeue_empty_raises():
    """Dequeue on an empty queue should raise QueueEmptyError."""
    q = TriageQueue()
    with pytest.raises(QueueEmptyError):
        q.dequeue()


def test_dequeue_empty_after_draining():
    """Dequeue should raise after all patients are drained."""
    q = TriageQueue()
    q.enqueue(make_patient("A", 1, 1))
    q.dequeue()
    with pytest.raises(QueueEmptyError):
        q.dequeue()


# --- peek ---


def test_peek_does_not_remove():
    """Peek should return the next patient without removing them."""
    q = TriageQueue()
    p1 = make_patient("Crit", 1, 1)
    q.enqueue(p1)

    assert q.peek() is p1
    assert q.peek() is p1
    assert len(q.list_queue()) == 1


def test_peek_empty_returns_none():
    """Peek on an empty queue should return None (not raise)."""
    q = TriageQueue()
    assert q.peek() is None


def test_peek_with_multiple_levels():
    """Peek should return the highest-priority patient."""
    q = TriageQueue()
    p2 = make_patient("Urg", 2, 1)
    p3 = make_patient("Std", 3, 2)
    p1 = make_patient("Crit", 1, 3)

    q.enqueue(p2)
    q.enqueue(p3)
    q.enqueue(p1)

    assert q.peek() is p1


# --- list_queue ---


def test_list_queue_order():
    """list_queue should return patients in attention order."""
    q = TriageQueue()
    p3a = make_patient("Std-A", 3, 1)
    p1a = make_patient("Crit-A", 1, 2)
    p2a = make_patient("Urg-A", 2, 3)
    p2b = make_patient("Urg-B", 2, 4)

    q.enqueue(p3a)
    q.enqueue(p1a)
    q.enqueue(p2a)
    q.enqueue(p2b)

    assert q.list_queue() == [p1a, p2a, p2b, p3a]


def test_list_queue_does_not_modify():
    """list_queue should not modify the queue."""
    q = TriageQueue()
    p1 = make_patient("A", 1, 1)
    q.enqueue(p1)

    q.list_queue()

    assert q.peek() is p1
    assert len(q.list_queue()) == 1


def test_list_queue_empty():
    """list_queue on an empty queue should return []."""
    q = TriageQueue()
    assert q.list_queue() == []


# --- stats ---


def test_stats_empty():
    """stats on an empty queue should be all zeros."""
    q = TriageQueue()
    assert q.stats() == {"level_1": 0, "level_2": 0, "level_3": 0, "total": 0}


def test_stats_counts():
    """stats should report counts per level and total."""
    q = TriageQueue()
    q.enqueue(make_patient("A", 1, 1))
    q.enqueue(make_patient("B", 1, 2))
    q.enqueue(make_patient("C", 2, 3))
    q.enqueue(make_patient("D", 3, 4))

    assert q.stats() == {"level_1": 2, "level_2": 1, "level_3": 1, "total": 4}


def test_stats_after_dequeue():
    """stats should update correctly after dequeuing."""
    q = TriageQueue()
    q.enqueue(make_patient("A", 1, 1))
    q.enqueue(make_patient("B", 2, 2))
    q.enqueue(make_patient("C", 3, 3))

    q.dequeue()  # removes level 1

    assert q.stats() == {"level_1": 0, "level_2": 1, "level_3": 1, "total": 2}


# --- full flow ---


def test_full_flow():
    """End-to-end flow: enqueue, peek, list, dequeue, stats."""
    q = TriageQueue()

    q.enqueue(make_patient("Paciente A", 3, 1))
    q.enqueue(make_patient("Paciente B", 2, 2))
    q.enqueue(make_patient("Paciente C", 1, 3))

    # Peek
    assert q.peek().name == "Paciente C"

    # List
    assert [p.name for p in q.list_queue()] == [
        "Paciente C",
        "Paciente B",
        "Paciente A",
    ]

    # Dequeue
    assert q.dequeue().name == "Paciente C"

    # Stats after
    assert q.stats() == {"level_1": 0, "level_2": 1, "level_3": 1, "total": 2}