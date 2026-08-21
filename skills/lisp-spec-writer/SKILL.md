---
name: lisp-spec-writer
description: Draft formal Common Lisp specifications in CLHS dictionary-entry style from design documents. Produces normative, implementor-focused specs with graduated language, protocol-grouped dictionary entries, and cross-reference indexing.
user-invocable: true
allowed-tools:
  - task
  - read_file
  - write_file
  - grep
  - web_search
  - web_fetch
---

# Lisp Spec Writer

Drafts formal Common Lisp specifications approaching ANSI CL spec (CLHS), AMOP, and CLIM quality. Takes design documents like design.org and produces spec chapters with CLHS-style concept sections, dictionary entries, graduated normative language, and cross-reference indexing.

**Audience:** Implementors, not users. Output is normative (defines what IS correct), not informative (how to USE). Every claim must be testable.

## When to Use

- `/lisp-spec-writer <domain>` — draft a spec chapter for a named domain (e.g., "equality", "reader-syntax", "iterator-protocol")
- `/lisp-spec-writer full` — multi-step interactive full specification from a design document
- `/lisp-spec-writer refine <chapter> <section>` — refine an existing spec section
- "write the spec for Sophie Lisp equality"
- "draft a specification chapter for..."
- "formalize this design into spec format"

## When NOT to Use

- Writing user documentation or tutorials → this is for implementor-facing normative specs
- Generating code directly → the spec defines contracts, not implementations
- Quick API docs → CLHS-style dictionary entries are formal, not summary-level
- Non-Lisp languages → the CLHS conventions are Lisp-specific

## Architecture

```
User Request → lisp-spec-writer skill (interactive) → Research phase (researcher subagent for CLHS precedents) → Draft phase (main agent synthesis) → Review → Save
```

The skill follows an interactive front-end pattern. It never generates a full spec in one shot — spec writing requires iteration and back-and-forth.

## Modes

### Chapter Mode (default)

User names a domain. Skill researches CLHS precedents, reads the design document, drafts one chapter (concept section + dictionary section).

### Full-Spec Mode

Multi-step interactive process: proposes chapter outline, user confirms, drafts chapters sequentially, maintains cross-reference index as chapters accumulate.

### Refinement Mode

Targets an existing spec section or dictionary entry. Updates it while maintaining consistency with the rest of the spec.

## Reference: CLHS Dictionary Entry Template

The CLHS defines 22 canonical section types (Section 1.4.4). Not all appear in every entry. Use this template when drafting dictionary entries:

| Section | When to Include | Content |
|---------|----------------|---------|
| **Name** (kind in italic) | Always | Defined name with kind: `Function`, `Generic Function`, `Macro`, `Accessor`, `Class`, `Condition Type`, `Type`, `Constant Variable`, `Variable`, `Declaration`, `Restart`, `Special Operator` |
| **Syntax** | Always for callables | Lambda list for functions; modified BNF for macros/special operators; character notation for reader macros. Use `→` for return values, `&rest` for required rest args |
| **Arguments and Values** | Always | English prose describing each parameter and return value with types. If type restrictions are violated: "The consequences are undefined." |
| **Description** | Always | Core normative content. Summary of all intended aspects. |
| **Side Effects** | If has side effects | What is changed by evaluation. "None." if none. |
| **Affected By** | If affected by external state | Dynamic variables, declarations, reader state that affect behavior |
| **Exceptional Situations** | If errors possible | 3 sub-categories: conditions detected and signaled, conditions handled, conditions that may be detected. Use "Signals an error of type X if..." |
| **See Also** | Always | Cross-references to related entries. Markdown internal links. |
| **Notes** | If useful | Advisory: cross-refs, code equivalences, typical uses, implementation hints. NOT part of the standard. |
| **Examples** | If illustrative | Code examples. NOT part of the standard. |
| **Method Signatures** | Generic functions only | Each method's parameters and specializers |
| **Argument Precedence Order** | Generic functions if non-default | Overrides default left-to-right order |
| **Class Precedence List** | Classes | Ordered list of standardized classes in the CPL |
| **Supertypes** | Types | Standardized supertypes |
| **Compound Type Specifier Kind/Syntax/Arguments/Description** | Compound type specifiers | Four subsections for type specifiers like `(vector ...)` |
| **Constant Value** | Constant variables | Unchanging type and value |
| **Initial Value** | Dynamic variables | Initial binding |
| **Valid Context** | Declarations | Where the declaration may appear |
| **Binding Types Affected** | Declarations | What kinds of bindings are affected |
| **Pronunciation** | Rare | Advisory pronunciation guide |

### Dictionary Entry Grouping

Per Sophie Lisp convention, dictionary entries are **grouped by protocol**, not one-per-defined-name. A protocol entry covers all methods in the protocol:

```
### Iterator Protocol _Protocol_

Covers: `make-iterator`, `iterator-endp`, `iterator-current`, `iterator-advance`

**Generic Function: make-iterator** _Generic Function_

**Syntax:** ...
```

Standalone functions still get individual entries.

### Graduated Normative Language

Use this precise vocabulary consistently:

| Term | Meaning |
|------|---------|
| **must** | Absolute requirement |
| **must not** | Absolute prohibition |
| **should** | Recommended; valid reason needed to deviate |
| **should not** | Discouraged; valid reason needed to do it |
| **may** | Truly optional |
| **consequences are undefined** | No requirements; anything can happen |
| **implementation-defined** | Implementation must document its choice |
| **implementation-dependent** | May vary; no documentation obligation |
| **is an error** | Detected by implementation; should signal an error |
| **signals an error of type** | Specific condition type, always signaled |
| **might signal an error** | Permitted but not required |

## Chapter Structure

Each spec chapter follows the CLHS two-part structure:

```markdown
# Chapter N: [Title]

## N.1 Concepts

[Prose explaining the domain: design rationale, key abstractions,
relationships between components, invariants, protocol overview.
References to CLHS where Sophie reuses or extends standard concepts.]

## N.2 Dictionary

[Protocol-grouped or individual dictionary entries, alphabetically
ordered within the chapter. Each entry follows the CLHS template above.]
```

### Proposed Sophie Lisp Chapter Map

From design.org analysis, the spec maps to these chapters:

| # | Chapter | Source in design.org | CLHS Analog |
|---|---------|---------------------|-------------|
| 1 | Introduction, Scope, Conventions | Core Design Principles, Vision, Scope | CLHS Ch 1 |
| 2 | Packages and Namespaces | Package Hierarchy, Activation Model | CLHS Ch 11 |
| 3 | Reader Syntax | Readtable (sl-core-syntax) | CLHS Ch 2, 23 |
| 4 | Iterator and Collector Protocols | Iterator Protocol, Collector Protocol | CLHS Ch 17 |
| 5 | Sequence Abstraction | Seqable Protocol | CLHS Ch 17 |
| 6 | Generic Sequence Operations | Sequence Operation Catalog | CLHS Ch 17 |
| 7 | Generic Equality and Comparison | Equality (CDR 8 model) | CLHS Ch 12, 18 |
| 8 | Binding and Destructuring | Binding & Destructuring | CLHS Ch 5 |
| 9 | Object System Extensions | Enhanced defclass | CLHS Ch 7 |
| 10 | Extended Iteration | Iteration (iter macro) | CLHS Ch 6 |
| 11 | String Operations | String Handling | CLHS Ch 16 |
| 12 | Core Utility Library | Utilities (IN symbols) | CLHS Ch 14 |
| A | Condition Types | Conditions & Errors | CLHS Ch 9 |
| B | Conformance | Activation Model | CLHS Ch 1 |
| C | Glossary | — | CLHS Ch 26 |

## Workflow

### Step 1: Parse Request

Extract from user input:
- **Mode**: chapter, full-spec, or refinement
- **Domain**: which spec domain (e.g., "equality", "reader-syntax", "iterator-protocol")
- **Source**: which design document to read from (default: look for `design.org` in project)

### Step 2: Read Source Material

Read the design document (typically `design.org`). For a specific domain, grep for relevant sections:

```
grep -n "Equality\|equals\|hash-code\|CDR 8\|compare" design.org
```

Extract: feature description, protocol contracts, lambda lists, invariants, edge cases, dependencies on other features.

### Step 3: Research CLHS Precedents

Delegate to the researcher subagent to find how CLHS specifies analogous features:

```
task(task="Load the researcher skill and research how CLHS specifies [analogous feature]. Fetch the relevant CLHS pages for [specific entries]. Return: (1) which CLHS chapters cover this domain, (2) the dictionary entry structure for the closest analogous functions/macros, (3) how CLHS handles [specific concern like protocol contracts, reader macros, etc.].", agent="generic-luna")
```

This step grounds the spec in CLHS conventions and prevents reinventing specification patterns.

### Step 4: Draft Plan

Present a 2-3 sentence plan:

"Plan: Draft Chapter 7 (Generic Equality and Comparison) with concept section covering CDR 8 alignment and protocol design, then dictionary entries for `equals` (generic function), `compare` (generic function), `hash-code` (generic function), and `#h()` (reader macro), following CLHS conventions for generics and dispatch macros."

Ask: "Proceed? (y/n/Modify)"

### Step 5: Draft the Spec Chapter

Write the chapter in two passes:

**Pass 1 — Concept section:**
- Domain overview and design rationale
- Relationship to standard CL (what's reused, what's extended)
- Key abstractions and protocols
- Invariants and contracts
- Reader syntax if applicable
- Package location (`sl.ext.*`)

**Pass 2 — Dictionary section:**
- Protocol-grouped entries (or individual entries for standalone functions)
- Each entry follows the CLHS template
- Include every applicable section from the template — omitting a section means "not applicable", not "I forgot"
- Use graduated normative language consistently
- Cross-reference related entries with Markdown internal links
- Include examples that demonstrate edge cases

For full-spec mode, draft chapters sequentially, maintaining the cross-reference index as it grows.

### Step 6: Review

Present the draft to the user in the response. The draft should be complete and ready for review.

Key review questions to surface:
- Are there sections that need more precision?
- Are there edge cases the spec doesn't cover?
- Is the graduated language used correctly?
- Are cross-references to other chapters correct?

### Step 7: Refine

Based on user feedback, refine the draft. For targeted changes, delegate to a generic subagent with the `lisp-implementor` skill if the spec file contains Lisp forms. Otherwise, edit directly.

### Step 8: Save

Ask: "Save to `spec/chapter-N-title.md`? (y/n)"

If yes, write the file. For full-spec mode, also update the cross-reference index at `spec/index.md`.

## Cross-Reference Index

Maintain a file `spec/index.md` mapping every defined name to its chapter and section:

```markdown
# Sophie Lisp Specification — Cross-Reference Index

| Defined Name | Kind | Chapter | Section |
|-------------|------|---------|---------|
| sl:equals | Generic Function | 7.2.1 | Equality |
| sl:compare | Generic Function | 7.2.2 | Equality |
| sl:hash-code | Generic Function | 7.2.3 | Equality |
| sl:make-iterator | Generic Function | 4.2.1 | Iterator Protocol |
| #h() | Reader Macro | 3.3 | Reader Syntax |
| ^() | Reader Macro | 3.2 | Reader Syntax |
| sl:bind | Macro | 8.2.1 | Binding |
| sl:seq-map | Generic Function | 6.2.1 | Sequence Operations |
...
```

Update this index after each chapter is saved. The index enables CLHS-style "See Also" cross-references.

## Issue Tracking (X3J13-Style)

For proposed changes to existing spec sections, use this issue format:

```markdown
## Issue SPEC-NNN: [One-line problem description]

**Affected Sections:** [list of chapter.section references]
**Status:** Proposed | Accepted | Rejected | Implemented

**Problem Description:**
[What's wrong with the current spec]

**Proposal:**
[What should change, in spec language]

**Impact:**
- Cost to Implementors: [low | medium | high — explanation]
- Cost to Users: [low | medium | high — explanation]
- Cost of Non-Adoption: [what breaks if we don't fix this]

**Discussion:**
[Rationale, alternatives considered, community input]
```

Store issues in `spec/issues/`. Number sequentially.

## Edge Cases & Guidelines

### When there's no CLHS analog

For features with no CLHS precedent (e.g., Iterator protocol as a user-extensible CLOS protocol), follow AMOP conventions:
- Define the protocol in the concept section
- Specify generic function contracts (what each method must do)
- Document method signatures for default methods
- State which methods users may override and the contract they must maintain
- Specify the call chain — what calls what, when

### When the design.org is ambiguous

If the design document doesn't specify a detail needed for the spec (e.g., exact error type for a condition), flag it explicitly:

```
**Exceptional Situations:**
- Signals an error if X. [TODO: specify exact condition type — design.org
  does not define a specific condition. Options: simple-error,
  sl:iterator-error, type-error.]
```

Never guess. Flag ambiguities for the user to resolve.

### Reader macro specification

Reader macros need special treatment. Specify:
1. What character triggers the reader macro
2. Whether it's a macro character or dispatch macro
3. The precise syntax (character-level notation with examples)
4. What the reader produces (the Lisp form)
5. What that form evaluates to
6. Edge cases (empty, malformed, conflicting syntax)

### Protocol contracts as testable invariants

Where possible, state properties that can be mechanically verified:

```
**Invariant (testable):**
(sl:equals a b) ⇒ (= (sl:hash-code a) (sl:hash-code b))
```

### Self-referential honesty

CLHS entries often include self-referential honesty about limitations:

```
**Notes:**
This is a minimal specification. Implementations may extend
the iterator protocol with additional optional methods.
```

## Verification

Test with:
- [ ] `/lisp-spec-writer equality` with design.org — produces Chapter 7 draft with concept + dictionary sections
- [ ] `/lisp-spec-writer "reader syntax"` — produces Chapter 3 with reader macro specifications
- [ ] `/lisp-spec-writer iterator-protocol` — produces Chapter 4 with AMOP-style protocol specification
- [ ] `/lisp-spec-writer full` — produces chapter outline, then iterates through chapters
- [ ] `/lisp-spec-writer refine spec/chapter-7-equality.md §7.2.1` — targets specific entry for refinement
- [ ] Cross-reference index maintained across multiple chapter drafts
- [ ] Graduated normative language used consistently (search for "should" that should be "must")
- [ ] All defined names from design.org appear in at least one chapter
