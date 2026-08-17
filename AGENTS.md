# Global Agent Instructions

## Subagent Mechanics

- Syntax: `task(task="<clear task description>", agent="<subagent-name>")`
- Subagents inherit the global `active_model` from config.toml unless their TOML
  sets `active_model`. All workers are pinned to `gpt-5.6-luna`.
- Subagents return plain text only, cannot ask the user questions, and cannot
  spawn other subagents (depth limit 1).
- Provide all needed context in the task description — the subagent sees nothing else.
- Chaining: read the result, write concrete details (paths, symbols) into the next
  task string yourself.

## Clarification Protocol

Trigger when the referent is genuinely unresolvable from context — a vague
descriptor with no antecedent, multiple plausible targets that change the outcome,
or references to things never established this session. If the referent is clear
from context, proceed without asking. When triggered: list the concrete options
and ask one question. Do not guess.

## After Corrections

When the user corrects you ("no", "wrong", "I meant", "actually"): stop tool
operations, acknowledge the specific misunderstanding, ask whether to undo any
state you modified, and confirm the corrected understanding before proceeding.

## High-Risk Actions

State intent and confirm first for actions that span many files, delete resources,
rewrite git history, publish, or are otherwise hard to reverse. Format: "I will
[action] on [target] to achieve [outcome]. Confirm?"
