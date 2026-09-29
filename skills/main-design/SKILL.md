---
name: main-design
description: "Shape an approved problem into a concise design with goals, constraints, rationale, non-goals. Delegates deep design analysis to sol-high subagents."
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - write_file
  - edit
  - task
---

# Main Design

Own the what and why before implementation. The orchestrator gathers context and frames the design question; sol-high subagents do the deep design analysis. The orchestrator synthesizes and owns the final design.

## Process

1. **Gather context.** Read applicable AGENTS.md files and user-named input documents. Delegate investigation of relevant existing artifacts and code to `sub-finder` or `sub-explorer` to identify interfaces, contracts, and dependencies.
2. **Frame the design question.** Define: the problem, constraints, preserved behavior, and what a good design must address. This is the input you pass to sol-high.
3. **Dispatch sol-high for design analysis.** Send a self-contained task to `generic-sol-high` with the `sub-advisor` skill:

```text
task(task="Load the sub-advisor skill. Design analysis for: <problem>. Context: <relevant code, interfaces, constraints>. Requirements: <what the design must address, preserved behavior, non-goals>. Return a recommended approach with rationale, alternatives rejected, risks, and assumptions.", agent="generic-sol-high")
```

For large or cross-cutting changes, dispatch sol-high with `sub-architecture-mapper` first to map the affected subsystems, then use that output to frame the design question.

4. **Synthesize.** Review sol-high's analysis. The orchestrator owns the final design — accept, adjust, or reject sol-high's recommendation. If sol-high's design misses something the user asked for, fix it.
5. **Present to the user.** Share the design inline in the conversation. Wait for the user to react before proceeding.

## Design content

The design covers:
- goal and user-visible outcome
- current context and assumptions
- constraints and preserved behavior
- chosen approach and rationale
- alternatives rejected and why
- explicit non-goals
- acceptance criteria and unresolved risks

Write the design to the task workspace (`~/.vibe/workspaces/<project>/tasks/<task>/state.md`) only for large or cross-cutting changes. For most tasks, the design is inline in the conversation.

## Constraints

- Do not implement code while designing.
- The orchestrator owns the design — sol-high advises, the orchestrator decides.
- Do not use `ask_user_question` — discuss design topics inline in the conversation.
