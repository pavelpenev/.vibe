# Mistral Vibe Custom Configuration

GLM-orchestrator + luna-worker architecture for Mistral Vibe CLI.

## Architecture

```
Main Agent (GLM-5.2 "orchestrator")
  Orchestrates, keeps context lean, delegates token-heavy work
  Auto-approve (bypass=true), system-prompt-large.md
    |
    v
Subagents (gpt-5.6-luna)
  bypass=false, permission=always on safe tools
  bash denylist (dangerous commands silently skipped)
```

## Models

| Alias | Model | Provider | Role | Compaction |
|---|---|---|---|---|
| orchestrator | glm-5-2 | mistral | main | 500k |
| worker | deepseek-v4-flash | opencode | unused (deepseek) | 800k |
| gpt-5.6-sol | gpt-5.6-sol | codex | advisor | 500k |
| gpt-5.6-luna | gpt-5.6-luna | codex | all subagents | 200k |

mistral-vibe-cli-latest (vision) and mistral-small-latest remain in config
without aliases for vision tasks via `/model`. Advisor runs on GPT-5.6-sol for
genuine model uplift. All non-advisor subagents run on GPT-5.6-luna, the default
cheap model. Sol and luna also serve as reviewer tiers (reviewer-sol,
reviewer-luna); GLM doubles as reviewer-glm in the standard review spread.

## Agents (20)

| Name | Purpose | Model | Safety |
|---|---|---|---|
| advisor | Independent perspective from a stronger model | gpt-5.6-sol | Safe |
| reviewer-luna | Independent artifact review (baseline tier) | gpt-5.6-luna | Safe |
| reviewer-glm | Independent artifact review (strong tier) | orchestrator | Safe |
| reviewer-sol | Independent artifact review (strongest tier) | gpt-5.6-sol | Safe |
| reviewer-ox-alpha-free | Independent artifact review | ox-alpha-free | Safe |
| reviewer-deepseek | Independent artifact review | worker | Safe |
| explorer | Project exploration | gpt-5.6-luna | Safe |
| finder | Pattern searching | gpt-5.6-luna | Safe |
| generic-implementor | Intent-based file editing (Python/JSON/YAML/MD/TOML) | gpt-5.6-luna | Neutral |
| generic-implementor-ox-alpha-free | Generic implementor (Ox Alpha Free) | ox-alpha-free | Neutral |
| generic-implementor-deepseek | Generic implementor (deepseek-v4-flash) | worker | Neutral |
| generic-implementor-glm | Generic implementor (glm-5-2) | orchestrator | Neutral |
| lisp-implementor | Intent-based Lisp editing with form extraction | gpt-5.6-luna | Neutral |
| lisp-implementor-ox-alpha-free | Lisp implementor (Ox Alpha Free) | ox-alpha-free | Neutral |
| lisp-implementor-deepseek | Lisp implementor (deepseek-v4-flash) | worker | Neutral |
| lisp-implementor-glm | Lisp implementor (glm-5-2) | orchestrator | Neutral |
| researcher | Technical research | gpt-5.6-luna | Safe |
| summarizer | Document summarization | gpt-5.6-luna | Safe |
| verifier | Run project verification commands | gpt-5.6-luna | Safe |
| worker | General-purpose misc tasks | gpt-5.6-luna | Neutral |

The three reviewers share one prompt (`prompts/reviewer.md`); each is pinned to a
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
| Quick | "quick"/"fast" or trivial change | 1-2 of {reviewer-luna, reviewer-deepseek} |
| Standard (default) | no tier cue | 3x reviewer-luna + reviewer-glm + reviewer-deepseek + reviewer-ox-alpha-free |
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
3. Set `active_model` to the alias for the tier (`gpt-5.6-luna` for most; `orchestrator`, `gpt-5.6-sol` for model-diverse roles)
4. `bypass_tool_permissions = false`, `permission = "always"` on safe tools, denylist on bash
5. Model-diverse roles (e.g. reviewers) share one prompt across multiple TOMLs — duplicate the TOML, change `active_model` and `display_name` only

## Notes

- TUI model changes strip comments from config.toml; keep notes here, not in config
- Subagents without `active_model` inherit the global default — always pin to `gpt-5.6-luna`
