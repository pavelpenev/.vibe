---
name: debugging
description: Systematic, language-agnostic debugging assistant that helps reproduce, isolate, diagnose, fix, and prevent bugs using a structured methodology with AI-powered root cause analysis and regression test generation.
---

# Debugging

## Description

Provides systematic debugging assistance for code, following a structured 6-step methodology to identify, reproduce, isolate, and fix bugs. Focuses on language-agnostic analysis with AI-powered root cause identification and prevention strategies. Generates clear, actionable markdown reports with reproduction steps, root cause analysis, and regression tests.

## Triggering Conditions

Activates when user requests debugging:
- `/debugging` - Debug current context or uncommitted changes
- `/debugging <file>` - Debug specific file
- `/debugging <error>` - Debug specific error message or pattern
- "debug this" - Debug referenced code
- "find the bug" - Identify bugs in code
- "why is this failing" - Analyze failing code/tests
- "troubleshoot" - Debug the current issue

## Step 1: Parse Request

**Extract:**
- **Target:** Files, errors, or code to debug
- **Scope:** Specific file/function or general context (default: narrow scope)
- **Description:** Error description or symptoms (prompt if missing)
- **Context:** Language, framework, project structure

**If target is unspecified:**
- Check for uncommitted changes via `git status`
- If changes exist: Identify modified files and focus on those
- If no changes: Check for recent errors in logs or ask user to specify

**If description is missing:**
- **Prompt user:** "What error or unexpected behavior are you seeing? (e.g., 'function returns wrong value', 'test is failing')"
- Wait for user response before proceeding

**If scope is too broad (>1000 lines or multiple files):**
- **Warn user:** "This scope is large. For better results, specify a file or function, or type 'continue' for full analysis."
- Prompt: "Specify scope or type 'continue': "

## Step 2: Reproduction

**Attempt to reproduce the issue based on description:**

1. **If error message provided:**
   - Search codebase for the error
   - Identify where it originates
   - Trace the execution path

2. **If test failure described:**
   - Locate the failing test
   - Run the test to confirm failure
   - Capture actual vs expected output

3. **If behavior issue described:**
   - Create minimal reproduction case
   - Document exact steps to reproduce
   - Verify the issue reproduces consistently

4. **If cannot reproduce:**
   - Guide user to provide more details
   - Ask for: exact inputs, environment, steps taken
   - Suggest adding logging/instrumentation

**Generate minimal reproduction if helpful:**
- Create standalone script/file that demonstrates the issue
- Include only essential code
- Document expected vs actual behavior

**Validate reproduction before proceeding to analysis.**

## Step 3: Analysis (Systematic Debugging Methodology)

Apply the 6-step systematic debugging process:

### 3.1 Isolate (Narrow Down Location)
**Techniques:**
- **Binary search debugging:** Divide codebase and test subsets to narrow down
- **Code segmentation:** Identify likely components based on error type
- **Dependency isolation:** Check if issue persists with mocked dependencies
- **Environment simplification:** Test in minimal environment
- **Git bisect:** If applicable, identify introducing commit

**Output:** Narrowed scope (file, function, or code segment)

### 3.2 Hypothesize (Generate Theories)
**Develop testable theories about the root cause:**
- Based on error patterns and symptoms
- Drawing from common bug categories:
  - Logic errors
  - Configuration issues
  - Environment problems
  - Integration failures
  - Performance bottlenecks
  - Security vulnerabilities

**Output:** List of hypotheses to test

### 3.3 Diagnose (Test Hypotheses)
**Validate each hypothesis:**
- Add targeted logging or instrumentation
- Run controlled tests with specific inputs
- Check edge cases and boundary conditions
- Review related code and dependencies
- Analyze execution traces (if available)

**Output:** Confirmed root cause

### 3.4 Root Cause Identification
**Identify and categorize the fundamental cause:**

**Categories:**
| Category | Description | Examples |
|----------|-------------|----------|
| Logic | Incorrect algorithm or implementation | Wrong condition, off-by-one, incorrect formula |
| Configuration | Misconfiguration | Wrong settings, missing config, environment mismatch |
| Integration | Interface/dependency issues | API contract violation, incompatible versions |
| Performance | Speed/memory issues | Inefficient algorithm, memory leak, timeout |
| Security | Vulnerability or exposure | Hardcoded secrets, injection, race condition |
| Data | Incorrect data handling | Wrong type, missing validation, corruption |
| Concurrency | Race conditions, deadlocks | Shared state issues, async problems |

**Output:** Root cause with category, location, and explanation

## Step 4: Language-Agnostic Checks

Run these universal checks on the narrowed scope. Report findings by severity.

### ERROR (Blocking - Must Fix)
- **Hardcoded secrets:** API keys, passwords, tokens, private keys in code
  - Patterns: `api[_-]?key`, `password`, `secret`, `token`, `private[_-]?key`, `access[_-]?key`, `auth`, `credential`
  - High-entropy strings that look like secrets
- **Security vulnerabilities:** SQL injection, XSS, command injection patterns

### WARNING (Should Fix)
- **Variables used before definition** (within visible scope)
- **Variables defined but never used**
- **Functions that should return a value but don't** (missing return statement)
- **Exception handlers that catch all exceptions** without handling (`except:` or `catch (`)
- **Missing error handling** for operations that can fail (file I/O, network calls, DB)
- **Infinite loop patterns** (no loop termination condition)
- **Unreachable code** (code after return/throw/break)

### INFO (Consider Fixing)
- **Line length > 120 characters**
- **Consecutive blank lines** (>2)
- **Trailing whitespace**
- **Mixed tabs and spaces**
- **File missing trailing newline**
- **Inconsistent naming conventions**
- **Commented-out code**

**Note:** Style checks only report if >5 violations exist per file.

## Step 5: Fix Suggestion & Validation

### 5.1 Suggest Fixes
For each confirmed issue, provide:
1. **Primary Fix:** Description + code snippet
   - **Rationale:** Why this fixes the issue
   - **Impact:** What changes and potential side effects

2. **Alternative Fixes** (if applicable):
   - Description of alternative approach
   - Trade-offs (pros/cons vs primary fix)

### 5.2 Generate Regression Test
Create a test case that:
- Reproduces the original issue
- Validates the fix
- Prevents future regressions

**Test structure:**
```
# Test for [issue description]
# Expected: [correct behavior]
# Actual (before fix): [incorrect behavior]

def test_[description]():
    # Arrange
    [setup code]
    
    # Act
    result = [function call]
    
    # Assert
    assert [condition], f"Expected {expected}, got {result}"
```

### 5.3 Validation Steps
Provide steps to verify the fix:
1. Apply the suggested change
2. Run the regression test
3. Test with original reproduction case
4. Check for new regressions in related functionality

## Step 6: Prevention & Documentation

### 6.1 Document Solution
- **Root Cause:** Clear explanation of what went wrong
- **Fix Applied:** What was changed
- **Why It Worked:** The reasoning behind the fix
- **Lessons Learned:** What to watch for in the future

### 6.2 Create Prevention Measures
- **Regression Test:** The test case from Step 5.2
- **Code Review Checklist:** Items to verify in future reviews
- **Process Improvement:** Suggestions for preventing similar issues

### 6.3 Update Knowledge Base
- Suggest documentation updates
- Recommend adding to team's common issues list
- Identify patterns to share with the team

## Output Format

Present all findings in a structured markdown report:

```markdown
## Debugging Report

**Target:** {files/errors debugged}
**Language:** {detected or specified}
**Scope:** {narrow/deep}
**Status:** {REPRODUCED/FIXED/NEEDS_INFO/NO_ISSUE_FOUND}

---

### Summary
{1-2 sentence overview of the issue and resolution status}

---

### Reproduction

**Steps:**
1. {step 1}
2. {step 2}
...

**Command:** `{command to reproduce, if applicable}`

**Expected:** {expected behavior}
**Actual:** {actual behavior}

---

### Root Cause Analysis

**Category:** {Logic/Configuration/Integration/Performance/Security/Data/Concurrency}
**Location:** {file:line or component}
**Description:** {detailed explanation of root cause}

---

### Findings

#### Blocking Issues (Must Fix)
{List of ERROR findings, if any}

- **[SECURITY]** Hardcoded {type} detected at `{file}:{line}`
  ```
  {code snippet}
  ```
  **Fix:** Move to environment variable or secret manager

#### Warnings (Should Fix)
{List of WARNING findings, if any}

- **[BUG]** Variable `{var}` used before definition at `{file}:{line}`
- **[BUG]** Variable `{var}` defined but never used at `{file}:{line}`
- **[BUG]** Function missing return value at `{file}:{line}`

#### Info (Consider Fixing)
{List of INFO findings, if >5 per file}

- **[STYLE]** Line {N} exceeds 120 characters at `{file}`
- **[STYLE]** Consecutive blank lines at `{file}:{line}`

---

### Suggested Fixes

1. **Primary Fix:** {description}
   ```{language}
   {code snippet}
   ```
   **Rationale:** {why this fixes the issue}
   **Impact:** {potential side effects}

2. **Alternative Fix:** {description}
   **Trade-offs:** {pros/cons}

---

### Regression Prevention

**Test Case:**
```{language}
{test code}
```

**Documentation:** {suggested docs update}
**Process:** {recommended workflow change}

---

### Next Steps
- [ ] Apply suggested fix
- [ ] Run regression test
- [ ] Update documentation
- [ ] Review related code for similar issues
```

## Quality Gates

Before finalizing the report, verify:
- [ ] Root cause is clearly identified and explained
- [ ] All findings are categorized by severity
- [ ] Suggested fixes are actionable and include reasoning
- [ ] Regression test covers the specific issue
- [ ] User can understand and apply the recommendations

## Red Flags

If any of these occur, escalate or request clarification:
- User requests debugging of auto-generated files (skip with warning)
- File is binary or non-code (skip with error)
- No testable code found in scope (warn user)
- Language cannot be determined (ask user or skip)
- Large file (>1000 lines) without specific scope (warn user)
- Security vulnerability detected (BLOCKING - require immediate attention)

## User Interaction Guidelines

1. **Always prompt for missing information:** Description, reproduction steps, expected behavior
2. **Request confirmation before:**
   - Running destructive commands
   - Modifying files
   - Executing code (if safety is a concern)
3. **Explain reasoning:** Provide clear rationale for findings and suggestions
4. **Offer options:** When multiple approaches are valid
5. **Ask for clarification:** When ambiguous or uncertain

## Configuration

Users can configure via AGENTS.md:

```markdown
## Debugging Settings
- Max file size without warning: 1000 (lines)
- Style warning threshold: 5 (violations per file)
- Block on secrets: true (default)
- Include integration test patterns: false (true | false)
```

## Verification

Test with:
- [ ] `/debugging` on uncommitted changes
- [ ] `/debugging file.py` on specific file
- [ ] `/debugging` with error message
- [ ] `/debugging` on large file (>1000 lines) - should warn
- [ ] `/debugging` with hardcoded secret (should detect and block)
- [ ] `/debugging` without description (should prompt)
- [ ] `/debugging` on auto-generated file (should skip with note)
