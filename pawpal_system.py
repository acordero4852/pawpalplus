"""PawPal+ class skeleton.

Generated from diagrams/uml.mmd. These are stubs only — names, attributes,
and empty method bodies. Implement scheduling logic in small increments.
"""

from __future__ import annotations

from datetime import time
from enum import Enum


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Task:
    def __init__(
        self,
        name: str,
        category: str,
        duration: int,
        priority: Priority,
        preferred_time: time | None = None,
        recurring: bool = False,
    ) -> None:
        self.name = name
        self.category = category
        self.duration = duration
        self.priority = priority
        self.preferred_time = preferred_time
        self.recurring = recurring

    def is_higher_priority_than(self, other: "Task") -> bool:
        ...

    def __repr__(self) -> str:
        ...


class Pet:
    def __init__(self, name: str, species: str, breed: str) -> None:
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        ...

    def edit_task(self, task: Task, **changes) -> None:
        ...

    def remove_task(self, task: Task) -> None:
        ...

    def get_tasks(self, filter_by=None) -> list[Task]:
        ...


class Owner:
    def __init__(
        self,
        name: str,
        available_minutes: int,
        preferences: dict | None = None,
    ) -> None:
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        ...

    def remove_pet(self, pet: Pet) -> None:
        ...


class PlanEntry:
    def __init__(self, start_time: time, task: Task) -> None:
        self.start_time = start_time
        self.task = task


class DailyPlan:
    def __init__(self) -> None:
        self.entries: list[PlanEntry] = []
        self.skipped: list[Task] = []
        self.total_minutes: int = 0

    def add_entry(self, start_time: time, task: Task) -> None:
        ...

    def to_display(self) -> str:
        ...

    def summary(self) -> str:
        ...


class Scheduler:
    def build_plan(self, tasks: list[Task], available_minutes: int) -> DailyPlan:
        ...

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        ...

    def fits(self, task: Task, remaining_minutes: int) -> bool:
        ...
