# Mistral Vibe Custom Configuration

Configuration and prompts for a role-based main agent with bounded generic subagents. The intended main default is `zai-glm-5-3` at high thinking. Two providers are active: Mistral (for `zai-glm-5-3` and Mistral Small, `openai` API style with the `mistral` backend) and Codex (local OpenAI proxy at `127.0.0.1:18080` exposing GPT-6.1-Sol, `openai-responses` API style with the `generic` backend).

The mandatory workflow is Understand, Respond, Design, Plan, Implement, Verify, Review, following the applicable task classification: trivial, implementation, review-only, design-only, plan-only, verification-only, or investigation-only. For non-trivial implementation, design acceptance gates planning; explicit plan acceptance gates implementation. Specialist edits, verification, and review are delegated to subagents.

## Roster

| Agent / tool | Model alias | Provider | Input $/M | Cached input $/M | Output $/M | Thinking | Intended use |
|---|---|---|---|---|---|---|---|
| `generic-sol-low` | `sol-low` | codex | $2.00 | $0.10 | $10.00 | low | Small tier: search, grep, explore, verify, and mechanical single-file edits. |
| `generic-sol-medium` | `sol-medium` | codex | $2.00 | $0.10 | $10.00 | medium | Default implementor and reviewer: implementation, debugging, test authoring, review, multi-step research — including novel algorithmic reasoning, difficult refactoring, and broad-impact work. |
| `generic-sol-high` | `sol-high` | codex | $2.00 | $0.10 | $10.00 | high | Advisor/planner/designer: architecture, cross-subsystem design, design/planning analysis, destructive-op second opinion. Deep reviewer. Not for implementation. |
| `generic-glm` | `zai-glm-5-3` | mistral | $1.40 | $0.14 | $4.40 | high | Cross-family second opinion. Deep reviewer. |
| `web_search` | `mistral-small-latest` | mistral | $0.15 | $0.01 | $0.60 | high | Web search tool model. |
| `generic-large-4` | `mistral-large-4` | mistral | $0.68 | $0.07 | $2.09 | high | Additional deep reviewer: third parallel reviewer alongside generic-sol-high and generic-glm in deep reviews. |

The three Sol aliases pin the same `gpt-6.1-sol` model at low, medium, and high thinking. `mistral-large-4` is listed at 50%-off public-preview prices; standard post-GA prices are $1.36 input / $4.18 output.

All generic agents use `prompts/generic-subagent.md` and are model-pinned in `agents/`. Each profile sets `bypass_tool_permissions = false` but overrides `write_file`, `edit`, `bash`, and `web_fetch` to `permission = "always"`. Profiles carry a shorter bash denylist than root and retain `.env` protections on `write_file` and `edit`; they do not simply inherit root permissions.

The task allowlist is the dispatch roster in `config.toml`. Dispatch rules are in `prompts/system-prompt-large.md` under "Delegation protocol" and "Dispatch routing" — sol-low handles search, exploration, verification, and mechanical single-file edits; sol-medium is the default implementor and reviewer for all other implementation work, however demanding, and handles multi-step research; sol-high handles architecture and design/planning analysis; glm provides cross-family second opinions.

Sol-high and glm dispatches require a stated escalation reason. Uncertainty, file count, session length, or lower-tier failure alone does not justify sol-high. Demanding implementation stays on sol-medium, not sol-high.

## Skills

Main workflow skills: `main-design`, `main-plan`, `main-review`, `main-debugging`, `main-git-workflow`, `main-lisp-spec-writer`, and `main-test-generator`.

Subagent role skills: `sub-advisor`, `sub-architecture-mapper`, `sub-cl-reviewer`, `sub-explorer`, `sub-finder`, `sub-implementor`, `sub-lisp-implementor`, `sub-prose-reviewer`, `sub-researcher`, `sub-reviewer`, `sub-summarizer`, `sub-verifier`, and `sub-worker`. `web-search` and `workspace` are shared workflow skills. `skill-creator` is vendor-provided and remains unchanged.

These 23 skills are enabled in `config.toml`; `sub-test-reviewer`, `sub-tui-implementor`, and `tui-design` are installed but dormant.

## Review tiers

Review tier composition, reviewer agents, and failure handling are owned by the `main-review` skill. In brief: Quick and Standard use Sol Medium; Deep dispatches generic-sol-high, generic-glm, and generic-large-4 in parallel, then synthesizes all three reports; Plans use the Deep procedure for plans, specifications, and designs.

A failed or unavailable listed reviewer is reported as a blocker with per-reviewer status. No unlisted substitutions without proposing a scope change to the user. Each phase allows one dispatch per listed reviewer and at most two refinement rounds unless the user approves more. The usage tool is retained for explicit user requests only; it is not called automatically.

## Workspaces

Workspace state files are optional: design and plan stay inline by default. Large, cross-cutting, or multi-session tasks use `~/.vibe/workspaces/<project>/tasks/<task>/state.md`. Project identity is recorded in the corresponding `project.toml`. Workspaces are ignored locally through `.git/info/exclude`; repository documentation is promoted explicitly rather than collected automatically.

## Layout

```
~/.vibe/
├── AGENTS.md
├── config.toml
├── agents/
├── prompts/
├── skills/
├── tools/prompts/
└── workspaces/<project>/tasks/<task>/
```
