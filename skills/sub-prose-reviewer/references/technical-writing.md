# Technical writing review rubric

Apply these rules as diagnostics, not mechanical edits. Report only issues that reduce clarity, precision, or usability in context.

## TW-01 — Prefer active voice
- **Diagnostic question:** Does an active construction make the responsible actor clearer?
- **Signal:** Passive clauses obscure an actor that matters to the reader.
- **Exception:** Keep passive voice when the actor is irrelevant, the affected object is central, or the process matters most; never flag it in normative requirements or error specifications.
- **Example:** Before: “The file is validated by the service.” After: “The service validates the file.”

## TW-02 — Avoid false agency
- **Diagnostic question:** Does an inanimate subject appear to perform a human judgment or communication?
- **Signal:** Phrases such as “the data tells us” or “the system decides” conceal the actual rule or actor.
- **Exception:** Retain conventional domain shorthand, such as “the compiler infers” or “the runtime manages.”
- **Example:** Before: “The data tells us the request failed.” After: “The error field indicates that the request failed.”

## TW-03 — Prefer direct subjects to empty openers
- **Diagnostic question:** Would naming the subject make a “there is/are” opening more direct?
- **Signal:** An existential opener delays the thing that performs or has the relevant property.
- **Exception:** Use it when introducing an enumeration in a specification, such as “There are three modes.”
- **Example:** Before: “There are errors returned by the parser.” After: “The parser returns errors.”

## TW-04 — Identify accountable actors
- **Diagnostic question:** Does the reader need to know who or what caused, owns, or must take an action?
- **Signal:** Actorless statements hide operational responsibility or the source of an outcome.
- **Exception:** Do not invent an actor when evidence is unavailable or attribution is immaterial.
- **Example:** Before: “Mistakes were made.” After: “The server returned 500 for 3% of requests.”

## TW-05 — Lead with the point
- **Diagnostic question:** Does the opening state the conclusion, result, or action the reader needs?
- **Signal:** A paragraph postpones its main instruction or finding behind background detail.
- **Exception:** Narrative and rationale sections may reasonably build toward a conclusion.
- **Example:** Before: “After several checks, the migration succeeded.” After: “The migration succeeded after several checks.”

## TW-06 — Give prerequisites before steps
- **Diagnostic question:** Can readers learn what they need before being told what to do?
- **Signal:** Credentials, tools, permissions, or inputs appear only after the procedure begins.
- **Exception:** Omit prerequisites that are guaranteed by the surrounding workflow.
- **Example:** Before: “Run the command; you need an admin token.” After: “Before running the command, obtain an admin token.”

## TW-07 — Put conditions ahead of outcomes
- **Diagnostic question:** Would presenting the condition first make the consequence easier to interpret?
- **Signal:** A conditional qualifier trails an outcome and changes how it must be read.
- **Exception:** Put the outcome first when it is short and its condition is long or complex.
- **Example:** Before: “The job retries, if the endpoint times out.” After: “If the endpoint times out, the job retries.”

## TW-08 — Keep one governing idea per paragraph
- **Diagnostic question:** Does every sentence develop the same claim, task, or explanation?
- **Signal:** A paragraph shifts from one independent topic to another without a structural break.
- **Exception:** Brief transitions may connect closely coupled ideas.
- **Example:** Split deployment instructions from the separate explanation of retention policy.

## TW-09 — Split overloaded paragraphs
- **Diagnostic question:** Is the paragraph difficult because it contains too many conceptual moves?
- **Signal:** A paragraph beyond roughly six to eight sentences introduces multiple claims, procedures, or exceptions.
- **Exception:** Length alone is not a defect when each sentence advances one tightly unified point.
- **Example:** Separate “how retries work” from “how to tune retry limits.”

## TW-10 — Make headings informative
- **Diagnostic question:** Can a reader predict the section’s purpose from its heading alone?
- **Signal:** Generic labels such as “Overview” or “Notes” hide the topic or reader action.
- **Exception:** A broad heading is acceptable when its scope is established by a higher-level outline.
- **Example:** Before: “Notes.” After: “Retry limits and backoff behavior.”

## TW-11 — Use sentence case in headings
- **Diagnostic question:** Do headings follow sentence case consistently?
- **Signal:** Every major word is capitalized without a project convention requiring title case.
- **Exception:** Preserve proper nouns, API names, and an explicitly required house style.
- **Example:** Before: “Configure The Cache.” After: “Configure the cache.”

## TW-12 — Use one term for one concept
- **Diagnostic question:** Does the text use a stable name for the same thing?
- **Signal:** Synonyms such as server, node, and host rotate without explaining a distinction.
- **Exception:** Different terms are correct when they deliberately identify different layers, such as a process versus a machine.
- **Example:** Define “node” as a machine, then avoid using it to mean the server process.

## TW-13 — Define terms once, then retain them
- **Diagnostic question:** Is an unfamiliar technical term explained at its first meaningful appearance?
- **Signal:** A term arrives without context or is repeatedly reintroduced with changing wording.
- **Exception:** Skip definitions for the intended audience’s established vocabulary.
- **Example:** “A lease is a time-limited ownership record.” Use “lease” thereafter.

## TW-14 — Expand unfamiliar acronyms first
- **Diagnostic question:** Does the first occurrence give readers the acronym’s full name?
- **Signal:** A specialized initialism appears before its expansion.
- **Exception:** Widely understood terms such as API, URL, and HTTP normally need no expansion.
- **Example:** “Use mutual TLS (mTLS) for service connections”; use “mTLS” later.

## TW-15 — Remove empty phrasing
- **Diagnostic question:** Does each word contribute meaning, emphasis, or necessary precision?
- **Signal:** Inflated phrases include “in order to,” “has the ability to,” or “due to the fact that.”
- **Exception:** Keep additional wording when it distinguishes a formal requirement or technical constraint.
- **Example:** Before: “In order to start, the client…” After: “To start, the client…”

## TW-16 — Prefer verbs over abstract noun phrases
- **Diagnostic question:** Can a noun-based action become a direct verb without changing meaning?
- **Signal:** Phrases such as “perform an analysis” and “make a determination” bury the action.
- **Exception:** Keep established technical nouns, including configuration and instantiation, when they name recognized concepts.
- **Example:** Before: “Perform an analysis of logs.” After: “Analyze the logs.”

## TW-17 — Untangle stacked modifiers
- **Diagnostic question:** Do several pre-noun modifiers force readers to guess the relationship among them?
- **Signal:** Three or more adjectives or noun modifiers precede a single noun.
- **Exception:** Retain compact established names when readers recognize the phrase as a term of art.
- **Example:** Before: “high-volume real-time event processing pipeline.” After: “pipeline for processing high-volume events in real time.”

## TW-18 — Test paragraphs for necessary content
- **Diagnostic question:** Would deleting this paragraph remove a fact, decision, example, or reasoning step?
- **Signal:** Restatement, throat-clearing, or unsupported reassurance adds no new value.
- **Exception:** Keep brief orientation when it helps readers navigate a complex section.
- **Example:** Remove “This section explains the following details” when the heading already does so.

## TW-19 — Avoid minimizing difficulty
- **Diagnostic question:** Does the wording assume a task is easier than it may be for the reader?
- **Signal:** “Simply,” “just,” “easily,” “quickly,” and “straightforward” add judgment rather than instruction.
- **Exception:** Keep the word when it states a literal, verifiable behavior, such as “the command simply returns 0.”
- **Example:** Before: “Just update the schema.” After: “Update the schema, then run the migration.”

## TW-20 — Avoid condescension
- **Diagnostic question:** Does the text dismiss knowledge that a reader may not have?
- **Signal:** “Obviously,” “of course,” “as everyone knows,” or “it goes without saying” precede an explanation.
- **Exception:** None in reader-facing technical prose; state the fact plainly if it matters.
- **Example:** Before: “Of course, tokens expire.” After: “Tokens expire after 24 hours.”

## TW-21 — Choose lists for the right material
- **Diagnostic question:** Are parallel items or ordered steps presented as a list, while reasoning remains prose?
- **Signal:** Dense sequences are buried in prose, or bullets replace an argument or nuanced comparison.
- **Exception:** Short inline sequences are fine when scanning is not important.
- **Example:** List installation steps; explain trade-offs between storage engines in paragraphs.

## TW-22 — Introduce lists with a full sentence
- **Diagnostic question:** Does the sentence before a list stand as a complete grammatical sentence?
- **Signal:** A fragment depends on list items to finish its syntax.
- **Exception:** Preserve a fragment only when a controlled documentation template explicitly requires it.
- **Example:** Before: “Required:” After: “Provide the following required values:”

## TW-23 — Make references and links precise
- **Diagnostic question:** Can readers identify the exact destination and its relevance before following it?
- **Signal:** Vague cues such as “see the documentation,” “click here,” or “this link” hide the target.
- **Exception:** A nearby, unambiguous embedded link may need no repeated locator.
- **Example:** Before: “See the documentation.” After: “See Section 4.2, “Error handling.””
