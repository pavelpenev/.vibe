---
name: main-review
description: Review code, diffs, branches, pull requests, docs, specifications, and plans through bounded multi-model levels and synthesize the findings.
user-invocable: true
allowed-tools:
  - task
  - bash
  - read_file
---

# Main Review

Review is a main-agent orchestration procedure. Reviewers are independent, read-only subagents that load `sub-reviewer`. The main agent owns target selection, intent, level choice, synthesis, and any follow-up.

## Target and intent

Use an explicitly named file, directory, diff, branch, pull request, or plan. If no target is named, use the uncommitted diff when one exists; otherwise ask the user for a target. Use the user's stated intent, the commit message, or the artifact goal. Ask one question only when the target or intent is genuinely unresolved.

For a pull request, fetch its branch before delegating, then review the branch comparison. Do not modify the target while reviewing.

## Review levels

- **Review (single reviewer):** the in-flight checkpoint during implementation. Dispatch on intermediate implementation steps of non-trivial work to catch issues early. Default reviewer: `generic-luna`, loading `sub-reviewer`. If `generic-luna` authored or materially contributed to any in-scope changes, use `generic-sol-medium` instead; this authorship substitution is approved policy, not a reviewer failure.
- **Deep review (parallel panel):** the finished-feature gate on the complete change set. Dispatch `generic-sol-high`, `generic-glm`, and `generic-large-4` in parallel, all loading `sub-reviewer`, then synthesize all three reports. If `generic-large-4` authored or materially contributed to any in-scope changes, `generic-sol-medium` takes the Mistral slot; this approved authorship substitution yields three reviewers across two families.

Use Deep review for plans, specifications, and designs.

Use only the listed agents. Do not call the usage tool automatically. Keep each phase bounded to one dispatch per selected reviewer. After Deep review synthesis, use bounded fix → re-review iteration: at most two refinement rounds by default, then escalate unresolved issues to the user unless the user approves a larger budget. Do not modify the target during a review phase.

If a selected reviewer fails or is unavailable, report the failure as a blocker in the synthesis with per-reviewer status. Do not silently substitute another agent for a failed reviewer. The authorship substitutions above are pre-approved; any other substitution requires user approval as a scope change.

## Dispatch

Each task string must be self-contained:

```text
task(task="Load the sub-reviewer skill. Review: <target>. Intent: <intent>. Level: <Review or Deep review>. Selected reviewers: <actual composition>. Authorship: <agents that authored or materially contributed>. Authorship substitution: <none or author → replacement>. Return the complete review report in the skill's format.", agent="<selected reviewer>")
```

When `generic-large-4` is selected as a reviewer, its dispatch must include scope, acceptance checks, known hazards, and the remaining attempt budget, per the system prompt's escalation-implementor rule.

Issue independent Deep review calls in one parallel tool block using the selected composition, including any approved authorship substitution. Synthesize all three reports, extracting consensus and notable divergent findings.

## Synthesis

Return one convergence view:

- target, intent, level, reviewer count, actual reviewers, and any authorship substitution
- consensus findings with reviewer counts and file/line locations
- divergent findings and confidence
- blocking issues
- per-reviewer status
- prioritized next steps
- whether another bounded round is warranted

A finding from two or more reviewers is consensus. Any blocker reported by a reviewer is blocking until resolved or explicitly accepted by the user. Do not claim a runtime or verification pass unless a command or behavioral test was actually observed.
