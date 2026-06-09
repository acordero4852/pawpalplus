"""Tests for core PawPal+ behaviors."""

from datetime import date, time, timedelta

from pawpal_system import Pet, Priority, Recurrence, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task from incomplete to complete."""
    task = Task("Morning walk", "walk", duration=30, priority=Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count."""
    pet = Pet("Biscuit", "Dog", "Golden Retriever")
    assert len(pet.tasks) == 0

    pet.add_task(Task("Feeding", "feeding", duration=10, priority=Priority.HIGH))

    assert len(pet.tasks) == 1


# --- Sorting correctness ---------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() returns tasks ordered by preferred_time, earliest first."""
    noon = Task("Lunch feed", "feeding", duration=10, priority=Priority.LOW,
                preferred_time=time(12, 0))
    morning = Task("Morning walk", "walk", duration=30, priority=Priority.LOW,
                   preferred_time=time(8, 0))
    evening = Task("Evening walk", "walk", duration=30, priority=Priority.HIGH,
                   preferred_time=time(18, 0))

    ordered = Scheduler().sort_by_time([noon, evening, morning])

    assert [t.name for t in ordered] == ["Morning walk", "Lunch feed", "Evening walk"]


def test_sort_by_time_places_untimed_tasks_last():
    """Tasks without a preferred_time sort after all timed tasks."""
    timed = Task("Walk", "walk", duration=30, priority=Priority.LOW,
                 preferred_time=time(9, 0))
    untimed = Task("Grooming", "grooming", duration=20, priority=Priority.LOW)

    ordered = Scheduler().sort_by_time([untimed, timed])

    assert [t.name for t in ordered] == ["Walk", "Grooming"]


# --- Recurrence logic ------------------------------------------------------


def test_completing_daily_task_creates_next_day_occurrence():
    """Marking a daily task complete enrolls a fresh task due the next day."""
    pet = Pet("Biscuit", "Dog", "Golden Retriever")
    today = date.today()
    task = Task("Morning walk", "walk", duration=30, priority=Priority.HIGH,
                recurrence=Recurrence.DAILY, due_date=today)
    pet.add_task(task)

    new_task = task.mark_complete()

    assert task.completed is True
    # A new, distinct, incomplete occurrence was created...
    assert new_task is not None
    assert new_task.completed is False
    assert new_task.task_id != task.task_id
    # ...due the following day...
    assert new_task.due_date == today + timedelta(days=1)
    # ...and auto-added to the pet.
    assert new_task in pet.tasks
    assert len(pet.tasks) == 2


def test_completing_non_recurring_task_creates_no_occurrence():
    """A one-off task does not spawn a follow-up when completed."""
    pet = Pet("Biscuit", "Dog", "Golden Retriever")
    task = Task("Vet visit", "health", duration=60, priority=Priority.HIGH)
    pet.add_task(task)

    result = task.mark_complete()

    assert result is None
    assert len(pet.tasks) == 1


# --- Conflict detection ----------------------------------------------------


def test_scheduler_flags_tasks_at_same_time():
    """Two tasks with overlapping preferred times produce a conflict warning."""
    walk = Task("Walk", "walk", duration=30, priority=Priority.HIGH,
                preferred_time=time(9, 0))
    feed = Task("Feed", "feeding", duration=10, priority=Priority.HIGH,
                preferred_time=time(9, 0))

    warnings = Scheduler().detect_conflicts([walk, feed])

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]


def test_scheduler_allows_back_to_back_tasks():
    """Adjacent tasks that merely touch (A ends when B starts) do not conflict."""
    first = Task("Walk", "walk", duration=30, priority=Priority.HIGH,
                 preferred_time=time(9, 0))
    second = Task("Feed", "feeding", duration=10, priority=Priority.HIGH,
                  preferred_time=time(9, 30))

    warnings = Scheduler().detect_conflicts([first, second])

    assert warnings == []
