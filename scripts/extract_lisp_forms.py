#!/usr/bin/env python3
"""
Extract top-level forms from Common Lisp files.
Returns JSON array of form objects with start/end lines and content.
"""

import sys
import json


def extract_top_level_forms(filepath):
    """Extract all top-level forms from a Lisp file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    state = {
        'in_block_comment': False,
        'in_string': False,
        'escape_next': False,
        'paren_count': 0,
        'current_form': None,
        'forms': [],
    }

    for line_num, line in enumerate(lines, 1):
        process_line(line, line_num, state)

    # Check for unclosed form at EOF
    if state['current_form'] is not None:
        start_line = state['current_form']['start']
        state['forms'].append({
            'type': 'error',
            'start': start_line,
            'end': line_num,
            'message': f'Unbalanced form: started at line {start_line}, runs to EOF'
        })

    return state['forms']


def process_line(line, line_num, state):
    i = 0
    # Track if we've seen non-whitespace on this line
    seen_non_whitespace = False

    # If we're in a block comment, check for end first
    if state['in_block_comment']:
        idx = line.find('|#')
        if idx != -1:
            state['in_block_comment'] = False
            # Process rest of line after |#
            rest = line[idx+2:]
            if rest:
                # Recursively process the rest
                process_line(rest, line_num, state)
        return  # Entire line is block comment

    # Add line to current form (once per line, not per character)
    if state['current_form'] is not None and state['paren_count'] > 0:
        if line_num > state['current_form']['start']:
            state['current_form']['end'] = line_num
            state['current_form']['lines'].append(line.rstrip('\n'))

    while i < len(line):
        char = line[i]

        # Track non-whitespace for detecting start of line
        if char not in (' ', '\t'):
            seen_non_whitespace = True

        # Handle escape sequences in strings
        if state['escape_next']:
            state['escape_next'] = False
            i += 1
            continue

        # String literals
        if char == '"' and not state['in_block_comment']:
            state['in_string'] = not state['in_string']
            i += 1
            continue

        # Escape in strings
        if char == '\\' and state['in_string'] and not state['in_block_comment']:
            state['escape_next'] = True
            i += 1
            continue

        # Block comments: #|
        if (not state['in_string'] and
            char == '#' and i + 1 < len(line) and line[i+1] == '|'):
            state['in_block_comment'] = True
            i += 2
            continue

        # Line comments
        if (not state['in_block_comment'] and
            not state['in_string'] and
            char == ';'):
            break  # Rest of line is comment

        # Parentheses - only count when not in comment or string
        if not state['in_block_comment'] and not state['in_string']:
            if char == '(':
                # Check for unbalanced: new top-level form while previous is open
                # Only check at start of line (before any non-whitespace)
                if (state['current_form'] is not None and
                    state['paren_count'] > 0 and
                    not seen_non_whitespace):
                    # New top-level form started while previous is open
                    state['forms'].append({
                        'type': 'error',
                        'start': state['current_form']['start'],
                        'end': line_num,
                        'message': f'Unbalanced: form started at line {state["current_form"]["start"]} runs into line {line_num}'
                    })
                    # Start new form (discard old)
                    state['current_form'] = {
                        'start': line_num,
                        'end': line_num,
                        'lines': [line.rstrip('\n')]
                    }
                    state['paren_count'] = 1  # Count this '('
                    i += 1
                    continue
                
                state['paren_count'] += 1
                # Top-level form starts when count goes from 0->1
                # Can be at any column (indented forms are valid)
                if (state['paren_count'] == 1 and
                    state['current_form'] is None):
                    state['current_form'] = {
                        'start': line_num,
                        'end': line_num,
                        'lines': [line.rstrip('\n')]
                    }
            elif char == ')':
                state['paren_count'] -= 1

        # Form completed when paren_count hits 0
        if (state['current_form'] is not None and
            state['paren_count'] == 0):
            state['forms'].append({
                'type': 'form',
                'start': state['current_form']['start'],
                'end': state['current_form']['end'],
                'content': '\n'.join(state['current_form']['lines'])
            })
            state['current_form'] = None

        i += 1


def main():
    if len(sys.argv) < 2:
        print(json.dumps([]))
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
