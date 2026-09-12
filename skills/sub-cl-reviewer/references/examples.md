# Common Lisp Style Reviewer Examples
## Naming
**Case:** Predicate uses an `is-` prefix. **Rule:** CL-03  
**Note:** The `-p` suffix convention identifies predicates.
**Before**
```lisp
(defun is-empty (queue) (null (queue-items queue)))
```
**After**
```lisp
(defun empty-p (queue) (null (queue-items queue)))
```
**Case:** Dynamic request state lacks earmuffs. **Rule:** CL-04  
**Note:** Earmuffs signal special binding.
**Before**
```lisp
(defvar current-user nil "User authenticated for this request.")
```
**After**
```lisp
(defvar *current-user* nil "User authenticated for this request.")
```
**Case:** A numeric constant lacks plus signs. **Rule:** CL-05  
**Note:** Plus signs make constants recognizable at use sites.
**Before**
```lisp
(defconstant pi-ratio 3.14159)
```
**After**
```lisp
(defconstant +pi-ratio+ 3.14159)
```
**Case:** A resource macro duplicates runtime behavior. **Rule:** CL-06  
**Note:** The function owns runtime behavior; the macro supplies lexical convenience.
**Before**
```lisp
(defmacro with-transaction ((db) &body body) `(let ((connection (open-connection ,db))) (unwind-protect (progn ,@body) (close-connection connection))))
```
**After**
```lisp
(defun call-with-transaction (db thunk) (let ((connection (open-connection db))) (unwind-protect (funcall thunk connection) (close-connection connection))))
(defmacro with-transaction ((connection db) &body body) `(call-with-transaction ,db (lambda (,connection) ,@body)))
```
**Case:** Application code reaches into another package's internals. **Rule:** CL-10  
**Note:** Import an exported interface instead of relying on internals.
**Before**
```lisp
(myapp::internal-function request)
```
**After**
```lisp
(defpackage #:web-handler (:use #:cl) (:import-from #:myapp #:process-request))
(process-request request)
```
## Formatting
**Case:** Closing parentheses occupy their own lines. **Rule:** CL-15  
**Note:** Stack related closing parentheses with the final form.
**Before**
```lisp
(defun active-account-p (account)
  (and account
       (account-email account)
       )
  )
```
**After**
```lisp
(defun active-account-p (account) (and account (account-email account)))
```
**Case:** A public function has no behavioral contract. **Rule:** CL-21, CL-22  
**Note:** The docstring gives an imperative summary, return value, and error behavior.
**Before**
```lisp
(defun render-invoice (invoice stream) (format stream "Invoice ~A~%" (invoice-number invoice)))
```
**After**
```lisp
(defun render-invoice (invoice stream) "Write INVOICE's summary to STREAM. Returns INVOICE. Signals INVOICE-VALIDATION-ERROR for missing required fields." (format stream "Invoice ~A~%" (invoice-number invoice)) invoice)
```
**Case:** A file-level section uses an inline-comment marker. **Rule:** CL-20  
**Note:** Four semicolons mark top-level file structure.
**Before**
```lisp
;; HTTP request routing
(defparameter *routes* (make-hash-table :test #'equal))
```
**After**
```lisp
;;;; HTTP request routing
(defparameter *routes* (make-hash-table :test #'equal))
```
**Case:** LET bindings and body have flat indentation. **Rule:** CL-18  
**Note:** Indent body forms two spaces from the opening parenthesis of the `let` form.
**Before**
```lisp
(let ((timeout (client-timeout client))
      (request (make-request url)))
(setf (request-timeout request) timeout)
(send-request client request))
```
**After**
```lisp
(let ((timeout (client-timeout client))
      (request (make-request url)))
  (setf (request-timeout request) timeout)
  (send-request client request))
```
**Case:** Retired code remains as a line comment. **Rule:** CL-24  
**Note:** Prefer removal; reader suppression keeps a temporary comparison valid code.
**Before**
```lisp
(defun retry-delay (attempt)
  ;; (min 60 (* attempt 5))
  (min 60 (expt 2 attempt)))
```
**After**
```lisp
(defun retry-delay (attempt) #+(or) (min 60 (* attempt 5)) (min 60 (expt 2 attempt)))
```
## Idioms
**Case:** Validation signals a bare string. **Rule:** CL-26  
**Note:** A condition type supports programmatic handling.
**Before**
```lisp
(unless (uuid-p x) (error "invalid input"))
```
**After**
```lisp
(unless (uuid-p x) (error 'invalid-input :value x))
```
**Case:** A handler invokes a restart after `handler-case` unwinds. **Rule:** CL-27  
**Note:** `handler-bind` runs while the restart context is active.
**Before**
```lisp
(handler-case (read-record stream) (end-of-file () (invoke-restart 'use-default-record)))
```
**After**
```lisp
(handler-bind ((end-of-file (lambda (c) (declare (ignore c)) (invoke-restart 'use-default-record)))) (read-record stream))
```
**Case:** Client code bypasses a class accessor. **Rule:** CL-33  
**Note:** The accessor preserves the class protocol.
**Before**
```lisp
(format stream "~A" (slot-value customer 'name))
```
**After**
```lisp
(format stream "~A" (name customer))
```
**Case:** Class implementation initializes a private slot. **Rule:** CL-33 exception  
**Note:** Direct slot access can be appropriate inside the class when no public protocol is intended.
**Before**
```lisp
(defmethod initialize-instance :after ((cache cache) &key) (setf (slot-value cache 'entries) (make-hash-table :test #'equal)))
```
**After:** No edit
**Case:** A mutable list is declared constant. **Rule:** CL-44  
**Note:** Lists are mutable objects, so `defconstant` makes an unsuitable promise.
**Before**
```lisp
(defconstant +colors+ '("red" "green" "blue"))
```
**After**
```lisp
(defparameter *colors* '("red" "green" "blue"))
```
**Case:** A public protocol starts with only a method. **Rule:** CL-31  
**Note:** The generic documents the public protocol independently of its first method.
**Before**
```lisp
(defmethod serialize ((report monthly-report) stream) (write-string (monthly-report-title report) stream))
```
**After**
```lisp
(defgeneric serialize (object stream) (:documentation "Write OBJECT to STREAM."))
(defmethod serialize ((report monthly-report) stream) (write-string (monthly-report-title report) stream))
```
**Case:** A macro merely forwards evaluated arguments. **Rule:** CL-37  
**Note:** A function has the same evaluation behavior and is simpler to use.
**Before**
```lisp
(defmacro log-event (level message) `(write-log ,level ,message))
```
**After**
```lisp
(defun log-event (level message) (write-log level message))
```
**Case:** A lock macro controls evaluation and cleanup. **Rule:** CL-37 exception  
**Note:** The macro must bracket an unevaluated body and guarantee dynamic cleanup.
**Before**
```lisp
(defmacro with-lock ((lock) &body body) `(progn (acquire-lock ,lock) (unwind-protect (progn ,@body) (release-lock ,lock))))
```
**After:** No edit

## Build and Portability
**Case:** ASDF uses `:serial t` as a shortcut for dependency order.
**Before**
```lisp
(asdf:defsystem #:my-app :serial t :components ((:file "package") (:file "model") (:file "service")))
```
**After**
```lisp
(asdf:defsystem #:my-app :components ((:file "package") (:file "model" :depends-on ("package")) (:file "service" :depends-on ("model"))))
```
**Rule:** CL-102  
**Note:** Declare each component's actual dependencies.

**Case:** A stream opened manually is not protected from non-local exit.
**Before**
```lisp
(let ((stream (open path)))
  (write-line text stream)
  (close stream))
```
**After**
```lisp
(with-open-file (stream path :direction :output :if-exists :supersede)
  (write-line text stream))
```
**Rule:** CL-116  
**Note:** `with-open-file` closes the stream during unwinding.

**Case:** A hash table uses `equalp` when identity-compatible keys need only `eql`.
**Before**
```lisp
(make-hash-table :test #'equalp)
```
**After**
```lisp
(make-hash-table :test #'eql)
```
**Rule:** CL-121  
**Note:** Use the narrowest equality predicate that meets the key semantics.

## API and Interop
**Case:** A public function mixes positional optional and keyword parameters.
**Before**
```lisp
(defun connect (host &optional port &key timeout) (declare (ignore host port timeout)))
```
**After**
```lisp
(defun connect (host &key port timeout) (declare (ignore host port timeout)))
```
**Rule:** CL-125  
**Note:** Keyword-only options make public calls unambiguous.

**Case:** A public API signals an untyped string error.
**Before**
```lisp
(defun parse-token (token) (unless token (error "Token is required")))
```
**After**
```lisp
(define-condition missing-token-error (error) ())
(defun parse-token (token) (unless token (error 'missing-token-error)))
```
**Rule:** CL-131  
**Note:** Typed conditions allow callers to handle the documented failure.

**Case:** SQL is assembled by concatenating user input.
**Before**
```lisp
(query db (concatenate 'string "SELECT * FROM users WHERE name = '" name "'"))
```
**After**
```lisp
(query db "SELECT * FROM users WHERE name = ?" name)
```
**Rule:** CL-137  
**Note:** Security finding — also refer to sub-reviewer for correctness verification.

## Testing and CI
**Case:** A test has an anonymous, non-descriptive name.
**Before**
```lisp
(test "test1" (is (null (dequeue (make-queue)))))
```
**After**
```lisp
(test "empty-queue-returns-nil" (is (null (dequeue (make-queue)))))
```
**Rule:** CL-146  
**Note:** Names should describe the behavior under test.

**Case:** A test writes diagnostic output on every successful run.
**Before**
```lisp
(test "queue" (format t "Running queue test~%") (is (queue-p (make-queue))))
```
**After**
```lisp
(test "queue-constructs" (is (queue-p (make-queue))))
```
**Rule:** CL-149  
**Note:** Keep successful test output quiet.

**Case:** CI tests only one Common Lisp implementation.
**Before**
```yaml
- run: sbcl --non-interactive --load run-tests.lisp
```
**After**
```yaml
strategy:
  matrix:
    lisp: [sbcl, ccl]
steps:
  - run: ${{ matrix.lisp }} --non-interactive --load run-tests.lisp
```
**Rule:** CL-155  
**Note:** A matrix exposes implementation-specific behavior.

## Advanced Idioms
**Case:** Recovery invokes a restart that no surrounding layer establishes.
**Before**
```lisp
(handler-bind ((error (lambda (c) (declare (ignore c)) (invoke-restart 'use-default))))
  (error "Unable to read value"))
```
**After**
```lisp
(restart-case (read-value stream)
  (use-default () :report "Use the default value." default-value))
```
**Rule:** CL-52  
**Note:** Establish restarts at the layer that can perform recovery.

**Case:** `print-object` performs expensive work while rendering an object.
**Before**
```lisp
(defmethod print-object ((report report) stream) (format stream "~A" (render-full-report report)))
```
**After**
```lisp
(defmethod print-object ((report report) stream)
  (print-unreadable-object (report stream :type t :identity t)
    (format stream "id=~A" (report-id report))))
```
**Rule:** CL-61  
**Note:** Printing should inspect simple, already-available slots.

**Case:** A lock is manually acquired and released without unwind protection.
**Before**
```lisp
(progn (acquire-lock lock) (update-cache cache) (release-lock lock))
```
**After**
```lisp
(with-lock-held (lock)
  (update-cache cache))
```
**Rule:** CL-75  
**Note:** The lock must be released even when the body exits abnormally.

**Case:** A compiler macro exists without a callable function definition.
**Before**
```lisp
(define-compiler-macro fast-add (&whole form x y) `(the fixnum (+ ,x ,y)))
```
**After**
```lisp
(defun fast-add (x y)
  (declare (type fixnum x y))
  (+ x y))
(define-compiler-macro fast-add (&whole form x y)
  `(the fixnum (+ ,x ,y)))
```
**Rule:** CL-85  
**Note:** The function defines runtime behavior; the compiler macro is an optimization.

