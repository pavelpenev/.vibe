# Hybrid Compaction Prompt

**Version**: 2.0  
**Strategy**: Combined approach - weighted context + explicit state + validation + consumer enforcement  
**Best for**: All tasks, especially long-running analysis like vibe log analysis

---

You are performing a CONTEXT CHECKPOINT COMPACTION. Create a structured, accurate handoff summary for another LLM to resume this task seamlessly.

**CONTEXT WEIGHTING (Critical)**:
- Allocate **40% of your token budget** to the first 10% of conversation (Initial Setup)
- Allocate **40% of your token budget** to the last 10% of conversation (Current State)
- Allocate **20% of your token budget** to the middle 80% (compress aggressively)

**CORE RULE**: If any task, action, or operation was completed, you MUST mark it with `[DONE]`. The next LLM will treat `[DONE]` as **ABSOLUTELY COMPLETED** and will **NEVER** redo, re-run, or repeat that work under any circumstances.

**ABSOLUTE NO-REDO PRINCIPLE**:
- `[DONE]` = **NEVER REPEAT** - Treat as immutable fact
- `[IN PROGRESS]` = Resume from interruption point
- `[PENDING]` = Has not been started
- **VIOLATION**: If the next LLM redoes a `[DONE]` item, the compaction has failed

**REQUIRED METADATA** (always include):
- Session ID: [session_xxx]
- Current token count: [X]
- CHECKPOINT.md: [exists/updated/not found]
- SUMMARY.md: [exists/updated/not found]

---

## 📋 CONSUMER INSTRUCTIONS (Include in Summary Output)

**FOR THE NEXT LLM - MANDATORY RULES:**

When you receive this summary:
1. **`[DONE]` is ABSOLUTE**: Treat marked items as **100% completed**. Never redo, verify, re-check, or repeat them.
2. **Start from `[IN PROGRESS]`**: Resume the first incomplete item at its interruption point.
3. **Skip `[DONE]` entirely**: Move directly to pending work. Do not reference `[DONE]` items as "already done" - simply omit them from your action plan.
4. **Cross-check with files**: If CHECKPOINT.md or SUMMARY.md exist in the current directory, validate this summary against them.
5. **Clarify ambiguity**: If unclear whether something is `[DONE]` or `[IN PROGRESS]`, ASK the user - do NOT assume.

**CRITICAL**: Redoing `[DONE]` work wastes tokens, breaks workflow continuity, and defeats the purpose of compaction.

---

## Required Structure

### Initial Context [40% - HIGH PRIORITY]
Preserve the problem setup verbatim or near-verbatim:
- Original user goal/request:
- Problem we're solving:
- Explicit constraints:
- User preferences:
- Initial setup completed:

### Current State [40% - HIGH PRIORITY]
Preserve the most recent work verbatim or near-verbatim:
- Last action completed: (MUST use [DONE] if finished)
- Current phase/status:
- Files currently open/touched (path: status):
- Tools currently in use:
- Partial operations in progress:
- **Token count**: [X] (from session metadata)

### Completion Audit [CRITICAL - Prevents Redo]
Format: `- [STATUS] Description`

**Status options (use EXACTLY as written):**
- `[DONE]` = **ABSOLUTELY COMPLETED** - Never to be repeated
- `[IN PROGRESS]` = Started but not finished - Resume from interruption
- `[PENDING]` = Not started - Awaiting execution

**AUDIT RULES - MANDATORY:**
1. **Scan comprehensively**: Review the ENTIRE conversation history for actionable items
2. **Every action gets a marker**: No actionable task should be left unmarked
3. **Be specific**: Include concrete details (file paths, counts, names) in each item
4. **Group logically**: Related tasks can share a line if they form one logical unit
5. **No duplicates**: Each task appears exactly once in the audit

**COMPLETION CRITERIA:**
- File created/written → `[DONE]`
- File modified/edited → `[DONE]`
- Tool command executed successfully → `[DONE]`
- Analysis completed → `[DONE]`
- Decision made → `[DONE]`
- Currently in middle of work → `[IN PROGRESS]`
- Not started → `[PENDING]`

**EXAMPLE - CORRECT:**
```
- [DONE] Indexed 27/76 session logs from /home/pav/.vibe/logs/session/
- [DONE] Extracted metadata from all sessions (87 total)
- [DONE] Identified 3 skill parsing errors in lisp-edit skill
- [IN PROGRESS] Analyzing tool usage patterns (batch 1 of 3, currently at 45/76)
- [PENDING] Analyze error patterns across all sessions
- [PENDING] Generate recommendations document
```

**EXAMPLE - WRONG (avoid these):**
```
- [DONE] Worked on indexing  (too vague)
- [DONE] Looked at files  (no specific outcome)
- [IN PROGRESS] Some analysis  (what analysis?)
- Stuff to do later  (missing [PENDING] marker)
```

### Key Decisions [10% - Middle conversation summary]
- Decision: Rationale (one line each, keep brief)

### Technical Context [10% - Middle conversation summary]
- Important findings:
- Errors encountered:
- Key data/identifiers:
- References:

### Next Steps [Included in Current State]
- Immediate next action:
- Priority:

---

## Validation Rules

**BEFORE OUTPUTTING YOUR SUMMARY, YOU MUST VERIFY IT MEETS ALL CRITERIA:**

### ✅ Structural Validation
- [ ] All required sections are present: Initial Context, Current State, Completion Audit, Key Decisions, Technical Context, Next Steps
- [ ] Consumer Instructions section is included at the top
- [ ] Section headers match exactly (case-sensitive)

### ✅ Completion Audit Validation
- [ ] **Every actionable item** from the conversation has a `[STATUS]` marker
- [ ] **No `[DONE]` item** appears in any other section as "to do" or "next"
- [ ] **All markers are valid**: Only `[DONE]`, `[IN PROGRESS]`, `[PENDING]` are used
- [ ] **No duplicates**: Each task appears exactly once
- [ ] **Specific**: Each item has concrete details (files, counts, names)

### ✅ Context Validation
- [ ] Initial Context accurately represents the original user goal
- [ ] Current State accurately represents the last completed work
- [ ] Required Metadata is complete: Session ID, token count, CHECKPOINT.md status, SUMMARY.md status
- [ ] All file paths mentioned in the conversation are included
- [ ] All tools used are listed
- [ ] Key decisions with rationale are captured

### ✅ Quality Validation
- [ ] First 10% (Initial Setup) and last 10% (Current State) have the most detail
- [ ] Middle 80% is aggressively compressed
- [ ] Summary is structured and readable
- [ ] No meta-discussion or preamble in the output

### ✅ Consumer Safety Validation
- [ ] Consumer Instructions are clear and prominent
- [ ] The **ABSOLUTE NO-REDO** principle is explicitly stated
- [ ] Cross-check instructions for CHECKPOINT.md/SUMMARY.md are included

**FINAL CHECK**: Read your summary as if you were the next LLM. Could you resume the task without redoing any `[DONE]` work? If NO, regenerate.

**IF ANY RULE FAILS**: Regenerate the summary with ALL missing information. Do not output until all checks pass.

---

## Output Rules

1. **Structure**: Use the exact section headers above
2. **Markers**: Use [DONE], [IN PROGRESS], [PENDING] exactly as shown
3. **Verbatim**: Preserve exact wording for Initial Context and Current State where possible
4. **Completeness**: Include all file paths, tool names, and technical details
5. **No redo**: Never suggest redoing [DONE] work in Next Steps
6. **Format**: Respond ONLY with the summary text (no preamble, no meta-discussion)

---

## Notes
Weighted context + explicit status markers + completion audit = reliable handoffs.
