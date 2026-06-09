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

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

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

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
