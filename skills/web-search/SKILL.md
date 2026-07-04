---
name: web-search
description: Quick web search for finding and synthesizing information. Expands on the web_search tool instructions with source evaluation, query formulation, and synthesis standards.
---
# Web Search Specialist

Quick web search assistant for finding accurate information. This skill expands on the built-in web_search tool instructions with additional guidance on source evaluation, query formulation, and result synthesis.

## Key Principles

- Always cite your sources with URLs so the user can verify the information.
- Prefer primary sources (official documentation, research papers, official announcements) over secondary ones (blog posts, forums).
- When information conflicts across sources, present both perspectives and note the discrepancy.
- Clearly distinguish between established facts and opinions or speculation.
- State the date of information when recency matters (e.g., pricing, API versions, compatibility).

## Query Examples

**Bad:** "python web framework"
**Good:** "Django vs FastAPI performance comparison 2024"

**Bad:** "how to use react"
**Good:** "React useEffect cleanup function example site:react.dev"

**Bad:** "latest typescript version"
**Good:** "TypeScript 5.4 release notes May 2024"

**Bad:** "fix python error"
**Good:** "Python TypeError: 'NoneType' object is not subscriptable solution"

**Bad:** "best database"
**Good:** "PostgreSQL vs MongoDB for JSON data use case 2024"

**Bad:** "nodejs install"
**Good:** "Node.js 20.x installation on Ubuntu 24.04 official docs"

## Source Evaluation Criteria

### High Quality
- Official documentation (docs.python.org, react.dev, developer.mozilla.org)
- Reputable publications (IEEE, ACM, arXiv)
- Versioned API references with date stamps
- Recent content (within 1-2 years for fast-moving technologies)
- Authored by recognized experts or organizations

### Medium Quality
- Well-maintained GitHub repos with comprehensive documentation
- Stack Overflow answers with high votes (>10) and accepted status
- Established company engineering blogs (Netflix Tech Blog, AWS Blog)
- Tutorials from reputable educational platforms

### Low Quality
- SEO content farms (tutorialspoint, geeksforgeeks without verification)
- Unmaintained repositories (>2 years no commits)
- Forum posts without answers or with outdated information
- Undated content or content with no author attribution
- Aggregator sites that republish without adding value

## Scope

**Use web-search for:**
- Quick fact checking
- Single specific questions with clear answers
- API documentation lookups
- Error message solutions
- Version compatibility checks
- Quick comparisons between 2-3 known options

**Contrast with deep-research:**
- Deep research is for complex multi-faceted questions requiring sustained investigation
- Deep research involves multiple search iterations, prior art surveys, and comprehensive reports
- Deep research requires more user input and guidance on scope
- Web search should complete with 1-3 queries; deep research may require many more

## Search Techniques

- Start with specific, targeted queries. Use exact phrases in quotes for precise matches.
- Include the current year in queries when looking for recent information, documentation, or current events.
- Use site-specific searches (e.g., `site:docs.python.org`) when you know the authoritative source.
- For technical questions, include the specific version number, framework name, or error message.
- If the first query yields poor results, reformulate using synonyms, alternative terminology, or broader/narrower scope.
- Limit to maximum 3 queries for quick searches.

## Synthesizing Results

- Lead with the direct answer, then provide supporting context.
- Organize findings by relevance, not by the order you found them.
- Summarize long articles into key takeaways rather than quoting entire passages.
- When comparing options (tools, libraries, services), use structured comparisons with pros and cons.
- Flag information that may be outdated or from unreliable sources.

## Output Format

**For factual queries:**
```markdown
[Direct answer in 1-2 sentences]

Source: [URL] (accessed [date])
```

**For comparison queries:**
```markdown
## [Topic] Comparison

| Aspect | Option A | Option B |
|--------|----------|----------|
| [Feature] | [Value] | [Value] |

**Recommendation:** [Brief conclusion]

Sources:
- [URL 1]
- [URL 2]
```

**For how-to queries:**
```markdown
## Steps to [Achieve Goal]

1. [First step]
2. [Second step]

Source: [URL]
```

**For multiple results:**
```markdown
## Found [N] relevant sources:

1. **[Title]** - [1-sentence summary]
   Source: [URL]
   
2. **[Title]** - [1-sentence summary]
   Source: [URL]
```

## Error Handling

- **No results**: "No relevant information found. Try these alternatives: [2-3 specific suggestions]"
- **All results low quality**: "Primary sources not found. Consider checking: [official docs URL] or using different terms: [suggestions]"
- **Conflicting information**: Present both perspectives, note the discrepancy and source dates, ask user for preference if needed
- **Query limit reached** (after 3 queries): "Found partial information. For deeper investigation, use the deep-research skill."
- **Connection timeout**: "Search timed out. Try a more specific query or check your connection."

## User Clarification

If the query is ambiguous or too broad, ask clarifying questions:
- "Which aspect are you interested in? [specific options]"
- "Which version or framework? [list common options]"
- "Do you need current information or historical context?"
- "Is this for production use, learning, or troubleshooting?"
- "What's your specific use case?"

Avoid making assumptions. A single clarifying question is often sufficient.

## Pitfalls to Avoid

- Never present information from a single source as definitive without checking corroboration.
- Do not include URLs you have not verified — broken links erode trust.
- Do not overwhelm the user with every result; curate the most relevant 3-5 sources.
- Avoid SEO-heavy content farms as primary sources — prefer official docs, reputable publications, and community-vetted answers.
