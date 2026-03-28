from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    task_id: str
    title: str
    category: str
    duration_min: int
    priority: int
    mandatory: bool = False
    completed: bool = False

    def mark_complete(self):
        pass

    def update_task(self):
        pass


@dataclass
class Pet:
    pet_id: str
    name: str
    species: str
    age: int
    notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def update_info(self):
        pass


@dataclass
class Owner:
    owner_id: str
    name: str
    available_minutes: int
    prefer_short_tasks_first: bool = False
    low_energy_mode: bool = False
    pets: List[Pet] = field(default_factory=list)

    def update_preferences(self):
        pass


class Planner:
    def filter_tasks(self, tasks: List[Task]) -> List[Task]:
        pass

    def score_task(self, task: Task, owner: Owner) -> float:
        pass

    def select_tasks(self, tasks: List[Task], owner: Owner) -> List[Task]:
        pass

    def generate_schedule(self, owner: Owner, tasks: List[Task]) -> dict:
        pass
