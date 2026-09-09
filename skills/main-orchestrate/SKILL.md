---
name: main-orchestrate
description: "Execution guidance for the implementation phase: task granularity, worker routing, state management, and verification during implementation."
user-invocable: true
allowed-tools:
  - task
  - read_file
  - write_file
  - edit
  - grep
  - bash
---

# Main Orchestrate

This skill provides detailed execution guidance for the implementation phase (Phase 4) of the mandatory workflow defined in `prompts/system-prompt-large.md`. The workflow phases (Understand, Respond, Design, Plan, Implement, Verify, Review) are in the system prompt and are not restated here. This skill covers task granularity, worker routing, and state management during execution.

The main agent owns task state, checkpoints, synthesis, and the final acceptance decision. Subagents are non-interactive: they return results and blockers, unless explicitly assigned an artifact path. Any scope, design, acceptance, destructive-operation, or budget change is a proposal; escalate it to the user before acting.

## Task granularity

Split implementation tasks into focused units so subagents complete faster. Minutes of waiting are acceptable for genuinely complex work — the goal is to cut unnecessary time, not to force every task to be trivial.

- **One file per implementor when practical.** If a change spans three files with no dependencies, dispatch three implementors in parallel. But a complex change in one file that needs deep reasoning is one task for a strong agent — do not split it artificially.
- **Provide context, not exploration.** Give each subagent the signatures, types, or interface contracts it needs so it does not grep and read sibling files to understand them. This is the biggest time saver — most subagent minutes are spent reading context the orchestrator already has.
- **Parallel over sequential when independent.** Dispatch independent edits simultaneously. Wait only when one edit's output is another's input.
- **Match the split to the task.** A feature touching five files with simple changes each: five parallel luna tasks. A refactor that restructures a core module: one sol or astra task with the full scope. Let the task's complexity decide the split, not a fixed rule.

## Worker routing

Dispatch the cheapest agent that can handle the task. The full dispatch table and rules are in `prompts/system-prompt-large.md` under "Model dispatch"; they are not restated here. In brief:

- `generic-luna` for trivial tasks (search, grep, verification, single-file edits).
- `generic-terra` for normal implementation (multi-file edits, feature work) and as the default reviewer.
- `generic-sol` for demanding implementation (complex logic, refactoring, broad impact).
- `generic-astra` for the most complex implementation, deep review, and design/planning support when the orchestrator needs a strong second perspective on approach, decomposition, or risk.
- `generic-glm` for rare cross-family second opinions.

Use astra to aid in design and planning: dispatch it with a design or plan target and the `sub-advisor` or `sub-reviewer` skill when the orchestrator needs to validate an approach, surface risks, or decompose a complex task before committing to implementation.

Each dispatch task names exactly one `sub-*` role skill, states the target and intent, and specifies the required result format. Review tiers are owned by `main-review` and are not restated here: follow `main-review` for tier composition, reviewer agents, and backup behavior.

## State and verification

Record phase progress, evidence, caveats, and blockers in the task's `state.md`. Keep source inspection, static checks, and fresh-session behavioral tests distinct. Never claim a runtime pass without observing it. Promote repository documentation explicitly; do not collect workspace artifacts automatically. Stop and report if an approved job cannot be completed or if a new destructive action is required.
