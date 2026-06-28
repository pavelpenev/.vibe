---
name: auto-task
description: Use for multi-step task requests requiring sequential actions, such as "implement X", "find out what causes bug Y", or "tell me how feature X is currently implemented". Handles planning, user confirmation, autonomous execution, and result summary.
user-invocable: true
---

# Auto-Task

## Overview

Handles small, self-contained multi-step tasks with autonomous execution. The skill follows a Plan-and-Execute pattern: first creating a detailed plan, obtaining user approval, then executing sequentially with user assessment points.

## When to Use

**Trigger phrases:**
- "implement X"
- "find out what causes bug Y"
- "tell me how feature X is currently implemented"
- Any request requiring multiple sequential actions

**When NOT to use:**
- Large-scale planning (use project-planner instead)
- Single-step trivial tasks (use normal workflow)
- Tasks requiring broad architectural changes (use project-planner)

## Workflow

### Step 1: Scope Assessment
Assess if the task is small and self-contained enough for autonomous execution. Use these explicit criteria to determine if a task is too broad:

**A task is TOO BROAD if it:**
- Requires adding new dependencies to the project (e.g., new libraries)
- Involves external services, APIs, or network calls
- Spans more than one directory or affects multiple subsystems
- Has more than ~5 discrete steps
- Requires configuration changes outside the code (env vars, config files, etc.)
- Cannot be completed and reviewed in a single session

**If the task is too broad:**
- Ask the user to break it down into smaller pieces
- Propose a smaller scope for initial execution
- Suggest using project-planner for large architectural efforts

**Ideal task characteristics:**
- Single file modification or creation
- Pure computation or local data processing
- Well-defined, self-contained objective
- Minimal or no external dependencies

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
Execute the user-approved steps sequentially:

- Execute one step at a time in order
- If you encounter a decision point during execution:
  - **Low-risk decisions**: Make the decision yourself and continue
  - **Unresolved decisions**: The plan was inadequate - stop execution, revise the plan with the user before continuing
- Use any tools and skills needed to complete the task
- You may query PLAN.md and research directories for information, but must not modify them unless explicitly instructed

### Step 5: Error Handling
If a step fails:
- Make one attempt to recover from the failure
- If you cannot recover after one attempt, stop execution
- Prompt the user with partial success and explain what was completed and what failed

### Step 6: Completion and Summary
After executing all approved steps:
- Stop and provide a summary of what was accomplished
- In case of success: Summarize completed work and results
- In case of failure: Summarize partial completion and explain the failure
- Wait for user assessment before continuing
- Todo items are for your tracking; if the user accepts the task, they won't be needed anymore; if the task needs rework, they may be useful as history

## Task Characteristics

- **Scope**: Tasks should be small and self-contained
- **Building**: Tasks can build on each other - subsequent tasks can reference work from previous ones
- **Review**: User should be able to review completed work in one go
- **Autonomy**: Tasks should be completable autonomously once approved

## Integration

- **PLAN.md**: You may read PLAN.md for context but must not modify it unless explicitly told
- **Research directory**: You may query the ./research/ directory for existing research but must not modify it unless explicitly told
- **Tools**: Use any tools needed (read, write_file, edit, bash, grep, etc.)
- **Skills**: Invoke other skills as needed (deep-research, project-planner, etc.)
- **Todo tool**: Use for tracking steps during planning and execution

## User Interaction

- Always present the plan before execution
- Stop after completion for user assessment
- If interrupted by user (via /exit or Ctrl+C), stop gracefully
- If you need clarification on a high-risk decision during execution, stop and ask the user
