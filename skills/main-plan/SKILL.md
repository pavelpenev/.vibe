---
name: main-plan
description: Turn an approved design into an executable, bounded plan with work packages, dependencies, safe parallelism, acceptance checks, verification, rollback, and scope.
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - write_file
  - edit
  - ask_user_question
---

# Main Plan

Plan how to deliver an approved design without expanding scope. Read the design artifact, applicable AGENTS.md files, and relevant code or configuration. If acceptance, scope, or a destructive action is unresolved, ask the user to resolve it rather than guessing.

Write the plan to the task workspace, normally `~/.vibe/workspaces/<project>/tasks/<task>/state.md`. The plan must define:

- bounded work packages and the capability needed for each
- dependencies and only safe parallel work
- exact files or artifact paths in scope
- acceptance checks and concrete verification commands
- behavioral checks, with source evidence separated from runtime evidence
- non-destructive rollback or inverse edits that preserve unrelated changes
- explicit blockers, assumptions, and non-goals

Phases are optional, not an automatic pipeline. Model switches and skill loads are not isolation boundaries; handoffs use explicit artifacts. Do not create recurring verify or final-report files. The main agent owns state and updates the single running record.

## Cross-cutting architecture changes

When the change spans multiple subsystems or touches shared interfaces, additionally require:

- **Independently verifiable stages**: each stage has its own acceptance check runnable without later stages.
- **Explicit ownership**: every stage names the exact files it may modify and any shared interfaces it touches; no two parallel stages may modify the same file or the opposite sides of the same interface.
- **Preserved invariants**: list the behavior, contracts, and persisted-state compatibility each stage must not break, with source references.
- **Runnable checkpoints**: after each dependency boundary, a command or behavioral check that confirms the system still works before the next stage starts.
- **Safe parallelism**: parallel stages only when their file sets and interfaces are disjoint; otherwise serialize.

For such changes, a bounded architecture map may be dispatched as input (a subagent loading `sub-architecture-mapper` with a bounded target and a specific question). Its output is supporting evidence for the plan; it is not task state. Only write it to the task workspace if the plan explicitly assigns it an artifact path; otherwise consume it from the dispatch result.

Return the plan path, dependencies, acceptance summary, and blockers. Do not implement the plan.
