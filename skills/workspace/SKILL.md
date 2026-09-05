---
name: workspace
description: Maintain stable project and task workspaces outside repositories, with explicit task identity, state handoffs, worktrees, and artifact promotion.
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
---

# Workspace

Use `~/.vibe/workspaces/<project>/project.toml` for stable project identity and `tasks/<task>/state.md` for the single running task record. Keep task records, research notes, snapshots, review inputs, and temporary artifacts outside the repository unless the user explicitly promotes an artifact.

Create or reuse a named task directory; never guess the latest task by timestamps or directory ordering. Record the repository root, project identity, task name, scope, phase progress, evidence, caveats, blockers, and next steps in `state.md`.

Use stable worktree paths when a worktree is required. Associate every artifact with its explicit project and task path. Do not create numbered review dumps, recurring `verify.md` or `final-report.md` files, or cleanup existing clutter as part of workspace maintenance.

Promote a workspace artifact into repository documentation only by an explicit user decision or an approved plan step. Before snapshots, establish ignore rules for workspace paths and exclude secrets and logs. Preserve unrelated files and use non-destructive inverse edits for rollback.
