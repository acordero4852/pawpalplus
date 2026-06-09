"""PawPal+ core implementation.

Domain model and scheduling logic for planning a pet owner's daily care tasks.
Data flow: Owner -> Pet -> Task -> Scheduler -> DailyPlan.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, time, timedelta
from enum import Enum

# Default time of day the scheduler starts placing tasks.
DAY_START = time(8, 0)


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def rank(self) -> int:
        """Lower rank = more important (sorts first)."""
        return {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}[self]


class Task:
    def __init__(
        self,
        name: str,
        category: str,
        duration: int,
        priority: Priority,
        preferred_time: time | None = None,
        recurring: bool = False,
        task_id: str | None = None,
    ) -> None:
        """Create a care task; generates a unique id if none is given."""
        self.task_id = task_id or str(uuid.uuid4())
        self.name = name
        self.category = category
        self.duration = duration
        self.priority = priority
        self.preferred_time = preferred_time
        self.recurring = recurring
        self.completed = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def is_higher_priority_than(self, other: "Task") -> bool:
        """Return True if this task outranks another in priority."""
        return self.priority.rank < other.priority.rank

    def __repr__(self) -> str:
        """Return a concise developer-readable representation."""
        return (
            f"Task({self.name!r}, {self.category}, {self.duration}min, "
            f"{self.priority.value})"
        )


class Pet:
    def __init__(self, name: str, species: str, breed: str) -> None:
        """Create a pet with an empty task list."""
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def edit_task(self, task_id: str, **changes) -> None:
        """Update fields of the task with the given id."""
        task = self._find(task_id)
        if task is None:
            raise KeyError(f"No task with id {task_id!r}")
        for field, value in changes.items():
            if not hasattr(task, field):
                raise AttributeError(f"Task has no field {field!r}")
            setattr(task, field, value)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given id, if present."""
        self.tasks = [t for t in self.tasks if t.task_id != task_id]

    def get_tasks(self, filter_by: Priority | None = None) -> list[Task]:
        """Return all tasks, optionally filtered by priority."""
        if filter_by is None:
            return list(self.tasks)
        return [t for t in self.tasks if t.priority == filter_by]

    def _find(self, task_id: str) -> Task | None:
        """Return the task with the given id, or None."""
        return next((t for t in self.tasks if t.task_id == task_id), None)


class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: dict | None = None,
    ) -> None:
        """Create an owner with a daily time budget and no pets yet."""
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Register a pet with this owner."""
        self.pets.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner, if present."""
        if pet in self.pets:
            self.pets.remove(pet)

    def all_tasks(self) -> list[Task]:
        """Collect tasks across every pet for the scheduler."""
        return [task for pet in self.pets for task in pet.tasks]


class PlanEntry:
    def __init__(self, start_time: time, task: Task) -> None:
        """Pair an assigned start time with a scheduled task."""
        self.start_time = start_time
        self.task = task

    def __repr__(self) -> str:
        """Return a human-readable schedule line."""
        return (
            f"{self.start_time.strftime('%H:%M')} — {self.task.name} "
            f"({self.task.duration} min) [priority: {self.task.priority.value}]"
        )


class DailyPlan:
    def __init__(self) -> None:
        """Create an empty daily plan."""
        self.entries: list[PlanEntry] = []
        self.skipped: list[Task] = []
        self.total_minutes: int = 0

    def add_entry(self, start_time: time, task: Task) -> None:
        """Append a scheduled task and update the running total."""
        self.entries.append(PlanEntry(start_time, task))
        self.total_minutes += task.duration

    def to_display(self) -> str:
        """Render the plan as a multi-line schedule string."""
        if not self.entries:
            return "No tasks scheduled."
        lines = [repr(entry) for entry in self.entries]
        return "\n".join(lines)

    def summary(self) -> str:
        """Return a one-line summary of scheduled and skipped tasks."""
        parts = [
            f"Scheduled {len(self.entries)} task(s), {self.total_minutes} min total."
        ]
        if self.skipped:
            names = ", ".join(t.name for t in self.skipped)
            parts.append(f"Skipped (out of time): {names}.")
        return " ".join(parts)


class Scheduler:
    def __init__(self, day_start: time = DAY_START) -> None:
        """Create a scheduler that starts placing tasks at day_start."""
        self.day_start = day_start

    def build_plan(self, tasks: list[Task], available_minutes: int) -> DailyPlan:
        """Greedily place tasks in priority order until time runs out."""
        plan = DailyPlan()
        cursor = datetime.combine(date.today(), self.day_start)
        remaining = available_minutes

        for task in self.sort_tasks(tasks):
            if self.fits(task, remaining):
                plan.add_entry(cursor.time(), task)
                cursor += timedelta(minutes=task.duration)
                remaining -= task.duration
            else:
                plan.skipped.append(task)

        return plan

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Highest priority first; shorter tasks first as a tiebreaker."""
        return sorted(tasks, key=lambda t: (t.priority.rank, t.duration))

    def fits(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits within the remaining time budget."""
        return task.duration <= remaining_minutes
