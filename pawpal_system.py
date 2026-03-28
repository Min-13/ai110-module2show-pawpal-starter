"""
pawpal_system.py
================
Core data model and scheduling logic for PawPal+.

Classes
-------
Task      — a single pet-care activity
Pet       — a pet that owns a list of Tasks
Owner     — a pet owner with preferences and a list of Pets
Scheduler — collects and ranks tasks based on owner preferences
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    """A single pet-care activity assigned to a pet.

    Attributes
    ----------
    task_id : str
        Unique identifier for the task.
    title : str
        Human-readable name (e.g. "Morning Walk").
    category : str
        Type of care (e.g. "exercise", "feeding", "hygiene").
    duration_min : int
        Estimated time to complete the task, in minutes.
    priority : int
        Scheduling priority — lower number = higher priority.
    mandatory : bool
        If True the task should always appear in the schedule.
    completed : bool
        True once the task has been finished for the day.
    """

    task_id: str
    title: str
    category: str
    duration_min: int
    priority: int
    mandatory: bool = False
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def update_task(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration_min: Optional[int] = None,
        priority: Optional[int] = None,
        mandatory: Optional[bool] = None,
        completed: Optional[bool] = None,
    ) -> None:
        """Update one or more fields on this task; only non-None values are applied."""
        pass


@dataclass
class Pet:
    """A pet owned by an Owner, holding its own list of Tasks.

    Attributes
    ----------
    pet_id : str
        Unique identifier for the pet.
    name : str
        Pet's name.
    species : str
        Animal type (e.g. "dog", "cat").
    age : int
        Pet's age in years.
    notes : str
        Free-text notes (health info, behavioural reminders, etc.).
    tasks : List[Task]
        Care tasks associated with this pet.
    """

    pet_id: str
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def update_info(
        self,
        name: Optional[str] = None,
        species: Optional[str] = None,
        age: Optional[int] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Update one or more profile fields for this pet; only non-None values are applied."""
        pass


@dataclass
class Owner:
    """A pet owner with scheduling preferences and a list of pets.

    Attributes
    ----------
    owner_id : str
        Unique identifier for the owner.
    name : str
        Owner's display name.
    available_minutes : int
        Total free time the owner has today, in minutes.
    prefer_short_tasks_first : bool
        If True, the Scheduler will surface shorter tasks earlier.
    low_energy_mode : bool
        If True, the Scheduler deprioritises high-effort tasks.
    pets : List[Pet]
        Pets belonging to this owner.
    """

    owner_id: str
    name: str
    available_minutes: int
    prefer_short_tasks_first: bool = False
    low_energy_mode: bool = False
    pets: List[Pet] = field(default_factory=list)

    def update_preferences(
        self,
        available_minutes: Optional[int] = None,
        prefer_short_tasks_first: Optional[bool] = None,
        low_energy_mode: Optional[bool] = None,
    ) -> None:
        """Update one or more scheduling preferences; only non-None values are applied."""
        pass


class Scheduler:
    """Collects, scores, and selects tasks for an owner's daily schedule."""

    def filter_tasks(self, owner: "Owner") -> List[Task]:
        """Return a flat list of every task across all of the owner's pets."""
        return [task for pet in owner.pets for task in pet.tasks]

    def score_task(self, task: Task, owner: Owner) -> float:
        """Compute a priority score for a task given the owner's preferences."""
        pass

    def select_tasks(self, tasks: List[Task], owner: Owner) -> List[Task]:
        """Select tasks that fit within the owner's available time, ordered by score."""
        pass

    def generate_schedule(self, owner: Owner, tasks: List[Task]) -> dict:
        """Build and return a schedule dictionary mapping order to Task objects."""
        pass
