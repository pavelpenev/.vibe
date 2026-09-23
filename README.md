# Mistral Vibe Custom Configuration

Configuration and prompts for a role-based main agent with bounded generic subagents. The intended main default is `zai-glm-5-3` at high thinking. Two providers are active: Mistral (for `zai-glm-5-3` and Mistral Small) and Codex (local OpenAI proxy at `127.0.0.1:18080` exposing GPT-6-Astra, GPT-6-Luna, and GPT-6-Sol).

## Roster

| Agent | Model | Provider | Output $/M | Thinking | Intended use |
|---|---|---|---|---|---|
| `generic-luna` | gpt-6-luna | codex | $0.50 | max | Default implementor and reviewer. Also search, grep, explore, verify, and mechanical single-file edits. |
| `generic-sol` | gpt-6-sol | codex | $10.00 | medium (high for the hardest tasks) | Escalation implementation: novel algorithmic reasoning, difficult refactoring, broad-impact work |
| `generic-astra` | gpt-6-astra | codex | $50.00 | low | Advisor/planner/designer: architecture, cross-subsystem design, design/planning analysis, destructive-op second opinion. Deep reviewer. Not for implementation. |
| `generic-glm` | zai-glm-5-3 | mistral | $4.40 | high | Cross-family second opinion. Deep reviewer. |

All generic agents use `prompts/generic-subagent.md`, are model-pinned in `agents/`, and retain the configured tool permissions, denylists, and sensitive-pattern protections. The task allowlist is the dispatch roster in `config.toml`. Dispatch rules are in `prompts/system-prompt-large.md` under "Delegation protocol" and "Dispatch routing" — luna is the default for implementation, review, search, and verification; sol is the escalation implementor; astra handles architecture and design/planning analysis; glm provides cross-family second opinions.

## Skills

Main workflow skills: `main-design`, `main-plan`, `main-review`, `main-debugging`, `main-git-workflow`, `main-lisp-spec-writer`, and `main-test-generator`.

Subagent role skills: `sub-advisor`, `sub-architecture-mapper`, `sub-cl-reviewer`, `sub-explorer`, `sub-finder`, `sub-implementor`, `sub-lisp-implementor`, `sub-prose-reviewer`, `sub-researcher`, `sub-reviewer`, `sub-summarizer`, `sub-test-reviewer`, `sub-verifier`, and `sub-worker`. `web-search` and `workspace` are shared workflow skills. `skill-creator` is vendor-provided and remains unchanged.

## Review tiers

Review tier composition, reviewer agents, and backup behavior are owned by the `main-review` skill. In brief: Quick and Standard use Luna; Deep dispatches Astra at low thinking and GLM at high thinking in parallel, then synthesizes both reports; Plans use the Deep procedure.

The review and orchestration skills keep rounds bounded. The usage tool is retained for explicit user requests only; it is not called automatically.

## Workspaces

Task records live outside repositories at `~/.vibe/workspaces/<project>/tasks/<task>/state.md`. Project identity is recorded in the corresponding `project.toml`. Workspaces are ignored locally through `.git/info/exclude`; repository documentation is promoted explicitly rather than collected automatically.

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
