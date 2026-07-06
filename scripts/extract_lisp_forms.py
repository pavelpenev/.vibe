#!/usr/bin/env python3
# SCRIPT-METADATA:
# name: extract_lisp_forms
# description: Extract top-level forms from Common Lisp / Emacs Lisp / ASDF files as JSON
# tags: lisp,parsing
# language: python
"""
Extract top-level forms from Common Lisp files.
Returns a JSON array of objects:
  {"type": "form",  "start": N, "end": N, "content": "..."}
  {"type": "error", "start": N, "end": N, "message": "..."}

Error messages emitted:
  - "Unbalanced form: started at line X, runs to EOF"
  - "Unbalanced: form started at line X runs into line Y"  (new top-level '(' at column 0 while a form is open)
  - "Unclosed string starting at line X"
  - "Unclosed block comment starting at line X"
  - "Extra closing parenthesis at line X"

Handles: nested #| |# block comments, #\( #\) #\" character literals,
; line comments, strings with escapes.

Run with no arguments (or --test) to execute the built-in self-tests.
"""

import sys
import json


def extract_top_level_forms(filepath):
    with open(filepath, 'r') as f:
        lines = f.read().splitlines()
    return scan(lines)


def scan(lines):
    forms = []
    in_string = False
    string_start = 0
    comment_depth = 0
    comment_start = 0
    paren_depth = 0
    form_start = 0
    line_num = 0

    def close_form(end_line):
        forms.append({
            'type': 'form',
            'start': form_start,
            'end': end_line,
            'content': '\n'.join(lines[form_start - 1:end_line]),
        })

    for line_num, line in enumerate(lines, 1):
        i = 0
        n = len(line)
        while i < n:
            ch = line[i]

            if in_string:
                if ch == '\\':
                    i += 2
                    continue
                if ch == '"':
                    in_string = False
                i += 1
                continue

            if comment_depth > 0:
                if ch == '|' and i + 1 < n and line[i + 1] == '#':
                    comment_depth -= 1
                    i += 2
                    continue
                if ch == '#' and i + 1 < n and line[i + 1] == '|':
                    comment_depth += 1
                    i += 2
                    continue
                i += 1
                continue

            # normal state
            if ch == ';':
                break  # rest of line is a comment
            if ch == '#' and i + 1 < n and line[i + 1] == '|':
                comment_depth = 1
                comment_start = line_num
                i += 2
                continue
            if ch == '#' and i + 1 < n and line[i + 1] == '\\':
                i += 3  # skip '#', '\', and the literal character itself
                continue
            if ch == '"':
                in_string = True
                string_start = line_num
                i += 1
                continue
            if ch == '(':
                # A '(' at column 0 while a form is still open marks the
                # previous top-level form as unbalanced (Emacs convention).
                if i == 0 and paren_depth > 0:
                    forms.append({
                        'type': 'error',
                        'start': form_start,
                        'end': line_num,
                        'message': (
                            f'Unbalanced: form started at line {form_start} '
                            f'runs into line {line_num}'
                        ),
                    })
                    form_start = line_num
                    paren_depth = 1
                    i += 1
                    continue
                if paren_depth == 0:
                    form_start = line_num
                paren_depth += 1
                i += 1
                continue
            if ch == ')':
                if paren_depth == 0:
                    forms.append({
                        'type': 'error',
                        'start': line_num,
                        'end': line_num,
                        'message': f'Extra closing parenthesis at line {line_num}',
                    })
                    i += 1
                    continue
                paren_depth -= 1
                if paren_depth == 0:
                    close_form(line_num)
                i += 1
                continue
            i += 1

    if in_string:
        forms.append({
            'type': 'error',
            'start': string_start,
            'end': line_num,
            'message': f'Unclosed string starting at line {string_start}',
        })
    if comment_depth > 0:
        forms.append({
            'type': 'error',
            'start': comment_start,
            'end': line_num,
            'message': f'Unclosed block comment starting at line {comment_start}',
        })
    if paren_depth > 0 and not in_string:
        forms.append({
            'type': 'error',
            'start': form_start,
            'end': line_num,
            'message': (
                f'Unbalanced form: started at line {form_start}, runs to EOF'
            ),
        })

    return forms


def run_self_tests():
    def check(name, source, expect):
        got = [
            (f['type'],) + ((f['message'],) if f['type'] == 'error' else (f['start'], f['end']))
            for f in scan(source.splitlines())
        ]
        assert got == expect, f'{name}:\n  expected {expect}\n  got      {got}'
        print(f'ok: {name}')

    check('two balanced forms',
          '(defun a ()\n  1)\n\n(defun b () 2)',
          [('form', 1, 2), ('form', 4, 4)])

    check('single-line block comment inside form',
          '(foo #| note |# bar)\n(baz)',
          [('form', 1, 1), ('form', 2, 2)])

    check('character literals are not delimiters',
          '(defun p (c)\n  (char= c #\\())\n(defun q (c)\n  (char= c #\\)))\n(defun r (c)\n  (char= c #\\"))',
          [('form', 1, 2), ('form', 3, 4), ('form', 5, 6)])

    check('nested block comments',
          '#| outer #| inner |# still comment |#\n(defun a () 1)',
          [('form', 2, 2)])

    check('unclosed string reported',
          '(defun a ()\n  "no closing quote\n  )',
          [('error', 'Unclosed string starting at line 2')])

    check('unclosed block comment reported',
          '(defun a () 1)\n#| never closed',
          [('form', 1, 1),
           ('error', 'Unclosed block comment starting at line 2')])

    check('stray closing paren reported, later forms survive',
          '(defun a () 1)\n)\n(defun b () 2)',
          [('form', 1, 1),
           ('error', 'Extra closing parenthesis at line 2'),
           ('form', 3, 3)])

    check('form running to EOF',
          '(defun a ()\n  (never closed',
          [('error', 'Unbalanced form: started at line 1, runs to EOF')])

    check('new top-level form while previous open',
          '(defun a ()\n  (oops\n(defun b () 2)',
          [('error', 'Unbalanced: form started at line 1 runs into line 3'),
           ('form', 3, 3)])

    check('parens in line comments and strings ignored',
          '; comment with (parens\n(defun a ()\n  "string with ) paren")',
          [('form', 2, 3)])

    check('escaped quote inside string',
          '(defun a () "she said \\"hi\\" (ok)")',
          [('form', 1, 1)])

    check('multiple forms on one line',
          '(in-package :foo) (defvar x 1)',
          [('form', 1, 1), ('form', 1, 1)])

    print('All tests passed!')


def main():
    if len(sys.argv) < 2 or sys.argv[1] == '--test':
        run_self_tests()
        sys.exit(0)

    filepath = sys.argv[1]
    try:
        forms = extract_top_level_forms(filepath)
        print(json.dumps(forms, indent=2))
    except Exception as e:
        import traceback
        print(json.dumps({'type': 'error', 'message': str(e)}), file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
