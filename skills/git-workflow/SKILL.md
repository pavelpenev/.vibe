---
name: git-workflow
description: "Generic git workflow assistance: gather context, generate conventional commit messages, create branches, and prepare pushes. History-rewriting and destructive operations are handoff-only. Repo-specific workflow rules belong in the project's AGENTS.md — follow those when present."
user-invocable: true
allowed-tools:
  - bash
  - read_file
---

# Git Workflow (generic)

This skill covers the generic git basics. **Repo-specific workflow rules — branch naming scheme, commit conventions, PR process, protected branches — live in the project's AGENTS.md.** Read the applicable AGENTS.md files first and follow them over anything here.

## Core principles

1. **Safety first.** Never run history-rewriting or destructive operations yourself, even with confirmation. Handoff-only (prepare the command, the user runs it):
   - `git push --force` / `--force-with-lease`
   - `git reset --soft/--mixed/--hard`
   - `git rebase`, `git commit --amend`, squash merges
   - `git clean`, discarding untracked files, `git checkout <file>` on files with unsaved work
2. **Conventional commits.** `<type>(<scope>): <subject>` — types: feat, fix, docs, style, refactor, test, chore. Keep subjects imperative, under 72 chars.
3. **Branch naming.** Short, lowercase, hyphenated: `feat/short-description`, `fix/issue-id-short-description` — unless AGENTS.md says otherwise.

## Basic flow

1. **Gather context:** `git status`, `git diff` (staged/unstaged), `git log --oneline -10`, branch tracking info.
2. **Commit:** stage the intended files explicitly, generate the message from the diff (never commit secrets or `.env` files), show the message to the user, commit on confirmation.
3. **Branch:** create from the up-to-date base branch, name per the convention above.
4. **Push:** plain `git push -u origin <branch>`; if the remote rejects, report and hand off — never force.
5. **Report:** one short summary of what was done, the branch, and the commit hashes.

## Conflict resolution

When a merge/rebase conflict appears (user-driven): identify conflicted files with `git status`, explain each hunk, propose a resolution strategy (ours/theirs/manual edit), and after resolution verify with a build/test run before committing the resolution.

## Red flags

- Uncommitted changes unrelated to the task: leave them alone, mention them.
- Protected branch or no upstream: stop and report.
- Anything requiring force-push or history rewrite: hand off with the exact command and the blast radius in one line.
