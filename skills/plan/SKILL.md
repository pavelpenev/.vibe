---
name: plan
description: "Run the planning phase: take a user-accepted design, orchestrate the planner subagent, and manage the plan review loop (plan-reviewer + empirical-reviewer in tandem) until the user accepts a concrete, bounded, verifiable plan."
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - agents_spawn
  - skill
---

# Plan

Plan is an orchestrator procedure covering the system prompt's planning phase: read the user-accepted design, produce a concrete plan via the `planner` subagent, and iterate review/fix cycles until the user accepts. The orchestrator owns the final plan.

## Phase 1 — Read the design

1. Read the accepted design (inline or a named document) and applicable AGENTS.md files.
2. Delegate any needed code/config investigation to `explorer` with a self-contained prompt, and fold the results into the planning brief.

## Phase 2 — Produce the plan

3. **Frame the planning question**: design goal, files and subsystems involved, cross-cutting concerns, and what the plan must address (dependencies, parallelism, verification, rollback).
4. **Dispatch the planner.** Self-contained spawn:

```text
agents_spawn(config_name="planner", prompt="Plan for: <design goal>. Design: <accepted approach>. Files and subsystems: <list>. Constraints: <dependencies, shared interfaces, preserved behavior>. Return: bounded work chunks, dependency order, safe parallelism, acceptance checks and verification commands per chunk, rollback approach.")
```

5. **Synthesize.** The orchestrator owns the plan — adjust chunk boundaries, fix missing dependencies, ensure the plan matches the accepted design. If the plan contradicts the design, trust the design.

## Phase 3 — Review loop until acceptance

6. Spawn `plan-reviewer` and `empirical-reviewer` in tandem (one parallel block), passing the plan, the design, and prior findings.
7. If both accept, present the plan inline to the user and wait for acceptance. Otherwise apply fixes inline and re-review the delta.
8. **Stopping conditions** (same anti-loop rules as the review skill): stop when both reviewers accept; on diminishing returns (only fix-text issues or nothing new substantive) do one targeted pass, then escalate; hard cap of 3 rounds, then escalate unresolved findings to the user.

## Plan content

The plan must define:
- bounded work chunks, each assignable to a single `executor` subagent
- dependencies, the implementation order, and only safe parallel chunks
- exact files or artifact paths in scope
- acceptance checks and concrete verification commands per chunk
- behavioral checks, with source evidence separated from runtime evidence
- non-destructive rollback or inverse edits that preserve unrelated changes
- explicit blockers, assumptions, and non-goals

For most tasks the plan is inline in the conversation. For large or cross-cutting changes, write it to a markdown file in the project (or the scratchpad) and reference it.

## Cross-cutting architecture changes

When the change spans multiple subsystems or touches shared interfaces, additionally require:
- **Independently verifiable stages**: each stage has its own acceptance check runnable without later stages.
- **Explicit ownership**: every stage names the exact files it may modify; no two parallel stages may modify the same file or opposite sides of the same interface.
- **Preserved invariants**: behavior, contracts, and persisted-state compatibility each stage must not break, with source references.
- **Runnable checkpoints**: after each dependency boundary, a check confirming the system still works before the next stage starts.
- **Safe parallelism**: parallel stages only when file sets and interfaces are disjoint; otherwise serialize.

## Constraints

- Do not implement the plan — planning only.
- The orchestrator owns the plan — the planner advises, the orchestrator decides, the user accepts.
- Reviewers are read-only; fixes between rounds are applied by the orchestrator.
