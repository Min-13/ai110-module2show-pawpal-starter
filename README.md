# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Scheduler` class in `pawpal_system.py` has been extended with several new features beyond basic plan generation:

### Sort by time
`Scheduler.sort_by_time(task_items)` orders any list of tasks by their `preferred_time` attribute using a lambda key that converts `"HH:MM"` strings to total minutes. Tasks with no preferred time sort to the end.

### Flexible filtering
`Scheduler.filter_by(owner, ...)` filters tasks across all pets by any combination of:
- **Pet name** — narrow results to a single pet
- **Status** — `"pending"`, `"completed"`, or `"all"`
- **Category** — e.g. `"grooming"`, `"feeding"`
- **Max priority** — e.g. `max_priority=2` returns only priority 1 and 2 tasks

### Recurring task auto-scheduling
`Scheduler.complete_task(pet, task)` marks a task complete and, for `daily` or `weekly` tasks, automatically appends a fresh instance to the pet's task list for the next due date — calculated with Python's `timedelta`.

### Conflict detection
`Scheduler.detect_conflicts(task_items)` checks every pair of timed tasks for overlapping `preferred_time` windows. It returns a list of warning dicts describing each conflict (which tasks, which overlap window) without raising exceptions or halting the program.

---

## Testing PawPal+

### Run the tests

```bash
python -m pytest test/ -v
```

### What the tests cover

The test suite lives in `test/test_scheduler_features.py` and contains **49 tests** across 7 groups:

| Group | What is tested |
|-------|---------------|
| `TestIsDueToday` | Non-recurring, daily, and weekly due-date logic including boundary cases (exactly 6 vs 7 days ago) |
| `TestNextOccurrence` | Daily/weekly next-date calculation, attribute copying, month/year boundary rollovers, non-recurring returns `None` |
| `TestCompleteTask` | Marks task done, appends next occurrence for recurring tasks, leaves list unchanged for non-recurring |
| `TestSortByTime` | Chronological ordering, tasks without a preferred time sort last, empty list, single task |
| `TestDetectConflicts` | Same-time duplicates, partial overlaps, back-to-back (no conflict), cross-pet conflicts, tasks with no preferred time skipped safely |
| `TestFilterBy` | Filter by pet name, category (case-insensitive), max priority, empty pet, no pets, unknown pet name |
| `TestGenerateSchedule` | Schedule fits budget, sorted output, tasks skipped when time gap causes overflow, preferred time moved when before day start |

Each group includes both **happy paths** (normal inputs, expected outputs) and **edge cases** (empty lists, boundary values, missing data).

### Confidence Level

**4 / 5 stars**

The core scheduling logic — recurrence, sorting, conflict detection, and filtering — is fully covered and all 49 tests pass. One star is withheld because the Streamlit UI layer (`app.py`) has no automated tests, and integration between the UI and `Scheduler` is not yet verified programmatically.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
