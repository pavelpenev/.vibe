---
name: main-design
description: Shape an approved problem into a concise design with goals, constraints, rationale, non-goals, and an explicit task-workspace artifact.
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - write_file
  - edit
  - ask_user_question
---

# Main Design

Own the what and why before implementation. Clarify the desired outcome, constraints, invariants, tradeoffs, and explicit non-goals. Keep the design role-neutral: describe capabilities needed, not a frozen model or agent assignment.

Read applicable AGENTS.md files and relevant existing artifacts before designing. Ask the user one focused question when acceptance or scope is genuinely unresolved. Do not implement code while designing.

Write the approved design in the Design section of the current task's `~/.vibe/workspaces/<project>/tasks/<task>/state.md`, preserving its plan, execution state, and evidence. Use `workspace` for task identity and storage conventions. Create a separate design document only when explicitly requested or when the user approves a justified exception. Include:

- goal and user-visible outcome
- current context and assumptions
- constraints and preserved behavior
- chosen approach and rationale
- alternatives rejected and why
- explicit non-goals
- acceptance criteria and unresolved risks

Return the artifact path and a short decision summary. The main agent owns task state; do not infer a latest task from directory ordering.
