---
name: design
description: "Run the design phase: scope and brainstorm with the user, delegate research to explorer/researcher subagents, orchestrate the designer subagent, and manage the design review loop until the user accepts the design."
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - agents_spawn
  - skill
---

# Design

Design is an orchestrator procedure covering the system prompt's research and design phases: scope and brainstorm with the user, consolidate research, propose a design via the `designer` subagent, and iterate review/fix cycles until the user accepts. The orchestrator owns the final design.

## Phase 1 — Scope, brainstorm, research

1. **Scope with the user.** Establish the goal, constraints, and preserved behavior in conversation. Ask only what is genuinely unresolved; do not use `ask_user_question` for design topics.
2. **Delegate research.** Spawn `explorer` (codebase mapping: interfaces, contracts, existing implementations) and `researcher` (external knowledge, web) in parallel, each with a self-contained prompt. For wide scopes, spawn `advisor` for a second opinion on the framing.
3. **Consolidate.** Merge the findings into a short research brief: what exists, what constrains the solution, what is unknown. This brief is the input to the designer.

## Phase 2 — Propose the design

4. **Frame the design question.** From the brief, define the problem, constraints, and what a good design must address.
5. **Dispatch the designer.** Self-contained spawn:

```text
agents_spawn(config_name="designer", prompt="Design proposal for: <goal>. Research brief: <consolidated findings>. Constraints: <list>. Non-goals: <list>. Return a high-level design: approach, components and responsibilities, trade-offs, alternatives rejected with reasons, risks, assumptions.")
```

6. **Synthesize.** The orchestrator owns the design — accept, adjust, or reject the proposal. Fix anything that misses what the user asked for.

## Phase 3 — Review loop until acceptance

7. Spawn `design-reviewer` and `empirical-reviewer` in tandem (one parallel block). Pass the design, the research brief, and any prior round's findings.
8. If both accept, present the design inline to the user and wait for acceptance. If either requests revisions, apply the fixes (inline — designs are prose) and re-review the delta.
9. **Stopping conditions** (same anti-loop rules as the review skill): stop when both reviewers accept; stop on diminishing returns — a re-run that surfaces only issues with the fix text itself gets one targeted pass, then escalate; hard cap of 3 rounds, then present unresolved findings to the user and let them decide.

## Design content

The design covers:
- goal and user-visible outcome
- current context and assumptions (from the research brief)
- constraints and preserved behavior
- chosen approach and rationale
- alternatives rejected and why
- explicit non-goals
- acceptance criteria and unresolved risks

For most tasks the design is inline in the conversation. For large or cross-cutting changes, write it to a markdown file in the project (or the scratchpad) and reference it.

## Constraints

- Do not implement code while designing.
- The orchestrator owns the design — the designer advises, the orchestrator decides, the user accepts.
- Reviewers are read-only; fixes between rounds are applied by the orchestrator.
