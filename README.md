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
| gpt-5.6-sol | gpt-5.6-sol | codex | advisor | 500k |
| gpt-5.6-luna | gpt-5.6-luna | codex | backup worker | 200k |

mistral-vibe-cli-latest (vision) and mistral-small-latest remain in config
without aliases for vision tasks via `/model`. Advisor runs on GPT-5.6-sol for
genuine model uplift. Luna-worker is a backup when deepseek is unavailable.

## Agents (12)

| Name | Purpose | Model | Safety |
|---|---|---|---|
| advisor | Independent perspective from a stronger model | gpt-5.6-sol | Safe |
| code-reviewer | Code quality review | worker | Safe |
| explorer | Project exploration | worker | Safe |
| finder | Pattern searching | worker | Safe |
| generic-implementor | Intent-based file editing (Python/JSON/YAML/MD/TOML) | worker | Neutral |
| lisp-implementor | Intent-based Lisp editing with form extraction | worker | Neutral |
| luna-worker | Backup worker (GPT-5.6-luna) | gpt-5.6-luna | Neutral |
| researcher | Technical research | worker | Safe |
| summarizer | Document summarization | worker | Safe |
| verifier | Run project verification commands | worker | Safe |
| worker | General-purpose misc tasks | worker | Neutral |

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
