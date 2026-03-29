from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple


@dataclass
class Task:
    task_id: str
    title: str
    category: str
    duration_min: int
    priority: int  # 1 = highest
    mandatory: bool = False
    completed: bool = False
    recurrence: str = "none"          # none, daily, weekly
    preferred_time: Optional[str] = None   # "HH:MM"
    last_completed_on: Optional[str] = None  # ISO date string

    def mark_complete(self, completed_on: Optional[str] = None) -> None:
        """Mark this task as completed and record the completion date.

        Args:
            completed_on: ISO date string (``YYYY-MM-DD``) for when the task
                was completed.  Defaults to today's date when omitted.
        """
        day = completed_on or date.today().isoformat()
        self.completed = True
        self.last_completed_on = day

    def reset_status(self) -> None:
        """Reset the completed flag to False without altering any other fields."""
        self.completed = False

    def update_task(
        self,
        title: Optional[str] = None,
        category: Optional[str] = None,
        duration_min: Optional[int] = None,
        priority: Optional[int] = None,
        mandatory: Optional[bool] = None,
        completed: Optional[bool] = None,
        recurrence: Optional[str] = None,
        preferred_time: Optional[str] = None,
    ) -> None:
        """Update one or more fields of this task in place.

        Only fields supplied with a non-``None`` value are changed; all other
        fields retain their current values.

        Args:
            title: New display title for the task.
            category: New category label (e.g. ``"health"``, ``"grooming"``).
            duration_min: New estimated duration in minutes.
            priority: New priority level (1 = highest).
            mandatory: Whether the task must appear in every schedule.
            completed: Override for the completion flag.
            recurrence: New recurrence rule (``"none"``, ``"daily"``, or
                ``"weekly"``).
            preferred_time: New preferred start time in ``"HH:MM"`` format.
        """
        if title is not None:
            self.title = title
        if category is not None:
            self.category = category
        if duration_min is not None:
            self.duration_min = duration_min
        if priority is not None:
            self.priority = priority
        if mandatory is not None:
            self.mandatory = mandatory
        if completed is not None:
            self.completed = completed
        if recurrence is not None:
            self.recurrence = recurrence
        if preferred_time is not None:
            self.preferred_time = preferred_time

    def _to_date(self, value: Optional[str] = None) -> date:
        """Convert an optional ISO date string to a :class:`datetime.date`.

        Args:
            value: ISO date string (``YYYY-MM-DD``), an existing
                :class:`datetime.date`, or ``None``.

        Returns:
            The parsed date, or today's date when *value* is ``None``.
        """
        if value is None:
            return date.today()
        if isinstance(value, date):
            return value
        return datetime.strptime(value, "%Y-%m-%d").date()

    def is_due_today(self, today: Optional[str] = None) -> bool:
        """Determine whether this task is due on the given date.

        The logic depends on the task's recurrence setting:

        - ``"daily"``: due if it has not already been completed today.
        - ``"weekly"``: due if it has never been completed, or if at least
          seven days have elapsed since the last completion.
        - ``"none"``: due if the ``completed`` flag is ``False``.

        Args:
            today: ISO date string (``YYYY-MM-DD``) representing the reference
                date.  Defaults to today's actual date when omitted.

        Returns:
            ``True`` if the task is due, ``False`` otherwise.
        """
        today_date = self._to_date(today)

        if self.recurrence == "daily":
            return self.last_completed_on != today_date.isoformat()

        if self.recurrence == "weekly":
            if self.last_completed_on is None:
                return True
            last_date = self._to_date(self.last_completed_on)
            return (today_date - last_date).days >= 7

        return not self.completed

    def next_occurrence(self, completed_on: Optional[str] = None) -> Optional["Task"]:
        """Return a reset copy of this task scheduled for its next due date.
        Returns None if the task is not recurring."""
        if self.recurrence == "none":
            return None

        day = completed_on or date.today().isoformat()
        completed_date = datetime.strptime(day, "%Y-%m-%d").date()

        if self.recurrence == "daily":
            next_date = completed_date + timedelta(days=1)
        else:  # weekly
            next_date = completed_date + timedelta(weeks=1)

        return Task(
            task_id=f"{self.task_id}_next_{next_date.isoformat()}",
            title=self.title,
            category=self.category,
            duration_min=self.duration_min,
            priority=self.priority,
            mandatory=self.mandatory,
            completed=False,
            recurrence=self.recurrence,
            preferred_time=self.preferred_time,
            last_completed_on=None,
        )

    def is_completed_for_filter(self, today: Optional[str] = None) -> bool:
        """Return whether this task counts as completed for filtering purposes.

        Mirrors the inverse logic of :meth:`is_due_today`:

        - ``"daily"``: completed if the last completion date equals *today*.
        - ``"weekly"``: completed if the last completion date falls within the
          past seven days.
        - ``"none"``: completed if the ``completed`` flag is ``True``.

        Args:
            today: ISO date string (``YYYY-MM-DD``) representing the reference
                date.  Defaults to today's actual date when omitted.

        Returns:
            ``True`` if the task should appear in a completed-tasks filter,
            ``False`` otherwise.
        """
        today_date = self._to_date(today)

        if self.recurrence == "daily":
            return self.last_completed_on == today_date.isoformat()

        if self.recurrence == "weekly":
            if self.last_completed_on is None:
                return False
            last_date = self._to_date(self.last_completed_on)
            return (today_date - last_date).days < 7

        return self.completed


@dataclass
class Pet:
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
        """Update one or more profile fields for this pet in place.

        Only fields supplied with a non-``None`` value are changed.

        Args:
            name: New display name for the pet.
            species: New species label (e.g. ``"dog"``, ``"cat"``).
            age: New age in years.
            notes: Free-text notes about the pet.
        """
        if name is not None:
            self.name = name
        if species is not None:
            self.species = species
        if age is not None:
            self.age = age
        if notes is not None:
            self.notes = notes

    def total_duration(self) -> int:
        """Return the sum of ``duration_min`` across all tasks for this pet.

        Returns:
            Total duration in minutes.
        """
        return sum(t.duration_min for t in self.tasks)

    def pending_tasks(self, today: Optional[str] = None) -> List[Task]:
        """Return all tasks that are due on the given date.

        Args:
            today: ISO date string (``YYYY-MM-DD``) used as the reference
                date.  Defaults to today's actual date when omitted.

        Returns:
            A list of :class:`Task` objects for which
            :meth:`Task.is_due_today` returns ``True``.
        """
        return [t for t in self.tasks if t.is_due_today(today)]


@dataclass
class Owner:
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
        """Update scheduling preferences for this owner in place.

        Only fields supplied with a non-``None`` value are changed.

        Args:
            available_minutes: Total minutes the owner has available for pet
                care on a given day.
            prefer_short_tasks_first: When ``True``, the scheduler boosts the
                score of tasks with a short duration.
            low_energy_mode: When ``True``, the scheduler penalises long
                non-mandatory tasks to reduce overall effort.
        """
        if available_minutes is not None:
            self.available_minutes = available_minutes
        if prefer_short_tasks_first is not None:
            self.prefer_short_tasks_first = prefer_short_tasks_first
        if low_energy_mode is not None:
            self.low_energy_mode = low_energy_mode


class Scheduler:
    def complete_task(
        self,
        pet: "Pet",
        task: Task,
        completed_on: Optional[str] = None,
    ) -> Optional[Task]:
        """Mark a task complete. If it recurs daily/weekly, append the next
        occurrence to the pet's task list and return it. Returns None otherwise."""
        task.mark_complete(completed_on)
        next_task = task.next_occurrence(completed_on)
        if next_task is not None:
            pet.tasks.append(next_task)
        return next_task

    def detect_conflicts(self, task_items: List[Tuple[str, Task]]) -> List[dict]:
        """Check tasks for overlapping preferred time windows.
        Tasks without a preferred_time are skipped.
        Returns a list of conflict dicts describing each overlapping pair."""
        conflicts = []

        # Only consider tasks that have a preferred_time set
        timed = [(pet_name, task) for pet_name, task in task_items if task.preferred_time]

        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                pet_a, task_a = timed[i]
                pet_b, task_b = timed[j]

                a_start = self._parse_time(task_a.preferred_time)
                a_end   = a_start + task_a.duration_min
                b_start = self._parse_time(task_b.preferred_time)
                b_end   = b_start + task_b.duration_min

                # Overlap when one interval starts before the other ends
                if a_start < b_end and b_start < a_end:
                    overlap_start = max(a_start, b_start)
                    overlap_end   = min(a_end, b_end)
                    conflicts.append({
                        "task_a": f"{pet_a} — {task_a.title} ({task_a.preferred_time}, {task_a.duration_min} min)",
                        "task_b": f"{pet_b} — {task_b.title} ({task_b.preferred_time}, {task_b.duration_min} min)",
                        "overlap": (
                            f"{overlap_start // 60:02d}:{overlap_start % 60:02d}"
                            f" – {overlap_end // 60:02d}:{overlap_end % 60:02d}"
                        ),
                    })

        return conflicts

    def _parse_time(self, value: Optional[str], fallback: int = 10**9) -> int:
        """Convert an ``"HH:MM"`` string to total minutes since midnight.

        Args:
            value: Time string in ``"HH:MM"`` format, or ``None``.
            fallback: Value returned when *value* is falsy.  Defaults to a
                large sentinel so un-timed tasks sort to the end.

        Returns:
            Integer representing minutes since midnight, or *fallback* if
            *value* is ``None`` or empty.
        """
        if not value:
            return fallback
        hour, minute = map(int, value.split(":"))
        return hour * 60 + minute

    def _format_time(self, total_minutes: int) -> str:
        """Convert total minutes since midnight to an ``"HH:MM"`` string.

        Args:
            total_minutes: Number of minutes since midnight.

        Returns:
            Zero-padded time string in ``"HH:MM"`` format.
        """
        hour = total_minutes // 60
        minute = total_minutes % 60
        return f"{hour:02d}:{minute:02d}"

    def filter_tasks(
        self,
        owner: Owner,
        pet_name: str = "All",
        status: str = "pending",
        today: Optional[str] = None,
    ) -> List[Tuple[str, Task]]:
        """Return tasks for an owner filtered by pet name and completion status.

        Args:
            owner: The :class:`Owner` whose pets' tasks are searched.
            pet_name: Name of a specific pet to include, or ``"All"`` to
                include every pet.
            status: ``"pending"`` returns tasks that are due today;
                ``"completed"`` returns tasks already completed today;
                ``"all"`` returns every task regardless of status.
            today: ISO date string (``YYYY-MM-DD``) used as the reference
                date.  Defaults to today's actual date when omitted.

        Returns:
            A list of ``(pet_name, Task)`` tuples matching the filters.
        """
        filtered: List[Tuple[str, Task]] = []

        for pet in owner.pets:
            if pet_name != "All" and pet.name != pet_name:
                continue

            for task in pet.tasks:
                if status == "pending" and task.is_due_today(today):
                    filtered.append((pet.name, task))
                elif status == "completed" and task.is_completed_for_filter(today):
                    filtered.append((pet.name, task))
                elif status == "all":
                    filtered.append((pet.name, task))

        return filtered

    def filter_by(
        self,
        owner: Owner,
        pet_name: str = "All",
        status: str = "all",
        category: Optional[str] = None,
        max_priority: Optional[int] = None,
        today: Optional[str] = None,
    ) -> List[Tuple[str, Task]]:
        """Return tasks filtered by pet, status, category, and priority.

        Extends :meth:`filter_tasks` with additional category and priority
        filters.

        Args:
            owner: The :class:`Owner` whose pets' tasks are searched.
            pet_name: Name of a specific pet to include, or ``"All"`` to
                include every pet.
            status: ``"pending"`` returns tasks due today; ``"completed"``
                returns tasks already completed today; ``"all"`` skips status
                filtering.
            category: If provided, only tasks whose ``category`` matches
                (case-insensitive) are returned.
            max_priority: If provided, only tasks with ``priority <=
                max_priority`` are returned (lower numbers = higher priority).
            today: ISO date string (``YYYY-MM-DD``) used as the reference
                date.  Defaults to today's actual date when omitted.

        Returns:
            A list of ``(pet_name, Task)`` tuples matching all active filters.
        """
        filtered = []

        for pet in owner.pets:
            # Filter by pet name
            if pet_name != "All" and pet.name != pet_name:
                continue

            for task in pet.tasks:
                # Filter by completion status
                if status == "pending" and not task.is_due_today(today):
                    continue
                if status == "completed" and not task.is_completed_for_filter(today):
                    continue

                # Filter by category (e.g. "health", "grooming")
                if category is not None and task.category.lower() != category.lower():
                    continue

                # Filter by priority (e.g. max_priority=2 returns priority 1 and 2 only)
                if max_priority is not None and task.priority > max_priority:
                    continue

                filtered.append((pet.name, task))

        return filtered

    def sort_by_time(self, task_items: List[Tuple[str, Task]]) -> List[Tuple[str, Task]]:
        """Sort task items by their preferred start time.

        Tasks without a ``preferred_time`` are placed at the end of the list.

        Args:
            task_items: A list of ``(pet_name, Task)`` tuples to sort.

        Returns:
            A new list sorted in ascending order by ``preferred_time``.
        """
        return sorted(
            task_items,
            key=lambda item: (
                int(item[1].preferred_time.split(":")[0]) * 60 + int(item[1].preferred_time.split(":")[1])
                if item[1].preferred_time
                else 10**9
            ),
        )

    def score_task(self, task: Task, owner: Owner) -> float:
        """Compute a scheduling priority score for a task.

        Higher scores cause a task to be selected earlier by
        :meth:`select_tasks`.  The score is derived from:

        - Base priority (priority 1 earns the most points).
        - A flat bonus for mandatory tasks.
        - A bonus for short tasks when the owner prefers short tasks first.
        - A penalty for long non-mandatory tasks in low-energy mode.
        - A small bonus when a preferred time is set.

        Args:
            task: The :class:`Task` to evaluate.
            owner: The :class:`Owner` whose preferences affect scoring.

        Returns:
            A float representing the task's scheduling score.
        """
        score = (6 - task.priority) * 10  # priority 1 gets highest score

        if task.mandatory:
            score += 35

        if owner.prefer_short_tasks_first:
            score += max(0, 20 - task.duration_min) / 2

        if owner.low_energy_mode and task.duration_min > 20 and not task.mandatory:
            score -= 8

        if task.preferred_time:
            score += 2

        return score

    def select_tasks(self, task_items: List[Tuple[str, Task]], owner: Owner) -> List[Tuple[str, Task]]:
        """Select the highest-scoring tasks that fit within the owner's time budget.

        Tasks are ranked by descending score (see :meth:`score_task`), then by
        preferred start time, then by duration.  Tasks are greedily added until
        the owner's ``available_minutes`` would be exceeded.

        Args:
            task_items: A list of ``(pet_name, Task)`` tuples to choose from.
            owner: The :class:`Owner` whose ``available_minutes`` and
                preferences drive selection.

        Returns:
            A subset of *task_items* that fits within the available time,
            ordered by their ranking.
        """
        ranked = sorted(
            task_items,
            key=lambda item: (
                -self.score_task(item[1], owner),
                self._parse_time(item[1].preferred_time),
                item[1].duration_min,
            ),
        )

        selected: List[Tuple[str, Task]] = []
        time_used = 0

        for pet_name, task in ranked:
            if time_used + task.duration_min <= owner.available_minutes:
                selected.append((pet_name, task))
                time_used += task.duration_min

        return selected

    def generate_schedule(
        self,
        owner: Owner,
        pet_name: str = "All",
        status: str = "pending",
        day_start: str = "08:00",
        today: Optional[str] = None,
    ) -> dict:
        """Build a time-blocked daily schedule for the owner's pet-care tasks.

        Tasks are filtered, scored, and selected to fit within
        ``owner.available_minutes``.  Each task is then placed sequentially
        starting from *day_start*, respecting each task's ``preferred_time``
        where possible.  Tasks that no longer fit after earlier tasks are
        placed are recorded as skipped.

        Args:
            owner: The :class:`Owner` for whom the schedule is generated.
            pet_name: Name of a specific pet to include, or ``"All"`` to
                include tasks from every pet.
            status: Task status filter passed to :meth:`filter_tasks`
                (``"pending"``, ``"completed"``, or ``"all"``).
            day_start: Earliest possible start time for the schedule in
                ``"HH:MM"`` format.  Defaults to ``"08:00"``.
            today: ISO date string (``YYYY-MM-DD``) used as the reference
                date.  Defaults to today's actual date when omitted.

        Returns:
            A dict with the following keys:

            - ``"schedule"`` (list[dict]): Ordered list of scheduled task
              rows, each containing timing, scoring, and conflict information.
            - ``"time_used"`` (int): Total minutes consumed by scheduled tasks.
            - ``"time_remaining"`` (int): Minutes left from
              ``owner.available_minutes`` after scheduling.
            - ``"skipped"`` (list[dict]): Tasks that could not be fitted,
              each with ``"pet"``, ``"task"``, and ``"reason"`` keys.
        """
        task_items = self.filter_tasks(owner, pet_name=pet_name, status=status, today=today)
        selected = self.select_tasks(task_items, owner)

        # sort scheduled tasks by preferred time first, then priority
        selected = sorted(
            selected,
            key=lambda item: (
                self._parse_time(item[1].preferred_time),
                item[1].priority,
                item[1].duration_min,
            ),
        )

        current_time = self._parse_time(day_start, fallback=8 * 60)
        day_end = current_time + owner.available_minutes

        schedule_rows = []
        skipped = []

        for pet_name_value, task in selected:
            desired_start = self._parse_time(task.preferred_time, fallback=current_time)
            actual_start = max(current_time, desired_start)
            actual_end = actual_start + task.duration_min

            conflict_note = ""
            if task.preferred_time and desired_start < current_time:
                conflict_note = (
                    f"Preferred time conflict: wanted {task.preferred_time}, "
                    f"moved to {self._format_time(actual_start)}."
                )

            if actual_end > day_end:
                skipped.append(
                    {
                        "pet": pet_name_value,
                        "task": task.title,
                        "reason": "Skipped because it no longer fits in the remaining time.",
                    }
                )
                continue

            reason_parts = []
            if task.mandatory:
                reason_parts.append("mandatory")
            reason_parts.append(f"priority {task.priority}")
            if owner.prefer_short_tasks_first and task.duration_min <= 20:
                reason_parts.append("short-task preference")
            if task.recurrence != "none":
                reason_parts.append(f"{task.recurrence} recurring")

            schedule_rows.append(
                {
                    "pet": pet_name_value,
                    "task": task.title,
                    "category": task.category,
                    "start_time": self._format_time(actual_start),
                    "end_time": self._format_time(actual_end),
                    "duration_min": task.duration_min,
                    "priority": task.priority,
                    "mandatory": task.mandatory,
                    "preferred_time": task.preferred_time or "-",
                    "recurrence": task.recurrence,
                    "score": round(self.score_task(task, owner), 2),
                    "reason": ", ".join(reason_parts),
                    "conflict": conflict_note if conflict_note else "No conflict",
                }
            )

            current_time = actual_end

        time_used = sum(row["duration_min"] for row in schedule_rows)

        return {
            "schedule": schedule_rows,
            "time_used": time_used,
            "time_remaining": owner.available_minutes - time_used,
            "skipped": skipped,
        }