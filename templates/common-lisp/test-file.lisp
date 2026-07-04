;;; <module>-test.lisp
;;; Tests for src/<module>.lisp
;;;
;;; License: <license, e.g., MIT>
;;; Author: <author>

(defpackage #:<package>.test.<module>
  (:use #:cl
        #:<package>.<module>
        #:parachute)
  (:export #:<module>-test))

(in-package #:<package>.test.<module>)

(define-test <module>-test
  :parent '<package>.test:<package>-test)
