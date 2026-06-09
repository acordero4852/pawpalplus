# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ supports three core actions:

1. **Add/manage a pet (and owner profile)** — enter owner info and create a pet with name, species/breed, and care preferences. This anchors all tasks and scheduling.
2. **Add/edit care tasks** — add walks, feeding, meds, enrichment, or grooming, each with at least a duration and priority, and edit or remove them as needs change.
3. **Generate and view today's plan** — run the scheduler over tasks and constraints (time, priority, preferences) to produce a clear, ordered daily plan with reasoning.

**a. Initial design**

My initial UML follows a clear data flow: **Owner → Pet → Task → Scheduler → DailyPlan**. I chose these classes and responsibilities:

- **Owner** — holds owner info, time budget (`available_minutes`), and preferences; manages the list of pets (`add_pet`, `remove_pet`).
- **Pet** — represents the animal and owns its care tasks; supports `add_task`, `edit_task`, `remove_task`, and `get_tasks`.
- **Task** — a single unit of care (name, category, duration, priority, optional preferred time, recurring flag); knows how to compare its own priority.
- **Priority** — an enum (HIGH/MEDIUM/LOW) so sorting and display are unambiguous.
- **Scheduler** — the "brain": takes tasks plus a time budget and produces a plan (`build_plan`, `sort_tasks`, `fits`). Kept separate from data and UI so it's easy to test.
- **DailyPlan** — the output; holds ordered `PlanEntry` items, skipped tasks, and totals, and formats itself for display.
- **PlanEntry** — pairs an assigned `start_time` with a `Task`, keeping scheduling output separate from intrinsic task data.

**b. Design changes**

Reviewing the skeleton against the "generate today's plan" action surfaced two gaps:

1. **Missing Owner → Scheduler bridge.** `Scheduler.build_plan` expects a flat `list[Task]`, but tasks live on individual `Pet`s under an `Owner`. Nothing collected them. I added `Owner.all_tasks()` to gather tasks across all pets, so the UI can pass `owner.all_tasks()` plus `owner.available_minutes` straight into the scheduler. This keeps the Scheduler decoupled from domain objects rather than making it traverse Owner→Pet→Task itself.

2. **No stable task identity (potential bottleneck).** `Pet.edit_task`/`remove_task` relied on object identity, which is fragile in a Streamlit UI where form submissions reference ids, not Python objects. I added a `task_id` attribute to `Task` so tasks can be looked up reliably for editing/removal and rendered consistently in the UI.

Both are additive — no relationships were removed.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

One deliberate tradeoff is that **conflict detection and plan placement use two different notions of "when."** `build_plan` greedily packs tasks back-to-back by priority from `DAY_START`, so the *placed* schedule never physically overlaps. Separately, `detect_conflicts` compares each task's `preferred_time` window (`[start, start + duration)`) and warns when those *intended* times collide. So a task flagged as conflicting at 08:00 may still print at 08:10 in the final plan — the warnings describe the owner's intentions, not the placed schedule.

This is reasonable here because the value is the heads-up ("you can't be in two places at once"), while the packer just fits everything into the time budget. Treating `preferred_time` as a hard constraint would turn scheduling into a much harder constraint-satisfaction problem; for one owner with a handful of daily tasks, a lightweight non-blocking warning plus priority packing delivers most of the benefit at far less complexity. I also used interval-overlap detection rather than exact time matches, so near-misses like 08:00 vs 08:15 are still caught.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

**c. AI Strategy**

**Most effective AI features.** The biggest wins came from giving the assistant the *actual* source file and asking grounded, comparative questions — e.g. "based on my final `pawpal_system.py`, what should change in my UML?" Because it could read the real code, it produced an accurate diff (the new `Recurrence` enum, the `Task.pet` back-reference, the conflict helpers) instead of guessing. Its ability to generate runnable `pytest` cases and then *run them* to confirm they passed turned testing into a fast feedback loop. Edge-case brainstorming was also valuable: asking "what should I test for sorting and recurrence?" surfaced cases I hadn't considered, like the midnight-wrap bug in `_end_time()`.

**A suggestion I modified.** When wiring up the Streamlit display, the assistant initially leaned toward having the scheduler reach into `Owner → Pet → Task` to gather and render tasks itself. I rejected that to keep the `Scheduler` decoupled from the domain objects — instead I kept `Owner.all_tasks()` as the bridge and had the scheduler operate on a plain `list[Task]`. This preserved the clean one-way data flow and kept the scheduler unit-testable in isolation.

**Separate sessions per phase.** Splitting work into phase-specific sessions — design/UML, implementation, testing, and documentation — kept each conversation focused on one mental model. The testing session wasn't cluttered with design debate, and the docs session could treat the code as finished and just describe it. It also made it easy to re-enter a phase later (revising the UML) without dredging through unrelated context.

**Being the lead architect.** The clearest lesson: the AI is a fast, literal implementer, but the *architecture is mine to own*. It will happily produce working code that quietly couples layers or drifts from the design if I don't hold the line. My job was to set the invariants (one-way data flow, scheduler stays decoupled, warnings are non-fatal), feed it the real artifacts so its answers were grounded, and verify every suggestion against those principles and the tests. The AI accelerated the *how*; I stayed responsible for the *what* and *why*.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
