# Anti-Slop Rubric for Technical Prose Review

## Governing principles

1. These rules are context-sensitive signals, not prohibitions. Every finding must name the harm a reader experiences; without reader harm, do not report a finding.
2. Do not infer or label authorship. “Sounds AI-generated” proves nothing; report observable, named patterns that a user can verify.
3. Retain valid technical-writing practice: passive constructions in normative requirements, repeated defined terms, warranted qualification, clarity-improving em dashes, and complete negative requirements.
4. Apply the smallest effective edit: remove the pattern while retaining the author’s voice and safeguarding technical meaning.

## Review patterns

### AS-01 — Delayed openings
- **Signal:** A preface announces an upcoming assertion before asserting it, such as “worth noting,” “important to note,” “the reality is,” or “here’s the thing.”
- **Reader harm:** The reader spends attention reaching a point that could have appeared immediately.
- **Minimal remedy:** Delete the preface and begin with the substantive assertion.
- **Technical-writing exception:** A safety-critical specification caveat may deliberately use “It is important to note that.”
- **Disposition:** In that exception, record INFO rather than WARNING.

### AS-02 — Staged oppositions
- **Signal:** A sentence theatrically rejects one framing before offering another: “not X; Y,” “the question is not X,” or “not merely X but Y.”
- **Reader harm:** The discarded alternative creates drama and delays the useful statement.
- **Minimal remedy:** Say the intended proposition directly.
- **Technical-writing exception:** Retain it when the contrast disambiguates requirements, for example distinguishing deprecation from a breaking change.
- **Disposition:** Flag only when the rejected side supplies no needed distinction.

### AS-03 — Insider-knowledge introductions
- **Signal:** The prose claims that “most people miss,” “everyone gets wrong,” or “nobody tells you” something before explaining it.
- **Reader harm:** It flatters the narrator or reader instead of supplying evidence or content.
- **Minimal remedy:** Remove the introduction and state the claim on its own merits.
- **Technical-writing exception:** There is rarely one; such wording is ordinarily reviewable technical-prose clutter.
- **Disposition:** Treat its appearance as a finding unless concrete audience evidence makes it necessary.

### AS-04 — Reveal-style colons
- **Signal:** A short setup ends in a colon followed by a supposedly dramatic lowercase revelation, as in “The central insight: …”.
- **Reader harm:** The punctuation performs emphasis rather than helping the reader parse information.
- **Minimal remedy:** Recast the construction as an ordinary declarative sentence.
- **Technical-writing exception:** Colons introducing lists, field labels, or definitions are conventional and useful.
- **Disposition:** Flag dramatic deployment, not normal structural punctuation.

### AS-05 — Significance-by-participle
- **Signal:** A trailing “-ing” phrase—“highlighting,” “underscoring,” “reflecting,” “showcasing,” or “demonstrating”—asserts importance without explaining it.
- **Reader harm:** The prose gestures at an implication while withholding the actual implication.
- **Minimal remedy:** Name a measurable consequence, causal connection, or decision; otherwise remove the phrase.
- **Technical-writing exception:** “Indicating” and “signaling” can be precise terms in a protocol or diagnostic description.
- **Disposition:** Preserve them when they identify an actual technical signal.

### AS-06 — Importance inflation
- **Signal:** The text says an event is pivotal, a testament, vital, significant, or position-solidifying without supplying a concrete basis.
- **Reader harm:** It instructs the reader to value a fact rather than allowing the fact to establish its relevance.
- **Minimal remedy:** State the fact and its specific consequence, or omit the appraisal.
- **Technical-writing exception:** None for specifications or comparable technical prose.
- **Disposition:** Report every unsupported instance as a finding.

### AS-07 — Unnamed authority
- **Signal:** Claims lean on unspecified groups or evidence: “experts agree,” “studies show,” “widely regarded,” “reports suggest,” or “many argue.”
- **Reader harm:** The reader cannot assess, locate, or challenge the asserted authority.
- **Minimal remedy:** Cite or name the authority, or remove the unsupported attribution.
- **Technical-writing exception:** Check apparent conformance language before flagging it; it may be normative rather than evidentiary.
- **Disposition:** Do not mistake an established implementation requirement for a vague appeal to consensus.

### AS-08 — Interpretive commentary
- **Signal:** The author interrupts to say “the key point is,” “as you can see,” “this matters,” or “in other words” without adding clarification.
- **Reader harm:** Commentary displaces explanation and can leave a weak assertion unsupported.
- **Minimal remedy:** Delete clear redundancy; where clarity is missing, add the missing evidence or explanation.
- **Technical-writing exception:** Sparse navigational signposts in a long specification can improve orientation.
- **Disposition:** Flag empty interpretation, not useful navigation.

### AS-09 — Indirect role verbs
- **Signal:** “Serves as,” “acts as,” or “functions as” appears where “is” or a direct action verb states the relationship plainly.
- **Reader harm:** The indirect verb adds words and obscures the actual relationship.
- **Minimal remedy:** Use “is” or name the direct behavior.
- **Technical-writing exception:** “Serves as the default” may imply an overridable role unlike “is the default.”
- **Disposition:** Keep role language when that distinction carries semantics.

### AS-10 — Term rotation
- **Signal:** One concept receives alternating labels solely to avoid repetition, such as “server,” then “node,” then “host.”
- **Reader harm:** Readers may infer separate entities, roles, or scopes.
- **Minimal remedy:** Reuse the established term consistently.
- **Technical-writing exception:** None; a stable term is clearer even when repetition is visible.
- **Disposition:** Report inconsistent naming whenever the referent is intended to be identical.

### AS-11 — Negative runway
- **Signal:** Several statements say what an item is not before eventually saying what it is.
- **Reader harm:** The definition arrives late and forces readers through irrelevant alternatives.
- **Minimal remedy:** Lead with the positive definition.
- **Technical-writing exception:** Complete negative scopes, such as “This does NOT apply to,” can be necessary requirements.
- **Disposition:** Never flag an exhaustive exclusion that establishes normative boundaries.

### AS-12 — Emphatic fragments
- **Signal:** Fragmented, clipped prose attempts emphasis: “That’s all. The whole story.”
- **Reader harm:** The cadence manufactures weight without increasing precision.
- **Minimal remedy:** Combine the thought into complete, direct sentences.
- **Technical-writing exception:** None in technical documentation or specifications.
- **Disposition:** Report it when fragmentation is emphatic rather than a legitimate label or example.

### AS-13 — Template cadence
- **Signal:** Sentence frames, paragraph shapes, lengths, or habitual three-item lists repeat with mechanical regularity.
- **Reader harm:** Monotony makes relationships harder to distinguish and suggests a template over deliberate explanation.
- **Minimal remedy:** Vary syntax and list cardinality where doing so improves the presentation.
- **Technical-writing exception:** Parallel dictionary entries and repeated specification forms often aid comparison.
- **Disposition:** Flag only when variation improves clarity, not merely to create stylistic novelty.

### AS-14 — Rhetorical staging
- **Signal:** The prose uses “What if I told you,” “Think about it,” “Plot twist,” or a question immediately answered by the author.
- **Reader harm:** The device can patronize readers while adding no technical information.
- **Minimal remedy:** State the conclusion or fact directly.
- **Technical-writing exception:** None for technical prose.
- **Disposition:** Report the device unless the question is an actual prompt requiring reader action.

### AS-15 — Aphoristic exits
- **Signal:** A section ends with a metaphor, slogan, or “mic-drop” line rather than a concrete conclusion.
- **Reader harm:** Decoration substitutes for an actionable result or verifiable takeaway.
- **Minimal remedy:** Delete the line and end on the clearest factual statement or required action.
- **Technical-writing exception:** None in technical specifications.
- **Disposition:** Report it when the ending introduces no technical content.

### AS-16 — Redundant closings
- **Signal:** “In conclusion,” “ultimately,” or “overall” precedes a final paragraph that simply repeats prior material.
- **Reader harm:** The reader rereads information without gaining organization, a decision, or a next step.
- **Minimal remedy:** End at the last substantive point, or replace the recap with an action or decision.
- **Technical-writing exception:** A summary in a long specification may provide useful structure.
- **Disposition:** Flag only summaries that add neither navigation nor a new conclusion.

### AS-17 — Decorative formatting
- **Signal:** Emoji headings, ornamental mid-sentence bolding, needless bullets, or headings atop two-sentence sections dominate the presentation.
- **Reader harm:** Visual treatment competes with content and fragments the reader’s flow.
- **Minimal remedy:** Let structure follow informational need; use prose when it reads more directly.
- **Technical-writing exception:** Bold defined terms on first use and lists of API parameters are standard.
- **Disposition:** Flag decoration, not semantically useful formatting.

### AS-18 — Dash-driven cadence
- **Signal:** Em dashes cluster or become the default joiner for ordinary clauses and parentheticals.
- **Reader harm:** Repeated interruption produces a choppy, mannered rhythm.
- **Minimal remedy:** Prefer periods, commas, or parentheses; short copy normally needs none and long drafts rarely need more than one or two.
- **Technical-writing exception:** A genuine aside or abrupt break can be clearest with an em dash.
- **Disposition:** Judge frequency and function, never the mere presence of a dash.

### AS-19 — Uninformative intensifiers
- **Signal:** Words such as “really,” “truly,” “fundamentally,” “crucially,” “inherently,” “inevitably,” “deeply,” or “genuinely” add force but no precision.
- **Reader harm:** Empty emphasis blurs what degree, condition, or mechanism actually matters.
- **Minimal remedy:** Remove the modifier unless it supplies a specific, defensible qualification.
- **Technical-writing exception:** “Literally” can be exact; “generally” and “usually” may express necessary specification scope.
- **Disposition:** Do not flag adverbs that contribute technical meaning.

### AS-20 — Needlessly elevated diction
- **Signal:** A Latinate or businesslike verb replaces a plainer equivalent: “utilize,” “facilitate,” “leverage,” “endeavor,” or “commence.”
- **Reader harm:** The wording increases reading effort without improving the meaning.
- **Minimal remedy:** Prefer the familiar verb, such as “use,” “enable,” “try,” or “start.”
- **Technical-writing exception:** A domain may define “utilize” or “leverage” as terms of art.
- **Disposition:** In that case record INFO and offer the plain alternative rather than a warning.

### AS-21 — Content-free declarations
- **Signal:** The prose announces that implications are significant, stakes are high, or reasons are structural without naming them.
- **Reader harm:** Readers are told an unspecified conclusion instead of receiving the information needed to evaluate it.
- **Minimal remedy:** Identify the implication, stake, or cause concretely.
- **Technical-writing exception:** An introduction may preview importance before supplying detail later.
- **Disposition:** Flag only when the promised detail never arrives.
