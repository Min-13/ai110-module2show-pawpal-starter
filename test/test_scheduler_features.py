"""
Tests for PawPal+ scheduler features.
Covers happy paths and edge cases for:
  - Recurring tasks (daily / weekly)
  - sort_by_time()
  - detect_conflicts()
  - filter_by()
  - complete_task() auto-scheduling
  - generate_schedule()
"""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scheduler():
    return Scheduler()


def make_task(task_id="t1", title="Walk", category="exercise",
              duration_min=30, priority=1, mandatory=False,
              recurrence="none", preferred_time=None, completed=False,
              last_completed_on=None):
    return Task(
        task_id=task_id,
        title=title,
        category=category,
        duration_min=duration_min,
        priority=priority,
        mandatory=mandatory,
        recurrence=recurrence,
        preferred_time=preferred_time,
        completed=completed,
        last_completed_on=last_completed_on,
    )


def make_owner(available_minutes=120, pets=None):
    return Owner(
        owner_id="o1",
        name="Alex",
        available_minutes=available_minutes,
        pets=pets or [],
    )


# ===========================================================================
# 1. Recurring tasks — is_due_today
# ===========================================================================

class TestIsDueToday:
    # --- Happy paths ---

    def test_non_recurring_not_completed_is_due(self):
        task = make_task(recurrence="none")
        assert task.is_due_today("2026-03-29") is True

    def test_non_recurring_completed_is_not_due(self):
        task = make_task(recurrence="none", completed=True)
        assert task.is_due_today("2026-03-29") is False

    def test_daily_not_completed_today_is_due(self):
        task = make_task(recurrence="daily", last_completed_on="2026-03-28")
        assert task.is_due_today("2026-03-29") is True

    def test_daily_completed_today_is_not_due(self):
        task = make_task(recurrence="daily", last_completed_on="2026-03-29")
        assert task.is_due_today("2026-03-29") is False

    def test_weekly_never_completed_is_due(self):
        task = make_task(recurrence="weekly", last_completed_on=None)
        assert task.is_due_today("2026-03-29") is True

    def test_weekly_completed_7_days_ago_is_due(self):
        task = make_task(recurrence="weekly", last_completed_on="2026-03-22")
        assert task.is_due_today("2026-03-29") is True

    def test_weekly_completed_8_days_ago_is_due(self):
        task = make_task(recurrence="weekly", last_completed_on="2026-03-21")
        assert task.is_due_today("2026-03-29") is True

    # --- Edge cases ---

    def test_weekly_completed_6_days_ago_is_not_due(self):
        """Boundary: 6 days is not enough — must be >= 7."""
        task = make_task(recurrence="weekly", last_completed_on="2026-03-23")
        assert task.is_due_today("2026-03-29") is False

    def test_daily_never_completed_is_due(self):
        """last_completed_on=None means it has never been done."""
        task = make_task(recurrence="daily", last_completed_on=None)
        assert task.is_due_today("2026-03-29") is True


# ===========================================================================
# 2. next_occurrence — recurring task auto-scheduling
# ===========================================================================

class TestNextOccurrence:
    # --- Happy paths ---

    def test_daily_next_is_tomorrow(self):
        task = make_task(task_id="t1", recurrence="daily")
        nxt = task.next_occurrence("2026-03-29")
        assert nxt is not None
        assert "2026-03-30" in nxt.task_id

    def test_weekly_next_is_7_days_later(self):
        task = make_task(task_id="t1", recurrence="weekly")
        nxt = task.next_occurrence("2026-03-29")
        assert nxt is not None
        assert "2026-04-05" in nxt.task_id

    def test_next_occurrence_resets_completed(self):
        task = make_task(recurrence="daily", completed=True)
        nxt = task.next_occurrence("2026-03-29")
        assert nxt.completed is False
        assert nxt.last_completed_on is None

    def test_next_occurrence_copies_attributes(self):
        task = make_task(task_id="t1", title="Feed", category="feeding",
                         duration_min=10, priority=2, mandatory=True,
                         recurrence="daily", preferred_time="08:00")
        nxt = task.next_occurrence("2026-03-29")
        assert nxt.title == "Feed"
        assert nxt.duration_min == 10
        assert nxt.preferred_time == "08:00"
        assert nxt.mandatory is True

    # --- Edge cases ---

    def test_non_recurring_returns_none(self):
        task = make_task(recurrence="none")
        assert task.next_occurrence("2026-03-29") is None

    def test_daily_crosses_month_boundary(self):
        """March 31 + 1 day → April 1."""
        task = make_task(task_id="t1", recurrence="daily")
        nxt = task.next_occurrence("2026-03-31")
        assert "2026-04-01" in nxt.task_id

    def test_daily_crosses_year_boundary(self):
        """Dec 31 + 1 day → Jan 1 next year."""
        task = make_task(task_id="t1", recurrence="daily")
        nxt = task.next_occurrence("2026-12-31")
        assert "2027-01-01" in nxt.task_id


# ===========================================================================
# 3. complete_task — marks done and appends next occurrence
# ===========================================================================

class TestCompleteTask:
    # --- Happy paths ---

    def test_complete_task_marks_done(self, scheduler):
        task = make_task(recurrence="none")
        pet = Pet("p1", "Buddy", "dog", 3, tasks=[task])
        scheduler.complete_task(pet, task, "2026-03-29")
        assert task.completed is True

    def test_complete_daily_appends_next(self, scheduler):
        task = make_task(task_id="t1", recurrence="daily")
        pet = Pet("p1", "Buddy", "dog", 3, tasks=[task])
        scheduler.complete_task(pet, task, "2026-03-29")
        assert len(pet.tasks) == 2
        assert pet.tasks[1].completed is False

    def test_complete_weekly_appends_next(self, scheduler):
        task = make_task(task_id="t1", recurrence="weekly")
        pet = Pet("p1", "Buddy", "dog", 3, tasks=[task])
        scheduler.complete_task(pet, task, "2026-03-29")
        assert len(pet.tasks) == 2

    def test_complete_non_recurring_does_not_append(self, scheduler):
        task = make_task(recurrence="none")
        pet = Pet("p1", "Buddy", "dog", 3, tasks=[task])
        scheduler.complete_task(pet, task, "2026-03-29")
        assert len(pet.tasks) == 1

    # --- Edge cases ---

    def test_complete_returns_none_for_non_recurring(self, scheduler):
        task = make_task(recurrence="none")
        pet = Pet("p1", "Buddy", "dog", 3, tasks=[task])
        result = scheduler.complete_task(pet, task, "2026-03-29")
        assert result is None

    def test_next_task_id_is_unique(self, scheduler):
        task = make_task(task_id="t1", recurrence="daily")
        pet = Pet("p1", "Buddy", "dog", 3, tasks=[task])
        scheduler.complete_task(pet, task, "2026-03-29")
        assert pet.tasks[0].task_id != pet.tasks[1].task_id


# ===========================================================================
# 4. sort_by_time
# ===========================================================================

class TestSortByTime:
    # --- Happy paths ---

    def test_sorts_ascending_by_preferred_time(self, scheduler):
        t1 = make_task("t1", preferred_time="10:00")
        t2 = make_task("t2", preferred_time="08:00")
        t3 = make_task("t3", preferred_time="14:30")
        result = scheduler.sort_by_time([("Buddy", t1), ("Buddy", t2), ("Buddy", t3)])
        times = [item[1].preferred_time for item in result]
        assert times == ["08:00", "10:00", "14:30"]

    def test_tasks_without_time_sort_last(self, scheduler):
        t1 = make_task("t1", preferred_time=None)
        t2 = make_task("t2", preferred_time="08:00")
        result = scheduler.sort_by_time([("Buddy", t1), ("Buddy", t2)])
        assert result[0][1].preferred_time == "08:00"
        assert result[1][1].preferred_time is None

    # --- Edge cases ---

    def test_empty_list_returns_empty(self, scheduler):
        assert scheduler.sort_by_time([]) == []

    def test_all_tasks_without_preferred_time(self, scheduler):
        """Should not crash and return all tasks."""
        t1 = make_task("t1", preferred_time=None)
        t2 = make_task("t2", preferred_time=None)
        result = scheduler.sort_by_time([("Buddy", t1), ("Buddy", t2)])
        assert len(result) == 2

    def test_single_task_returns_unchanged(self, scheduler):
        t1 = make_task("t1", preferred_time="09:00")
        result = scheduler.sort_by_time([("Buddy", t1)])
        assert result[0][1].task_id == "t1"


# ===========================================================================
# 5. detect_conflicts
# ===========================================================================

class TestDetectConflicts:
    # --- Happy paths ---

    def test_overlapping_same_time_detected(self, scheduler):
        t1 = make_task("t1", duration_min=30, preferred_time="08:00")
        t2 = make_task("t2", duration_min=30, preferred_time="08:00")
        conflicts = scheduler.detect_conflicts([("Buddy", t1), ("Mochi", t2)])
        assert len(conflicts) == 1

    def test_partial_overlap_detected(self, scheduler):
        t1 = make_task("t1", duration_min=30, preferred_time="08:00")  # 08:00–08:30
        t2 = make_task("t2", duration_min=30, preferred_time="08:15")  # 08:15–08:45
        conflicts = scheduler.detect_conflicts([("Buddy", t1), ("Buddy", t2)])
        assert len(conflicts) == 1
        assert conflicts[0]["overlap"] == "08:15 – 08:30"

    def test_no_conflict_for_sequential_tasks(self, scheduler):
        """Back-to-back tasks must NOT count as a conflict."""
        t1 = make_task("t1", duration_min=30, preferred_time="08:00")  # ends 08:30
        t2 = make_task("t2", duration_min=30, preferred_time="08:30")  # starts 08:30
        conflicts = scheduler.detect_conflicts([("Buddy", t1), ("Buddy", t2)])
        assert conflicts == []

    def test_no_conflict_for_separate_tasks(self, scheduler):
        t1 = make_task("t1", duration_min=30, preferred_time="08:00")
        t2 = make_task("t2", duration_min=30, preferred_time="10:00")
        conflicts = scheduler.detect_conflicts([("Buddy", t1), ("Buddy", t2)])
        assert conflicts == []

    # --- Edge cases ---

    def test_empty_list_returns_no_conflicts(self, scheduler):
        assert scheduler.detect_conflicts([]) == []

    def test_single_task_returns_no_conflicts(self, scheduler):
        t1 = make_task("t1", duration_min=30, preferred_time="08:00")
        assert scheduler.detect_conflicts([("Buddy", t1)]) == []

    def test_tasks_without_preferred_time_are_skipped(self, scheduler):
        t1 = make_task("t1", duration_min=30, preferred_time=None)
        t2 = make_task("t2", duration_min=30, preferred_time=None)
        assert scheduler.detect_conflicts([("Buddy", t1), ("Buddy", t2)]) == []

    def test_cross_pet_conflict_detected(self, scheduler):
        t1 = make_task("t1", duration_min=20, preferred_time="08:00")
        t2 = make_task("t2", duration_min=20, preferred_time="08:00")
        conflicts = scheduler.detect_conflicts([("Buddy", t1), ("Mochi", t2)])
        assert len(conflicts) == 1


# ===========================================================================
# 6. filter_by
# ===========================================================================

class TestFilterBy:
    def _make_owner(self):
        walk  = make_task("t1", title="Walk",    category="exercise", priority=1,
                          preferred_time="08:00")
        groom = make_task("t2", title="Groom",   category="grooming", priority=3,
                          preferred_time="11:00")
        feed  = make_task("t3", title="Feed Cat", category="feeding", priority=1,
                          preferred_time="07:30")
        buddy = Pet("p1", "Buddy", "dog", 3, tasks=[walk, groom])
        mochi = Pet("p2", "Mochi", "cat", 5, tasks=[feed])
        return make_owner(pets=[buddy, mochi])

    # --- Happy paths ---

    def test_filter_all_returns_every_task(self, scheduler):
        owner = self._make_owner()
        result = scheduler.filter_by(owner, status="all")
        assert len(result) == 3

    def test_filter_by_pet_name(self, scheduler):
        owner = self._make_owner()
        result = scheduler.filter_by(owner, pet_name="Buddy", status="all")
        assert all(name == "Buddy" for name, _ in result)
        assert len(result) == 2

    def test_filter_by_category(self, scheduler):
        owner = self._make_owner()
        result = scheduler.filter_by(owner, category="grooming", status="all")
        assert len(result) == 1
        assert result[0][1].title == "Groom"

    def test_filter_by_max_priority(self, scheduler):
        owner = self._make_owner()
        result = scheduler.filter_by(owner, max_priority=1, status="all")
        assert all(task.priority <= 1 for _, task in result)

    # --- Edge cases ---

    def test_pet_with_no_tasks(self, scheduler):
        empty_pet = Pet("p1", "Buddy", "dog", 3, tasks=[])
        owner = make_owner(pets=[empty_pet])
        result = scheduler.filter_by(owner, status="all")
        assert result == []

    def test_owner_with_no_pets(self, scheduler):
        owner = make_owner(pets=[])
        result = scheduler.filter_by(owner, status="all")
        assert result == []

    def test_unknown_pet_name_returns_empty(self, scheduler):
        owner = self._make_owner()
        result = scheduler.filter_by(owner, pet_name="Ghost", status="all")
        assert result == []

    def test_category_filter_is_case_insensitive(self, scheduler):
        owner = self._make_owner()
        result = scheduler.filter_by(owner, category="GROOMING", status="all")
        assert len(result) == 1


# ===========================================================================
# 7. generate_schedule
# ===========================================================================

class TestGenerateSchedule:
    # --- Happy paths ---

    def test_schedule_fits_within_available_minutes(self, scheduler):
        t1 = make_task("t1", duration_min=20, preferred_time="08:00")
        t2 = make_task("t2", duration_min=20, preferred_time="09:00")
        buddy = Pet("p1", "Buddy", "dog", 3, tasks=[t1, t2])
        owner = make_owner(available_minutes=60, pets=[buddy])
        result = scheduler.generate_schedule(owner)
        assert result["time_used"] <= 60

    def test_tasks_sorted_by_preferred_time_in_output(self, scheduler):
        t1 = make_task("t1", duration_min=15, preferred_time="10:00")
        t2 = make_task("t2", duration_min=15, preferred_time="08:00")
        buddy = Pet("p1", "Buddy", "dog", 3, tasks=[t1, t2])
        owner = make_owner(available_minutes=60, pets=[buddy])
        result = scheduler.generate_schedule(owner)
        starts = [row["start_time"] for row in result["schedule"]]
        assert starts == sorted(starts)

    def test_task_exceeding_budget_is_skipped(self, scheduler):
        # Both tasks fit in the 60-min budget (30+30), but t2's preferred_time
        # creates a gap that pushes its end past day_end → it gets skipped.
        # day: 08:00–09:00 (60 min). t1: 08:00–08:30. t2 preferred 08:45 →
        # placed 08:45–09:15, which exceeds 09:00.
        t1 = make_task("t1", duration_min=30, preferred_time="08:00")
        t2 = make_task("t2", duration_min=30, preferred_time="08:45")
        buddy = Pet("p1", "Buddy", "dog", 3, tasks=[t1, t2])
        owner = make_owner(available_minutes=60, pets=[buddy])
        result = scheduler.generate_schedule(owner, day_start="08:00")
        assert len(result["skipped"]) >= 1

    # --- Edge cases ---

    def test_pet_with_no_tasks_returns_empty_schedule(self, scheduler):
        buddy = Pet("p1", "Buddy", "dog", 3, tasks=[])
        owner = make_owner(pets=[buddy])
        result = scheduler.generate_schedule(owner)
        assert result["schedule"] == []
        assert result["skipped"] == []

    def test_no_pets_returns_empty_schedule(self, scheduler):
        owner = make_owner(pets=[])
        result = scheduler.generate_schedule(owner)
        assert result["schedule"] == []

    def test_preferred_time_before_day_start_is_moved(self, scheduler):
        """A task preferred at 06:00 should be moved to day_start (08:00)."""
        t1 = make_task("t1", duration_min=20, preferred_time="06:00")
        buddy = Pet("p1", "Buddy", "dog", 3, tasks=[t1])
        owner = make_owner(available_minutes=60, pets=[buddy])
        result = scheduler.generate_schedule(owner, day_start="08:00")
        assert result["schedule"][0]["start_time"] == "08:00"
        assert "conflict" in result["schedule"][0]
