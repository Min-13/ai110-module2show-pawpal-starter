from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(task_id="t1", title="Morning Walk", category="exercise", duration_min=30, priority=1)

    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(pet_id="p1", name="Buddy", species="dog", age=3)
    task = Task(task_id="t1", title="Feed Buddy", category="feeding", duration_min=5, priority=1)

    assert len(pet.tasks) == 0
    pet.tasks.append(task)
    assert len(pet.tasks) == 1
