# Common Lisp idioms and usage rubric
### CL-25 — Application condition hierarchy
**Signal:** Library or application failures reported only with built-in conditions.
**Problem:** Callers cannot distinguish domain failures or choose an appropriate recovery path.
**Exception:** A genuinely generic failure may use a standard condition.
**Example:**
```lisp
;; Before: (error "invalid request")
(define-condition request-error (error) ())
(define-condition invalid-request-error (request-error) ()) ; After
```
### CL-26 — Typed error signaling
**Signal:** `(error "...")` is used for an anticipated, domain-level failure.
**Problem:** It produces `simple-error`, which clients cannot handle by application meaning.
**Exception:** Rare, unexpected internal failures may use a diagnostic string.
**Example:**
```lisp
;; Before: (error "bad id")
(error 'invalid-request-error :id id) ; After
```
### CL-27 — Choose the handler's unwind behavior
**Signal:** `handler-case` is used to inspect, log, or restart after a condition.
**Problem:** `handler-case` unwinds before its clause runs, losing dynamic context and restarts.
**Exception:** Use it when replacing a failed computation with a returned result is intended.
**Example:**
```lisp
;; Good: restart established at the recovery layer
(defun parse-record (data)
  (restart-case
    (if (valid-p data)
        (make-record data)
        (error 'parse-error :data data))
    (use-value (new-value)
      :report "Use a default value instead"
      new-value)
    (skip ()
      :report "Skip this record"
      nil)))
```
### CL-28 — Offer recoverable restarts
**Signal:** A correctable error is signaled without a restart at its recovery boundary.
**Problem:** Higher layers have no standard way to retry, skip, or supply a replacement.
**Exception:** Failures with no meaningful safe recovery need not provide one.
**Example:**
```lisp
;; Before: (error 'invalid-request-error :id id)
(restart-case (error 'invalid-request-error :id id) (use-value (value) value)) ; After
```
### CL-29 — Do not mask unknown failures
**Signal:** Production code uses `ignore-errors` or a `t` handler around ordinary work.
**Problem:** Programming defects disappear, making diagnosis and correctness harder.
**Exception:** A top-level process boundary or REPL wrapper may contain all conditions deliberately.
**Example:**
```lisp
;; Before: (ignore-errors (parse-request input))
(handler-case (parse-request input) (invalid-request-error () nil)) ; After
```
### CL-30 — Cleanup safely with unwind-protect
**Signal:** Resource cleanup is absent, or its cleanup form can signal a new unhandled error.
**Problem:** Resources leak, or cleanup hides the original failure.
**Exception:** Cleanup may signal when its own failure is explicitly handled by the cleanup policy.
**Example:**
```lisp
;; Before: (let ((s (open path))) (read-line s))
(let ((s (open path))) (unwind-protect (read-line s) (ignore-errors (close s)))) ; After
```
## CLOS
### CL-31 — Declare public generic functions
**Signal:** A public `defmethod` appears without a preceding explicit `defgeneric`.
**Problem:** The implicit generic has no central contract or public documentation.
**Exception:** A private, single-method generic can be introduced directly.
**Example:**
```lisp
;; Before: (defmethod render ((x widget)) ...)
(defgeneric render (object) (:documentation "Contract: accepted objects, return value, and method combination.")) ; After
```
### CL-32 — Keep slot options consistently ordered
**Signal:** `defclass` slot options appear in different orders across nearby classes.
**Problem:** Inconsistent declarations impede scanning and obscure class interfaces.
**Exception:** Follow an established project order even if it differs from this rubric.
**Example:**
```lisp
;; Before: (name :type string :initarg :name :accessor widget-name)
(name :accessor widget-name :initarg :name :type string :documentation "Display name.") ; After
```
### CL-33 — Respect the accessor protocol
**Signal:** Application code uses `slot-value` or broadly uses `with-slots`.
**Problem:** Direct slot access bypasses accessor methods and future protocol extension.
**Exception:** `with-slots` is reasonable in the class's own methods or a proven hot loop; `slot-value` is reasonable when no public accessor protocol is intended.
**Example:**
```lisp
;; Before: (slot-value widget 'name)
(widget-name widget) ; After
```
### CL-34 — Expose mutation only when required
**Signal:** A slot has `:accessor` although clients should not change it.
**Problem:** An unnecessary setter weakens invariants and practical immutability.
**Exception:** Use an accessor when mutation is explicitly part of the object protocol.
**Example:**
```lisp
;; Before: (id :accessor request-id :initarg :id)
(id :reader request-id :initarg :id) ; After
```
### CL-35 — Use auxiliary methods intentionally
**Signal:** An accessor's primary method is redefined, or a wrapper `:around` omits `call-next-method`.
**Problem:** It can replace generated behavior or silently prevent the wrapped operation.
**Exception:** An `:around` method may omit it when deliberately implementing terminal behavior.
**Example:**
```lisp
;; Before: (defmethod widget-name ((x widget)) (log x) (slot-value x 'name))
(defmethod widget-name :around ((x widget)) (log x) (call-next-method)) ; After
```
### CL-36 — Match the object facility to the data
**Signal:** `defclass` models plain records, or `defstruct` is stretched to need CLOS behavior.
**Problem:** The representation either adds needless machinery or blocks needed dispatch and identity.
**Exception:** Existing interface commitments can justify either choice.
**Example:**
```lisp
;; Before: (defclass point () ((x :initarg :x) (y :initarg :y)))
(defstruct point x y) ; After
```
## Macros
### CL-37 — Reserve macros for syntactic needs
**Signal:** A macro merely computes values with ordinary argument evaluation.
**Problem:** Macros complicate reasoning, debugging, and compilation without semantic benefit.
**Exception:** Syntax, binding, declaration placement, or evaluation control warrants a macro.
**Example:**
```lisp
;; Before: (defmacro square (x) `(* ,x ,x))
(defun square (x) (* x x)) ; After
```
### CL-38 — Mark executable bodies with &body
**Signal:** A macro accepts trailing forms through `&rest` when they are code to execute.
**Problem:** Readers and editors lose the body intent and conventional indentation support.
**Exception:** Keep `&rest` when the trailing arguments are data rather than forms.
**Example:**
```lisp
;; Before: (defmacro with-x ((x) &rest forms) ...)
(defmacro with-x ((x) &body forms) ...) ; After
```
### CL-39 — Preserve hygiene and evaluation count
**Signal:** Expansion temporaries use ordinary symbols, or a user form is inserted repeatedly.
**Problem:** Names can capture user bindings and repeated evaluation can duplicate effects.
**Exception:** Repeated evaluation is acceptable when the macro documents and requires it.
**Example:**
```lisp
;; Before: `(let ((value ,form)) (+ value value))
(let ((g (gensym "VALUE-"))) `(let ((,g ,form)) (+ ,g ,g))) ; After
```
### CL-40 — Put runtime work in functions
**Signal:** A large macro includes substantial runtime control flow or resource logic.
**Problem:** Expansion obscures debugging, tests, and recompilation of ordinary behavior.
**Exception:** A small macro with a trivial expansion need not be split.
**Example:**
```lisp
;; Before: (defmacro with-foo (...) `(progn ...complex runtime work...))
(defmacro with-foo ((x) &body body) `(call-with-foo ,x (lambda () ,@body))) ; After
```
### CL-41 — Describe macro syntax in its lambda list
**Signal:** A macro manually picks `first`, `second`, and `third` from structured arguments.
**Problem:** Shape validation and the intended syntax are hidden in expansion code.
**Exception:** Manual processing is suitable for genuinely variable grammar; use `&key`, `&whole`, or `&environment` when their respective syntax or expansion context is needed.
**Example:**
```lisp
;; Before: (defmacro range (spec &body body) (let ((v (first spec)) ...) ...))
(defmacro range ((var start end) &body body) ...) ; After
```
### CL-42 — Explain macro-generating macros
**Signal:** A macro that defines or returns macros lacks expansion-focused documentation.
**Problem:** Users cannot infer source syntax, evaluation rules, visible bindings, or limits.
**Exception:** None beyond truly private, self-evident local machinery.
**Example:**
```lisp
;; Before: (defmacro define-query (name) ...)
(defmacro define-query (name) "Defines NAME; arguments evaluate once." ...) ; After
```
## Type declarations
### CL-43 — Validate at boundaries; declare proven facts
**Signal:** Public inputs rely only on `declare`, or declarations assert facts not ensured by code.
**Problem:** Declarations are optimization assertions and bad ones can yield undefined behavior.
**Exception:** Internal declarations are appropriate after invariants establish their truth.
**Example:**
```lisp
;; Before: (defun f (x) (declare (type fixnum x)) (+ x 1))
(defun f (x) (check-type x fixnum) (+ x 1)) ; After
```
### CL-44 — Do not make mutable objects constants
**Signal:** `defconstant` binds a list, string, vector, or another mutable object.
**Problem:** Redefining it to a non-`eql` value has undefined ANSI Common Lisp consequences.
**Exception:** Numbers, characters, and symbols that are truly immutable are suitable constants.
**Example:**
```lisp
;; Before: (defconstant +headers+ '("accept"))
(defparameter *headers* '("accept")) ; After
```
### CL-45 — Make unused bindings explicit
**Signal:** A binding is unused without an `ignore` or `ignorable` declaration.
**Problem:** It leaves misleading code and warning suppression can conceal useful diagnostics.
**Exception:** Bindings needed for interface shape may be declared appropriately.
**Example:**
```lisp
;; Before: (multiple-value-bind (value status) (read-x) value)
(multiple-value-bind (value status) (read-x) (declare (ignore status)) value) ; After
```
## Iteration
### CL-46 — Use mapping and reduction for simple collection work
**Signal:** Hand-written traversal performs only `mapcar`/`mapcan`/`mapc` work or a single fold.
**Problem:** It obscures a standard operation and can hide accumulator initialization choices.
**Exception:** Use explicit iteration when control flow or several accumulators improve clarity.
**Example:**
```lisp
;; Before: (let ((sum 0)) (dolist (x xs sum) (incf sum x)))
(reduce #'+ xs :initial-value 0) ; After
```
### CL-47 — Keep iteration constructs proportionate
**Signal:** A multi-clause loop is encoded as tangled mappings/recursion, or one `loop` does everything.
**Problem:** Either form hides iteration structure; dense loops and mixed `loop`/`iterate` styles make maintenance difficult.
**Exception:** `dolist` and `dotimes` are preferable for a single simple traversal; put major `loop` clauses on aligned lines.
**Example:**
```lisp
;; Before: (dolist (x xs) (when (validp x) (collect-result x)))
(loop for x in xs when (validp x) collect (result x)) ; After
```
### CL-48 — Do not assume tail-call optimization
**Signal:** Unbounded list processing uses self recursion as its default iteration strategy.
**Problem:** Portable Common Lisp does not require tail-call optimization, risking stack exhaustion.
**Exception:** Bounded-depth recursion that clarifies an algorithm, such as tree walking, is sound.
**Example:**
```lisp
;; Before: (defun visit (xs) (when xs (work (car xs)) (visit (cdr xs))))
(dolist (x xs) (work x)) ; After
```
## Reader macros
### CL-49 — Scope reader extensions
**Signal:** Code installs a reader macro into the current or standard readtable globally.
**Problem:** Reader behavior leaks into unrelated code and makes source interpretation context-sensitive.
**Exception:** A project-wide syntax may do so only with explicit project consensus.
**Example:**
```lisp
;; Before: (set-macro-character #\@ #'read-at)
(named-readtables:defreadtable :my-syntax (:merge :standard) (:macro-char #\@ #'read-at)) ; After
```
### CL-50 — Keep read-time evaluation pure
**Signal:** `#.` evaluates a form that can mutate state, perform I/O, or affect correctness.
**Problem:** Loading or compiling then gains hidden effects whose timing is difficult to control.
**Exception:** Side-effect-free constant folding is acceptable when its result is stable.
**Example:**
```lisp
;; Before: #.(progn (format t "loaded~%") 42)
#.(+ 20 22) ; After
```
## Advanced conditions and restarts
### CL-51 — Select signaling by recovery
**Signal:** Advisory conditions abort, diagnostics use `signal`, or `cerror` has no stated continuation. **Problem:** Callers cannot tell whether work may safely proceed. **Exception:** `break` is limited to interactive debugging; use `signal` for recoverable advice, `warn` for nonfatal diagnostics, `error` for unsafe continuation, and `cerror` only with its documented continue restart.
**Example:**
```lisp
(signal 'cache-stale) ; `(error ...)` only when continuing is unsafe
```
### CL-52 — Place restarts beside recovery
**Signal:** Recovery is invented by the caller rather than where it is feasible. **Problem:** Restart safety and names become guesswork, and recoverable error paths offer none. **Exception:** Irrecoverable failures need no restart; define recovery-layer `restart-case` or `restart-bind` with names such as `use-value`, `retry`, or `skip` rather than ambiguous `continue`.
**Example:**
```lisp
(restart-case (error 'parse-error) (use-value (value) value))
```
### CL-53 — Build condition families
**Signal:** Domain errors all inherit directly from `error`. **Problem:** Handlers cannot choose broad versus precise recovery. **Exception:** A genuinely standalone failure may be direct.
**Example:**
```lisp
(define-condition invalid-field-error (parse-error) ())
```
### CL-54 — Keep reports safe and concise
**Signal:** A condition report is noisy, nondeterministic, leaks implementation data, or adds an `Error:` prefix/newline. **Problem:** `*error-output*` becomes misleading or discloses secrets. **Exception:** A private debug condition may carry more context; ordinary reports should state the failed operation and salient values concisely.
**Example:**
```lisp
(:report (lambda (c s) (format s "Invalid field ~S" (field c))))
```
### CL-55 — Publish only needed condition readers
**Signal:** Every condition slot is exported through a reader. **Problem:** Handlers become coupled to private representation. **Exception:** A slot intentionally part of the handling protocol needs a reader.
**Example:**
```lisp
(field :initarg :field :reader invalid-field-error-field)
```
### CL-56 — Bind condition machinery in each worker
**Signal:** Threaded code expects handlers or restarts to reach another thread. **Problem:** Dynamic bindings do not cross thread boundaries. **Exception:** A supervisor may receive an explicit structured result.
**Example:**
```lisp
(make-thread (lambda () (handler-bind ((error #'report)) (work))))
```
## Advanced CLOS
### CL-57 — Use initialize-instance :after for post-setup
**Signal:** Creation-only derived state is computed in `shared-initialize`. **Problem:** Reinitialization receives unintended work. **Exception:** Shared behavior belongs in `shared-initialize`.
**Example:**
```lisp
(defmethod initialize-instance :after ((x widget) &key) (setf (checksum x) (hash x)))
```
### CL-58 — Share initialization deliberately
**Signal:** Creation and reinitialization duplicate slot setup. **Problem:** Their behavior drifts apart. **Exception:** A replacement protocol may intentionally omit the next method.
**Example:**
```lisp
(defmethod shared-initialize :after ((x widget) slots &key) (declare (ignore slots)) (normalize x))
```
### CL-59 — Respect unbound slots
**Signal:** An `unbound-slot` is caught and silently converted to `nil`. **Problem:** Meaningful absence is hidden. **Exception:** A documented accessor protocol may define that result.
**Example:**
```lisp
(if (slot-boundp object 'value) (value object) :missing)
```
### CL-60 — Wrap construction that has invariants
**Signal:** Clients repeatedly call `make-instance` with essential initargs. **Problem:** Required setup is easy to omit. **Exception:** Open-ended extensible construction can remain direct.
**Example:**
```lisp
(defun make-queue (&key capacity) (make-instance 'queue :capacity capacity))
```
### CL-61 — Make print-object nonintrusive
**Signal:** `print-object` invokes costly work, unrelated I/O, conditions, recursive computation, or possibly unbound accessors. **Problem:** Diagnostics can recurse, fail, or mutate state. **Exception:** Writing the object's representation to the supplied stream is the method's intended operation and is not prohibited.
**Example:**
```lisp
(print-unreadable-object (x stream :type t :identity t))
```
### CL-62 — Define load reconstruction completely
**Signal:** `make-load-form` is supplied without defined persistence semantics. **Problem:** Loaded objects differ from their originals. **Exception:** `make-load-form-saving-slots` suffices when persisted slots define state.
**Example:**
```lisp
(defmethod make-load-form ((x widget) &optional environment) (make-load-form-saving-slots x :environment environment))
```
### CL-63 — Migrate live instances after class change
**Signal:** A changed class leaves existing instances without a transition path. **Problem:** Their old layout or state becomes invalid. **Exception:** No migration is needed when no live instances can exist.
**Example:**
```lisp
(defmethod update-instance-for-redefined-class :after
    ((x widget) added discarded plist &rest initargs)
  (declare (ignore added discarded plist initargs))
  ;; migrate instance state here
  )
```
## Declaration discipline
### CL-64 — Scope optimization policy narrowly
**Signal:** Files broadly lower safety or impose deployment qualities. **Problem:** Bugs become harder to detect and local hot paths are obscured. **Exception:** Measured, verified hot code may use a local declaration.
**Example:**
```lisp
(locally (declare (optimize (speed 3) (safety 1))) (fast-step x))
```
### CL-65 — Choose inline declarations intentionally
**Signal:** Redefinable functions receive global `inline` declarations. **Problem:** Redefinition, profiling, and code size suffer. **Exception:** A small stable hot function may be inline.
**Example:**
```lisp
(declaim (notinline dispatch-request))
```
### CL-66 — Prove dynamic extent before declaring it
**Signal:** A closure or object declared `dynamic-extent` can escape. **Problem:** Its lifetime assumptions yield undefined behavior. **Exception:** A nonescaping temporary is suitable.
**Example:**
```lisp
(let ((buffer (make-array 128)))
  (declare (dynamic-extent buffer))
  ;; fill-buffer does not retain or return buffer
  (fill-buffer buffer))
```
### CL-67 — Distinguish ignore from ignorable
**Signal:** `ignore` marks a variable that some path may read. **Problem:** The declaration itself invites warnings. **Exception:** An intentionally unused binding should use `ignore`.
**Example:**
```lisp
(let ((trace *trace*)) (declare (ignorable trace)) (when trace (log trace)))
```
### CL-68 — Match the declaration to its purpose
**Signal:** `the` validates public input. **Problem:** Low safety may eliminate the check. **Exception:** Proven local facts can use `the`; global function contracts use `ftype`.
**Example:**
```lisp
(defun accept (x) (check-type x integer) (1+ x))
```
### CL-69 — Keep global declarations near targets
**Signal:** A distant `declaim` governs unrelated-looking definitions. **Problem:** Readers miss the contract it establishes. **Exception:** A compilation-unit policy may be grouped at its start.
**Example:**
```lisp
(declaim (ftype (function (string) string) normalize-name))
```
## Format and printing
### CL-70 — Pick the simplest output primitive
**Signal:** `format` is used for plain display. **Problem:** Formatting syntax hides a simple intent. **Exception:** Interpolation, alignment, or iteration warrants `format`.
**Example:**
```lisp
(princ message stream)
```
### CL-71 — Use conventional format directives
**Signal:** Format strings use readable directives for display or literal line breaks. **Problem:** Output contracts become unclear and strings hard to maintain. **Exception:** A fixed short format string can remain inline.
**Example:**
```lisp
(format stream "~&Item: ~A~%" item)
```
### CL-72 — Pretty-print structured output explicitly
**Signal:** Complex forms depend only on `*print-pretty*`. **Problem:** Layout is accidental and unsuitable for distinct output modes. **Exception:** Simple atomic debugging output needs no pretty printer.
**Example:**
```lisp
(pprint form stream)
```
### CL-73 — Bind circular-printing controls when needed
**Signal:** Shared or cyclic graphs are printed without `*print-circle*`. **Problem:** Output may loop or duplicate identity misleadingly. **Exception:** Acyclic tree data need not pay for it.
**Example:**
```lisp
(let ((*print-circle* t)) (write graph :stream stream))
```
### CL-74 — Route diagnostics to the right stream
**Signal:** Library diagnostics go to `*standard-output*`. **Problem:** They corrupt caller output. **Exception:** A command's documented normal output may use that stream.
**Example:**
```lisp
(format *error-output* "~&Bad request: ~A~%" request)
```
## Concurrency
### CL-75 — Release locks on every exit
**Signal:** Lock acquire/release calls are paired manually. **Problem:** A nonlocal exit can retain the lock forever. **Exception:** A deliberately cross-boundary lock lifetime must be documented.
**Example:**
```lisp
(with-lock-held (lock) (update-state state))
```
### CL-76 — Establish a lock order
**Signal:** Multiple locks are acquired without an agreed order. **Problem:** Different paths can deadlock. **Exception:** A single lock requires no ordering policy.
**Example:**
```lisp
(with-lock-held (account-lock) (with-lock-held (ledger-lock) (transfer)))
```
### CL-77 — Recheck predicates after waits
**Signal:** A condition variable wait is not inside a predicate loop. **Problem:** Wakeups can be spurious or the state can change first. **Exception:** None for condition-variable waits.
**Example:**
```lisp
(loop until ready-p do (condition-wait condition lock))
```
### CL-78 — Use the synchronization primitive matching state
**Signal:** A condition variable acts as a resource counter. **Problem:** Counter semantics are needlessly reimplemented. **Exception:** State transitions with predicates belong to condition variables.
**Example:**
```lisp
(wait-on-semaphore permits)
```
### CL-79 — State thread contracts
**Signal:** Thread-using APIs omit ownership, callback, and blocking guarantees. **Problem:** Clients cannot use them safely. **Exception:** A private implementation detail may need only local documentation.
**Example:**
```lisp
(defun start-worker () "Runs callback on a worker thread; may block during shutdown." ...)
```
## Foreign function interface
### CL-80 — Separate C bindings from Lisp wrappers
**Signal:** One layer mixes C naming and calling details with the public Lisp API. **Problem:** The interface becomes neither faithful nor idiomatic. **Exception:** A tiny private binding may be direct.
**Example:**
```lisp
(cffi:defcfun ("open_fd" %open-fd) :int (path :string))
```
### CL-81 — Assign foreign memory ownership
**Signal:** `foreign-alloc` has no visible release policy. **Problem:** Native memory leaks or is freed ambiguously. **Exception:** Dynamic allocations can use a scoped CFFI macro.
**Example:**
```lisp
(cffi:with-foreign-object (buffer :char 256) (fill-buffer buffer))
```
### CL-82 — Keep retained foreign strings alive
**Signal:** C stores a pointer from a temporary foreign string. **Problem:** Later C access reaches released memory. **Exception:** A C function documented to copy the string may receive a temporary.
**Example:**
```lisp
;; Avoid: allocation with no cleanup
(setf (handle-name-pointer handle) (cffi:foreign-string-alloc name))
;; Good: document ownership and provide cleanup
(setf (handle-name-pointer handle) (cffi:foreign-string-alloc name))
;; handle owns name-pointer; free it in handle's destructor
```
### CL-83 — Prevent exits across C callbacks
**Signal:** A callback can signal or throw through foreign frames. **Problem:** C cannot safely unwind Lisp control transfer. **Exception:** A callback may catch and marshal its failure.
**Example:**
```lisp
(cffi:defcallback on-event :void ((code :int)) (handler-case (process code) (error (e) (record e))))
```
### CL-84 — Translate foreign types at the boundary
**Signal:** Public Lisp functions expose raw foreign pointers. **Problem:** Callers inherit lifetime and representation hazards. **Exception:** A low-level internal package may expose them.
**Example:**
```lisp
(cffi:define-foreign-type handle-type () () (:actual-type :pointer))
```
## Compiler macros
### CL-85 — Optimize an existing function only
**Signal:** A compiler macro supplies behavior absent from its function. **Problem:** Interpreted and compiled calls diverge. **Exception:** None; the ordinary function remains authoritative.
**Example:**
```lisp
(defun square (x) (* x x))
(define-compiler-macro square (x)
  (alexandria:once-only (x)
    `(* ,x ,x)))
```
### CL-86 — Preserve call semantics in expansions
**Signal:** An optimization changes evaluation, values, conditions, or dynamic effects. **Problem:** Compilation changes correctness. **Exception:** Return the original form when safety cannot be proven.
**Example:**
```lisp
(define-compiler-macro identity-call (&whole form x) (if (constantp x) x form))
```
### CL-87 — Allow lexical functions to shadow macros
**Signal:** A compiler macro assumes every matching call reaches the global function. **Problem:** `flet` and `labels` alter the binding. **Exception:** An expansion may use environment information when portable support permits.
**Example:**
```lisp
(flet ((square (x) x)) (square 4))
```
### CL-88 — Use macros for syntax, compiler macros for calls
**Signal:** A compiler macro is used instead of defining its function. **Problem:** Nonexpanded uses have no contract. **Exception:** Syntax or evaluation-rule changes require a regular macro.
**Example:**
```lisp
(defun square (x) (* x x))
```
## EVAL-WHEN
### CL-89 — Introduce eval-when only for phase needs
**Signal:** Top-level forms are mechanically wrapped in `eval-when`. **Problem:** Phase behavior becomes harder to reason about. **Exception:** A real compile/load/execute requirement justifies it.
**Example:**
```lisp
(eval-when (:compile-toplevel :load-toplevel :execute) (defparameter *table* (make-hash-table)))
```
### CL-90 — Declare compilation dependencies by phase
**Signal:** Later forms need a macro or reader setup unavailable while compiling. **Problem:** Compilation fails or produces phase-dependent output. **Exception:** Runtime-only definitions need no compile-time situation.
**Example:**
```lisp
(eval-when (:compile-toplevel :load-toplevel :execute) (defmacro when-let (x &body body) `(when ,x ,@body)))
```
### CL-91 — Keep macro expansion free of side effects
**Signal:** A macro expander performs I/O or mutation. **Problem:** Compilation unexpectedly changes the world. **Exception:** Pure expansion-time computation is acceptable.
**Example:**
```lisp
;; Avoid: side effect at expansion time
(defmacro announce ()
  (format t "expanding announce~%")  ; runs at macroexpansion time
  `(format t "started~%"))
;; Good: side effect in the expansion only
(defmacro announce ()
  `(format t "started~%"))
```
### CL-92 — Do not confuse top-level and nested eval-when
**Signal:** Nested `eval-when` expects compilation-unit effects. **Problem:** Its surrounding form prevents those effects. **Exception:** A nested runtime use may be intentional.
**Example:**
```lisp
(eval-when (:compile-toplevel) (defmacro helper () nil))
```
## Method combination
### CL-93 — Prefer standard method combination
**Signal:** `:before` or `:after` methods calculate the operation's essential result. **Problem:** Their return values are discarded under standard combination; `:around` methods that return values other than `call-next-method`'s result can also lose the primary result. **Exception:** Side effects, wrapping, or vetoing suit auxiliary qualifiers.
**Example:**
```lisp
(defmethod render :around ((x widget)) (authorize x) (call-next-method))
```
### CL-94 — Use short combinations only for obvious algebra
**Signal:** A short-form combination hides dependent or order-sensitive work. **Problem:** Its result and ordering are difficult to infer. **Exception:** Independent methods with clear aggregation are suitable.
**Example:**
```lisp
(defgeneric enabled-p (x) (:method-combination and))
```
### CL-95 — Treat custom combinations as protocols
**Signal:** A custom combination merely renames standard behavior. **Problem:** It adds an undocumented dispatch mechanism. **Exception:** A real protocol can define ordering, roles, results, and errors.
**Example:**
```lisp
(define-method-combination pipeline () ((steps () :required t)) `(progn ,@(mapcar #'(lambda (m) `(call-method ,m)) steps)))
```
### CL-96 — Cover all method qualifiers
**Signal:** An applicable qualifier matches no method group. **Problem:** Effective-method construction has undefined intent. **Exception:** Reject invalid roles explicitly while constructing the method.
**Example:**
```lisp
(method-combination-error "Unknown qualifier")
```
## MOP
### CL-97 — Extend metaobjects; do not redefine them
**Signal:** Code alters specified standard metaobject classes directly. **Problem:** Portable MOP extension rules are violated. **Exception:** Subclass a metaobject class and specialize with a nonstandard class.
**Example:**
```lisp
(defclass audited-class (standard-class) ())
```
### CL-98 — Preserve next-method protocol results
**Signal:** An extension method silently replaces prescribed behavior. **Problem:** Metaobject invariants can be lost. **Exception:** The specific protocol may explicitly authorize replacement.
**Example:**
```lisp
(defmethod shared-initialize :around ((instance audited-widget) slots &rest initargs)
  (let ((result (call-next-method)))
    result))
```
### CL-99 — Hide MOP dependence behind portability code
**Signal:** Application code calls implementation MOP APIs throughout. **Problem:** Non-ANSI assumptions spread unchecked. **Exception:** A narrow documented abstraction can depend on `closer-mop`.
**Example:**
```lisp
(defun class-slots* (class) (closer-mop:class-slots class))
```
### CL-100 — Install metaclass behavior before use
**Signal:** Instances or subclasses precede methods their metaclass requires. **Problem:** Late installation can break optimizations and portability restrictions. **Exception:** No special ordering is needed without custom protocol methods.
**Example:**
```lisp
(defmethod closer-mop:validate-superclass ((c audited-class) (s standard-class)) t)
```

