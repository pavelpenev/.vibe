---
name: research-synthesis
description: Synthesize multiple research documents from {cwd}/research/ into a coherent unified output with cross-cutting themes, conflicts, gaps, and traceable citations.
user-invocable: true
allowed-tools:
  - task
  - read_file
  - grep
  - write_file
---

# Research Synthesis

Synthesizes multiple deep-research reports from `{cwd}/research/` into a coherent, structured synthesis. Extracts key findings from each document, identifies cross-cutting themes, resolves conflicts, flags knowledge gaps, and recommends follow-up research — all with traceable citations back to source documents.

## When to Use

- `/research-synthesis` — synthesize all documents in `{cwd}/research/`
- `/research-synthesis <directory>` — synthesize documents in specified directory
- `/research-synthesis <keyword>` — filter documents by topic keyword, then synthesize
- "synthesize my research"
- "merge these research reports"
- "what are the cross-cutting themes in my research?"

## When NOT to Use

- Running new web research → Use `/deep-research`
- Single document summarization → Read it directly or delegate to `summarizer`
- Quick overview of one report → Read the file directly

## Architecture

```
User Request → research-synthesis skill (interactive) → Map phase (summarizer subagents or direct read) → Reduce phase (main agent synthesis) → Results
```

### Document Thresholds

| Document Count | Strategy |
|---|---|
| 0 docs | Prompt: "No research documents found. Run /deep-research first?" |
| 1 doc | Summarize directly; no cross-document synthesis needed |
| 2–5 docs | Main agent reads all documents directly |
| 6–15 docs | Map: parallel summarizer subagents. Reduce: main agent |
| 16+ docs | Two-pass: metadata extraction first, then deep-read relevant docs. Warn user |

## Step 1: Discover Documents

Use `grep` to find all `.md` files in the target directory (default: `{cwd}/research/`):

```
grep -l "" research/*.md
```

If zero documents found: "No research documents found in {dir}. Run /deep-research to create some first."

If one document: note that this is a single-document summary, not a cross-document synthesis. Proceed to Step 2.

## Step 2: Scope Confirmation

Present discovered documents to the user:

```
Found N research documents in {dir}:

1. topic-a-20260601.md — "Topic A: Key Findings" (detailed, 2026-06-01)
2. topic-b-20260615.md — "Topic B: Prior Art Survey" (exhaustive, 2026-06-15)
...

Synthesize all N documents? (y/n/Select specific)
```

If the user wants a subset, ask them to specify which (by number, keyword, or date range).

If >10 documents: "This is a large set (N documents). Limit to a specific theme or date range? For example: [suggest 2-3 themes based on document titles]"

## Step 3: Synthesis Plan

Write a 1–2 sentence plan based on the documents' titles and topics:

"Plan: Extract key findings from N documents via [strategy], then synthesize across themes: [list 2–3 likely themes]."

Example: "Plan: Extract key findings from 8 research documents via parallel summarizer subagents, then synthesize across themes: document synthesis techniques, agent skill architecture, and conflict resolution patterns."

Ask: "Proceed? (y/n/Modify)"

If "Modify": incorporate user feedback and present revised plan.

## Step 4: Map Phase — Extract from Each Document

**For 2–5 documents:** Read each document directly with `read_file`. For each, extract:
- Topic and research question
- Key findings (as a list)
- Recommendations
- Sources cited (titles, URLs, types)
- Research depth (quick/detailed/exhaustive)
- Document date
- Open questions

**For 6–15 documents:** Delegate each document to a summarizer subagent in parallel:

```
task(task="Summarize {filepath}. Extract: topic, key findings (as a list), recommendations, sources (titles and URLs), research depth (quick/detailed/exhaustive), document date, open questions. Return structured summary.", agent="summarizer")
```

Launch all tasks in parallel. Wait for all results before proceeding.

**For 16+ documents:** Warn the user about processing time. Use a two-pass approach:
1. First pass: extract only topics and metadata from each document via summarizer
2. Present topic clusters to the user; ask which to deep-read
3. Second pass: deep-read only selected documents

## Step 5: Reduce Phase — Cross-Document Synthesis

Synthesize on the main agent (strongest model). Process in order:

1. **Consolidate findings:** Merge semantically similar findings across documents. Flag exact duplicates. For each consolidated finding, note which documents support it and assign a confidence level:
   - `high`: confirmed by 3+ documents or by an exhaustive study
   - `medium`: confirmed by 2 documents
   - `low`: single document only

2. **Cross-cutting themes:** Identify 3–5 themes that span multiple documents. For each theme, note which documents contribute to it and summarize the collective insight.

3. **Conflicts:** Where documents disagree on factual claims or recommendations, resolve using this hierarchy:
   1. **Recency** — prefer newer research over older
   2. **Authority** — prefer exhaustive over quick research
   3. **Consensus** — prefer findings confirmed by multiple documents
   4. **Detail** — prefer documents with more specific evidence and citations
   5. **Escalate** — if unresolvable, flag as "unresolved" and present both positions

   Never silently discard contradictory evidence. Always document the conflict and resolution rationale.

4. **Gaps:** Identify questions or topics that one document raises but no document addresses. Also flag topics that appear obviously relevant but are absent from all documents.

5. **Next research:** Based on identified gaps, weak/low-confidence findings, and unresolved conflicts, recommend 3–5 topics for follow-up research via `/deep-research`.

6. **Outdated findings:** If documents have dates, flag findings from documents older than 3 months (fast-moving fields) or 12 months (stable topics). Note where newer documents provide updated information.

## Step 6: Present Results

Present the synthesis in a human-readable format:

```markdown
## Research Synthesis: {topic area}

**Documents Synthesized:** N reports spanning {date_range}
**Synthesis Date:** {today}

### Cross-Cutting Themes

- **Theme 1** (documents: [1], [3], [5]): ...
- **Theme 2** (documents: [2], [4]): ...

### Consolidated Findings

- [HIGH] Finding X — confirmed by docs [1], [3], [5]
- [MEDIUM] Finding Y — confirmed by docs [2], [4]
- [LOW] Finding Z — from doc [6] only

### Conflicts & Resolutions

- **Conflict 1:** Doc [2] claims A, while doc [4] claims B.
  *Resolution:* Prefer doc [4] (newer, exhaustive depth).

### Knowledge Gaps

- Topic X is discussed in doc [1] but absent from docs [2] and [3] where it would be relevant.
- No document addresses question Y.

### Recommended Next Research

1. Investigate gap X via /deep-research
2. Re-research topic Y (last covered 2026-03-01, may be outdated)
3. ...

### Source Index

| # | Document | Topic | Date | Depth |
|---|----------|-------|------|-------|
| 1 | topic-a-20260601.md | Topic A | 2026-06-01 | detailed |
| 2 | topic-b-20260615.md | Topic B | 2026-06-15 | exhaustive |
...
```

## Step 7: Save (Optional)

Ask: "Save synthesis report? (y/n)"

If yes: save to `{cwd}/research/synthesis-{YYYYMMDD}.md`. If the user specifies an alternative path, save there instead.

Use `write_file` to create the report. The report should be a self-contained markdown document with all sections from Step 6, plus the full consolidated findings and conflict details.

## Conflict Resolution Hierarchy

When documents disagree:

1. **Recency**: Prefer newer research over older (date from filename or metadata)
2. **Authority**: Prefer exhaustive-depth research over quick surveys
3. **Consensus**: Prefer findings confirmed by 3+ documents over single-document claims
4. **Detail**: Prefer documents with more specific evidence, data, and citations
5. **Escalate**: Flag as "unresolved conflict" — present both positions with sources

Always document the conflict. Never silently pick a winner without noting the disagreement.

## Edge Cases

| Case | Response |
|---|---|
| Empty research/ directory | "No research documents found in {dir}. Run /deep-research to create some first." |
| Single document | Summarize directly. Note: "Only one document found — this is a summary, not a cross-document synthesis." |
| 16+ documents | Warn user about processing time. Use two-pass approach: metadata first, then deep-read. Offer to cluster by topic. |
| Unparseable .md files | "Warning: {file} doesn't appear to be a research report. Skip it? (y/n)" If user skips, list skipped files in output. |
| Duplicate findings (3+ docs) | Consolidate as high-confidence finding. Note all source documents. |
| Findings with no source overlap | Flag as low-confidence (single source only). |
| Mixed content in research/ | Present list to user for confirmation. Don't auto-exclude — false negatives are worse than false positives. |
| Documents from different projects | v1.0 limits to current project's research/ directory. Cross-project synthesis is not yet supported. |

## Verification

Test with:
- [ ] `/research-synthesis` with existing research/ directory — discovers, confirms, synthesizes
- [ ] `/research-synthesis` with empty research/ — prompts to run deep-research
- [ ] Single document — summarizes directly
- [ ] 2–5 documents — reads directly and synthesizes
- [ ] 6–15 documents — delegates to summarizer subagents and synthesizes
- [ ] Documents with conflicting findings — resolves and documents conflicts
- [ ] Saves synthesis report to research/synthesis-YYYYMMDD.md when requested
