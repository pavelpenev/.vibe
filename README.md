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
Sol and luna also serve as reviewer tiers (reviewer-sol, reviewer-luna); GLM
doubles as reviewer-glm in the standard review spread.

## Agents (14)

| Name | Purpose | Model | Safety |
|---|---|---|---|
| advisor | Independent perspective from a stronger model | gpt-5.6-sol | Safe |
| reviewer-deepseek | Independent artifact review (baseline tier) | worker | Safe |
| reviewer-luna | Independent artifact review (peer tier) | gpt-5.6-luna | Safe |
| reviewer-glm | Independent artifact review (strong tier) | orchestrator | Safe |
| reviewer-sol | Independent artifact review (strongest tier) | gpt-5.6-sol | Safe |
| explorer | Project exploration | worker | Safe |
| finder | Pattern searching | worker | Safe |
| generic-implementor | Intent-based file editing (Python/JSON/YAML/MD/TOML) | worker | Neutral |
| lisp-implementor | Intent-based Lisp editing with form extraction | worker | Neutral |
| luna-worker | Backup worker (GPT-5.6-luna) | gpt-5.6-luna | Neutral |
| researcher | Technical research | worker | Safe |
| summarizer | Document summarization | worker | Safe |
| verifier | Run project verification commands | worker | Safe |
| worker | General-purpose misc tasks | worker | Neutral |

The four reviewers share one prompt (`prompts/reviewer.md`); each is pinned to a
different model tier so the orchestrator can fan them out in parallel and
synthesize. Vibe CLI binds a subagent's model at config time, so model diversity
requires separate agents.

## Skills (10)

debugging, deep-research, git-workflow, lisp-spec-writer, research-synthesis,
review, skill-creator, subagent-creator, test-generator, web-search.

## Review Workflow

Tiered multi-model review. The `/review` skill picks a tier, fans out the
matching reviewers in parallel, and synthesizes reports into a convergence view
(consensus vs divergent findings, round-over-round convergence).

| Tier | When | Composition |
|---|---|---|
| Quick | "quick"/"fast" or trivial change | 1-2 of {reviewer-deepseek, reviewer-luna} |
| Standard (default) | no tier cue | 3x reviewer-deepseek + reviewer-luna + reviewer-glm |
| Deep | "deep"/"thorough" or architectural change | Standard + reviewer-sol |
| Plans | plan, spec, or design doc | Always reviewer-sol (typically deep-tier) |

Reviews cover code, docs, specs, and plans — not just code.

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
3. Set `active_model` to the alias for the tier (`worker` for most; `orchestrator`, `gpt-5.6-sol`, `gpt-5.6-luna` for model-diverse roles)
4. `bypass_tool_permissions = false`, `permission = "always"` on safe tools, denylist on bash
5. Model-diverse roles (e.g. reviewers) share one prompt across multiple TOMLs — duplicate the TOML, change `active_model` and `display_name` only

## Notes

- TUI model changes strip comments from config.toml; keep notes here, not in config
- Subagents without `active_model` inherit the global default — always pin to `worker`
