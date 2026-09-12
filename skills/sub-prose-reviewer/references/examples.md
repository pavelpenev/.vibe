# Prose reviewer examples
## Technical Writing
### False agency — **Case:** A retry decision is attributed to a system rather than its policy.
**Before:**
```
The system decides to retry the request after a timeout.
```
**After:**
```
The retry policy triggers a new request after a timeout.
```
**Rule:** TW-02
**Note:** Names the rule that causes the behavior rather than assigning judgment to the system.
### Front-load the result — **Case:** The result is buried after procedural background.
**Before:**
```
The router evaluates the path prefix, compares the tenant identifier, and checks the route table. The request is rejected when no route matches.
```
**After:**
```
The router rejects a request when no route matches. To determine a match, it evaluates the path prefix, tenant identifier, and route table.
```
**Rule:** TW-05
**Note:** The reader learns the outcome before the supporting mechanism.
### Stacked modifiers — **Case:** Several modifiers obscure the storage relationship.
**Before:**
```
The default configurable persistent key-value store retains session state.
```
**After:**
```
By default, session state is retained in a persistent key-value store. Implementations can configure that store.
```
**Rule:** TW-17
**Note:** Separating the properties makes their relationships explicit.
### Remove minimizing language — **Case:** An instruction characterizes a potentially consequential operation as easy.
**Before:**
```
Simply set the flag to enable request signing.
```
**After:**
```
Set the flag to enable request signing.
```
**Rule:** TW-19
**Note:** The instruction retains its action without judging its difficulty.
### Informative heading — **Case:** A generic section title conceals its topic.
**Before:**
```
## Overview
```
**After:**
```
## Request Routing Model
```
**Rule:** TW-10
**Note:** The replacement lets readers predict the section's contents.
### Consistent terminology — **Case:** Three names refer to the same request-processing component.
**Before:**
```
The endpoint receives the request. The service selects a route. The handler returns the response.
```
**After:**
```
The request handler receives the request, selects a route, and returns the response.
```
**Rule:** TW-12
**Note:** A single term prevents readers from inferring separate components.
## Anti-Slop
### Remove throat-clearing — **Case:** A preface delays a normative statement.
**Before:**
```
It is worth noting that the implementation must validate all inputs.
```
**After:**
```
The implementation must validate all inputs.
```
**Rule:** AS-01
**Note:** The substantive requirement appears immediately.
### Security caveat counterexample — **Case:** An attention cue introduces a security-critical limitation.
**Before:**
```
It is important to note that key rotation does not revoke tokens issued before the rotation timestamp.
```
**After:** No edit
**Rule:** AS-01 (exception; INFO)
**Note:** The cue deliberately foregrounds a security-relevant caveat and should be recorded as INFO, not a warning.
### Remove importance puffery — **Case:** The prose appraises an API release without giving a technical consequence.
**Before:**
```
This API marks a pivotal moment in our platform evolution.
```
**After:**
```
This API adds batch retrieval for audit records.
```
**Rule:** AS-06
**Note:** The factual capability lets readers assess relevance themselves.
### Avoid synonym cycling — **Case:** Different labels are used for one gateway component.
**Before:**
```
The gateway forwards requests. The proxy applies rate limits. The intermediary logs responses.
```
**After:**
```
The gateway forwards requests, applies rate limits, and logs responses.
```
**Rule:** AS-10
**Note:** Repetition is clearer than implying three distinct intermediaries.
### Negative scope counterexample — **Case:** The specification states exhaustive exclusions.
**Before:**
```
This specification does NOT apply to: embedded systems, real-time controllers, or safety-critical firmware.
```
**After:** No edit
**Rule:** AS-11 (exception)
**Note:** This is a complete normative boundary, not a delayed positive definition.
### Em-dash counterexample — **Case:** An em dash isolates a genuine parenthetical qualification.
**Before:**
```
The client MUST preserve the original request identifier — even when a retry uses a new connection.
```
**After:** No edit
**Rule:** AS-18 (exception)
**Note:** One dash clearly introduces a relevant aside; it is not dash-driven cadence.
### Replace superficial analysis — **Case:** A trailing participle claims a quality without explaining the mechanism.
**Before:**
```
The retry mechanism handles transient failures, highlighting the system's resilience.
```
**After:**
```
The retry mechanism handles transient failures by reissuing requests with exponential backoff.
```
**Rule:** AS-05
**Note:** The revision supplies the causal behavior instead of an unsupported appraisal.
## Normative Language
### Split stacked requirements — **Case:** Independent requirements at three levels appear in one sentence.
**Before:**
```
Implementations MUST validate the header and SHOULD log malformed entries and MAY skip processing.
```
**After:**
```
1. Implementations MUST validate the header.
2. Implementations SHOULD log each malformed entry.
3. Implementations MAY skip processing after detecting a malformed header.
```
**Rule:** NL-10
**Note:** Each obligation is independently visible and testable.
### Make the requirement testable — **Case:** The requirement uses an indeterminate quality.
**Before:**
```
The implementation MUST be robust against malformed input.
```
**After:**
```
The implementation MUST reject malformed input with a 400 response.
```
**Rule:** NL-11
**Note:** A conformance test can now observe the required response.
### BCP 14 keyword consistency — **Case:** Comparable RFC 8174 requirements mix uppercase and lowercase modality.
**Before:**
```
A client MUST send the Content-Type header. A server must reject requests without it.
```
**After:**
```
A client MUST send the Content-Type header. A server MUST reject requests without it.
```
**Rule:** NL-01
**Note:** Under RFC 8174, lowercase “must” is potentially non-normative; use uppercase if obligation is intended.
### CLHS semantic distinction — **Case:** A documentation obligation is accidentally imposed on permitted variation.
**Before:**
```
The order of equal-priority handlers is implementation-defined.
```
**After:**
```
Author review required: determine whether the order is implementation-defined (and must be documented) or implementation-dependent (and need not be documented).
```
**Rule:** NL-02
**Note:** The terms have different CLHS consequences, so a reviewer must flag high semantic risk rather than choose one.
### Defined-term protection counterexample — **Case:** “Endpoint” is a defined term in the terminology section.
**Before:**
```
Each endpoint MUST expose a health resource.
```
**After:** No edit
**Rule:** NL-13
**Note:** Replacing the defined term “endpoint” with “URL” would alter contractual vocabulary.
### Well-formed requirement counterexample — **Case:** Scope, observable behavior, and rationale are distinct.
**Before:**
```
For authenticated POST requests, the server MUST return 401 when the Authorization header is absent. Rationale: Returning 401 allows clients to obtain credentials before retrying.
```
**After:** No edit
**Rule:** NL-11, NL-12 — **Note:** The requirement has clear scope and a testable result; the nonbinding rationale is separated.
