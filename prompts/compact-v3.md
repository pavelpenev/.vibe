# Two-Stage Compaction Prompt

**Version**: 3.0
**Strategy**: Create self-contained handoff with embedded reorientation protocol
**Best for**: All tasks

---

You are performing a CONTEXT CHECKPOINT COMPACTION. Create a **self-contained handoff document** that the next agent will receive. This document must include both the summary of work and the instructions for how the next agent should use it.

**CORE RULE**: If any task, action, or operation was completed, you MUST mark it with `[DONE]`. The next LLM will treat `[DONE]` as **ABSOLUTELY COMPLETED** and will **NEVER** redo it. The only exception: if concrete evidence contradicts a `[DONE]` mark (the file it claims to have created is missing, the test it claims passed now fails), verify cheaply before building on it — do not silently redo the work, and surface the discrepancy to the user.

**STATUS MARKERS** (use exactly as written):
- `[DONE]` = Absolutely completed, never to be repeated
- `[IN PROGRESS]` = Started but not finished - resume from interruption point
- `[PENDING]` = Not started - awaiting execution
- `[UNCERTAIN]` = Completion status unclear - next agent MUST ask user
- `[BLOCKED]` = Waiting on external dependency - next agent MUST verify

**CONTEXT WEIGHTING**:
- Allocate 40% of your token budget to the first 10% of conversation (Initial setup)
- Allocate 40% of your token budget to the last 10% of conversation (Current work)
- Allocate 20% of your token budget to the middle 80% (compress aggressively)

---

## Required Output Format

Your response must be a single document with these **exact** section headers in this order. Do not add any preamble or meta-discussion.

### Next Agent: Reorientation Protocol

Read this first:

1. **Recover Governing Context**
   - Read project-local `AGENTS.md` (current directory and all parent directories up to repo root)
   - Read `PLAN.md` if it exists in the current directory
   - Read global `AGENTS.md` at `~/.vibe/AGENTS.md`
   - **Priority order**: Project AGENTS.md > PLAN.md > Global AGENTS.md > This summary
   - Explicit user instructions override everything

2. **Review Completion Status**
   - Go to `Completion Audit` section
   - Identify first `[IN PROGRESS]` item - this is your resumption point
   - Note all `[UNCERTAIN]` and `[BLOCKED]` items

3. **Ask Before Acting**
   - If anything in this summary conflicts with AGENTS.md or PLAN.md, ASK the user
   - If any item is marked `[UNCERTAIN]`, ASK the user for clarification
   - If any item is marked `[BLOCKED]`, identify the blocker and ASK if it's resolved
   - If the resumption point is unclear, ASK the user where to continue

4. **Proceed with Work**
   - Only after completing steps 1-3, resume from the first `[IN PROGRESS]` item
   - Never redo `[DONE]` work
   - Skip `[DONE]` items entirely in your planning

**CRITICAL**: When in doubt, ASK. Recover full context before taking action.

### Context
- Goal: [one sentence, verbatim from first user message]
- Constraints: [bullet list of explicit constraints]
- Preferences: [bullet list of user preferences]

### Completion Audit
- [STATUS] [specific action with concrete details - include file paths, counts, names]
- Every actionable item from the conversation MUST have a status marker
- Use only: [DONE], [IN PROGRESS], [PENDING], [UNCERTAIN], [BLOCKED]

### Current State
- Phase: [current phase name]
- Last action: [what was just completed or in progress]
- Files open: [path: status for each relevant file]
- Tools in use: [list of tools actively being used]

### Key Decisions
- Decision: [rationale in one line each]

### Next Steps
- Immediate: [concrete next action]
- Priority: [high/medium/low]

---

## Validation Rules

**BEFORE OUTPUTTING YOUR SUMMARY, VERIFY IT MEETS ALL CRITERIA:**

- [ ] All 6 required sections are present in the correct order
- [ ] "Next Agent: Reorientation Protocol" is the first section
- [ ] Every actionable item from the conversation has a `[STATUS]` marker in Completion Audit
- [ ] No `[DONE]` item appears in any other section as pending or to-do
- [ ] All markers use only: [DONE], [IN PROGRESS], [PENDING], [UNCERTAIN], [BLOCKED]
- [ ] Completion Audit items include concrete details (file paths, counts, names)
- [ ] Goal is verbatim from the first user message
- [ ] First and last sections (Context, Current State) have the most detail
- [ ] Middle conversation is aggressively compressed

**IF ANY RULE FAILS**: Regenerate the summary with ALL missing information. Do not output until all checks pass.

---

## Output Rules

1. Respond ONLY with the summary document (no preamble, no meta-discussion)
2. Use the exact section headers shown above
3. Use status markers exactly as written: [DONE], [IN PROGRESS], [PENDING], [UNCERTAIN], [BLOCKED]
4. Be specific: include file paths, tool names, counts, and other concrete details
