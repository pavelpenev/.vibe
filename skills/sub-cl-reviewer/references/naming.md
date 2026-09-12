# Naming and Package Conventions

## CL-01 — Lowercase, hyphen-separated symbols
**Signal:** Look for camelCase, underscores, mixed-case spellings, or joined words in symbols.
**Problem:** Uniform lowercase hyphenation makes word boundaries and repository searches predictable.
**Exception:** A foreign-function binding may retain the foreign API's established spelling.
**Example:**
```lisp
;; Avoid: (defun parseJSON_data () ...)
(defun parse-json-data () ...)
```

## CL-02 — Spell out names
**Signal:** Flag unexplained shortenings such as `db-conn` or `cfg-mgr` in public or nonlocal code.
**Problem:** Expanded names communicate domain meaning without forcing readers to decode local jargon.
**Exception:** Tiny, unmistakable scopes may use `i` or `x`; established CL names such as `defun`, `car`, `cdr`, and `nth` remain idiomatic.
**Example:**
```lisp
;; Avoid: (defun open-db-conn () ...)
(defun open-database-connection () ...)
```

## CL-03 — Predicate endings
**Signal:** Check boolean-returning function names for `-p` on multiword names and `p` on one-word names.
**Problem:** A consistent ending tells callers that the result is intended as a truth test.
**Exception:** Do not use `?` or `-?` as alternate predicate markers.
**Example:**
```lisp
;; Avoid: (defun queue-empty? (queue) ...)
(defun queue-empty-p (queue) ...)
```

## CL-04 — Earmuffs for special variables
**Signal:** Dynamic or special bindings should have names enclosed by asterisks.
**Problem:** Earmuffs immediately distinguish ambient state from ordinary lexical bindings.
**Exception:** Lexical variables and constants must not acquire earmuffs merely for emphasis.
**Example:**
```lisp
(defvar *current-request* nil)
(let ((current-request request)) ...)
```

## CL-05 — Plus signs for constants
**Signal:** Names introduced with `defconstant` should begin and end with `+`.
**Problem:** The delimiter identifies immutable, globally named values at the use site.
**Exception:** Variables use earmuffs, not plus signs; constants do not use earmuffs.
**Example:**
```lisp
;; Avoid: (defconstant *maximum-retries* 3)
(defconstant +maximum-retries+ 3)
```

## CL-06 — `with-` and `call-with-` pairs
**Signal:** Resource, dynamic-context, and scoped-execution macros should be named `with-foo` and normally call `call-with-foo`.
**Problem:** The macro owns convenient binding syntax while the function keeps semantic work testable and reusable.
**Exception:** Omit `call-with-` when a macro is genuinely trivial and expands to one form.
**Example:**
```lisp
(defmacro with-connection ((connection) &body body) ...)
(defun call-with-connection (function) ...)
```

## CL-07 — `do-` versus `ensure-`
**Signal:** Inspect prefixed operations: `do-foo` should repeat or iterate; `ensure-foo` should establish or confirm a state.
**Problem:** Distinct verbs prevent callers from guessing whether an operation loops, mutates, or is safe to repeat.
**Exception:** Use another verb when neither repeated execution nor idempotent establishment describes the operation.
**Example:**
```lisp
(defun do-pending-jobs () ...)
(defun ensure-cache-directory () ...)
```

## CL-08 — No package name duplicated in symbols
**Signal:** Flag symbols that repeat their package identity, such as `myapp-database-connection` inside package `myapp.database`.
**Problem:** Repetition lengthens call sites without adding useful distinction in the current namespace.
**Exception:** Keep the prefix when it represents a real sub-namespace concept rather than package branding.
**Example:**
```lisp
;; In MYAPP.DATABASE, prefer:
(defun database-connection () ...)
```

## CL-08b — No special marking for internal symbols
**Signal:** Flag prefix or suffix characters used to distinguish internal helpers, such as `%parse-header`, `_internal-sort`, or `render%-table`.
**Problem:** Package boundaries already separate public from private symbols — `:export` controls visibility. Decorating names with `%`, `_`, or other markers duplicates that mechanism, adds noise, and breaks the lowercase-hyphen naming convention.
**Exception:** foreign function bindings may use a `%` prefix to distinguish the low-level CFFI binding from its Lisp wrapper (e.g., `%open-fd` is the CFFI binding, `open-fd` is the Lisp wrapper). This is the only permitted use of `%` as a naming marker.
**Example:**
```lisp
;; Avoid: (defun %parse-header (stream) ...)
;; Avoid: (defun _internal-sort (sequence) ...)
;; Instead: plain name, kept unexported in the package
(defun parse-header (stream) ...)
;; If parse-header is not exported, callers cannot reach it
;; via myapp:parse-header — that is the intended access control.
```

## CL-09 — Deliberate, narrow exports
**Signal:** Review package definitions for a small explicit `:export` list and unintended public symbols.
**Problem:** A restrained external API preserves freedom to refactor implementation details.
**Exception:** A package designed as a broad facade may intentionally export a larger, still curated interface.
**Example:**
```lisp
(defpackage #:myapp.api
  (:use #:cl) (:export #:start-server #:stop-server))
```

## CL-10 — Avoid `::` in production
**Signal:** Search production sources for `package::internal-symbol` references.
**Problem:** Double-colon access bypasses package boundaries and couples clients to implementation details.
**Exception:** Test packages may use `::` to exercise non-exported behavior directly.
**Example:**
```lisp
;; Avoid: (storage::flush-cache cache)
(storage:flush-cache cache)
```

## CL-11 — Import selected symbols
**Signal:** When only a few names are needed, prefer `:import-from` to a broad `:use` clause.
**Problem:** Explicit imports show provenance and reduce accidental name conflicts.
**Exception:** `:use` suits packages such as `:cl` whose vocabulary is broadly needed; package-inferred `:use-reexport` is intentional.
**Example:**
```lisp
(:import-from #:myapp.json #:encode #:decode)
;; Avoid: (:use #:myapp.json)
```

## CL-12 — Justify shadowing CL names
**Signal:** Look for `:shadow` or local definitions that replace standard names such as `cl:map` or `cl:list`.
**Problem:** Reusing familiar CL names changes reader expectations and obscures which operation is called.
**Exception:** Shadowing `cl:do` for an iteration library is common; other necessary cases should explain their rationale.
**Example:**
```lisp
;; Prefer a distinct name:
(defun map-records (function records) ...)
```

## CL-13 — One package focus per file
**Signal:** A source file should define or contribute to one package, with related packages named hierarchically.
**Problem:** Package-focused files clarify ownership and let ASDF package-inferred systems derive dependencies from definitions.
**Exception:** Generated or tightly coupled package-definition files may intentionally group declarations.
**Example:**
```lisp
(defpackage #:myapp.core ...)
;; Related packages: myapp.utils, myapp.api
```

## CL-14a — HTTP handler names
**Signal:** Examine request-entry functions whose names do not convey the HTTP verb and resource, or use `handle-` away from a framework boundary.
**Problem:** Verb-and-resource names make routing intent visible, while reserving `handle-` identifies functions that accept framework request objects.
**Exception:** Follow a web framework's required naming pattern, such as a Hunchentoot dispatch convention.
**Example:**
```lisp
(defun get-users (request) ...)
(defun post-login (request) ...)
(defun handle-user-request (request) ...)
```

## CL-14b — Database operation names
**Signal:** Flag persistence functions whose names omit either their operation or target entity, and driver-level functions lacking a backend distinction.
**Problem:** Names such as `find-user` state the data operation clearly; a backend prefix separates raw SQL or driver calls from domain persistence.
**Exception:** Retain names imposed by an ORM API.
**Example:**
```lisp
(defun find-user (id) ...)
(defun insert-user (user) ...)
(defun pg-execute (statement) ...)
```

## CL-14c — Constructors, lookups, and mutations
**Signal:** Check whether creation, optional lookup, idempotent establishment, scoped access, and mutation use verbs matching their contracts.
**Problem:** `make-`, `find-`, `ensure-`, `with-`, and explicit mutation verbs communicate caller expectations; predicates should describe the property being tested.
**Exception:** None beyond established API terminology.
**Example:**
```lisp
(defun make-session () ...)
(defun find-user (id) ...)
(defun ensure-cache-directory () ...)
(defun authorized-request-p (request) ...)
```

## CL-14d — Multiple-value result names
**Signal:** Identify functions with co-equal multiple return values whose names give callers no reason to expect multiple values.
**Problem:** Naming both results prompts correct use of `multiple-value-bind`; the docstring must state their order.
**Exception:** Name for the principal result when remaining values are secondary, as with `read-line`.
**Example:**
```lisp
(defun parse-host-and-port (text)
  "Return the host followed by the port parsed from TEXT."
  ...)
(multiple-value-bind (host port) (parse-host-and-port text) ...)
```

## CL-14e — Names for visible effects
**Signal:** Review functions with observable mutation for names that conceal it, or `n-` prefixes on functions that are not destructive counterparts.
**Problem:** Verbs such as `update-`, `clear-`, `delete-`, and `register-` make effects apparent; `n-` has the narrow conventional meaning of destructive variant.
**Exception:** An already-mutating operator such as `setf`, `incf`, or `push` needs no extra marker.
**Example:**
```lisp
(defun update-cache (entry) ...)
(defun clear-queue (queue) ...)
(defun delete-session (id) ...)
```

## CL-15a — Do not restate package mechanics
**Signal:** Flag comments that label symbols as interface or internal when `:export` or package visibility already establishes that fact.
**Problem:** Repeating mechanically expressed visibility drifts from the package definition, which is authoritative.
**Exception:** Explain an export that appears internal when its rationale would otherwise be surprising.
**Example:**
```lisp
(defpackage #:myapp.api
  (:export #:start-server))
;; Avoid: ;; Public interface
```

## CL-15b — Direct docstrings
**Signal:** Look for docstrings beginning with filler such as “This function returns” or “This documentation explains.”
**Problem:** Direct verbs or declarations convey behavior more clearly and compactly.
**Exception:** A complicated contract may begin with a noun phrase that characterizes it.
**Example:**
```lisp
(defun next-prime (n)
  "Return the first prime greater than N."
  ...)
```

## CL-15c — Grammatically consistent comments
**Signal:** Find comments with inconsistent capitalization, uncapitalized symbol references, or incomplete prose where a sentence is intended.
**Problem:** Consistent prose improves readability; full comments should be capitalized and punctuated, while brief inline notes may remain fragments.
**Exception:** End-of-line fragments may omit a final period.
**Example:**
```lisp
;; CACHE-KEY identifies the shared cache entry.
(setf timeout 30) ; seconds
```

## CL-15d — Localize reader conditionals
**Signal:** Search ordinary implementation code for scattered `#+` and `#-` forms.
**Problem:** A portability boundary keeps platform variation understandable and prevents conditional logic from pervading the program.
**Exception:** ASDF system definitions may conditionally include components.
**Example:**
```lisp
;; Keep implementation-specific selection in one portability module.
#+sbcl (defun monotonic-time () ...)
```

## CL-16a — Package-local nicknames
**Signal:** Review dependency references for repeated long package names or opaque single-letter local nicknames in public sources.
**Problem:** Local nicknames reduce qualified-name noise without globally reserving an alias; documented names remain intelligible to readers.
**Exception:** Short aliases are acceptable in exploratory REPL work or a temporary prototype.
**Example:**
```lisp
(uiop:define-package #:myapp.web
  (:local-nicknames (#:json #:com.inuoe.jzon)))
```

## CL-16b — Intentional shadowing imports
**Signal:** Flag `:shadowing-import-from` unless it establishes a documented, durable conflict-resolution policy.
**Problem:** Explicit qualification better preserves distinctions between two APIs that happen to share a symbol name.
**Exception:** A compatibility package may apply shadowing systematically as part of its adaptation policy.
**Example:**
```lisp
(defpackage #:myapp.compat
  (:shadowing-import-from #:legacy-api #:open)
  ;; OPEN deliberately selects the legacy compatibility operation.
  )
```

## CL-16c — Choosing `uiop:define-package`
**Signal:** `uiop:define-package` is used but no UIOP-specific features (local nicknames, reexports, package mixing) are employed; or UIOP is otherwise a dependency solely for package syntax.
**Problem:** Plain `cl:defpackage` keeps simple packages portable and avoids unnecessary coupling. Using `uiop:define-package` for features such as local nicknames, reexports, or package mixing justifies the dependency; using it without those features does not.
**Exception:** None; using a UIOP-specific feature is sufficient justification, but introducing UIOP solely for package syntax without using those features should be flagged.
**Example:**
```lisp
(uiop:define-package #:myapp.api
  (:use #:cl)
  (:reexport #:myapp.core))
(cl:defpackage #:myapp.minimal
  (:use #:cl))
```

