# Normative Language Review Rubric

> **Critical principle:** Normative wording is the highest-risk prose in a specification: an incorrect edit can alter an implementation obligation. A reviewer must never silently alter modality (`must` to `should`, or `should` to `may`), negation (`must` to `must not`), or a defined term. Never substitute **implementation-defined** for **implementation-dependent**, or the reverse; they have different consequences. When meaning is uncertain, report high semantic risk and recommend author review instead of proposing exact replacement text.

## Use of profiles

The dispatching task must name one profile. If none is named, report that limitation, inspect the document for contextual evidence, and do not infer a profile as fact. Apply the selected profile together with all cross-cutting checks.

## NL-01 — BCP 14 (RFC 2119 / RFC 8174)

- Uppercase `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` carry requirement force.
- Under RFC 8174, lowercase forms are non-normative unless the document explicitly says otherwise.
- Check for confusing mixtures of uppercase and lowercase forms in comparable requirements.
- Report missing RFC 2119/8174 keyword boilerplate as **INFO**.

### NL-01a — Requirements and deviations

- Every `MUST` needs an observable outcome, conformance criterion, or practical test.
- Report a `MUST` without such evidence as a finding.
- A `SHOULD` or `SHOULD NOT` must state when departure is justified.
- Missing deviation conditions are a **WARNING**, because implementers cannot judge an exception.

### NL-01b — Optionality and packing

- `MAY` must describe a real option, not an implied obligation.
- `MAY be ignored` can be coherent; `MAY be required` is internally contradictory.
- Do not let one sentence bundle independently actionable `MUST`, `SHOULD`, and `MAY` clauses.
- Prefer separately numbered requirements when the obligations can stand alone.

## NL-02 — CLHS (Common Lisp HyperSpec conventions)

- Lowercase `must`, `must not`, `should`, `should not`, and `may` are normative.
- `consequences are undefined` imposes no requirement; any result is permitted.
- `implementation-defined` requires documentation of the implementation's choice.
- `implementation-dependent` permits variation without a documentation duty.

### NL-02a — Error terminology

- `is an error` means the situation is erroneous — the implementation must detect and signal an error of type `error` (or a subtype). This is stronger than "should signal"; it is a mandatory signaling requirement.
- `signals an error of type X` requires that specified condition to be signaled.
- `might signal an error` grants permission to signal, but does not require it.
- Verify that mandatory and optional error language matches the stated intent.

### NL-02b — Meaning boundaries

- Treat undefined behavior, implementation-defined behavior, and implementation-dependent behavior as distinct categories.
- Flag inconsistent category use; never recommend interchanging the terms casually.
- If a programmer mistake is not required to be caught, use `consequences are undefined`, not `is an error`.
- If detection and signaling are intended, `is an error` is the appropriate stronger statement.

## NL-03 — Document-defined vocabulary

- Locate a `Conventions`, `Terminology`, or equivalent section defining requirement words.
- Apply its declared vocabulary and verify that levels are distinct, consistent, and testable.
- If it defines no vocabulary while using `shall`, `required`, `must`, or `should`, report a **WARNING**.
- Do not assume BCP 14 or CLHS meanings merely from the words used.

## Cross-cutting checks

### NL-10 — One requirement per sentence

- Split a sentence that combines independent requirements at different levels, such as `MUST`, `SHOULD`, and `MAY`.
- Give each independently testable obligation its own numbered item where practical.
- A compound construction can remain when separating it would hide a necessary relationship.
- For that exception, report **INFO** rather than treating the construction as a defect.

### NL-11 — Testability

- Each normative statement needs observable behavior, a conformance check, or a feasible test.
- `The implementation MUST be robust` is too indeterminate to test.
- `The implementation MUST reject packets with invalid checksums` provides a checkable outcome.
- Report untestable obligations as **WARNING**.

### NL-12 — Rationale separation

- Put explanatory rationale apart from the requirement, or label it clearly, for example `Rationale:`.
- Interleaving reasons with obligations can obscure which words are binding.
- Preserve any intentional coupling, but identify unclear boundaries between rule and explanation.
- Report tangled rationale as **INFO**.

### NL-13 — Defined-term protection

- Use glossary and terminology terms consistently with their defined meanings.
- Report a term reused for a different concept as a **WARNING**.
- Do not propose a synonym for a defined term, even when it appears stylistically clearer.
- Defined terminology is contractual language and requires author-level resolution.

### NL-14 — Exception and scope clarity

- A `MUST` or `SHOULD` should identify its subject, operating scope, and applicable exceptions.
- For example, determine whether `all requests` includes health checks and cached responses.
- Where the boundary is unclear, report a **WARNING** rather than selecting an interpretation.
- Recommend that the author state the intended scope explicitly.

### NL-15 — Conformance section

- A specification should include a conformance section describing what an implementation must do to conform.
- Its absence weakens the interpretation and assessment of individual normative statements.
- This is a document-structure concern, not a prose-quality defect.
- Report a missing conformance section as **INFO**.
