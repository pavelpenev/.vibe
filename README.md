# Mistral Vibe Custom Configuration

GLM-orchestrator + flash-worker architecture for Mistral Vibe CLI.

## Architecture

```
Main Agent (GLM-5.2 "orchestrator")
  Orchestrates, keeps context lean, delegates token-heavy work
  Auto-approve (bypass=true), system-prompt-large.md
    |
    v
Subagents (deepseek-v4-flash "worker")
  bypass=false, permission=always on safe tools
  bash denylist (dangerous commands silently skipped)
```

## Models

| Alias | Model | Provider | Role | Compaction |
|---|---|---|---|---|
| orchestrator | glm-5-2 | mistral | main | 500k |
| worker | deepseek-v4-flash | opencode | all subagents | 800k |

mistral-vibe-cli-latest (vision) and mistral-small-latest remain in config
without aliases for vision tasks via `/model`. Advisor runs on worker for an
independent peer perspective — same ability tier, different model.

## Agents (10)

| Name | Purpose | Safety |
|---|---|---|
| advisor | Independent peer perspective on hard decisions | Safe |
| code-reviewer | Code quality review | Safe |
| explorer | Project exploration | Safe |
| finder | Pattern searching | Safe |
| generic-implementor | Intent-based file editing (Python/JSON/YAML/MD/TOML) | Neutral |
| lisp-implementor | Intent-based Lisp editing with form extraction | Neutral |
| researcher | Technical research | Safe |
| summarizer | Document summarization | Safe |
| verifier | Run project verification commands | Safe |
| worker | General-purpose misc tasks | Neutral |

## Skills (10)

code-review, debugging, deep-research, git-workflow, lisp-spec-writer,
research-synthesis, skill-creator, subagent-creator, test-generator, web-search.

## Compaction

- Prompt: `compact-v4.md` (`<summary>` tags, qualitative compression)
- Threshold: 500k tokens
- Compaction model: inherits active model

## Directory Structure

```
~/.vibe/
├── AGENTS.md                # Cross-cutting instructions (all agents)
├── config.toml              # Vibe CLI configuration
├── agents/                  # Subagent TOML configurations
├── prompts/                 # System prompts + compaction
├── scripts/                 # Helper scripts (extract_lisp_forms.py)
├── skills/                  # Skill definitions
├── templates/               # Lisp test templates
└── tools/prompts/           # Custom tool description overrides
```

## Creating New Subagents

1. Create TOML in `agents/<name>.toml` and prompt in `prompts/<name>.md`
2. Add to `[tools.task]` allowlist in config.toml
3. Set `active_model = "worker"`, `bypass_tool_permissions = false`
4. `permission = "always"` on safe tools, denylist on bash

## Notes

- TUI model changes strip comments from config.toml; keep notes here, not in config
- Subagents without `active_model` inherit the global default — always pin to `worker`
