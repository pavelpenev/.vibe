;;; Tests for function: <function>

;;; Basic functionality
(define-test test-<function>
  :parent '<module>-test
  "Test <function> with normal inputs"
  (is equal <expected> (<package>.<module>:<function> <arg1> <arg2>)))

;;; Nil inputs
(define-test test-<function>-nil
  :parent '<module>-test
  (is equal <expected> (<package>.<module>:<function> nil)))

;;; Empty collections
(define-test test-<function>-empty
  :parent '<module>-test
  (is equal <expected> (<package>.<module>:<function> '())))

;;; Boundary values
(define-test test-<function>-boundary
  :parent '<module>-test
  (is equal <expected> (<package>.<module>:<function> 0))
  (is equal <expected> (<package>.<module>:<function> most-positive-fixnum)))

;;; Error conditions
(define-test test-<function>-error
  :parent '<module>-test
  (fail (<package>.<module>:<function> <invalid-input>) <error-type>))
