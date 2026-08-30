# Global Agent Instructions

## Subagent Mechanics

- Syntax: `task(task="<clear task description>", agent="<subagent-name>")`
- Subagents inherit the global `active_model` from config.toml unless their TOML
  sets `active_model`. Each generic subagent is pinned to a specific model.
- Subagents return plain text only, cannot ask the user questions, and cannot
  spawn other subagents (depth limit 1).
- Provide all needed context in the task description — the subagent sees nothing else.
- Chaining: read the result, write concrete details (paths, symbols) into the next
  task string yourself.

## Model Roster

| Agent | Model | Tier |
|-------|-------|------|
| generic-deepseek | deepseek-v4-flash | cheapest — bulk/baseline work |
| generic-luna | gpt-5.6-luna | cheap default — most delegated work |
| generic-glm-flash | glm-5.3-flash | low cost — extra parallel capacity |
| generic-glm | glm-5-2 | strong — strong-tier review |
| generic-sol | gpt-5.6-sol | strongest — advisor, deep review, plan review |
| generic-glm53 | glm-5.3 | strongest — advisor, deep review, plan review (cross-family second opinion to sol) |

Use the cheapest model capable of the task. Reserve generic-sol and
generic-glm53 for advisor calls and deep/plan reviews; never for mechanical
work (simple edits, searches, summarization, verification).

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

## Local AGENTS file

At the start of every session, check the working directory for a
project-specific `AGENTS.local.md`. It is gitignored (via `.git/info/exclude`,
not a tracked `.gitignore`) and Vibe does not auto-load it. If it exists, read
it before doing anything else. It is untracked and local — never commit it,
and never reference its contents in tracked files.
