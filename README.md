# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## ✨ Features

PawPal+ turns a list of pet care tasks into an explainable daily plan. The implemented algorithms are:

- **Priority-based packing** — `Scheduler.build_plan()` greedily fills the owner's time budget, placing higher-priority tasks first (HIGH → MEDIUM → LOW via `Priority.rank`) and using shorter duration as a tiebreaker. Tasks that don't fit are reported as *skipped* rather than dropped silently.
- **Sorting by priority** — `Scheduler.sort_tasks()` orders tasks by `(priority, duration)` for scheduling decisions.
- **Sorting by time** — `Scheduler.sort_by_time()` orders tasks chronologically by `preferred_time` (earliest first), with untimed tasks placed last via a stable sort.
- **Conflict warnings** — `Scheduler.detect_conflicts()` flags any two tasks whose `[start, start + duration)` windows overlap, labeling whether the clash is within the *same pet* or across *different pets*. It is non-fatal: it returns human-readable warning strings and never raises.
- **Daily & weekly recurrence** — completing a recurring task (`Task.mark_complete()`) automatically spawns its next occurrence (`Task.next_occurrence()`), advancing the due date by one interval (daily = +1 day, weekly = +7 days) and re-enrolling it with the pet.
- **Filtering** — `Owner.filter_tasks()` narrows tasks by completion status and/or pet name; `Pet.get_tasks()` filters by priority.
- **Plan explanation** — each `PlanEntry` renders its start time, task, duration, and priority, and `DailyPlan.summary()` reports totals, skipped tasks, and conflict counts.

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

## 🖥️ Sample Output

Terminal output from running `python main.py`, which builds an `Owner` with two pets and four tasks, then generates the daily plan:

```
Today's Schedule for Andy
========================================
08:00 — Feeding (10 min) [priority: high]
08:10 — Morning walk (30 min) [priority: high]
08:40 — Litter cleanup (15 min) [priority: medium]
08:55 — Play / enrichment (20 min) [priority: low]
----------------------------------------
Scheduled 4 task(s), 75 min total.
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

### What the tests cover

The suite in [`tests/test_pawpal.py`](tests/test_pawpal.py) exercises the core scheduling behaviors:

- **Task status** — `mark_complete()` flips a task from incomplete to complete.
- **Pet task management** — adding a task to a `Pet` increases its task count.
- **Sorting correctness** — `Scheduler.sort_by_time()` returns tasks in chronological order by `preferred_time`, and places untimed tasks last.
- **Recurrence logic** — completing a daily task spawns a fresh, incomplete occurrence with a new id, due the following day, auto-added to the pet; one-off tasks spawn nothing.
- **Conflict detection** — `Scheduler.detect_conflicts()` flags tasks whose preferred times overlap, while leaving back-to-back (touching but non-overlapping) tasks unflagged.

### Sample test output

```
============================= test session starts ==============================
platform darwin -- Python 3.10.4, pytest-9.0.3, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: /Users/andycordero/Desktop/CodePath/AI 110/pawpalplus
plugins: anyio-4.7.0
collecting ... collected 8 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 12%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 25%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 37%]
tests/test_pawpal.py::test_sort_by_time_places_untimed_tasks_last PASSED [ 50%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_occurrence PASSED [ 62%]
tests/test_pawpal.py::test_completing_non_recurring_task_creates_no_occurrence PASSED [ 75%]
tests/test_pawpal.py::test_scheduler_flags_tasks_at_same_time PASSED     [ 87%]
tests/test_pawpal.py::test_scheduler_allows_back_to_back_tasks PASSED    [100%]

============================== 8 passed in 0.01s ===============================
```

### Confidence Level

Rating: ★★★☆☆ (3 / 5)

All 8 tests pass and they cover the three highest-risk behaviors (sorting, recurrence, conflict detection) along with their key boundary cases. Confidence is held at 3 stars because several known edge cases are not yet tested — notably the midnight-wrap case in `_end_time()` (a task ending after 00:00 reports the wrong finish time), recurrence with no `due_date` defaulting to "today," and the divergence between `build_plan`'s priority ordering and the chronological `sort_by_time` view. Reliability for the tested paths is high; full-system confidence will rise as these gaps are closed.

## 📐 Smarter Scheduling

Beyond basic priority packing, PawPal+ implements four "smarter scheduling" behaviors. Each is summarized below and documented in detail after the table.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | Priority + duration, or chronological by preferred time |
| Filtering | `Owner.filter_tasks()` | By completion status and/or pet name |
| Conflict detection | `Scheduler.detect_conflicts()` | Warns on overlapping preferred-time windows; never crashes |
| Recurring tasks | `Task.mark_complete()`, `Task.next_occurrence()` | Daily/weekly tasks auto-spawn the next occurrence |

### Sorting behavior

- **`Scheduler.sort_tasks(tasks)`** — the scheduler's default ordering: highest priority first (`Priority.rank`), with shorter tasks first as a tiebreaker. This is what `build_plan` uses to decide what to fit into the time budget.
- **`Scheduler.sort_by_time(tasks)`** — orders tasks chronologically by `preferred_time` (earliest first). Tasks with no preferred time are placed last while preserving their original relative order (a stable sort).

### Filtering behavior

- **`Owner.filter_tasks(completed=None, pet_name=None)`** — returns tasks across all pets, optionally narrowed by:
  - `completed` — keep only completed (`True`) or only pending (`False`) tasks.
  - `pet_name` — keep only tasks belonging to the named pet (case-insensitive).
  - Both filters are optional; passing neither returns every task. It lives on `Owner` because that's the object that knows the pet → task relationship.

### Conflict detection logic

- **`Scheduler.detect_conflicts(tasks)`** — a lightweight, non-fatal check that returns a list of human-readable warning strings (never raises). Two tasks conflict when their `[start, start + duration)` windows overlap — interval overlap, not just identical start times — whether they belong to the **same pet** or **different pets** (the message labels which). Tasks without a `preferred_time` are ignored. `build_plan` stores the results on `DailyPlan.warnings`, and `DailyPlan.summary()` reports the count.
  - Helpers: `Scheduler._end_time()` computes a task's finish time via `timedelta`; `Scheduler._conflict_message()` formats each warning.

### Recurring task logic

- **`Task.mark_complete()`** — marks a task complete and, if it recurs, automatically creates the next occurrence and adds it to the same pet (via the back-reference set in `Pet.add_task`). Returns the new `Task` (or `None` for one-off tasks).
- **`Task.next_occurrence()`** — builds the next instance: a fresh, incomplete copy with a new id and the `due_date` advanced by one interval.
- **`Recurrence`** enum (`NONE` / `DAILY` / `WEEKLY`) with a `.delta` property supplying the `timedelta` between occurrences (daily = +1 day, weekly = +7 days). A legacy `recurring=True` flag is treated as daily for backward compatibility.

## 📸 Demo Walkthrough

Launch the interactive app with:

```bash
streamlit run app.py
```

### Main UI features

The Streamlit app ([`app.py`](app.py)) lets a user:

- **Set up owner & pet** — enter the owner's name, the daily time budget (minutes), and the pet's name and species.
- **Add tasks** — give each task a title, duration, priority, an optional preferred time, and a repeat cadence (none / daily / weekly).
- **Sort & filter the task list** — choose *Sort by: preferred time or priority* (backed by `Scheduler.sort_by_time()` / `sort_tasks()`) and *Filter by priority* (backed by `Pet.get_tasks()`). Results render in a clean table.
- **See conflict warnings live** — as soon as two preferred times overlap, the app shows a yellow warning; otherwise a green "No time conflicts" confirmation.
- **Generate today's schedule** — builds the plan within the time budget and renders it as a table, with a success summary plus any skipped tasks and conflicts.

### Example workflow

1. Enter owner **Andy** with **60 minutes** available, and pet **Biscuit** (dog).
2. Add **Feeding** (10 min, high, 08:00), **Morning walk** (30 min, high, 08:00), **Litter cleanup** (15 min, medium, 09:00), and **Play / enrichment** (20 min, low, 17:00).
3. In the task list, switch **Sort by** to *preferred time* — tasks reorder chronologically. The app flags that **Feeding** and **Morning walk** both start at 08:00 with a conflict warning.
4. Click **Generate schedule** — PawPal+ packs the tasks by priority into the time budget and displays the timed plan plus a summary.

### Key Scheduler behaviors shown

- **Sorting** — the schedule is packed in priority order, while the task list can be viewed chronologically.
- **Conflict warnings** — the two 08:00 tasks raise a *same-pet* overlap warning.
- **Recurrence** — marking a daily task complete enrolls tomorrow's occurrence automatically.
- **Filtering** — pending vs. completed and per-pet views.

### Sample CLI output

Running the headless demo (`python main.py`) exercises the same logic without the UI:

```text
Today's Schedule for Andy
========================================
08:00 — Feeding (10 min) [priority: high]
08:10 — Morning walk (30 min) [priority: high]
08:40 — Litter cleanup (15 min) [priority: medium]
08:55 — Play / enrichment (20 min) [priority: low]
----------------------------------------
Scheduled 4 task(s), 75 min total. 1 time conflict(s) detected.

Tasks sorted by preferred time
========================================
08:00 — Feeding
08:00 — Morning walk
09:00 — Litter cleanup
17:00 — Play / enrichment

Filters
========================================
Pending (3): Feeding, Morning walk, Litter cleanup
Completed (1): Play / enrichment
Biscuit's tasks (2): Feeding, Morning walk

Conflict warnings
========================================
⚠️  Conflict (same pet): Feeding (Biscuit) at 08:00 overlaps Morning walk (Biscuit) at 08:00.
```
