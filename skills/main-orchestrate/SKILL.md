---
name: main-orchestrate
description: Execute an approved task plan through bounded work, explicit state checkpoints, verification, review, refinement, and user escalation for scope or acceptance changes.
user-invocable: true
allowed-tools:
  - task
  - read_file
  - write_file
  - edit
  - grep
  - bash
  - ask_user_question
---

# Main Orchestrate

Execute approved scope only. Read the design and plan artifacts plus applicable AGENTS.md files. The main agent owns task state, checkpoints, synthesis, and the final acceptance decision. Subagents are non-interactive: they return results and blockers, unless explicitly assigned an artifact path.

Decompose work into bounded jobs, dispatch independent jobs in parallel, checkpoint after each dependency boundary, run declared verification, and review the result before refinement. Default to at most two refinement rounds per artifact. Any scope, design, acceptance, destructive-operation, or budget change is a proposal; escalate it to the user before acting.

## Worker routing

- `generic-glm-flash` is the primary worker for implementor, explorer, and general worker roles, and the default for any unrouted routine role (finder, researcher, summarizer, verifier, and similar).
- Use `generic-luna` as the fallback when Ollama capacity is observed unavailable or exhausted; do not probe providers or call usage tools automatically.
- `generic-deepseek` is supplementary reviewer-only capacity, not a primary implementation worker.
- Use `generic-astra` for strong work and the second phase of Deep or Plans review; use `generic-glm53` as the Astra backup when Astra is unavailable.
- `generic-omen` is manual evaluation only. Never auto-dispatch it and do not create an automatic promotion or evaluation path.

Each dispatch task names exactly one `sub-*` role skill, states the target and intent, and specifies the required result format. Review tiers are owned by `main-review` and are not restated here: follow `main-review` for tier composition, reviewer agents, and backup behavior.

## State and verification

Record phase progress, evidence, caveats, and blockers in the task's `state.md`. Keep source inspection, static checks, and fresh-session behavioral tests distinct. Never claim a runtime pass without observing it. Promote repository documentation explicitly; do not collect workspace artifacts automatically. Stop and report if an approved job cannot be completed or if a new destructive action is required.
