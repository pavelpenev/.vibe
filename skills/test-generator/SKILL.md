---
name: test-generator
description: Generate unit and integration tests for a single file/module with framework detection and self-review. Scope is limited to single file/module only.
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - grep
  - todo
  - task
  - skill
  - ask_user_question
  - web_search
---

# Test Generator

## Overview

Generates unit and integration tests for a **single file or module** with automatic framework detection, comprehensive edge case coverage, and self-review of output. Uses code-review skill to validate generated tests before presentation.

**Scope Limitation**: This skill is designed for single file/module test generation only. Requests for large subsystems or entire codebases are out of scope and should be rejected with guidance to break down the request.

## Triggering Conditions

Activates when user requests test generation:
- `/test-generator <file>` - Generate tests for specific file
- `/test-generator <file> <scope>` - Generate tests for specific scope (function, class, method)
- `/test-generator` - Generate tests for current context (single file only)
- "generate unit tests for..."
- "write tests for..."
- "create test cases for..."
- "test-generator: ..."

## Step 1: Parse Request and Validate Scope

Extract:
- **Target:** File or module to generate tests for
- **Scope:** Specific function, class, or method (optional, user-specified)
- **Test Type:** Unit tests (default) or integration tests (if explicitly requested)
- **Description:** Natural language description of desired test behavior (optional)

**Scope Validation:**
- If request is for "entire project", "all files", "whole codebase", or similar: **REJECT** with message: "Test generation is limited to single file/module. Please specify a single file or module."
- If request is for a directory or multiple files: **REJECT** with message: "Test generation is limited to single file/module. Please specify a single file."
- If target is unspecified:
  - Check project context for relevant single file
  - If ambiguous: prompt "Which single file or module should I generate tests for?"

If scope is unspecified for large files (>1000 lines):
- Warn user: "This file has {N} lines. For better results, specify a function/class or continue with full file."
- Prompt: "Specify scope or type 'continue' for full file: "
- If user does not respond or responds ambiguously: **ABORT**

Use the todo tool to track the test generation task.

## Step 2: Determine Context

Analyze project to detect:
- **Language:** From file extension and content (primarily Python and Common Lisp)
- **Framework:** From project structure, configuration files, and import statements
- **Test conventions:** From existing test files (naming, structure, location)
- **Project-specific instructions:** Check project AGENTS.md for test location and run instructions

**Framework Detection:**
| Language | File Extension | Framework Indicators | Test Location | Naming Convention |
|----------|---------------|---------------------|---------------|-------------------|
| Python | .py | pytest, unittest imports | tests/ | test_*.py, *_test.py |
| Common Lisp | .lisp, .cl | CL test frameworks (e.g., Prove, FiveAM) | tests/, t/ | test-*.lisp, *-test.lisp |

**Note:** This skill is designed primarily for Python and Common Lisp projects. For other languages, it will attempt generic test patterns, but project AGENTS.md should provide specific guidance.

If framework cannot be determined:
- Check project AGENTS.md for framework instructions
- Use language defaults
- Note: "Detected {language} but framework unclear. Using generic patterns. Check project AGENTS.md for framework-specific instructions."
- Prompt user: "Framework unclear. Should I proceed with generic patterns, or do you have specific framework preferences?"

## Step 3: Analyze Target Code

For the target file/scope:
1. Parse code structure (functions, classes, methods, exports)
2. Identify public API surface (public methods, exported functions)
3. Extract type signatures and parameter information
4. Identify dependencies (imports, external calls)
5. Detect code patterns (error handling, async operations, side effects)

For user-specified scope:
- Focus only on the specified function/class/method
- Ignore other code in the file

## Step 4: Generate Tests

For each testable unit (function, method, class):

### Test Structure (AAA Pattern)
```
[Arrange] Setup test data, mocks, and preconditions
[Act] Call the function/method under test
[Assert] Verify the outcome
```

### Test Case Types (Generate All Applicable)
1. **Happy Path:** Normal input, expected output
2. **Edge Cases:** Boundary values, empty inputs, maximum/minimum values
3. **Error Cases:** Invalid inputs, exceptions, error conditions
4. **Null/Undefined:** Missing or null parameters
5. **Type Variations:** Different input types (if dynamically typed language)
6. **Side Effect Verification:** Changes to external state, mock calls

### Naming Conventions by Framework
- **Generic:** `test{FunctionName}_{Scenario}_{ExpectedResult}`
- **pytest:** `test_function_name_scenario`
- **unittest:** `test_function_name_scenario` or `TestClassName.test_method_name`
- **Prove (Common Lisp):** `test-function-name-scenario` or nested `is` tests

### Deep Edge Case Analysis
- **Boundary Values:** 0, 1, -1, MAX_INT, MIN_INT, empty strings, empty arrays, NIL/null
- **Time-related:** Past dates, future dates, current time, timezones (if applicable)
- **State Transitions:** Valid state changes, invalid state changes
- **Input Combinations:** Test combinations of optional parameters
- **Type-related:** For dynamically typed languages, test with different types

### Test Content Generation
For each test case:
- Generate descriptive name following framework conventions
- Create test setup (arrange)
- Write test execution (act)
- Add assertions (assert) with clear messages
- Include necessary imports and mocks
- Add **docstrings/comments** explaining:
  - What the test is verifying
  - Why this edge case is important
  - Any non-obvious setup or assumptions
- Ensure tests are well-documented and readable

### Mocking Strategy
- Identify external dependencies (API calls, database, files)
- Generate mock implementations for isolated testing
- Follow framework-specific mocking patterns:
  - pytest: `pytest-mock` or `unittest.mock`
  - unittest: `unittest.mock`
  - Prove (Common Lisp): Framework-specific mocking utilities

## Step 5: Review Existing Tests and Plan Changes

Before creating or modifying any test files, review existing tests:

**Existing Test Review:**
- Read any existing test file for the target module
- Identify what functionality is already tested
- Check for duplicates with planned new tests
- Note any gaps in existing coverage
- **Do NOT remove or replace existing tests** - only append or modify to expand coverage

**Plan Test Changes:**
- Determine which new tests are needed (avoiding duplicates)
- Identify any existing tests that should be updated or expanded
- Create a todo list of test changes
- Present plan to user: "I will add {N} new tests and update {M} existing tests in {test_file_path}. Continue? [Y/N]"
- **REQUIRE explicit user confirmation (Y/yes) before proceeding**

## Step 6: Create Test Files

Determine test file location based on project conventions and project AGENTS.md:
- If project AGENTS.md specifies test location: Use that
- If `tests/` directory exists: Place there, mirroring source structure
- If `__tests__/` directories exist: Place adjacent to source
- Otherwise: Create `tests/` directory and mirror structure

**File Creation Rules:**
- If file exists: Append new tests (with separator comment)
- If file doesn't exist: Create new file with proper header
- **Always preserve existing tests** - never remove tested functionality
- Add file header with generated date and source reference
- Ensure test file is well-organized with no duplicates

**Example Output Structure:**
```
# For pytest
 tests/
   test_calculator.py
   test_utils.py

# For Common Lisp (Prove)
 tests/
   test-calculator.lisp
   test-utils.lisp
```

## Step 7: Self-Review

Use the code-review skill to assess the generated tests:
- Invoke code-review skill on the generated test file
- Check for quality issues, style problems, or bugs in the tests
- If code-review identifies issues: Attempt to fix them automatically
- If issues persist after one fix attempt: Surface to user for resolution

## Step 8: Quality Validation

Before finalizing, verify:
- [ ] Tests follow AAA pattern
- [ ] Naming follows framework conventions
- [ ] Tests are isolated (no dependencies between tests)
- [ ] Edge cases are covered
- [ ] Mocking is appropriate
- [ ] Assertions are meaningful
- [ ] Test file location follows project conventions

**If validation fails:**
- Attempt to fix issues automatically (one attempt per issue)
- After repeated failure on any issue: **STOP** and prompt user: "Validation failed: {issue}. Unable to fix automatically. Please review."

## Step 9: Test Execution

**Run the generated tests** using project-specific or framework-default commands:
- If project AGENTS.md specifies test run command: Use that
- Otherwise, use framework defaults:
  - pytest: `pytest {test_file_path} -v`
  - unittest: `python -m unittest {test_file_path}`
  - Prove (Common Lisp): Implementation-specific, check project

**Handle test failures:**
If tests fail, determine the cause:
1. **Expected failure** (user requested tests before implementation/bugfix): Report as expected, note that implementation is needed
2. **Test is wrong**: Attempt to fix the test (one attempt), if still failing go to step 3
3. **Test found a bug in tested code**: Report the bug found, suggest fixing the source code

If cause is unclear or cannot be fixed automatically:
- Prompt user: "Tests failed. Possible causes: (a) expected failure before implementation, (b) test bug, (c) bug in tested code. I {attempted fix/could not determine}. Please advise."

## Step 10: Output

Present results:
```markdown
## Test Generation Complete

**Target:** {file}:{scope}
**Language:** {language}
**Framework:** {framework}
**Test Type:** {unit/integration}
**Tests Generated:** {count}

### Files Created/Modified:
- `{test_file_path}` ({N} new tests)

### Test Summary:
| Test | Type | Coverage |
|------|------|----------|
| test_function_happy_path | Happy Path | Core functionality |
| test_function_empty_input | Edge Case | Input validation |
| test_function_invalid_input | Error Case | Error handling |

**Next Steps:**
- Review generated tests in {test_file_path}
- Run tests to verify they pass: `{run_command}`
- Modify tests as needed for your specific requirements
```

If tests were appended to existing file:
```markdown
**Note:** {N} tests appended to existing file {test_file_path}
```

## Configuration

Users can configure via AGENTS.md:

```markdown
## Test Generator Settings
- Default test type: unit (unit | integration)
- Max file size without warning: 1000 (lines)
- Include integration test patterns: false (true | false)
- Framework detection: auto (auto | specify)
```

## Quality Gates

Before output, verify:
1. All generated tests are syntactically valid for the target language
2. Tests cover at least happy path and one edge case per function
3. Test file structure matches project conventions
4. No duplicate test names in output file

## Red Flags

- User requests tests for auto-generated files (skip with warning)
- File is binary or non-code (skip with error)
- No testable functions found (warn user)
- Language cannot be determined (ask user or skip)
- Request for entire codebase or multiple files (reject with scope error)

## Error Handling

**When errors occur:**
- **Recoverable errors** (framework unclear, scope needs clarification): Prompt user for input, continue after resolution
- **Irrecoverable errors** (binary file, no testable functions, out of scope request): **STOP** and prompt user for help
- **Validation failures**: Attempt one automatic fix, then **STOP** and surface to user
- **Test failures after generation**: Handle per Step 9 (Test Execution)

**User Prompting:**
- For all errors requiring user input: Clearly state the issue and ask for resolution
- If user does not respond: **ABORT** the task (interactive harness will handle this)
- Include context: What was being attempted, why it failed, what needs to be resolved

## Integration

- **Context priority**: Project-local AGENTS.md > PLAN.md > Global AGENTS.md
- **PLAN.md**: You may read PLAN.md for context but must not modify it unless explicitly told
- **Skills**: May invoke code-review for self-assessment of generated tests
- **Todo tool**: Use for tracking test generation steps and issues
- **Project AGENTS.md**: Check for project-specific test location, framework, and run instructions

## Verification

Test with:
- [ ] `/test-generator` on a simple Python file with functions
- [ ] `/test-generator file.py function_name` for specific function
- [ ] `/test-generator` on a Common Lisp file
- [ ] `/test-generator` on a large file (>1000 lines) - should warn
- [ ] `/test-generator` with integration test request
- [ ] `/test-generator` on file with unclear framework - should detect or ask
- [ ] `/test-generator` on entire project request - should reject with scope error
- [ ] `/test-generator` on directory request - should reject with scope error
