# Mistral Vibe Custom Configuration

GLM-5.2 main agent + multi-model generic subagents for Mistral Vibe CLI.

## Architecture

```
Main Agent (GLM-5.2)
  Orchestrates, keeps context lean, delegates token-heavy work
  Auto-approve (bypass=true), system-prompt-large.md
    |
    v
Generic Subagents (one per model)
  Load role skills to specialize (implementor, reviewer, advisor, etc.)
  bypass=false, permission=always on tools, bash denylist
```

## Models

| Alias | Model | Provider | Role | Compaction |
|---|---|---|---|---|
| glm-5-2 | glm-5-2 | mistral | main | 500k |
| deepseek-v4-flash | deepseek-v4-flash | opencode | generic subagent | 800k |
| gpt-5.6-sol | gpt-5.6-sol | codex | generic subagent | 500k |
| gpt-5.6-luna | gpt-5.6-luna | codex | generic subagent | 200k |
| ox-alpha-free | ox-alpha-free | opencode | generic subagent | 500k |

mistral-vibe-cli-latest (vision) and mistral-small-latest remain in config
without aliases for vision tasks via `/model`. Generic subagents run on each
model; the main agent picks the model by cost/tier and the role skill by
task. Sol serves as the advisor/deep-review tier; luna is the cheap default;
GLM doubles as a strong-tier reviewer in the standard review spread.

## Agents (5)

One generic subagent per model. Each loads a role skill (implementor,
lisp-implementor, reviewer, advisor, explorer, finder, researcher, summarizer,
verifier, worker) to specialize. Roles live in `skills/`, not in per-role
agent TOMLs.

| Name | Model | Safety |
|---|---|---|
| generic-sol | gpt-5.6-sol | Neutral |
| generic-luna | gpt-5.6-luna | Neutral |
| generic-glm | glm-5-2 | Neutral |
| generic-deepseek | deepseek-v4-flash | Neutral |
| generic-ox-alpha-free | ox-alpha-free | Neutral |

All share one prompt (`prompts/generic-subagent.md`); each is pinned to a
different model. The main agent picks the model by cost/tier and the skill by
role: `task(task="Load the <skill> skill and <intent>", agent="generic-<model>")`.

### Model dispatch

Use the cheapest model capable of the task. Defaults:

| Role | Default | Escalate to | When |
|------|---------|-------------|------|
| implementor / lisp-implementor | generic-luna | generic-sol | Multi-file architectural changes |
| reviewer | generic-luna | generic-glm / generic-sol | Per review tier |
| advisor | generic-sol | — | Always sol |
| explorer / verifier | generic-luna | — | Mechanical tasks |
| finder / summarizer / worker | generic-deepseek | generic-luna | Cheapest for bulk work |
| researcher | generic-luna | — | Cost sweet spot |
| (any, parallel) | generic-ox-alpha-free | — | Free extra capacity |

Never use generic-sol for mechanical work — it's 25x the cost of luna with no
quality benefit for simple edits, searches, or verification.

## Skills (17)

debugging, git-workflow, lisp-spec-writer, review, skill-creator,
test-generator, web-search, implementor, lisp-implementor, reviewer, advisor,
explorer, finder, researcher, summarizer, verifier, worker.

The first 7 are user-invocable workflow skills. The last 10 are role skills
loaded by generic subagents (not user-invocable).

## Review Workflow

Tiered multi-model review. The `/review` skill picks a tier, fans out the
matching reviewers in parallel, and synthesizes reports into a convergence view
(consensus vs divergent findings, round-over-round convergence).

| Tier | When | Composition |
|---|---|---|
| Quick | "quick"/"fast" or trivial change | 1-2 of {generic-luna, generic-deepseek} with `reviewer` skill |
| Standard (default) | no tier cue | 3x generic-luna + generic-deepseek + generic-ox-alpha-free, all with `reviewer` skill |
| Deep | "deep"/"thorough" or architectural change | Standard + generic-glm + generic-sol with `reviewer` skill |
| Plans | plan, spec, or design doc | Always generic-sol with `reviewer` skill (typically deep-tier) |

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

1. Copy `agents/generic-luna.toml` to `agents/generic-<suffix>.toml` and change `display_name`, `description`, and `active_model`
2. Add the new agent name to `[tools.task]` allowlist in config.toml
3. To add a new role, create `skills/<role>/SKILL.md` with frontmatter (`user-invocable: false`, `allowed-tools`) and add the skill name to `enabled_skills` in config.toml
4. `bypass_tool_permissions = false`, `permission = "always"` on tools, denylist on bash
5. All generic subagents share `prompts/generic-subagent.md` — no per-role prompts needed

## Notes

- TUI model changes strip comments from config.toml; keep notes here, not in config
- Generic subagents load role skills via the `skill` tool — roles are defined in `skills/`, not duplicated across agent TOMLs
