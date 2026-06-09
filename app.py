from datetime import time

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Recurrence, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner & Pet")
owner_name = st.text_input("Owner name", value="Jordan")
available_minutes = st.number_input(
    "Time available today (minutes)", min_value=5, max_value=600, value=60, step=5
)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Create the Owner + Pet once, then keep them in the session "vault" so tasks
# persist across re-runs. Sync the editable fields on every run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(owner_name, available_minutes=int(available_minutes))
    st.session_state.pet = Pet(pet_name, species, breed="")
    st.session_state.owner.add_pet(st.session_state.pet)

owner = st.session_state.owner
pet = st.session_state.pet
owner.name = owner_name
owner.available_minutes = int(available_minutes)
pet.name = pet_name
pet.species = species

st.markdown("### Tasks")
st.caption("Add care tasks for your pet. These feed directly into the scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    use_time = st.checkbox("Set a preferred time", value=True)
    preferred = st.time_input("Preferred time", value=time(8, 0), disabled=not use_time)
with col5:
    recurrence = st.selectbox("Repeats", [r.value for r in Recurrence], index=0)

if st.button("Add task"):
    pet.add_task(
        Task(
            name=task_title,
            category="general",
            duration=int(duration),
            priority=Priority(priority),
            preferred_time=preferred if use_time else None,
            recurrence=Recurrence(recurrence),
        )
    )

scheduler = Scheduler()

if pet.tasks:
    st.write("**Current tasks**")

    fcol, scol = st.columns(2)
    with fcol:
        priority_filter = st.selectbox(
            "Filter by priority", ["all", "high", "medium", "low"]
        )
    with scol:
        sort_mode = st.selectbox(
            "Sort by", ["preferred time", "priority"]
        )

    # Filtering via Pet.get_tasks, then sorting via the Scheduler's methods.
    selected = (
        pet.get_tasks()
        if priority_filter == "all"
        else pet.get_tasks(filter_by=Priority(priority_filter))
    )
    if sort_mode == "preferred time":
        selected = scheduler.sort_by_time(selected)
    else:
        selected = scheduler.sort_tasks(selected)

    if selected:
        st.table(
            [
                {
                    "Task": t.name,
                    "Duration": f"{t.duration} min",
                    "Priority": t.priority.value,
                    "Preferred time": (
                        t.preferred_time.strftime("%H:%M")
                        if t.preferred_time
                        else "—"
                    ),
                    "Repeats": t.recurrence.value,
                    "Done": "✅" if t.completed else "⬜",
                }
                for t in selected
            ]
        )
    else:
        st.info(f"No {priority_filter}-priority tasks.")

    # Surface scheduling conflicts up front, before a plan is even built.
    conflicts = scheduler.detect_conflicts(pet.tasks)
    if conflicts:
        for warning in conflicts:
            st.warning(warning)
    else:
        st.success("No time conflicts among preferred times.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generates today's plan from your tasks and time budget.")

if st.button("Generate schedule"):
    plan = scheduler.build_plan(owner.all_tasks(), owner.available_minutes)
    if plan.entries:
        st.success(plan.summary())
        st.table(
            [
                {
                    "Start": entry.start_time.strftime("%H:%M"),
                    "Task": entry.task.name,
                    "Duration": f"{entry.task.duration} min",
                    "Priority": entry.task.priority.value,
                }
                for entry in plan.entries
            ]
        )
    else:
        st.info("No tasks scheduled. Add some tasks first.")
    if plan.skipped:
        st.warning(
            "⏰ Skipped (out of time): "
            + ", ".join(t.name for t in plan.skipped)
        )
    for warning in plan.warnings:
        st.warning(warning)
