---
name: main-review
description: Review code, diffs, branches, pull requests, docs, specifications, and plans through bounded multi-model tiers and synthesize the findings.
user-invocable: true
allowed-tools:
  - task
  - bash
  - read_file
---

# Main Review

Review is a main-agent orchestration procedure. Reviewers are independent, read-only subagents that load `sub-reviewer`. The main agent owns target selection, intent, tier choice, synthesis, and any follow-up.

## Target and intent

Use an explicitly named file, directory, diff, branch, pull request, or plan. If no target is named, use the uncommitted diff when one exists; otherwise ask the user for a target. Use the user's stated intent, the commit message, or the artifact goal. Ask one question only when the target or intent is genuinely unresolved.

For a pull request, fetch its branch before delegating, then review the branch comparison. Do not modify the target while reviewing.

## Tiers

- **Quick:** one `generic-sol-medium` reviewer. Use for quick, fast, trivial, or rename-only reviews.
- **Standard:** dispatch one `generic-sol-medium` reviewer, loading `sub-reviewer`.
- **Deep:** dispatch `generic-sol-high` and `generic-glm` in parallel, both loading `sub-reviewer`, then synthesize both reports.
- **Plans:** use the Deep procedure for plans, specifications, and designs.

Use only the listed agents. Do not call the usage tool automatically. Keep each phase bounded to one dispatch per listed reviewer and at most two refinement rounds unless the user approves a larger budget.

If a listed reviewer fails or is unavailable, report the failure as a blocker in the synthesis with per-reviewer status. Do not silently substitute an unlisted agent for an approved tier slot; a substitution is a scope change to propose to the user.

## Dispatch

Each task string must be self-contained:

```text
task(task="Load the sub-reviewer skill. Review: <target>. Intent: <intent>. Tier: <tier>. Return the complete review report in the skill's format.", agent="<agent>")
```

Issue independent Deep calls in one parallel tool block. For Deep and Plans, synthesize the sol-high and glm reports, extracting consensus and notable divergent findings.

## Synthesis

Return one convergence view:

- target, intent, tier, and reviewer count
- consensus findings with reviewer counts and file/line locations
- divergent findings and confidence
- blocking issues
- per-reviewer status
- prioritized next steps
- whether another bounded round is warranted

A finding from two or more reviewers is consensus. Any blocker reported by a reviewer is blocking until resolved or explicitly accepted by the user. Do not claim a runtime or verification pass unless a command or behavioral test was actually observed.
