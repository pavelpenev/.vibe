---
name: web-search
description: Search the web for focused factual, documentation, compatibility, and comparison questions, evaluate sources, and synthesize cited results.
user-invocable: true
allowed-tools:
  - web_search
  - web_fetch
---

# Web Search

Use this shared procedure for direct main-agent searches and delegated searches. It does not require interactive delegation and never calls the usage tool.

## Procedure

1. Form a specific query. Include the product, version, error text, or current year when relevant.
2. Prefer primary sources: official documentation, release notes, standards, papers, and maintained repositories.
3. Use one to three queries for a focused question. Reformulate if the first results are poor.
4. Fetch the most relevant sources when search snippets are insufficient.
5. Separate facts, interpretation, and uncertainty. Note conflicting sources and their dates.
6. Cite every material claim with a verified URL. Do not invent or include unchecked URLs.

## Scope

Use this skill for focused fact checks, API/documentation lookups, error solutions, version compatibility, and small comparisons. Use `sub-researcher` for a broad or multi-faceted investigation requiring many iterations.

## Output

Lead with the direct answer. Then provide concise supporting context, caveats, and a `Sources` list with URLs and access dates. For comparisons, use a table and state a recommendation only when the evidence supports one. If no reliable source is found, say so and identify what remains uncertain.
