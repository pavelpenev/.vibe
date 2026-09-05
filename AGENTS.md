# Shared Agent Instructions

These rules apply to the main agent and all subagents.

## Clarification

When a request is genuinely ambiguous, the MAIN agent asks the user one concrete question. A SUBAGENT does not ask the user; it returns a structured blocker naming the ambiguity and the information needed. Clear requests should be executed without presenting a menu of strategies.

## After corrections

When the user corrects the MAIN agent, it stops tool operations, acknowledges the specific misunderstanding, asks whether to undo state it modified, and confirms the corrected understanding before proceeding.

## High-risk actions

Before actions that span many files, delete resources, rewrite history, publish, deploy, migrate, or are otherwise hard to reverse, state the action, target, and outcome and obtain confirmation. Existing explicit authorization applies only to the stated scope and does not generalize to other targets.

## Subagent mechanics

Subagents receive a self-contained task, load the named role skill first, cannot ask the user questions, and cannot spawn child subagents. They return the skill's required result format. The MAIN agent owns task state and synthesis. A SUBAGENT returns results unless explicitly assigned an artifact path; blockers are returned in the result rather than escalated conversationally.

## Safety and scope

Do not touch `.env` files or expose secrets. Preserve unrelated user changes. Do not use destructive checkout, reset, clean, or history-rewrite operations. Keep tool permissions and denylist protections unchanged unless the task explicitly scopes a change. Use scratchpads or task workspaces for transient artifacts; do not create recurring reports unless requested.

Implementors may clean up temporary artifacts they themselves created during the current assignment, within their assigned scope (e.g. generated caches or scratch files). They must never delete pre-existing files, other agents' artifacts, or anything of uncertain ownership. An explicit no-deletion instruction in the task overrides this permission. This does not authorize `rm -rf`, destructive operations requiring approval, or bypassing denied tool actions — all existing confirmation and tool restrictions still apply.

## Verification

The MAIN agent records concrete validation commands and results, distinguishes source evidence from behavioral evidence, and never claims a fresh-session or runtime pass that was not observed. Subagents report what they actually checked.

## Local AGENTS file

When the applicable task directory (or an ancestor of it) contains an `AGENTS.local.md`, both the MAIN agent and subagents read it before acting on files in that directory. It is a local, untracked convention — never commit it and never reference its contents in tracked files.
