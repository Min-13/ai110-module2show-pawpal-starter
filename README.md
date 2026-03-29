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
