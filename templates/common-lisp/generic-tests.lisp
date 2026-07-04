;;; Tests for generic function: <generic>

;;; Basic method
(define-test test-<generic>
  :parent '<module>-test
  (let ((obj (make-instance '<class>)))
    (is equal <expected> (<package>.<module>:<generic> obj <arg>))))

;;; Method specialization
(define-test test-<generic>-<specialization>
  :parent '<module>-test
  (let ((obj (make-instance '<specialized-class>)))
    (is equal <expected> (<package>.<module>:<generic> obj <arg>))))

;;; Method combination
(define-test test-<generic>-combination
  :parent '<module>-test
  (let* ((obj (make-instance '<class>))
         (result (<package>.<module>:<generic> obj <arg>)))
    (true (listp result))
    (is = <n> (length result))))

;;; Next-method-p behavior
(define-test test-<generic>-next-method-p
  :parent '<module>-test
  (let ((called-p nil))
    (defmethod <package>.<module>:<generic> :around ((obj <class>) &rest args)
      (setf called-p t)
      (call-next-method))
    (let ((obj (make-instance '<class>)))
      (<package>.<module>:<generic> obj <arg>)
      (true called-p))))
