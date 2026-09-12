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

Task workspaces live at `~/.vibe/workspaces/<project>/tasks/<task>/state.md`. Project identity is in `~/.vibe/workspaces/<project>/project.toml`.

## When to use workspace state

- **Inline by default**: most tasks keep design and plan inline in the conversation. No workspace file is needed.
- **Large or cross-cutting tasks**: create a workspace state file to track progress across phases, sessions, and compaction.
- **Multi-session tasks**: if work may span compaction or multiple sessions, create a state file early so the compaction summary can reference it.

## Creating a workspace

1. Determine the project name from the repository directory (e.g., `/home/pav/myproject` → `myproject`).
2. Create or reuse `~/.vibe/workspaces/<project>/project.toml` with `name`, `repository_root`, `workspace_root`, and `tasks_root`.
3. Create `~/.vibe/workspaces/<project>/tasks/<task-name>/state.md`. Use a short, descriptive task name.

Never guess the latest task by timestamps or directory ordering. If the user names a task, use that name. If not, ask or infer from context.

## state.md content

Record: task name, scope, current workflow phase, phase progress, evidence, caveats, blockers, and next steps. Update it at phase transitions during execution.

## Rules

- Keep task records, research notes, snapshots, review inputs, and temporary artifacts outside the repository unless the user explicitly promotes an artifact.
- Do not create numbered review dumps, recurring `verify.md` or `final-report.md` files.
- Promote a workspace artifact into repository documentation only by an explicit user decision or an approved plan step.
- Before snapshots, establish ignore rules for workspace paths and exclude secrets and logs.
- Preserve unrelated files and use non-destructive inverse edits for rollback.
