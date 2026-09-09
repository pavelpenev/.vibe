# Mistral Vibe Custom Configuration

Configuration and prompts for a role-based main agent with bounded generic subagents. The intended main default is GLM-5.2 on Mistral; `config.toml` keeps `active_model = "glm-5-2"`. Two providers are active: Mistral (for GLM-5.2 and Mistral Small) and Codex (local OpenAI proxy at `127.0.0.1:18080` exposing GPT-6-Astra, GPT-5.6-Luna, GPT-5.6-Sol, and GPT-5.6-Terra).

## Roster

| Agent | Model | Provider | Thinking | Intended use |
|---|---|---|---|---|
| `generic-astra` | gpt-6-astra | codex | medium | Deep review, architecture, most complex implementation, and design/planning support |
| `generic-sol` | gpt-5.6-sol | codex | low | Demanding implementation: complex logic, refactoring, broad impact |
| `generic-terra` | gpt-5.6-terra | codex | medium | Implementation: multi-file edits, feature work |
| `generic-luna` | gpt-5.6-luna | codex | medium | Trivial tasks: search, grep, verification, single-file edits |
| `generic-glm` | glm-5-2 | mistral | high | Cross-family subagent |

All generic agents use `prompts/generic-subagent.md`, are model-pinned in `agents/`, and retain the configured tool permissions, denylists, and sensitive-pattern protections. The task allowlist is the dispatch roster in `config.toml`. Dispatch rules are in `prompts/system-prompt-large.md` under "Model dispatch" — match agent to task complexity, from luna for trivial work up to astra for deep review, architecture, and the most complex implementation.

## Skills

Main workflow skills: `main-design`, `main-plan`, `main-orchestrate`, `main-review`, `main-debugging`, `main-git-workflow`, `main-lisp-spec-writer`, and `main-test-generator`.

Subagent role skills: `sub-advisor`, `sub-architecture-mapper`, `sub-explorer`, `sub-finder`, `sub-implementor`, `sub-lisp-implementor`, `sub-researcher`, `sub-reviewer`, `sub-summarizer`, `sub-verifier`, and `sub-worker`. `web-search` is shared. `skill-creator` is vendor-provided and remains unchanged.

## Review tiers

Review tier composition, reviewer agents, and backup behavior are owned by the `main-review` skill. In brief: Quick is Terra only; Standard defaults to Terra, optionally with Luna for a second perspective; Deep runs Standard first, then Astra; Plans use the Deep procedure.

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
