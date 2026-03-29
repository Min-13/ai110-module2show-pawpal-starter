from pawpal_system import Task, Pet, Owner, Scheduler

# --- Tasks for Buddy (dog) — added OUT OF ORDER intentionally ---
evening_walk = Task(
    task_id="t5",
    title="Evening Walk",
    category="exercise",
    duration_min=20,
    priority=2,
    mandatory=False,
    preferred_time="18:00",
)

morning_walk = Task(
    task_id="t1",
    title="Morning Walk",
    category="exercise",
    duration_min=30,
    priority=1,
    mandatory=True,
    preferred_time="08:00",
)

grooming = Task(
    task_id="t6",
    title="Brush Coat",
    category="grooming",
    duration_min=15,
    priority=3,
    mandatory=False,
    preferred_time="11:30",
)

feeding_buddy = Task(
    task_id="t2",
    title="Feed Buddy",
    category="feeding",
    duration_min=5,
    priority=1,
    mandatory=True,
    preferred_time="07:30",
)

# --- Tasks for Mochi (cat) — added OUT OF ORDER intentionally ---
# NOTE: Playtime is set to 08:00 (same as Morning Walk) to trigger a conflict warning
playtime = Task(
    task_id="t7",
    title="Playtime",
    category="exercise",
    duration_min=15,
    priority=3,
    mandatory=False,
    preferred_time="08:00",
)

feeding_mochi = Task(
    task_id="t3",
    title="Feed Mochi",
    category="feeding",
    duration_min=5,
    priority=1,
    mandatory=True,
    preferred_time="07:45",
)

litter_box = Task(
    task_id="t4",
    title="Clean Litter Box",
    category="hygiene",
    duration_min=10,
    priority=2,
    mandatory=False,
    preferred_time="09:00",
)

# --- Pets ---
buddy = Pet(pet_id="p1", name="Buddy", species="dog", age=3, tasks=[evening_walk, morning_walk, grooming, feeding_buddy])
mochi = Pet(pet_id="p2", name="Mochi", species="cat", age=5, tasks=[playtime, feeding_mochi, litter_box])

# --- Owner ---
alex = Owner(
    owner_id="o1",
    name="Alex",
    available_minutes=60,
    prefer_short_tasks_first=False,
    low_energy_mode=False,
    pets=[buddy, mochi],
)

# --- Print Today's Schedule ---
scheduler = Scheduler()

WIDTH = 44

print()
print("=" * WIDTH)
print("  PawPal+  —  Today's Schedule".center(WIDTH))
print(f"  Owner: {alex.name}   Available: {alex.available_minutes} min".center(WIDTH))
print("=" * WIDTH)

total_minutes = 0

for pet in alex.pets:
    species = pet.species.capitalize()
    print(f"\n  {pet.name} ({species}, age {pet.age})")
    print("  " + "-" * (WIDTH - 2))

    for task in pet.tasks:
        status = "x" if task.completed else " "
        flag   = " (!)" if task.mandatory else "    "
        dur    = f"{task.duration_min} min"
        title  = task.title

        # left side: checkbox + title, right side: duration + flag
        left  = f"  [{status}] {title}"
        right = f"{dur}{flag}"
        gap   = WIDTH - len(left) - len(right)
        print(left + " " * max(gap, 1) + right)

        total_minutes += task.duration_min

remaining = alex.available_minutes - total_minutes

print()
print("=" * WIDTH)
print(f"  Total needed : {total_minutes} min")
print(f"  Time left    : {remaining} min")
print("=" * WIDTH)
print("  (!) = mandatory task")
print()

# --- Test sort_by_time() ---
print("=" * WIDTH)
print("  sort_by_time() — All Tasks by Preferred Time".center(WIDTH))
print("=" * WIDTH)

all_tasks = scheduler.filter_by(alex, status="all")
sorted_tasks = scheduler.sort_by_time(all_tasks)

for pet_name, task in sorted_tasks:
    time = task.preferred_time or "--:--"
    print(f"  {time}  [{pet_name}]  {task.title} ({task.duration_min} min)")

print()

# --- Test filter_by() — pending only ---
print("=" * WIDTH)
print("  filter_by() — Pending Tasks Only".center(WIDTH))
print("=" * WIDTH)

pending = scheduler.filter_by(alex, status="pending")
for pet_name, task in pending:
    print(f"  [ ] {task.title}  ({pet_name}, priority {task.priority})")

print()

# --- Test filter_by() — Buddy's grooming tasks ---
print("=" * WIDTH)
print("  filter_by() — Buddy's Grooming Tasks".center(WIDTH))
print("=" * WIDTH)

grooming_tasks = scheduler.filter_by(alex, pet_name="Buddy", category="grooming", status="all")
for pet_name, task in grooming_tasks:
    print(f"  {task.title}  ({task.duration_min} min, priority {task.priority})")

print()

# --- Test filter_by() — High priority (1-2) only ---
print("=" * WIDTH)
print("  filter_by() — High Priority Tasks (1-2)".center(WIDTH))
print("=" * WIDTH)

high_priority = scheduler.filter_by(alex, max_priority=2, status="all")
sorted_high = scheduler.sort_by_time(high_priority)
for pet_name, task in sorted_high:
    time = task.preferred_time or "--:--"
    print(f"  {time}  P{task.priority}  [{pet_name}]  {task.title}")

print()

# --- Conflict Detection ---
print("=" * WIDTH)
print("  detect_conflicts() — Scheduling Warnings".center(WIDTH))
print("=" * WIDTH)

all_tasks = scheduler.filter_by(alex, status="all")
conflicts = scheduler.detect_conflicts(all_tasks)

if conflicts:
    for c in conflicts:
        print(f"  WARNING: Preferred time conflict detected!")
        print(f"    Task A : {c['task_a']}")
        print(f"    Task B : {c['task_b']}")
        print(f"    Overlap: {c['overlap']}")
        print()
else:
    print("  No conflicts detected.")
    print()
