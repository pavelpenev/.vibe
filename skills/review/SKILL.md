---
name: review
description: Front-end for the tiered reviewer subagents. Parses the review target, gathers the change description, picks a tier, fans out multiple model-tiered reviewers in parallel, and synthesizes their reports into a single convergence view. Triggers on review requests for code, diffs, branches, PRs, docs, specs, or plans.
user-invocable: true
allowed-tools:
  - task
  - bash
  - read_file
---

# Review — Tiered Multi-Model Review Front-end

**Role:** Interactive orchestrator. This skill handles the interactive parts (target selection, change description, tier selection) and delegates the actual reviews to the non-interactive reviewer subagents, which own all check categories, severity rules, and the report format. Because Vibe CLI binds a subagent's model at config time, each model tier has its own reviewer subagent; this skill fans them out in parallel and synthesizes the results.

## Architecture

```
User Request → review skill (interactive) → tiered reviewer subagents (parallel) → synthesis
```

## Reviewer Subagents

All share one prompt (`~/.vibe/prompts/reviewer.md`) but run on different models:

| Agent | Model | Tier |
|-------|-------|------|
| `reviewer-deepseek` | deepseek-v4-flash (worker) | baseline |
| `reviewer-luna` | gpt-5.6-luna | baseline |
| `reviewer-glm` | glm-5.2 (orchestrator) | strong |
| `reviewer-sol` | gpt-5.6-sol | strongest |
| `reviewer-ox-alpha-free` | Ox Alpha Free (ox-alpha-free) | — |

## Triggering Conditions

- `/review` — review uncommitted changes
- `/review <file>` — review specific file(s)
- `/review <branch>` — review branch diff against main
- `/review PR <number>` — review pull request changes
- `/review plan <path>` or `/review <plan-or-spec-path>` — review a plan, spec, or doc
- "review my changes", "review this code", "review this plan", "give this spec a review"

## Step 1: Determine Target

Extract the target from the request. If unspecified:
- Run `git status --short` to check for uncommitted changes
- If changes exist: the target is the uncommitted diff
- If no changes: prompt "No uncommitted changes found. Specify a file, branch, commit, or plan to review."

For PR reviews, fetch the PR branch first (reviewers are read-only and cannot fetch):
```bash
git fetch origin pull/<number>/head:pr-<number>
```
Then delegate as a branch comparison: `Review: main...pr-<number>`.

For plans/specs/docs: the target is a file path (or directory). These are reviewed as artifacts, not git diffs.

## Step 2: Get the Change Description

Reviewers compare against intent, so they need a description.
- If the user provided one, use it
- If reviewing a commit, the reviewer will use the commit message
- Otherwise prompt: "What should these changes accomplish? (e.g., 'add user authentication', 'fix login bug')" and wait for the response

For plans/specs: the intent is the plan's stated goal. If the document has a clear goal section, use it; otherwise prompt briefly.

## Step 3: Run Verification (code only)

Before delegating a code review, run the project's verification commands:

```python
task(task="Run verification on the changed files", agent="verifier")
```

Capture the output. If the verifier returns "No verification commands found", proceed without results. Skip this step for non-code artifacts.

## Step 4: Pick a Tier

| Tier | When | Composition |
|------|------|-------------|
| **Quick** | User says "quick"/"fast", or the change is trivial (one-liner, rename) | 1–2 of {reviewer-luna, reviewer-deepseek} |
| **Standard** (default) | User doesn't name a tier, or says "review"/"standard" | 3× reviewer-luna + reviewer-glm + reviewer-deepseek + reviewer-ox-alpha-free |
| **Deep** | User says "deep"/"thorough", or architectural change | Standard + reviewer-sol |
| **Plans** | Target is a plan, spec, or design doc | Always include reviewer-sol (typically a deep-tier spread) |

Inference rules:
- The word "quick"/"fast" → quick tier
- The word "deep"/"thorough"/"comprehensive" → deep tier
- A plan/spec/design doc path → plans tier (sol mandatory)
- Architectural or multi-file change with no tier cue → deep tier
- Everything else → standard tier

When unsure, default to standard.

## Step 5: Fan Out (parallel)

Launch all reviewers for the tier **in parallel** — issue every `task()` call in a single response block. Each reviewer gets the same task string (target + intent + verification results), so their reports are directly comparable.

Construct the shared task string, prepending verification results if code:

```
Verification results captured:
{verifier_output}

Review: <target>. Intent: <description>
```

Delegation (standard tier example — issue all four in one block):
```python
task(task="{task_string}", agent="reviewer-luna")
task(task="{task_string}", agent="reviewer-luna")
task(task="{task_string}", agent="reviewer-luna")
task(task="{task_string}", agent="reviewer-glm")
```

Target formats the reviewers understand:
- `Review: file1.py, file2.py` — specific files
- `Review directory: src/` — a directory
- `Review git diff` / `Review staged changes` — working tree state
- `Review: HEAD~1` or a commit ref
- `Review: main...feature-branch` — branch comparison
- `Review: path/to/plan.md` — a plan, spec, or doc

## Step 6: Synthesize

You now have N independent markdown reports. Synthesize them into a single view — do not just concatenate. The value of multi-model review is finding different things and converging; surface that.

Structure the synthesis:

```markdown
## Review Synthesis

**Target:** {files/diff reviewed}
**Intent:** {description used}
**Tier:** {quick/standard/deep/plans} — {N} reviewers
**Round:** {this is round 1, or "round 2+ since last review"}

### Consensus Findings (flagged by multiple reviewers)
{each finding, with count: "3/5 reviewers flagged X at file:line" — these are high-confidence}

### Divergent Findings (reviewers disagreed)
{findings only one or a few reviewers raised — note which reviewer; lower confidence, may warrant a follow-up}

### Blocking Issues
{aggregated blocking findings across all reviewers; empty = none}

### Round-over-Round Convergence
{if round 2+: which round-1 findings were addressed, which remain, what's new}
{if round 1: "Baseline established — address consensus findings, then run another round."}

### Per-Reviewer Status
{one line per reviewer: agent — status — # warnings — # blocking}

### Next Steps
{prioritized fix list before merging, drawn from consensus + blocking}
```

**Synthesis rules:**
- A finding flagged by ≥2 reviewers is consensus — higher confidence, fix first.
- A finding flagged by 1 reviewer is divergent — note it, but it may be a false positive.
- Any reviewer returning FAILED (blocking) → the synthesis flags blocking issues.
- Across rounds, convergence = fewer divergent findings and resolution of prior consensus items. When reviewers converge (all PASS or all flag the same small set), the artifact is review-clean.

If a reviewer reports "No changes found to review", note it in Per-Reviewer Status and proceed with the others.

## Notes

- All review logic (check categories, severity levels, report format) lives in `~/.vibe/prompts/reviewer.md` — do not duplicate it here.
- Reviewers are read-only; this skill must not modify files either.
- Other skills may invoke this skill; the flow is identical.
- For iterative review rounds, keep the tier and target the same across rounds so reports are comparable; the synthesis tracks convergence.
