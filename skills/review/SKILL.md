---
name: review
description: "Review designs, plans, code, and docs by spawning the right reviewer subagents in tandem, iterating bounded review/fix cycles, and stopping on diminishing returns instead of looping. Synthesizes findings into one convergence view."
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - agents_spawn
  - skill
---

# Review

Review is an orchestrator procedure that expands the review steps of the system prompt (design review, plan review, per-chunk verification, final review). Reviewers are independent, read-only subagents; the orchestrator owns target selection, synthesis, and the fix/re-review loop.

## Choosing reviewers

Every review round is a tandem: one domain reviewer plus the `empirical-reviewer`, spawned together in one parallel block. A round is accepted only when both accept.

| Artifact under review | Domain reviewer | Also spawn |
|---|---|---|
| design proposal | `design-reviewer` | `empirical-reviewer` |
| implementation plan | `plan-reviewer` | `empirical-reviewer` |
| code / diff / chunk output | `code-reviewer` | `empirical-reviewer` |
| prose (docs, reports) | `doc-reviewer` | `empirical-reviewer` |
| any factual claim | — | `empirical-reviewer` alone |

Reviewer models are pinned per subagent in `~/.vibe/agents/`, so reviewers are independent from the `executor` by construction — no authorship substitution is needed.

## Dispatch

Each spawn prompt must be self-contained (subagents do not see this conversation):

```text
agents_spawn(config_name="code-reviewer", prompt="Review: <target: files, diff, or artifact>. Intent: <goal>. Context: <relevant plan chunk or design>. Return findings with file:line, severity, and a verdict: APPROVE or CHANGES REQUESTED.")
agents_spawn(config_name="empirical-reviewer", prompt="Empirically verify: <claims to check>. Run the relevant tests/checks. Return per-claim CONFIRMED or REFUTED with the commands run and observed output.")
```

## Target and intent

Use an explicitly named file, directory, diff, or artifact. If none is named, use the uncommitted diff when one exists; otherwise ask the user for a target. Reviewers never modify the target; fixes are applied by the orchestrator or an `executor` between rounds, never during a round.

## Review/fix cycles (bounded iteration)

1. Run the tandem review round. Record the findings (id, severity, location).
2. Apply fixes — via `executor` for code, inline for plans/docs/designs.
3. Re-run the same tandem on the delta (what changed since the last round), passing the prior findings so reviewers can check they were actually fixed.
4. Compare rounds: track how many prior findings are resolved and how many new substantive findings appear.

## Stopping conditions — do not loop forever

Stop the cycle and move on (or escalate) when any of these holds:

- **Both reviewers accept** the round — done.
- **Diminishing returns**: a re-run surfaces no new substantive findings, or only issues with the fix text itself (fix-induced regressions), not with the original target. Fix-induced issues get one targeted fix pass, then are escalated, not re-reviewed endlessly.
- **No convergence**: after 3 rounds, if severity-weighted findings are not decreasing, stop and escalate the unresolved findings to the user with a summary. The user decides: accept, expand the review budget, or drop the item.
- A reviewer-reported blocker stays blocking until resolved or explicitly accepted by the user.

Never claim a verification pass unless a command or behavioral test was actually observed by the `empirical-reviewer`.

## Synthesis

Return one convergence view:

- target, intent, artifact type, round number, reviewers spawned
- consensus findings (both reviewers agree) with file:line locations
- divergent findings and which reviewer raised each
- blocking issues and their status across rounds
- prioritized next steps
- whether another round is warranted, and which stopping condition applies

## Constraints

- Reviewers are read-only; do not modify the target during a review round.
- One dispatch per reviewer per round; do not re-spawn a reviewer mid-round.
- If a reviewer fails, report it as a blocker in the synthesis — do not silently substitute another subagent.
- Do not use `ask_user_question` for review topics — discuss inline in the conversation.
