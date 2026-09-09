---
name: main-plan
description: "Turn an approved design into an executable, bounded plan with work packages, dependencies, safe parallelism, acceptance checks, and verification. Delegates deep planning analysis to astra subagents."
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - write_file
  - edit
  - task
---

# Main Plan

Plan how to deliver an approved design without expanding scope. The orchestrator reads the design and frames the planning question; astra subagents do the deep planning analysis. The orchestrator synthesizes and owns the final plan.

## Process

1. **Read the design.** Read the approved design artifact (inline or workspace `state.md`), applicable AGENTS.md files, and relevant code or configuration.
2. **Frame the planning question.** Define: the design goal, the files and subsystems involved, any cross-cutting concerns, and what the plan must address (dependencies, parallelism, verification, rollback).
3. **Dispatch astra for planning analysis.** Send a self-contained task to `generic-astra` with the `sub-advisor` skill:

```text
task(task="Load the sub-advisor skill. Planning analysis for: <design goal>. Design: <approved approach>. Files and subsystems: <list>. Constraints: <dependencies, shared interfaces, preserved behavior>. Return: bounded work packages, dependency order, safe parallelism, acceptance checks per package, verification commands, and rollback approach.", agent="generic-astra")
```

For cross-cutting changes that span multiple subsystems, dispatch astra with `sub-architecture-mapper` first to map interfaces and dependencies, then use that output to frame the planning question.

4. **Synthesize.** Review astra's plan. The orchestrator owns the final plan — adjust work package boundaries, fix missing dependencies, and ensure the plan matches the approved design. If astra's plan contradicts the design, trust the design.
5. **Present to the user.** Share the plan inline in the conversation. Wait for the user to react before proceeding to implementation.

## Plan content

The plan must define:
- bounded work packages and the capability needed for each
- dependencies and only safe parallel work
- exact files or artifact paths in scope
- acceptance checks and concrete verification commands
- behavioral checks, with source evidence separated from runtime evidence
- non-destructive rollback or inverse edits that preserve unrelated changes
- explicit blockers, assumptions, and non-goals

Write the plan to the task workspace (`~/.vibe/workspaces/<project>/tasks/<task>/state.md`) only for large or cross-cutting changes. For most tasks, the plan is inline in the conversation.

## Cross-cutting architecture changes

When the change spans multiple subsystems or touches shared interfaces, additionally require:
- **Independently verifiable stages**: each stage has its own acceptance check runnable without later stages.
- **Explicit ownership**: every stage names the exact files it may modify and any shared interfaces it touches; no two parallel stages may modify the same file or the opposite sides of the same interface.
- **Preserved invariants**: list the behavior, contracts, and persisted-state compatibility each stage must not break, with source references.
- **Runnable checkpoints**: after each dependency boundary, a command or behavioral check that confirms the system still works before the next stage starts.
- **Safe parallelism**: parallel stages only when their file sets and interfaces are disjoint; otherwise serialize.

## Constraints

- Do not implement the plan — planning only.
- The orchestrator owns the plan — astra advises, the orchestrator decides.
- Do not use `ask_user_question` — discuss planning topics inline in the conversation.
