# API and Interoperability

## CL-125 — Positional core, keyword policy
- **Signal:** Required identity or input is positional; optional policy is keyword-based.
- **Problem:** Mixing `&optional` and `&key` in a new interface makes calls and defaults harder to reason about.
- **Exception:** Retain an established mixed signature when compatibility requires it.
- **Example:**
  ```lisp
  (defun open-store (name &key read-only timeout) ...)
  ```

## CL-126 — Distinguish omitted from NIL
- **Signal:** A `supplied-p` variable records whether an argument was actually passed.
- **Problem:** Sentinels such as `:unset` add a fake value when omission can be represented directly.
- **Exception:** Use a sentinel only when the API must preserve an independently meaningful supplied-p value.
- **Example:**
  ```lisp
  (defun find-user (id &key (include-deleted nil deleted-p))
    ...)
  ```

## CL-127 — Describe every return contract
- **Signal:** Public documentation covers values, multiple values, side effects, conditions, and ownership.
- **Problem:** Undocumented returns leave callers guessing about resources, threads, and cleanup obligations.
- **Exception:** Private trivial helpers may rely on immediately obvious local conventions.
- **Example:**
  ```lisp
  ;; Returns object and its newly acquired lock; caller releases the lock.
  ```

## CL-128 — Keep the export surface narrow
- **Signal:** Only deliberate public entry points are exported, and removals are preceded by deprecation.
- **Problem:** Exporting helpers for convenience creates accidental API commitments and qualification-free coupling.
- **Exception:** Export a helper when it is a supported abstraction, not merely because callers dislike package prefixes.
- **Example:**
  ```lisp
  (defpackage #:store (:use #:cl) (:export #:open-store #:close-store))
  ```

## CL-129 — Select functional or object style intentionally
- **Signal:** Pure transformations favor functions; dispatch, identity, extensibility, or mutable state favor CLOS.
- **Problem:** Forcing one paradigm onto every API obscures the natural protocol and its invariants.
- **Exception:** A public interface may provide both styles when it documents their distinct purposes.
- **Example:**
  ```lisp
  (defgeneric render (object stream)) ; extensible protocol
  ```

## CL-130 — Keep application entry thin
- **Signal:** A stable entry function parses arguments and configuration, then delegates to library code.
- **Problem:** Putting application behavior in `main` makes reuse, testing, and alternate launchers difficult.
- **Exception:** A tiny command with no reusable behavior may keep its delegation local.
- **Example:**
  ```lisp
  (defun main () (run-app (parse-command-line) (load-config)))
  ```

## CL-131 — Signal typed, catchable conditions
- **Signal:** Errors that callers can handle have named condition types rather than only formatted text.
- **Problem:** `(error "...")` in a public API forces clients to parse prose or catch overly broad conditions.
- **Exception:** A genuinely unrecoverable internal invariant may use a generic error.
- **Example:**
  ```lisp
  (define-condition missing-record (error) ((key :initarg :key :reader record-key)))
  ```

## CL-132 — Make reports concise and stable
- **Signal:** A `:report` method states the failed operation and useful values without noise or newlines.
- **Problem:** Prefixes like `Error:` and implementation details make reports redundant, brittle, or unsafe for streams.
- **Exception:** Add detail when the target audience and stream explicitly require it.
- **Example:**
  ```lisp
  (:report (lambda (c s) (format s "Unable to open ~A" (path c))))
  ```

## CL-133 — Offer only sound recovery restarts
- **Signal:** `retry`, `use-value`, `skip`, or `abort` is available when a caller can act meaningfully.
- **Problem:** A generic `continue` can resume with corrupted or incomplete state and conceal the failure.
- **Exception:** Do not add a restart merely to decorate an error; omit it when recovery is impossible.
- **Example:**
  ```lisp
  (restart-case (read-record stream) (use-value (value) value) (abort () nil))
  ```

## CL-134 — Keep diagnostics apart from user text
- **Signal:** Debug detail goes to `*error-output*` or `*trace-output*`; user-facing text remains stable and safe.
- **Problem:** Mixed output leaks paths, secrets, implementation details, or debugging chatter to users.
- **Exception:** Deliberate verbose or diagnostic modes may expose extra context through an explicit interface.
- **Example:**
  ```lisp
  (format *error-output* "retrying request~%")
  ```

## CL-135 — Map serialized data explicitly
- **Signal:** A boundary converts JSON or XML representations into validated domain objects with documented key/null rules.
- **Problem:** Passing parsed JSON directly inward couples business logic to string-vs-keyword and null-vs-`nil` choices.
- **Exception:** A deliberately generic pass-through component may preserve external data, but must declare that contract.
- **Example:**
  ```lisp
  (make-user :id (gethash "id" json) :name (gethash "name" json))
  ```

## CL-136 — Use a purposeful HTTP layer
- **Signal:** Clack suits portable servers, Hunchentoot suits direct server control, and Dexador suits outbound requests.
- **Problem:** Unmotivated mixing of server and client libraries obscures ownership and portability.
- **Exception:** Combine libraries when separate inbound and outbound roles are explicit and tested.
- **Example:**
  ```lisp
  (defun get-users-handler (request) (declare (ignore request)) ...)
  ```

## CL-137 — Parameterize SQL and bound transactions
- **Signal:** Postmodern or CLSQL supports direct SQL; Mito supports ORM and migrations; queries use parameters.
- **Problem:** Concatenated SQL permits injection and blurs transaction behavior.
- **Note:** This is a style-adjacent security finding. If the reviewer detects string-concatenated SQL, file it as a WARNING and note in limitations that sub-reviewer should verify the security impact.
- **Exception:** Dynamic SQL fragments may be assembled only from validated identifiers, never raw user values.
- **Example:**
  ```lisp
  (postmodern:query "select * from users where id = $1" user-id)
  ```

## CL-138 — Validate parsed input at the boundary
- **Signal:** JSON, YAML, and XML input is checked for types, required fields, and permitted ranges before processing.
- **Problem:** Parser output is data, not a trusted application object; unchecked assumptions fail deep inside the system.
- **Exception:** A separately verified internal producer may use a narrower validation path with documented provenance.
- **Example:**
  ```lisp
  (check-type age (integer 0 150))
  ```

## CL-139 — Compile regular expressions outside hot paths
- **Signal:** CL-PPCRE scanners are created once and reused while iteration performs only matching.
- **Problem:** Calling `create-scanner` inside a loop repeats compilation and can dominate runtime.
- **Exception:** Per-call patterns are acceptable when the pattern itself is dynamic and the cost is intentional.
- **Example:**
  ```lisp
  (let ((scanner (cl-ppcre:create-scanner "^[A-Z]+$")))
    (loop for word in words when (cl-ppcre:scan scanner word) collect word))
  ```

## CL-140 — Make boundary encodings explicit
- **Signal:** System or I/O configuration states external formats where encoding affects correctness; internal text uses character APIs.
- **Problem:** Treating character codes as a particular encoding breaks portability and corrupts non-ASCII data.
- **Note:** The exact external-format designator varies by implementation. Use UIOP or a portability library for cross-implementation encoding.
- **Exception:** Numeric code comparisons belong only in a documented encoding-specific adapter.
- **Example:**
  ```lisp
  ;; The exact external-format designator varies by implementation.
  ;; Use UIOP or check your implementation's documentation.
  #+sbcl (with-open-file (in path :external-format :utf-8) ...)
  #+ccl (with-open-file (in path :external-format :utf-8) ...)
  ;; Or use a portability library that normalizes encoding keywords.
  ```
