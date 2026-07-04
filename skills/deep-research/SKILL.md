---
name: deep-research
description: Front-end for researcher subagent. Gathers requirements, asks clarifying questions, constructs research query, and delegates to researcher subagent for execution. Always provides a chat summary; saves detailed report to {cwd}/research/ on request.
user-invocable: true
allowed-tools:
  - task
  - read_file
  - grep
---

# Deep Research - Front-end for Researcher Subagent

**Role:** Interactive orchestrator that prepares research tasks and delegates to the non-interactive `researcher` subagent.

Use for technical topics requiring sustained investigation. This skill handles the interactive parts (requirements gathering, clarification, report requests) and delegates execution to the `researcher` subagent.

## Triggering Conditions

Activates when user requests sustained investigation:
- `/deep-research` - start interactive research
- `/deep-research <topic>` - research specific topic
- "research <topic>"
- "prior art survey on <topic>"
- "survey prior art for <topic>"
- "survey <topic>"

## When NOT to Use

- Quick factual lookups → Use `/web_search` directly or delegate to `researcher` directly
- Yes/no questions or simple definitions
- Tasks requiring immediate action
- When you need a definitive single answer without exploration

## Architecture

```
User Request → deep-research skill (interactive) → researcher subagent (execution) → Results
```

This skill is the **interactive front-end**. The `researcher` subagent is the **non-interactive execution engine**.

## Error Handling

**Invalid input:**
- Empty or whitespace-only topic: Prompt "Please provide a research topic."

## Known Limitations

- Requires web access for full functionality (researcher subagent needs web_search/web_fetch)
- Source quality depends on web search results and availability
- May miss very recent information (within days/weeks of current date)
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

Show plan to user, then ask: "Proceed with this plan? (y/n/Modify)"
- If "y" or "Proceed": continue to Step 4
- If "n" or "Modify": revise plan and ask again

## Step 4: Construct Research Task

Build a task string for the researcher subagent. Include parameters as needed:

```
Research {topic} depth:{depth} save_to_file:{path} local_context:{files}
```

**Parameters:**
- `depth`: "quick" (1-2 searches), "detailed" (3-5 searches, default), "exhaustive" (5+ searches, auto-saves report)
- `save_to_file`: Path to save full report (e.g., "{cwd}/research/{topic}-{YYYYMMDD}.md")
- `report_directory`: Alternative directory for report (default: cwd)
- `local_context`: Comma-separated files/directories to incorporate (e.g., "src/main.py,config.json")

## Step 5: Delegate to Researcher Subagent

Use the `task` tool to delegate to the researcher subagent:

```python
task(task="{constructed_task_string}", agent="researcher")
```

Wait for the researcher subagent to return JSON results.

## Step 6: Present Results

The researcher subagent will return JSON with:
- `summary`: Key findings, recommendations, quick answer, open questions
- `sources`: Cited sources with metadata (title, url, type, relevance)
- `conflicts`: Any disagreements between sources with resolutions
- `outdated_sources`: Flagged outdated information
- `report_saved`: Path to saved report (if any)
- `files_read`: Local files incorporated
- `searches_performed`: Number of searches executed

**Format the results for the user:**

```markdown
## Research Results: {topic}

**Quick Answer:** {summary.quick_answer}

**Key Findings:**
{summary.key_findings.map(f => `- ${f}`).join('\n')}

**Recommendations:**
{summary.recommendations.map(r => `- ${r}`).join('\n')}

**Sources:**
{sources.map((s, i) => `- [${i+1}] ${s.title} (${s.type}, ${s.relevance}) - ${s.url}`).join('\n')}

{conflicts.length > 0 ? `
**Conflicts Detected:**
${conflicts.map(c => `- ${c.disagreement}: ${c.resolution || 'Unresolved'}`).join('\n')}` : ''}

{outdated_sources.length > 0 ? `
**Outdated Sources:**
${outdated_sources.map(s => `- ${s.title} from ${s.date}`).join('\n')}` : ''}

{report_saved ? `
**Report saved to:** ${report_saved}` : ''}
```

## Direct Delegation (Simple Queries)

For simple queries that don't need interactive orchestration, users or the main agent can call researcher subagent directly:

```python
task(task="What is Mistral Vibe?", agent="researcher")
```

This skill is optimized for **complex, multi-step research** that benefits from interactive clarification.

## Verification

Test with:
- [ ] `/deep-research` with no topic (should prompt for topic)
- [ ] `/deep-research <valid topic>` (should gather requirements, get approval, delegate, present results)
- [ ] Broad topic (should ask for narrowing)
- [ ] Request full report (should save report)

