---
name: testing
description: "Single testing skill for generation and review, loaded by the executor when writing tests and by the code-reviewer when reviewing them. Generate high-value, fast, isolated, parallel-safe tests for a single file/module or a bounded subsystem boundary; guard against over-testing (no redundant or trivial tests, no timeouts/sleeps/flaky patterns). Test execution is delegated to the empirical-reviewer. Repo-wide generation is out of scope."
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - agents_spawn
  - skill
---

# Test Generator

Generate tests for a single file/module, or bounded characterization tests at an explicit subsystem boundary. Repo-wide test generation is out of scope. Read the project's AGENTS.md first for the test framework, commands, and conventions — those win over anything here.

## Guard against over-testing

Tests are only worth writing when they protect real behavior. Before writing each test, ask: *would this test catch a realistic bug?* If not, skip it.

- **No trivial tests**: do not test getters/setters, pass-through wrappers, framework boilerplate, or behavior the type system already guarantees.
- **No redundancy**: one test per behavior, not one per code path. Do not duplicate coverage that existing tests already provide — review them first (Step 4).
- **High-value targets first**: error handling and edge cases around the module's actual contracts, boundary conditions, state transitions, and the failure modes seen in past bugs (see git log/issues if relevant).
- **Prefer characterization tests at subsystem boundaries** over deep internals: test what the module promises, not how it is implemented.
- If you end up with fewer tests than expected, that is fine — a small sharp suite beats a large noisy one. Say so in the output instead of padding.

## Fast, isolated, parallel-safe tests

Tests must be simple unit tests that run isolated and in parallel without becoming flaky or slow:

- **No timeouts, sleeps, or wall-clock dependencies.** Never `sleep` to wait for async behavior — use the framework's synchronization primitives (mocks, fakes, latches) instead. Tests must not depend on real time, real network, real databases, or real files outside the scratchpad.
- **No shared state between tests.** Each test sets up and tears down its own fixtures. No global mutable state, no reliance on execution order, no port or file collisions — use per-test temp dirs and ephemeral resources.
- **Deterministic and fast.** A test that needs more than a few seconds is a red flag; prefer a smaller, more focused case. Flaky-by-construction patterns (random inputs without a seed, timing races, uncontrolled concurrency) are out.
- **Parallel-safe by construction.** The suite must pass under the runner's parallel mode (e.g. `pytest -n auto`, `prove -j`). If a test cannot be made parallel-safe, it does not belong in the unit suite — say so in the output.

## Steps

1. **Parse and validate scope.** Target file(s)/boundary must be explicit. If scope is broad or unclear, narrow it or report what is missing.
2. **Determine context.** Detect the test framework from existing files/config; read AGENTS.md for the test command and conventions.
3. **Analyze the target code.** Identify the public contract: inputs, outputs, error cases, side effects, state.
4. **Review existing tests** for the module/subsystem to avoid duplication; note gaps.
5. **Generate tests** using AAA (arrange/act/assert), framework naming conventions, and a sensible mocking strategy (mock at system boundaries, not internals).
6. **Write the test file(s)** next to the existing test layout.
7. **Self-review** the generated tests against the over-testing guard above: every test must earn its place.
8. **Delegate execution to the empirical-reviewer** — do not claim tests pass without a run:

```text
agents_spawn(config_name="empirical-reviewer", prompt="Run the test suite for <module>: <command from AGENTS.md or framework default>, including the new tests in <file>. Report pass/fail with observed output, and root-cause any failure (load the debugging skill if needed).")
```

9. **Output** a short report: files created, behaviors covered, behaviors deliberately not tested (and why), test run result as reported by the empirical-reviewer.

## Quality gates

- [ ] Every test maps to a real behavior or failure mode — no trivial or redundant tests.
- [ ] Every test is isolated and parallel-safe: no timeouts/sleeps, no wall-clock or shared-state dependencies, no external services.
- [ ] Existing tests were reviewed; no duplicated coverage.
- [ ] Framework and naming conventions match the project.
- [ ] Tests were actually run by the empirical-reviewer; result reported verbatim.

## Red flags

- Auto-generated or vendored code: skip with a note.
- No test runner detectable: report instead of inventing one.
- Target is a boundary you cannot characterize: say so, propose the narrower target.

# Reviewing tests

The code-reviewer loads this same skill when reviewing test code. Review read-only; report findings per the shared review contract (severity, file:line, one row per finding), and re-check prior finding IDs when supplied (Resolved / Persisting / Unverifiable).

Apply the nine review dimensions as a checklist, in priority order:

| Dimension | Practical question |
|---|---|
| Behavioral correctness | Do setup, action, and outcome substantiate the stated claim? |
| Assertion strength | Would a plausible wrong result or omitted side effect fail? |
| Coverage | Are relevant boundaries, failure paths, and invalid inputs protected? |
| Isolation/determinism | Can it run alone, reordered, and in parallel where supported? |
| Dependency fidelity | Do doubles preserve the relevant contract; do integration tests cross their claimed boundary? |
| Fixture lifecycle | Are scope, ownership, cleanup, and partial-setup failure handled? |
| Speed | Is there demonstrable avoidable cost without a confidence benefit? |
| Readability | Can a reader trace arrange-act-assert and diagnose failure? |
| Maintainability | Would behavior-preserving changes break the test unnecessarily? |

Investigate these anti-patterns (prompts, not bans — report demonstrated harm, not mere pattern presence): false-green oracles (tautologies, expected values computed through the same faulty path, truthiness instead of required content); missing verification (unobserved side effects, unreached assertions, unawaited operations, broad exception acceptance); implementation coupling (private structure, call order, duplicated logic); flakiness/interdependence (shared mutable state, ordering, fixed ports, sleeps, uncontrolled time/randomness); general fixtures/mystery guests; opaque tests; signal-erasing maintenance (weakened assertions, unjustified skips/xfails, blanket retries, unexamined snapshot updates).

Apply the test-level overlay matching each test's level — unit (focused behavioral cases, deterministic, doubles isolate rather than replace the behavior under test), integration (exercise the actual claimed boundary: config, schema, transactions, serialization, dependency versions), end-to-end (meaningful user outcomes, resilient locators, independent sessions, condition-based waits, lifecycle cleanup).
