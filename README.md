# Mistral Vibe Custom Configuration

Configuration and prompts for a role-based main agent with bounded generic subagents. The intended main default is GLM-5.2 on Mistral; `config.toml` intentionally keeps the current `active_model = "gpt-6-astra"` until the user switches it.

## Roster

| Agent | Model | Intended use |
|---|---|---|
| `generic-astra` | gpt-6-astra | Strong work and Deep/Plans review phase two |
| `generic-glm53` | glm-5.3 | Astra backup and strong cross-family review |
| `generic-glm-flash` | glm-5.3-flash | Primary implementor, explorer, and general worker |
| `generic-luna` | gpt-5.6-luna | Reviewer and fallback worker when Ollama is exhausted |
| `generic-deepseek` | deepseek-v4-flash | Supplementary reviewer |
| `generic-glm` | glm-5-2 | Available strong subagent |
| `generic-omen` | omen-alpha | Manual evaluation only; never auto-dispatched or promoted automatically |

All generic agents use `prompts/generic-subagent.md`, are model-pinned in `agents/`, and retain the configured tool permissions, denylists, and sensitive-pattern protections. The task allowlist is the dispatch roster in `config.toml`.

## Skills

Main workflow skills: `main-design`, `main-plan`, `main-orchestrate`, `main-review`, `main-debugging`, `main-git-workflow`, `main-lisp-spec-writer`, and `main-test-generator`.

Subagent role skills: `sub-advisor`, `sub-architecture-mapper`, `sub-explorer`, `sub-finder`, `sub-implementor`, `sub-lisp-implementor`, `sub-researcher`, `sub-reviewer`, `sub-summarizer`, `sub-verifier`, and `sub-worker`. `web-search` is shared. `skill-creator` is vendor-provided and remains unchanged.

## Review tiers

Review tier composition, reviewer agents, and backup behavior are owned by the `main-review` skill and are not restated here. In brief: Quick is Flash only; Standard runs Luna, Flash, and Deepseek independently in parallel; Deep runs Standard first, then Astra with glm53 as backup; Plans use the Deep procedure.

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
