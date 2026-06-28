---
name: deep-research
description: Use for sustained technical investigation, prior art surveys, or complex problem-solving. Always provides a chat summary; saves detailed report to {cwd}/research/ on request. Triggers on requests to research, survey prior art, or solve complex technical problems.
user-invocable: true
allowed-tools:
  - read
  - write_file
  - bash
  - grep
  - web_search
  - web_fetch
---

# Deep Research

Use for technical topics requiring sustained investigation. Defaults to quick summary; full report on request.

## Triggering Conditions

Activates when user requests sustained investigation:
- `/deep-research` - start interactive research
- `/deep-research <topic>` - research specific topic
- "research <topic>"
- "prior art survey on <topic>"
- "survey prior art for <topic>"
- "survey <topic>"

## When NOT to Use

- Quick factual lookups → Use `/web_search` directly
- Yes/no questions or simple definitions
- Tasks requiring immediate action
- When you need a definitive single answer without exploration

## Error Handling

**Invalid input:**
- Empty or whitespace-only topic: Prompt "Please provide a research topic."

## Known Limitations

- Requires web access for full functionality
- Source quality depends on web search results and availability
- May miss very recent information (within days/weeks of current date)
- Model has a knowledge cutoff date; recent developments after that date are discovered via web search
- Cannot access paywalled content, private repositories, or internal documentation
- Research depth depends on query formulation and topic specificity

## Step 1: Parse Request and Load Context

Extract:
- **Topic**: The subject to research
- **Type**: Prior art survey, problem-solving, or general investigation
- **Scope indicators**: Broad terms ("AI", "database") vs specific ("React hooks optimization")

**Load project context:**
- Check for AGENTS.md in current directory and parent directories
- Check for PLAN.md in current directory
- If found, read and incorporate project-specific instructions and context to inform research scope

## Step 2: Scope Check

If topic seems broad (multiple subtopics, vague terms):

Ask user: "This topic is broad. Limit to a specific aspect? For example:
- Focus on: {suggestion 1}
- Focus on: {suggestion 2}
- Or proceed with full scope?"

If user accepts a limitation, narrow the topic. If user says "proceed with full scope", continue but note it may take longer.

## Step 3: Research Plan

Write a 1-2 sentence plan:
"Plan: {action 1}, then {action 2}, focusing on {key aspect}."

Example: "Plan: Search for existing Lisp implementations, then compare performance characteristics, focusing on concurrency models."

Show plan to user, then proceed (no approval needed).

## Step 4: Iterative Search

Run 2-4 targeted searches. Start broad, then narrow.

**Query generation:**
- Main query: {topic}
- Comparative: {topic} vs alternatives
- Technical: {topic} how it works
- Recent: {topic} 2025 2026

Use `web_search` for each. For strong results, use `web_fetch` to read full content.

## Step 5: Collect and Organize

For each relevant result, record:
```
[{n}] Title | URL | Date: {YYYY-MM} | Type: {official/academic/community}
```

**Type classification:**
- `official`: Official docs, standards, RFCs
- `academic`: Papers, peer-reviewed research
- `secondary`: Industry reports, analyses
- `community`: Blogs, forums, Q&A

## Step 6: Conflict Detection

If sources disagree:
1. Try to resolve (check dates, authority, context)
2. If resolvable (e.g., one source outdated): Use the better source, note resolution
3. If unresolved: Flag in both summary and report

**Simple resolution cases:**
- Source A (2024) vs Source B (2021) → Prefer A, note B is outdated
- Source A (official docs) vs Source B (forum opinion) → Prefer A
- Source A (detailed) vs Source B (snippet only) → Use A

## Step 7: Date Context

Flag outdated sources based on topic type:

| Topic Type | Outdated If | Flag Threshold |
|------------|-------------|----------------|
| JavaScript/Node/Web | > 1 year old | Flag if >12 months |
| Python/Rust/Go | > 18 months old | Flag if >18 months |
| Lisp/Functional | > 2 years old | Flag if >24 months |
| Math/Algorithms/CS | > 3 years old | Flag if >36 months |

Mark as: `(outdated: {source} from {date})`

## Step 8: Generate Summary (Tier 1 - Always)

Format:
```
## Summary: {topic}

**Key Finding:** {one-sentence core insight}

**Sources:**
- [1] {Title} - {main insight}
- [2] {Title} - {supporting evidence}
{...}

**Notable:**
- {Conflict note if unresolved}
- {Outdated source note if relevant}

**Quick Answer:** {actionable takeaway or next step if obvious}
```

**Conflicts in summary:** Only if unresolved and significant. Example: "Sources disagree on performance impact [1][2]."

## Step 9: Check for Full Report Request

After displaying summary, check if user wants detailed report:
- User says: "full report", "detailed", "save to file", "more detail"
- Or explicitly: "/deep-research save"

If yes: Proceed to Step 10. If no: Done.

## Step 10: Generate Full Report (Tier 2 - On Request)

Filename: `{cwd}/research/{topic-slug}-{YYYYMMDD}-{HHMMSS}.md`

**Report location:** Reports are saved to the current working directory's `research/` folder by default unless user specifies an alternative path.

Structure:
```markdown
# Research: {topic}
**Generated:** {YYYY-MM-DD HH:MM:SS}
**Scope:** {original request}

## Quick Answer
{ Repeat Tier 1 summary }

## Research Plan
{ Plan from Step 3 }

## Findings

### {Theme 1}
{Analysis with citations [1][2]}

### {Theme 2}
{Analysis with citations [3][4]}

## Conflicts
- **Conflict 1:** Source A [1] says X, Source B [2] says Y. {Resolution or note that it's unresolved}.

## Outdated Sources
- [3] {Title} from {date} - outdated for this topic type

## Sources
[1] Title | URL | Date: {YYYY-MM} | Type: {type}
[2] ...
```

Save to file, confirm: "Report saved to {cwd}/research/{filename}"

## Quality Checks

Before final output:
- [ ] All claims have source citations
- [ ] Conflicts are noted and resolved/flagged
- [ ] Outdated sources are flagged
- [ ] Summary is concise (3-7 bullet points max)
- [ ] Filename is unique (date-stamped)

## Verification

Test with:
- [ ] `/deep-research` with no topic (should prompt)
- [ ] `/deep-research <valid topic>` (should research and summarize)
- [ ] `/deep-research` then request full report (should save to file with unique timestamp)
- [ ] `/deep-research` with empty input (should re-prompt)
