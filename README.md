# Mistral Vibe Custom Configuration

Configuration and prompts for a role-based main agent with bounded generic subagents. The intended main default is GLM-5.2 on Mistral; `config.toml` keeps `active_model = "glm-5-2"`. Two providers are active: Mistral (for GLM-5.2 and Mistral Small) and Codex (local OpenAI proxy at `127.0.0.1:18080` exposing GPT-6-Astra, GPT-5.6-Luna, GPT-5.6-Sol, and GPT-5.6-Terra).

## Roster

| Agent | Model | Provider | Thinking | Intended use |
|---|---|---|---|---|
| `generic-astra` | gpt-6-astra | codex | medium | Architecture, deep review, design/planning analysis. Not for implementation. |
| `generic-sol` | gpt-5.6-sol | codex | low | Demanding implementation: novel algorithmic reasoning, difficult refactoring, broad impact |
| `generic-terra` | gpt-5.6-terra | codex | medium | Implementation, debugging, test authoring. Default implementor and reviewer. |
| `generic-luna` | gpt-5.6-luna | codex | medium | Search, grep, explore, verify, mechanical single-file edits |
| `generic-glm` | glm-5-2 | mistral | high | Cross-family second opinion (rare) |

All generic agents use `prompts/generic-subagent.md`, are model-pinned in `agents/`, and retain the configured tool permissions, denylists, and sensitive-pattern protections. The task allowlist is the dispatch roster in `config.toml`. Dispatch rules are in `prompts/system-prompt-large.md` under "Delegation protocol" and "Dispatch routing" — match agent to task complexity, from luna for search and verification up to terra for implementation, sol for demanding novel implementation, and astra for architecture, deep review, and design/planning.

## Skills

Main workflow skills: `main-design`, `main-plan`, `main-review`, `main-debugging`, `main-git-workflow`, `main-lisp-spec-writer`, and `main-test-generator`.

Subagent role skills: `sub-advisor`, `sub-architecture-mapper`, `sub-cl-reviewer`, `sub-explorer`, `sub-finder`, `sub-implementor`, `sub-lisp-implementor`, `sub-prose-reviewer`, `sub-researcher`, `sub-reviewer`, `sub-summarizer`, `sub-test-reviewer`, `sub-verifier`, and `sub-worker`. `web-search` and `workspace` are shared workflow skills. `skill-creator` is vendor-provided and remains unchanged.

## Review tiers

Review tier composition, reviewer agents, and backup behavior are owned by the `main-review` skill. In brief: Quick is Terra only; Standard defaults to Terra, optionally with Luna for a second perspective; Deep runs Standard first, then Astra for architecture, security, or cross-subsystem findings only; Plans use the Deep procedure.

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
