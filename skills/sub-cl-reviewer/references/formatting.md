# Common Lisp Formatting, Comments, and Docstrings

## CL-14 — Two-Space Indentation Base
**Signal:** Indentation uses tab characters or advances by a width other than two spaces as the default nesting increment.
**Problem:** Inconsistent horizontal structure makes Lisp forms harder to scan and edits render differently across tools.
**Exception:** Semantic indentation (CL-18) overrides the two-space default for standard forms where editor convention dictates wider alignment — `let` bindings at four spaces, `cond` clauses on their own lines, etc. The two-space rule is the baseline; SLIME/SLY semantic indentation is authoritative for standard forms.
**Example:**
```lisp
;; Two-space baseline for ordinary calls:
(foo bar
  (baz qux))
;; Semantic override for let — bindings at four, body at two:
(let ((total 0))
  (incf total))
```

## CL-15 — Tight Parentheses and Stacked Closures
**Signal:** Forms contain padding next to parentheses, or a closing parenthesis occupies a line by itself.
**Problem:** Spaced parentheses obscure form boundaries, while isolated closers make nesting needlessly difficult to follow.
**Exception:** None.
**Example:**
```lisp
;; Avoid: ( foo bar )
;; Good:  (foo bar)
;; Stacked closers — don't put them on their own line:
;; Avoid:
;; (+ 1
;;    (* 2 3)
;;    )
;; Good:
(+ 1 (* 2 3))
```

## CL-16 — Top-Level Form Separation
**Signal:** Top-level definitions have no separator, multiple blank separators, or arbitrary blank lines inside short forms.
**Problem:** A uniform single blank line distinguishes independent definitions without fragmenting the file.
**Exception:** Closely coupled forms constituting one unit, such as a `defvar` and its `defpackage` export, may be adjacent.
**Example:**
```lisp
(defun start () :started)

(defun stop () :stopped)
```

## CL-17 — One-Hundred-Column Lines
**Signal:** Lines exceed 100 columns, unless the repository visibly applies a tighter 80- or 72-column convention.
**Problem:** Long lines impair side-by-side reading and produce unwieldy diffs.
**Exception:** Follow the project’s established shorter limit where one is evident.
**Example:**
```lisp
(process-request request
                 :timeout timeout
                 :retry-count retry-count)
```

## CL-18 — Semantic Standard-Form Indentation
**Signal:** Standard forms depart from SLIME/SLY-style semantic indentation or place unrelated clauses on crowded lines.
**Problem:** Conventional layout exposes a form’s roles—bindings, clauses, bodies, and branches—at a glance.
**Exception:** A custom macro may legitimately supply a `common-lisp-indent-function` indentation property.
**Example:**
```lisp
(let ((item (first items)))
  (if item
      (handle item)
      (report-empty)))
```

Use four spaces from the operator for `let` and `let*` binding pairs, then two for their bodies.
Put each `cond`, `case`, or `typecase` clause on its own line and indent its body beneath the clause.
Keep a short definition lambda list on its opening line; otherwise continue it cleanly and indent the body two spaces.
Place one `defclass` slot per line with slot options aligned; align major `loop` clauses beneath `loop` and indent nested clauses further.

## CL-19 — Purposeful Internal Blank Lines
**Signal:** A definition contains scattered empty lines, or short definitions use internal vertical spacing without a structural reason.
**Problem:** Random whitespace hides the real phases of a routine and weakens visual grouping.
**Exception:** Forms shorter than roughly 15 lines should normally have no internal blank lines.
**Example:**
```lisp
(defun run-job (job)
  (let ((state (prepare job)))

    (execute state)

    (cleanup state)))
```

## CL-20 — Semicolon Scope Hierarchy
**Signal:** The number of leading semicolons does not correspond to the scope of the comment.
**Problem:** Readers cannot readily tell whether prose describes the file, a section, a local block, or one expression.
**Exception:** None; use the hierarchy consistently.
**Example:**
```lisp
;;;; File overview
;;; Request processing
  ;; Preserve order for protocol compatibility.
  (send request) ; May block on the peer.
```

Use `;;;;` at column zero for file headers or major divisions, and `;;;` at column zero for top-level sections.
Use `;;` within forms at the code’s indentation; reserve `;` for an end-of-line note separated from code by one space.

## CL-21 — Docstrings for Public Definitions
**Signal:** Exported functions, macros, generic functions, types, classes, packages, or externally meaningful slots lack documentation strings.
**Problem:** Public callers need an interface contract available through standard Lisp introspection.
**Exception:** Internal helpers may instead use a nearby `;;` explanation when that is more useful.
**Example:**
```lisp
(defun open-session (endpoint)
  "Open a session to ENDPOINT and return it."
  (make-session endpoint))
```

A public docstring should state purpose, argument meanings, return value, side effects, and conditions signaled when applicable.

## CL-22 — Structured Docstrings
**Signal:** A docstring starts with detail rather than a summary, omits important contract facts, or becomes a verbose implementation narrative.
**Problem:** Predictable structure lets users find interface behavior quickly in documentation tools.
**Exception:** Very small, self-evident public accessors may need only a concise summary.
**Example:**
```lisp
(defun parse-header (stream)
  "Read and parse an HTTP header from STREAM.
Returns a plist of header fields. Signals PARSE-ERROR
if the header is malformed."
  ...)
```

Start with one concise sentence; then add paragraphs for arguments (with parameter names capitalized), returns, side effects, and conditions.

## CL-23 — Explain Reasons, Not Mechanics
**Signal:** A comment merely translates the immediately following expression into English.
**Problem:** Such narration drifts out of date and adds no information beyond the code itself.
**Exception:** A terse mechanical note is acceptable when the code cannot make an external protocol or workaround apparent.
**Example:**
```lisp
;; Bad: Add 1 to x.
;; Good: Offset by 1 because protocol indices are 1-based.
(incf x)
```

Prefer comments that record a non-obvious decision, constraint, trade-off, or subtle failure mode.

## CL-24 — No Commented-Out Code
**Signal:** Disabled executable forms remain in ordinary comments under version control.
**Problem:** Dead snippets confuse maintenance and duplicate information already retained by history.
**Exception:** Code may be briefly commented during active debugging, but it must not be committed that way.
**Example:**
```lisp
#+(or)
(expensive-experiment input)

#-(and)
(legacy-path input)
```

Remove obsolete code; use read-time conditionals such as `#+(or)` or `#-(and)` only when conditional compilation is intentional.
