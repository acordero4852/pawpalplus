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


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"

    @property
    def delta(self) -> timedelta | None:
        """Time between occurrences, or None for non-recurring tasks."""
        return {
            Recurrence.NONE: None,
            Recurrence.DAILY: timedelta(days=1),
            Recurrence.WEEKLY: timedelta(weeks=1),
        }[self]


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
        recurrence: Recurrence = Recurrence.NONE,
        due_date: date | None = None,
        task_id: str | None = None,
    ) -> None:
        """Create a care task; generates a unique id if none is given."""
        self.task_id = task_id or str(uuid.uuid4())
        self.name = name
        self.category = category
        self.duration = duration
        self.priority = priority
        self.preferred_time = preferred_time
        # Backward compat: a bare recurring=True means a daily task.
        if recurrence is Recurrence.NONE and recurring:
            recurrence = Recurrence.DAILY
        self.recurrence = recurrence
        self.due_date = due_date
        self.completed = False
        # Set by Pet.add_task so a completed recurring task can re-enroll itself.
        self.pet: "Pet | None" = None

    @property
    def recurring(self) -> bool:
        """True if this task repeats on a daily or weekly cycle."""
        return self.recurrence is not Recurrence.NONE

    def next_occurrence(self) -> "Task":
        """Build the next instance of a recurring task (fresh, incomplete).

        The due date advances by one recurrence interval; everything else
        (name, duration, priority, preferred time) carries over. A new id is
        generated so the occurrences stay distinct.
        """
        delta = self.recurrence.delta
        if delta is None:
            raise ValueError("next_occurrence() called on a non-recurring task")
        base_date = self.due_date or date.today()
        return Task(
            name=self.name,
            category=self.category,
            duration=self.duration,
            priority=self.priority,
            preferred_time=self.preferred_time,
            recurrence=self.recurrence,
            due_date=base_date + delta,
        )

    def mark_complete(self) -> "Task | None":
        """Mark this task complete; if recurring, spawn the next occurrence.

        When the task belongs to a pet, the new occurrence is automatically
        added to that pet's task list. The new Task is returned (or None for a
        one-off task) so callers can use it directly when there's no pet.
        """
        self.completed = True
        if not self.recurring:
            return None
        upcoming = self.next_occurrence()
        if self.pet is not None:
            self.pet.add_task(upcoming)
        return upcoming

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
        task.pet = self
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

    def filter_tasks(
        self,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional; passing neither returns every task.
        - completed: keep only tasks whose ``completed`` flag matches.
        - pet_name: keep only tasks belonging to the named pet (case-insensitive).
        """
        result: list[Task] = []
        for pet in self.pets:
            if pet_name is not None and pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if completed is not None and task.completed != completed:
                    continue
                result.append(task)
        return result


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
        self.warnings: list[str] = []
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
        if self.warnings:
            parts.append(f"{len(self.warnings)} time conflict(s) detected.")
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

        plan.warnings = self.detect_conflicts(tasks)
        return plan

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return warning messages for tasks whose preferred times overlap.

        Lightweight, non-fatal check: it only compares tasks that have a
        ``preferred_time`` and never raises — callers get back a (possibly
        empty) list of human-readable strings to display instead of a crash.
        Tasks overlap when their [start, start + duration) windows intersect,
        whether they belong to the same pet or to different pets.
        """
        timed = sorted(
            (t for t in tasks if t.preferred_time is not None),
            key=lambda t: t.preferred_time,
        )
        warnings: list[str] = []
        for i, first in enumerate(timed):
            for second in timed[i + 1:]:
                # Sorted by start time, so once second starts at/after first
                # ends, no later task can overlap first either.
                if second.preferred_time >= self._end_time(first):
                    break
                warnings.append(self._conflict_message(first, second))
        return warnings

    @staticmethod
    def _end_time(task: Task) -> time:
        """Clock time at which a task finishes, based on its preferred start."""
        start = datetime.combine(date.today(), task.preferred_time)
        return (start + timedelta(minutes=task.duration)).time()

    @staticmethod
    def _conflict_message(first: Task, second: Task) -> str:
        """Build a readable warning describing two overlapping tasks."""
        def label(task: Task) -> str:
            """Format a task as 'name (pet)', or '(Unassigned)' if it has no pet."""
            owner = task.pet.name if task.pet is not None else "Unassigned"
            return f"{task.name} ({owner})"

        same_pet = (
            first.pet is not None
            and second.pet is not None
            and first.pet is second.pet
        )
        scope = "same pet" if same_pet else "different pets"
        return (
            f"⚠️  Conflict ({scope}): {label(first)} at "
            f"{first.preferred_time.strftime('%H:%M')} overlaps "
            f"{label(second)} at {second.preferred_time.strftime('%H:%M')}."
        )

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Highest priority first; shorter tasks first as a tiebreaker."""
        return sorted(tasks, key=lambda t: (t.priority.rank, t.duration))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by preferred_time (earliest first).

        Tasks without a preferred_time are placed last, preserving their
        original relative order.
        """
        return sorted(
            tasks,
            key=lambda t: (t.preferred_time is None, t.preferred_time or time.min),
        )

    def fits(self, task: Task, remaining_minutes: int) -> bool:
        """Return True if the task fits within the remaining time budget."""
        return task.duration <= remaining_minutes
