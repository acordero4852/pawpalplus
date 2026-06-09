"""Tests for core PawPal+ behaviors."""

from pawpal_system import Pet, Priority, Task


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
