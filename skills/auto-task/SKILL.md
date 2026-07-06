---
name: auto-task
description: Explicit /auto-task invocation only - do NOT trigger on natural language. Structured Plan-and-Execute workflow for small, self-contained multi-step tasks - planning, user confirmation, sequential execution, result summary. Uses code-review to assess its own output.
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - todo
  - task
  - skill
  - ask_user_question
  - web_search
---

# Auto-Task

## Overview

Handles small, self-contained multi-step tasks with autonomous execution. The skill follows a Plan-and-Execute pattern: first creating a detailed plan, obtaining user approval, then executing sequentially with user assessment points.

## When to Use

**Only on explicit invocation:**
- `/auto-task <task description>`

Do NOT activate on natural-language requests like "implement X" or "create a..." - those follow the normal agent workflow. This skill is an opt-in scaffold the user reaches for deliberately.

## When NOT to Use

- Large-scale planning (use project-planner instead)
- Tasks requiring deep research (use deep-research skill)
- Tasks spanning multiple directories or subsystems
- Tasks requiring new dependencies or external services
- Tasks that cannot be completed and reviewed in a single session
- Single-step trivial tasks (use normal workflow)

## Workflow

### Step 1: Scope Assessment
Assess if the task is small and self-contained enough for autonomous execution.

**First:** Scan conversation for user corrections ("no", "wrong", "I meant", "actually") and address these before proceeding.

Use these explicit criteria to determine if a task is too broad:

**A task is TOO BROAD if it:**
- Has more than ~5 discrete steps - this is a hard cap, not a warning; a weak orchestrator loses track of a plan beyond this
- Affects multiple logical subsystems (e.g., rewiring how two unrelated modules interact) - NOT the same as touching multiple directories; a source file plus its matching test file is one small task, not two
- Cannot be completed and reviewed in a single session
- Requires exploratory architecture decisions or open-ended requirements gathering (that's project-planner's job, not a bounded plan)

**These are NOT scope-rejects on their own** - flag them as a high-risk decision point in the plan (Step 2/3) instead, so the user approves that specific step rather than the whole task being rejected:
- Adding a new dependency
- Calling an external service or network API
- Editing operational config (env vars, secrets, infra-as-code) - editing an ordinary project config file (pyproject.toml, package.json) to wire in a dependency is routine, not high-risk

**If the task is too broad:**
- Ask the user to break it down into smaller pieces
- Propose a smaller scope for initial execution
- Suggest using project-planner for large architectural efforts

**Ideal task characteristics:**
- One to a few files, touched for a single well-defined objective (source + its test file counts as one objective)
- Well-defined, self-contained objective
- Any external calls or new dependencies are a known, plannable step - not an automatic disqualifier

### Step 2: Planning
Use the todo tool to create a step-by-step plan for the task:

1. Analyze what needs to be done
2. Break the task into discrete, actionable steps
3. Order steps logically with dependencies in mind
4. Identify any decisions that need to be made and classify them as low-risk (you can decide) or high-risk (needs user input)

### Step 3: User Confirmation
Present the entire plan to the user for approval:

- Display the complete step-by-step plan
- Highlight any high-risk decisions that require user input
- If the user deems the plan too big, revise the scope or make refinements as requested
- Only proceed with user-approved steps

### Step 4: Execution
Execute the user-approved steps sequentially, following the same delegation rules as normal operation:

- Execute one step at a time in order
- File creation/modification/deletion → delegate to `file-editor` (or `lisp-editor` for .lisp/.el/.asd) with literal content, never intent. Pattern search → delegate to `finder`. Do not call `write_file`/`edit`/`bash` directly for these - route through the same subagents the main agent would use
- If you encounter a decision point during execution:
  - **Low-risk decisions** (reversible, minimal impact): Make the decision, document it briefly, and continue
  - **High-risk decisions** (irreversible, significant impact): Stop execution and ask user
  - **Unresolved in plan**: Stop execution, revise plan with user before continuing
- You may query PLAN.md and research directories for information, but must not modify them unless explicitly instructed

### Step 5: Error Handling
Follow the system prompt's "Stop when stuck" rules. One addition specific to this skill: after any stop, report what was attempted, what succeeded, what failed and why, and what the user needs to decide before continuing.

### Step 6: Completion and Summary
After executing all approved steps:
- Use code-review skill to assess output quality before presenting to user
- Stop and provide a structured summary:
  - **Status**: SUCCESS / PARTIAL / FAILED
  - **Completed**: List of successfully executed steps with file paths/outcomes
  - **Failed**: List of failed steps with specific error reasons
  - **Decisions made**: Any autonomous low-risk decisions taken (with brief justification)
- Wait for user assessment before continuing
- Todo items are for your tracking; if the user accepts the task, they won't be needed anymore; if the task needs rework, they may be useful as history

## Task Characteristics

- **Scope**: Tasks should be small and self-contained
- **Building**: Tasks can build on each other - subsequent tasks can reference work from previous ones
- **Review**: User should be able to review completed work in one go
- **Autonomy**: Tasks should be completable autonomously once approved

## Integration

- **Context priority**: Project-local AGENTS.md > PLAN.md > Global AGENTS.md > Research directory
- **PLAN.md**: You may read PLAN.md for context but must not modify it unless explicitly told
- **Research directory**: You may query the ./research/ directory for existing research but must not modify it unless explicitly told
- **Tools**: `read_file`/`grep` directly for investigation; all writes and searches go through subagents per Step 4, same as normal operation
- **Skills**: May invoke debugging, test-generator, code-review, git-workflow, or web_search for specific sub-tasks. Do NOT invoke deep-research or project-planner.
- **Todo tool**: Use for tracking steps during planning and execution

## User Interaction

- Always present the plan before execution
- Stop after completion for user assessment
- If interrupted by user (via /exit or Ctrl+C), stop gracefully
- If you need clarification on a high-risk decision during execution, stop and ask the user

## Red Flags

- User insists on continuing after step failures without addressing root cause
- Task scope expands beyond original plan without re-approval
- User provides contradictory instructions during execution
- Task requires deep-research or project-planner skills (out of scope)
- User correction in conversation history is ignored

## Verification

Test with:
- [ ] Simple file creation task (1-2 steps)
- [ ] Multi-step modification task (3-5 steps)
- [ ] Task requiring web_search for documentation lookup
- [ ] Task with user decision point during execution
- [ ] Task that fails mid-execution
- [ ] Task with user correction in conversation history
- [ ] Task approaching step limit (warn user)
