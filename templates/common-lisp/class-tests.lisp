;;; Tests for class: <class>

;;; Constructor with defaults
(define-test test-make-<class>
  :parent '<module>-test
  (let ((instance (make-instance '<class>)))
    (false (<class>-<slot> instance))
    (true (typep instance '<class>))))

;;; Constructor with arguments
(define-test test-make-<class>-with-args
  :parent '<module>-test
  (let ((instance (make-instance '<class> :<slot> <value>)))
    (is equal <value> (<class>-<slot> instance))))

;;; Accessor tests
(define-test test-<class>-<accessor>
  :parent '<module>-test
  (let ((instance (make-instance '<class> :<slot> <value>)))
    (is equal <value> (<accessor> instance))))

;;; Inheritance
(define-test test-<class>-inheritance
  :parent '<module>-test
  (let ((instance (make-instance '<class>)))
    (true (typep instance '<parent-class>))))
