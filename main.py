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

    # 3. Add at least three tasks, with different preferred times and priorities.
    biscuit.add_task(
        Task("Morning walk", "walk", duration=30, priority=Priority.HIGH,
             preferred_time=time(8, 0))
    )
    biscuit.add_task(
        Task("Feeding", "feeding", duration=10, priority=Priority.HIGH,
             preferred_time=time(8, 30))
    )
    mittens.add_task(
        Task("Litter cleanup", "grooming", duration=15, priority=Priority.MEDIUM,
             preferred_time=time(9, 0))
    )
    mittens.add_task(
        Task("Play / enrichment", "enrichment", duration=20, priority=Priority.LOW,
             preferred_time=time(17, 0))
    )

    # 4. Generate today's plan from all tasks + the owner's time budget.
    scheduler = Scheduler()
    plan = scheduler.build_plan(owner.all_tasks(), owner.available_minutes)

    # 5. Print "Today's Schedule" to the terminal.
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)
    print(plan.to_display())
    print("-" * 40)
    print(plan.summary())


if __name__ == "__main__":
    main()
