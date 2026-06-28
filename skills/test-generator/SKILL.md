---
name: test-generator
description: Automatic generation of unit and integration tests from code with framework detection
---

# Test Generator

## Triggering Conditions

Activates when user requests test generation:
- `/test-generator <file>` - Generate tests for specific file
- `/test-generator <file> <scope>` - Generate tests for specific scope (function, class, method)
- `/test-generator` - Generate tests for current context/files
- "generate unit tests for..."
- "write tests for..."
- "create test cases for..."
- "test-generator: ..."

## Step 1: Parse Request

Extract:
- **Target:** File(s) or code to generate tests for
- **Scope:** Specific function, class, or method (optional, user-specified)
- **Test Type:** Unit tests (default) or integration tests (if explicitly requested)
- **Description:** Natural language description of desired test behavior (optional)

If target is unspecified:
- Check project context for relevant files
- If ambiguous: prompt "Which file or code should I generate tests for?"

If scope is unspecified for large files (>1000 lines):
- Warn user: "This file has {N} lines. For better results, specify a function/class or continue with full file."
- Prompt: "Specify scope or type 'continue' for full file: "

## Step 2: Determine Context

Analyze project to detect:
- **Language:** From file extension and content
- **Framework:** From project structure, configuration files, and import statements
- **Test conventions:** From existing test files (naming, structure, location)

**Framework Detection:**
| Language | File Extension | Framework Indicators | Test Location | Naming Convention |
|----------|---------------|---------------------|---------------|-------------------|
| Python | .py | pytest, unittest imports | tests/ | test_*.py, *_test.py |
| Java | .java | JUnit imports | src/test/java | *Test.java |
| JavaScript/TypeScript | .js, .ts | Jest, Mocha, Vitest | __tests__/, tests/ | *.test.js, *.spec.js |
| Go | .go | testing package | *test.go files | *Test |
| Ruby | .rb | RSpec, Minitest | spec/, test/ | *_spec.rb, test_*.rb |
| Rust | .rs | Cargo test conventions | tests/ | lib.rs, mod.rs patterns |

If framework cannot be determined:
- Use language defaults
- Note: "Detected {language} but framework unclear. Using generic patterns. Specify framework with --framework flag if needed."

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
- **JUnit:** `shouldReturnX_whenY` or `whenA_thenB`
- **Jest:** `describe("FunctionName", () => { it("should do X when Y", () => {...}) })`

### Deep Edge Case Analysis
- **Boundary Values:** 0, 1, -1, MAX_INT, MIN_INT, empty strings, empty arrays
- **Time-related:** Past dates, future dates, current time, timezones
- **State Transitions:** Valid state changes, invalid state changes
- **Concurrency:** If async code, test race conditions, timeouts
- **Input Combinations:** Test combinations of optional parameters

### Test Content Generation
For each test case:
- Generate descriptive name following framework conventions
- Create test setup (arrange)
- Write test execution (act)
- Add assertions (assert) with clear messages
- Include necessary imports and mocks
- Add comments explaining edge cases if non-obvious

### Mocking Strategy
- Identify external dependencies (API calls, database, files)
- Generate mock implementations for isolated testing
- Follow framework-specific mocking patterns:
  - pytest: `pytest-mock` or `unittest.mock`
  - JUnit: Mockito
  - Jest: `jest.fn()`, `jest.mock()`

## Step 5: Create Test Files

Determine test file location based on project conventions:
- If `tests/` directory exists: Place there, mirroring source structure
- If `__tests__/` directories exist: Place adjacent to source
- If framework-specific (JUnit): Place in `src/test/java` mirroring `src/main/java`
- Otherwise: Create `tests/` directory and mirror structure

**File Creation Rules:**
- If file exists: Append new tests (with separator comment)
- If file doesn't exist: Create new file with proper header
- Always preserve existing tests
- Add file header with generated date and source reference

**Example Output Structure:**
```
# For pytest
 tests/
   test_calculator.py
   test_utils.py

# For JUnit
 src/test/java/com/example/
   CalculatorTest.java
   UtilsTest.java

# For Jest
 __tests__/
   calculator.test.js
   utils.test.js
```

## Step 6: Quality Validation

Before finalizing, check:
- [ ] Tests follow AAA pattern
- [ ] Naming follows framework conventions
- [ ] Tests are isolated (no dependencies between tests)
- [ ] Edge cases are covered
- [ ] Mocking is appropriate
- [ ] Assertions are meaningful
- [ ] Test file location follows project conventions

If issues found, regenerate or warn user.

## Step 7: Output

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

## Verification

Test with:
- [ ] `/test-generator` on a simple Python file with functions
- [ ] `/test-generator file.py function_name` for specific function
- [ ] `/test-generator` on a Java class
- [ ] `/test-generator` on a large file (>1000 lines) - should warn
- [ ] `/test-generator` with integration test request
- [ ] `/test-generator` on file with unclear framework - should detect or ask
