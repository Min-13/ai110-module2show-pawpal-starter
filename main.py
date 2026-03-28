from pawpal_system import Task, Pet, Owner, Scheduler

# --- Tasks for Buddy (dog) ---
morning_walk = Task(
    task_id="t1",
    title="Morning Walk",
    category="exercise",
    duration_min=30,
    priority=1,
    mandatory=True,
)

feeding_buddy = Task(
    task_id="t2",
    title="Feed Buddy",
    category="feeding",
    duration_min=5,
    priority=1,
    mandatory=True,
)

# --- Tasks for Mochi (cat) ---
feeding_mochi = Task(
    task_id="t3",
    title="Feed Mochi",
    category="feeding",
    duration_min=5,
    priority=1,
    mandatory=True,
)

litter_box = Task(
    task_id="t4",
    title="Clean Litter Box",
    category="hygiene",
    duration_min=10,
    priority=2,
    mandatory=False,
)

# --- Pets ---
buddy = Pet(pet_id="p1", name="Buddy", species="dog", age=3, tasks=[morning_walk, feeding_buddy])
mochi = Pet(pet_id="p2", name="Mochi", species="cat", age=5, tasks=[feeding_mochi, litter_box])

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
