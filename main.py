"""Temporary testing ground for PawPal+ logic.

Run with:  python main.py

A scratch script to verify the domain model and scheduler work end-to-end in
the terminal before wiring them into the Streamlit UI. Not part of the test
suite — edit freely while experimenting.
"""

from datetime import time

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def main() -> None:
    # 1. Create an owner with a daily time budget (minutes).
    owner = Owner(name="Andy", available_minutes=90)

    # 2. Create at least two pets and register them with the owner.
    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever")
    mittens = Pet(name="Mittens", species="Cat", breed="Tabby")
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # 3. Add tasks out of chronological order to exercise sort_by_time().
    #    Note: Morning walk and Feeding are BOTH at 08:00 on purpose, so the
    #    scheduler's conflict detection has a real same-time clash to catch.
    mittens.add_task(
        Task("Play / enrichment", "enrichment", duration=20, priority=Priority.LOW,
             preferred_time=time(17, 0))
    )
    biscuit.add_task(
        Task("Feeding", "feeding", duration=10, priority=Priority.HIGH,
             preferred_time=time(8, 0))
    )
    mittens.add_task(
        Task("Litter cleanup", "grooming", duration=15, priority=Priority.MEDIUM,
             preferred_time=time(9, 0))
    )
    biscuit.add_task(
        Task("Morning walk", "walk", duration=30, priority=Priority.HIGH,
             preferred_time=time(8, 0))
    )

    # Mark one task complete so the completion filter has something to show.
    mittens.tasks[0].mark_complete()  # Play / enrichment

    # 4. Generate today's plan from all tasks + the owner's time budget.
    scheduler = Scheduler()
    plan = scheduler.build_plan(owner.all_tasks(), owner.available_minutes)

    # 5. Print "Today's Schedule" to the terminal.
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(plan.to_display())
    print("-" * 40)
    print(plan.summary())

    # 6. Verify sort_by_time(): tasks were added out of order above.
    print("\nTasks sorted by preferred time")
    print("=" * 40)
    for task in scheduler.sort_by_time(owner.all_tasks()):
        when = task.preferred_time.strftime("%H:%M") if task.preferred_time else "--:--"
        print(f"{when} — {task.name}")

    # 7. Verify filter_tasks() by completion status and by pet name.
    print("\nFilters")
    print("=" * 40)
    pending = owner.filter_tasks(completed=False)
    done = owner.filter_tasks(completed=True)
    print(f"Pending ({len(pending)}): {', '.join(t.name for t in pending)}")
    print(f"Completed ({len(done)}): {', '.join(t.name for t in done)}")
    biscuit_tasks = owner.filter_tasks(pet_name="Biscuit")
    print(f"Biscuit's tasks ({len(biscuit_tasks)}): "
          f"{', '.join(t.name for t in biscuit_tasks)}")

    # 8. Verify conflict detection: Morning walk and Feeding are both at 08:00.
    print("\nConflict warnings")
    print("=" * 40)
    if plan.warnings:
        for warning in plan.warnings:
            print(warning)
    else:
        print("No scheduling conflicts found.")


if __name__ == "__main__":
    main()
