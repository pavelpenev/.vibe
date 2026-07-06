---
name: code-review
description: Front-end for the code-reviewer subagent. Parses the review target, gathers the change description, delegates the review, and presents the report. Triggers on code review requests for files, diffs, branches, or PRs.
user-invocable: true
allowed-tools:
  - task
  - bash
  - read_file
---

# Code Review - Front-end for Code Reviewer Subagent

**Role:** Interactive orchestrator. This skill handles the interactive parts (target selection, change description) and delegates the actual review to the non-interactive `code-reviewer` subagent, which owns all check categories, severity rules, and the report format.

## Architecture

```
User Request → code-review skill (interactive) → code-reviewer subagent (execution) → Report
```

## Triggering Conditions

- `/code-review` - review uncommitted changes
- `/code-review <file>` - review specific file(s)
- `/code-review <branch>` - review branch diff against main
- `/code-review PR <number>` - review pull request changes
- "review my changes", "review this code", "code review"

## Step 1: Determine Target

Extract the target from the request. If unspecified:
- Run `git status --short` to check for uncommitted changes
- If changes exist: the target is the uncommitted diff
- If no changes: prompt "No uncommitted changes found. Specify a file, branch, or commit to review."

For PR reviews, fetch the PR branch first (the subagent is read-only and cannot fetch):
```bash
git fetch origin pull/<number>/head:pr-<number>
```
Then delegate as a branch comparison: `Review: main...pr-<number>`.

## Step 2: Get the Change Description

The reviewer compares code against intent, so it needs a description.
- If the user provided one, use it
- If reviewing a commit, the subagent will use the commit message
- Otherwise prompt: "What should these changes accomplish? (e.g., 'add user authentication', 'fix login bug')" and wait for the response

## Step 3: Delegate

Construct a task string and delegate:

```
task(task="Review: <target>. Intent: <description>", agent="code-reviewer")
```

Target formats the subagent understands:
- `Review: file1.py, file2.py` - specific files
- `Review directory: src/` - a directory
- `Review git diff` / `Review staged changes` - working tree state
- `Review: HEAD~1` or a commit ref
- `Review: main...feature-branch` - branch comparison

## Step 4: Present Results

The subagent returns a markdown report (summary, blocking issues, warnings, info, correctness check, status). Relay it to the user unchanged, then state clearly whether blocking issues were found.

If the subagent reports "No changes found to review", relay that and ask the user for a target.

## Notes

- All review logic (check categories, severity levels, report format) lives in `~/.vibe/prompts/code-reviewer.md` - do not duplicate it here
- The subagent is read-only; this skill must not modify files either
- Other skills (e.g., auto-task self-review) may invoke this skill; the flow is identical
