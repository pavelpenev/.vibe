# Testing, Benchmarks, CI, and Layout Rules

### CL-141 — Standard project layout
**Requirement:** The repository has a README, LICENSE, ASDF system, `src/`, and `tests/`.
**Problem:** Missing or improvised structure makes a Common Lisp project harder to discover and build.
**Exception:** A published generated artifact may intentionally use a different layout.
**Example:**
```text
README.md  LICENSE  myapp.asd  src/  tests/
```

### CL-142 — Source and test separation
**Requirement:** Library implementation and tests live in distinct directories or systems.
**Problem:** Tests shipped in `src/` can become accidental runtime dependencies.
**Exception:** A tiny executable may deliberately keep its test harness beside its entrypoint.
**Example:**
```text
src/reader.lisp   tests/reader.lisp   myapp-test.asd
```

### CL-143 — Predictable test-system names
**Requirement:** The test system follows a recognizable name and loads through the normal ASDF path.
**Problem:** An opaque or inseparable test system frustrates automation and independent diagnosis.
**Exception:** Retain an established public name when changing it would break documented users.
**Example:**
```lisp
(asdf:defsystem "myapp-test"
  :depends-on ("myapp" "fiveam"))
```

### CL-144 — Generated output stays out of source
**Requirement:** Documentation output, FASLs, images, and build products are absent from source trees.
**Problem:** Committed generated files obscure review and create stale or platform-specific artifacts.
**Exception:** Include generated material only when publication of that material is an explicit project goal.
**Example:**
```text
src/reader.lisp   ; not src/reader.fasl or src/api.html
```

### CL-145 — Logical definition order
**Requirement:** A file moves from package and declarations toward methods, implementation, and public entrypoints.
**Problem:** Scattered related definitions increase the effort needed to understand dependencies.
**Exception:** Keep protocol declarations near the API when that ordering improves discoverability.
**Example:**
```lisp
(defpackage ...) (define-condition ...) (defgeneric ...) (defun read-input ...)
```

### CL-146 — Descriptive test names
**Requirement:** Every test has a stable name that states the behavior under examination.
**Problem:** Anonymous or numeric labels make failures difficult to identify without opening the body.
**Exception:** Framework-generated names are acceptable when the surrounding suite supplies the missing context.
**Example:**
```lisp
(test parses-empty-input (is (null (parse ""))))
```

### CL-147 — Organized test suites
**Requirement:** Tests are grouped by feature, subsystem, or domain, with nested suites where useful.
**Problem:** One large flat assertion file hides coverage boundaries and becomes difficult to navigate.
**Exception:** A genuinely small project need not manufacture hierarchy; flag disorder, not file size alone.
**Example:**
```lisp
(def-suite parser) (in-suite parser) (test rejects-invalid-token ...)
```

### CL-148 — Failure diagnostics
**Requirement:** Failed checks expose expected and actual values plus relevant input context.
**Problem:** A bare assertion forces every failure investigation to reproduce the test manually.
**Exception:** A framework assertion is sufficient when it already prints complete diagnostics.
**Example:**
```lisp
(is (= expected actual) "input=~S expected=~S actual=~S" input expected actual)
```

### CL-149 — Quiet CI execution
**Requirement:** The test command supports batch or quiet operation and emits output only when useful.
**Problem:** Unconditional progress and debug printing obscures failures in automated logs.
**Exception:** Output is appropriate when console output itself is the behavior under test.
**Example:**
```lisp
(asdf:test-system :myapp-test) ; no unconditional FORMAT progress stream
```

### CL-150 — Pure and side-effecting tests separated
**Requirement:** Tests that alter globals, files, processes, or threads are isolated from pure checks.
**Problem:** Shared mutable environment makes unrelated tests order-sensitive and harder to repeat.
**Exception:** Deliberate integration suites may share setup when teardown is explicit and reliable.
**Example:**
```text
tests/unit/   tests/integration/   ; global-state and thread tests stay isolated
```

### CL-151 — Individually runnable tests
**Requirement:** A single test can run without relying on an earlier test's definitions or mutations.
**Problem:** Sequence-dependent tests produce misleading failures and prevent focused debugging.
**Exception:** Shared immutable fixture construction is fine when the framework manages it per test.
**Example:**
```lisp
(test lookup-missing-key (with-fixture (fresh-table) (is (null (lookup :x)))))
```

### CL-152 — Benchmarks separate from tests
**Requirement:** Performance experiments reside under `benchmarks/` or in a dedicated ASDF system.
**Problem:** Timing code mixed with correctness assertions makes both suites slower and less predictable.
**Exception:** A test may enforce a functional complexity property without measuring wall-clock time.
**Example:**
```text
benchmarks/parser.lisp   tests/parser.lisp
```

### CL-153 — Benchmark context is recorded
**Requirement:** Results identify implementation, optimization settings, hardware, inputs, warm-up, and repetitions.
**Problem:** A naked timing number cannot be compared or reproduced responsibly.
**Exception:** Exploratory local measurements may omit metadata, but committed results should not.
**Example:**
```lisp
(format t "SBCL ~A, speed=3, input=~D, runs=~D~%" *version* 10000 30)
```

### CL-154 — Tolerant performance regression checks
**Requirement:** Performance gates use a justified range rather than one exact elapsed-time cutoff.
**Problem:** Scheduler and machine variation can make hard timing thresholds fail healthy builds.
**Exception:** A controlled benchmark environment may use strict limits when its stability is documented.
**Example:**
```lisp
(assert (< measured (* baseline 1.20))) ; allow 20 percent variance
```

### CL-155 — Multiple implementation coverage
**Requirement:** A portable library runs CI on SBCL and at least one additional implementation.
**Problem:** Single-implementation CI can hide portability defects until users encounter them.
**Exception:** Document an intentional implementation restriction and test the supported target explicitly.
**Example:**
```yaml
matrix:
  lisp: [sbcl, ccl]
```

### CL-156 — Unexpected warnings fail CI
**Requirement:** Compilation keeps warnings visible and treats unanticipated warnings as failures.
**Problem:** Global warning suppression lets interface mistakes and portability issues accumulate unnoticed.
**Exception:** A narrowly documented, known warning may be locally excluded with an explanation.
**Example:**
```lisp
(handler-bind ((warning #'error)) (asdf:load-system :myapp))
```

### CL-157 — Reproducible dependency selection
**Requirement:** CI uses a lockfile, pinned Qlot/CLPM environment, or named distribution snapshot.
**Problem:** Floating dependency resolution means the same commit may build differently over time.
**Exception:** A deliberately rolling development job may float versions, but release checks should be pinned.
**Example:**
```text
qlfile.lock   ; dependency versions are resolved from the committed lock
```

### CL-158 — ASDF test-op is the CI entrypoint
**Requirement:** Local and CI verification invoke the project's ASDF test operation. A failing assertion or unhandled test condition must cause the verification command to exit unsuccessfully.
**Problem:** Ad-hoc scripts can skip systems, setup, or tests that the declared project interface includes; invoking `test-op` without checking its return status can mask failures.
**Exception:** Additional lint or matrix jobs may supplement, but should not replace, the test operation.
**Example:**
```lisp
(asdf:test-system :myapp-test)
```
