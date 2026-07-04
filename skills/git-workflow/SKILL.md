---
name: git-workflow
description: Git workflow assistance - commit messages, branch management, safe rebase/squash operations
---

# Git Workflow

Provides conversation-driven git workflow assistance with safety-first operations. Use for commit message generation, branch creation, and safe rebase/squash operations.

## Tools

Available: `bash`, `read_file`, `grep`, `edit`, `write_file`, `ask_user_question`

**Usage Guidelines:**
- `bash`: Ask before running (allow: git commands, safe file operations)
- `read_file`: Always for reading files
- `grep`: Always for searching
- `edit`: Ask before modifying files
- `write_file`: Ask before creating files

## When to Use

Activates when user requests git assistance:
- `/git-workflow` - General git workflow help
- `/git-workflow commit` - Generate commit message from changes
- `/git-workflow branch` - Create and checkout a new branch
- `/git-workflow rebase` - Assist with rebase operation
- `/git-workflow squash` - Assist with squash operation
- `/git-workflow stash` - Stash uncommitted changes
- `/git-workflow stash pop` - Restore stashed changes
- `/git-workflow undo` - Undo last commit or operation
- `/git-workflow push` - Push branch with safety checks
- Natural language: "create a git branch for...", "generate git commit message", "help me with git rebase", "squash my git commits", "stash my changes", "undo my commit", "push my branch"

## Core Principles

### 1. Safety First
- **Blocking**: Refuse to execute force push, reset --hard, or rebase on shared branches without explicit user confirmation
- **Warning**: Alert user before any history-rewriting operation
- **Detection**: Check if current branch is shared/protected before dangerous operations

### 2. Conventional Commits Standard
All commit messages follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:
- **Format**: `<type>: <short description>`
- **Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `build`, `ci`, `perf`, `revert`
- **Subject**: ≤50 characters, imperative mood, present tense
- **Body**: Optional, explains *why* not *what*, wrapped at 72 characters
- **Footer**: Optional, for breaking changes or issue references

### 3. Branch Naming Convention
- `feature/<short-description>` - New features
- `fix/<short-description>` - Bug fixes
- `chore/<short-description>` - Maintenance tasks
- `refactor/<short-description>` - Code refactoring
- Use kebab-case, include issue/ticket number if available: `feature/VIC-123-user-auth`

### 4. Workflow Patterns Supported
- **Trunk-Based Development**: Short-lived feature branches (1-3 days), frequent merges
- **GitHub Flow**: Feature branches from main, PR-based merging
- Detect and adapt to user's existing workflow

---

## Step 1: Parse Request

Extract from user input:
- **Operation**: commit, branch, rebase, squash, status, log, or general help
- **Context**: Current branch, uncommitted changes, recent commits
- **Intent**: What the user wants to accomplish

If request is ambiguous, ask for clarification:
- "What type of commit is this? (feat, fix, docs, refactor, etc.)"
- "What should the branch be named?"
- "Which branch are you rebasing onto?"

---

## Step 2: Gather Git Context

Run these commands to understand current state:
```bash
# Current branch and status (includes staged/unstaged changes)
git status --porcelain --branch

# Changes summary
git diff --stat HEAD
git diff --cached --stat

# Recent commits and branch tracking
git log --oneline -10 --decorate

# Check if current branch exists on remote (shared branch detection)
git ls-remote --heads origin | grep -q "refs/heads/$(git branch --show-current)"
```

---

## Step 2.5: Pre-Operation Validation

Before executing any operation, validate:

**For all operations:**
- Working directory must be a git repository (`git rev-parse --is-inside-work-tree`)
- No merge conflicts exist (`git diff --check` for conflict markers)

**For commit:**
- Changes must exist (staged or unstaged)

**For branch creation:**
- Branch name must follow convention (feature/, fix/, chore/, refactor/)
- Branch name must use kebab-case
- Branch name must be ≤50 characters
- Branch must not already exist locally or remotely

**For rebase/squash:**
- Working directory must be clean (no uncommitted changes)
- Current branch must not be shared (see context gathering)
- Current branch must not be protected (main, master, develop, release/*)

**Validation Commands:**
```bash
# Check for conflicts
if git diff --check | grep -q "^<<<<<<<"; then
    echo "CONFLICT: Resolve merge conflicts first"
    exit 1
fi

# Check if branch is protected
protected_patterns=("main" "master" "develop" "release/")
current_branch=$(git branch --show-current)
for pattern in "${protected_patterns[@]}"; do
    if [[ "$current_branch" == "$pattern" || "$current_branch" == "$pattern"* ]]; then
        echo "BLOCKED: Cannot rebase/squash protected branch"
        exit 1
    fi
done
```

---

## Step 3: Execute Operation

### Operation: Commit Message Generation (`/git-workflow commit` or "generate commit message")

**Workflow:**
1. Check for staged changes with `git diff --cached --stat`
2. If no staged changes, prompt: "No changes staged. Stage changes first with `git add` or use `git commit -a`? (y/n)"
3. Analyze diff to determine change type using patterns:
   - `feat`: New files, new functions/classes, "add", "implement", "introduce"
   - `fix`: "fix", "bug", "patch", "resolve", "correct"
   - `refactor`: Code restructuring, renaming, moving (no functional change)
   - `docs`: Changes to `.md`, `.rst`, `.txt` documentation files
   - `test`: Changes to test files (`test_*`, `*_test.*`, `tests/`, `spec/`)
   - `style`: Formatting, whitespace, semicolons, lint fixes
   - `chore`: Build config, package.json, dependency updates, scripts
   - `build`: Build system, compilation, pipeline changes
   - `ci`: CI/CD configuration, workflow files
   - `perf`: Performance optimizations, algorithm improvements
   - `revert`: Reverting previous commits
4. If ambiguous, prompt user: "Which commit type? (feat, fix, docs, refactor, test, chore, build, ci, perf, revert)"
5. Generate Conventional Commits message:
   - **Type**: Detected or user-selected type
   - **Subject**: ≤50 chars, imperative mood, summarizing the change
   - **Body**: Explain the *why* and context if non-obvious
6. Present message for user approval
7. If approved, stage and commit: `git commit -m "<message>"`

**Example Output:**
```
Detected changes:
- src/auth.ts: Added JWT validation middleware
- tests/auth.test.ts: Added authentication tests

Suggested commit message:
```
feat: add JWT authentication middleware

Implement token validation for protected API endpoints.
Adds Bearer token extraction and verification using jsonwebtoken.
Addresses security requirement from VIC-456.
```

Use this message? (y/n/Edit)
```

**Quality Checks:**
- Subject line ≤50 characters
- Type is valid Conventional Commit type
- Message is in imperative mood
- Body explains intent, not just changes

---

### Operation: Branch Creation (`/git-workflow branch` or "create a branch")

**Workflow:**
1. Check current branch: `git branch --show-current`
2. Prompt for branch name if not provided:
   - Suggest based on issue context: `feature/<issue>-<description>`
   - Or use pattern: `feature/short-description`, `fix/short-description`
3. Validate branch name:
   - **Not empty**: Must have at least 1 character
   - **Prefix**: Must start with `feature/`, `fix/`, `chore/`, or `refactor/`
   - **Kebab-case**: Only lowercase letters, numbers, and hyphens
   - **Length**: Must be ≤50 characters
   - **Not exists**: Must not exist locally or remotely
4. If validation fails, prompt: "Invalid branch name. Must be prefixed (feature/fix/chore/refactor), kebab-case, ≤50 chars, and unique. Try again?"
5. Create and checkout branch: `git checkout -b <branch-name>`
6. Set upstream if remote branch exists: `git branch --set-upstream-to=origin/<branch-name>`

**Example Output:**
```
Current branch: main
All changes committed.

Suggested branch name: feature/VIC-123-user-authentication

Create and checkout this branch? (y/n/Edit name)

Branch 'feature/VIC-123-user-authentication' created and checked out.
```

---

### Operation: Rebase Assistance (`/git-workflow rebase` or "rebase onto")

**Workflow:**
1. **Safety Check**: Verify current branch is NOT shared and NOT protected
   ```bash
   current_branch=$(git branch --show-current)
   
   # Check if branch is shared (exists on remote)
   git ls-remote --heads origin | grep -q "refs/heads/$current_branch"
   
   # Check if branch is protected
   protected_patterns=("main" "master" "develop" "release/")
   for pattern in "${protected_patterns[@]}"; do
       if [[ "$current_branch" == "$pattern" || "$current_branch" == "$pattern"* ]]; then
           echo "BLOCKED: Cannot rebase protected branch"
           exit 1
       fi
   done
   ```
   - If shared: **BLOCK** and warn: "This branch exists on remote. Rebasing will rewrite shared history. Use with caution."
   - If protected: **BLOCK** and warn: "Cannot rebase protected branch (main/master/develop/release/*)"
   - Require explicit confirmation: "Type 'REBASE' to confirm you understand the risks:"

2. Determine target branch (default: main or develop)

3. Check for conflicts before starting:
   ```bash
   git fetch origin
git merge-base HEAD origin/<target-branch>
   git diff $(git merge-base HEAD origin/<target-branch>)..HEAD --name-only
   ```

4. Guide user through rebase:
   ```bash
   git rebase origin/<target-branch>
   ```
   - If conflicts occur, provide resolution guidance
   - Explain each step: checkout conflicted files, resolve, `git add`, `git rebase --continue`

5. After successful rebase, prompt to force push (with warning):
   - Only suggest `git push --force-with-lease` (safer than `--force`)
   - Require explicit confirmation

**Example Output:**
```
⚠️  WARNING: Branch 'feature/user-auth' exists on remote.

Rebasing will rewrite history visible to others.
This can cause issues for collaborators who have based work on this branch.

Type 'REBASE' to confirm you understand and accept these risks: 

[User types: REBASE]

Rebasing feature/user-auth onto main...
First, rewinding head to replay your work on top of it...
Applying: feat: add login form
Applying: feat: add auth middleware
Using index info to reconstruct a base tree...
M   src/auth.ts
CONFLICT (content): Merge conflict in src/auth.ts

Conflict detected in src/auth.ts
1. Open the file and resolve the conflict markers (<<<<<<<, =======, >>>>>>>)
2. Stage the resolved file: git add src/auth.ts
3. Continue rebase: git rebase --continue

Need help resolving this conflict? (y/n)
```

---

### Operation: Squash Assistance (`/git-workflow squash` or "squash my commits")

**Workflow:**
1. **Safety Check**: Same as rebase - verify branch is not shared and not protected
   - See Step 2.5 Pre-Operation Validation for protected branch patterns

2. Show commit history to squash:
   ```bash
   git log --oneline HEAD~5..HEAD  # Show last 5 commits
   ```

3. Determine squash point:
   - Ask: "Squash all commits since branch from main? (y/n)"
   - Or: "Squash last N commits?" with interactive selection

4. Guide through interactive rebase for squashing:
   ```bash
   git rebase -i HEAD~N  # Where N is number of commits to squash
   ```
   - Provide the rebase todo list with squash instructions
   - Explain how to edit the todo list

5. After squashing, prompt to update commit message
6. After successful squash, prompt to force push (with warning)

**Example Output:**
```
Last 5 commits on feature/user-auth:
1. a1b2c3d feat: add password reset endpoint
2. d4e5f6g feat: add password reset email service
3. h7i8j9k fix: typo in email template
4. m1n2o3p refactor: extract auth constants
5. p4q5r6s docs: update API documentation

Squash all 5 commits into one? (y/n/Specific range)

[User selects: y]

Interactive rebase todo list (edit this in your editor):

pick p4q5r6s docs: update API documentation
squash m1n2o3p refactor: extract auth constants
squash h7i8j9k fix: typo in email template
squash d4e5f6g feat: add password reset email service
squash a1b2c3d feat: add password reset endpoint

1. Save and close the editor
2. A new editor will open for the combined commit message
3. Save and close to complete squashing

Need me to explain any step in detail? (y/n)
```

---

### Operation: Stash (`/git-workflow stash` or "stash my changes")

**Workflow:**
1. Check for uncommitted changes: `git status --porcelain`
2. If no changes: "No changes to stash"
3. Check for staged changes: `git diff --cached --stat`
4. Prompt: "Stash staged changes only, unstaged only, or both? (staged/unstaged/both)"
5. Execute appropriate stash:
   - Both: `git stash push -u -m "<auto-generated message>"`
   - Staged only: `git stash push -S -m "<auto-generated message>"`
   - Unstaged only: `git stash push -u --keep-index -m "<auto-generated message>"`
6. Confirm: "Changes stashed. Use `/git-workflow stash pop` to restore."

**Example Output:**
```
Uncommitted changes:
 M  src/index.js
?? config.tmp

Stash both staged and unstaged changes? (y/n)
[User: y]

Changes stashed as: WIP on feature/user-auth: 5a6b7c8 Add new feature
To restore: /git-workflow stash pop
```

---

### Operation: Stash Pop (`/git-workflow stash pop` or "restore stashed changes")

**Workflow:**
1. List stashes: `git stash list`
2. If no stashes: "No stashes found"
3. If one stash: Prompt "Apply stash? (y/n)"
4. If multiple stashes: Prompt "Which stash? [0, 1, 2...]"
5. Apply: `git stash apply stash@{<n>}` or `git stash pop stash@{<n>}`
6. If conflicts: See Conflict Resolution section

**Example Output:**
```
Stashes:
  stash@{0}: WIP on feature/user-auth: 5a6b7c8 Add new feature
  stash@{1}: WIP on main: 3d4e5f6 Fix bug

Apply stash@{0}? (y/n/Select other)
[User: y]

Stash applied. Conflicts detected in src/index.js.
See Conflict Resolution section.
```

---

### Operation: Undo (`/git-workflow undo` or "undo my last commit")

**Workflow:**
1. Check if user wants to undo commit, rebase, or other operation
2. **Undo last commit (keep changes staged):**
   - `git reset --soft HEAD~1`
3. **Undo last commit (keep changes unstaged):**
   - `git reset HEAD~1`
4. **Undo last commit (discard changes):**
   - **BLOCK**: Require explicit confirmation "Type 'DISCARD' to permanently discard changes"
   - `git reset --hard HEAD~1`
5. **Undo rebase:**
   - `git rebase --abort`
6. **Undo merge:**
   - `git merge --abort`
7. **Find lost commits:**
   - `git reflog`
   - Guide user to find and restore lost commits

**Example Output:**
```
Last commit: feat: add login form (a1b2c3d)

Undo options:
1. Undo commit, keep changes staged (soft reset)
2. Undo commit, keep changes unstaged (mixed reset)
3. Undo commit, DISCARD all changes (hard reset) - DANGEROUS
4. Undo rebase/merge
5. Find lost commits with reflog

Select option: [1-5]
```

---

### Operation: Push (`/git-workflow push` or "push my branch")

**Workflow:**
1. Check current branch: `git branch --show-current`
2. Check if branch has upstream: `git rev-parse --abbrev-ref @{u} 2>/dev/null`
3. If no upstream:
   - Prompt: "No upstream set. Set upstream to origin/<branch>? (y/n)"
   - If yes: `git push --set-upstream origin <branch>`
4. If upstream exists:
   - Check if branch is behind/ahead: `git log --oneline @{u}..HEAD` and `git log --oneline HEAD..@{u}`
   - If behind: "Your branch is behind remote. Pull first? (y/n)"
   - If diverged: Warn about force push requirement
5. If shared branch and diverged:
   - **BLOCK**: Require explicit confirmation "Type 'FORCE PUSH' to overwrite remote history"
   - Suggest `--force-with-lease` instead of `--force`
6. Execute push: `git push` or `git push --force-with-lease`

**Example Output:**
```
Branch: feature/user-auth
Upstream: origin/feature/user-auth
Status: 2 commits ahead, 1 commit behind

Your branch has diverged from remote. Options:
1. Pull and merge (recommended)
2. Rebase onto remote and force push
3. Force push (overwrites remote) - DANGEROUS

Select option: [1-3]
```

---

### Operation: General Git Help (`/git-workflow` or "help with git")

**Workflow:**
1. Show current git status: branch, uncommitted changes, recent commits
2. Suggest next actions based on context:
   - Uncommitted changes → suggest commit or stash
   - On main branch → suggest create feature branch
   - Diverged from main → suggest pull or rebase
   - Merge conflicts → suggest resolution steps

3. Provide relevant git commands for the situation

**Example Output:**
```
Current Git Status:
- Branch: feature/user-auth
- Upstream: origin/feature/user-auth
- Uncommitted changes: 2 files modified
- Recent commits: 3 ahead of main

Suggested Actions:
1. Review changes: git diff
2. Stage changes: git add -p (interactive) or git add .
3. Commit: /git-workflow commit
4. Push: git push
5. Rebase onto main: /git-workflow rebase

What would you like to do?
```

---

## Step 4: Safety Layer (CRITICAL)

### Blocking Operations
These operations **must never** be executed without explicit user confirmation:

```bash
# Force push (overwrites remote history)
git push --force
git push --force-with-lease  # Still dangerous, just safer

# Hard reset (discards local changes)
git reset --hard

# Rebase on shared branch
git rebase origin/main  # When current branch is shared
```

**Confirmation Protocol:**
1. Detect the operation is about to rewrite history
2. Check if branch is shared (exists on remote)
3. Display clear warning of consequences
4. Require user to type a specific confirmation string (e.g., "FORCE PUSH", "REBASE", "RESET")
5. Only then execute the operation

### Warning Operations
These operations should trigger a warning but can proceed with simple confirmation:

```bash
# Soft reset (preserves changes in working directory)
git reset --soft

# Mixed reset (preserves changes as unstaged)
git reset --mixed

# Amend commit (rewrites last commit)
git commit --amend

# Squash merge
git merge --squash
```

**Warning Protocol:**
1. Detect the operation
2. Display warning: "This will modify git history. Continue? (y/n)"
3. Proceed if user confirms

### Safe Operations
These can be executed directly:
- `git status`
- `git diff`
- `git log`
- `git branch`
- `git checkout` (non-destructive)
- `git add`
- `git commit` (with generated message)
- `git pull` (without rebase)
- `git fetch`

---

## Conflict Resolution

When merge or rebase conflicts occur, guide user through resolution:

### Identifying Conflicts
- Check for conflict markers: `git diff --check | grep -q "^<<<<<<<"`
- List conflicted files: `git status --porcelain | grep "^UU"`
- Show conflict details: `git diff` on each conflicted file

### Resolution Strategies

**1. Manual Resolution:**
- Open each conflicted file
- Find conflict markers: `<<<<<<< HEAD`, `=======`, `>>>>>>> branch-name`
- Edit to keep desired changes, remove markers
- Stage resolved file: `git add <file>`
- Continue operation: `git rebase --continue` or `git commit`

**2. Using Merge Tool:**
- Configure tool: `git config --global merge.tool vimdiff`
- Launch: `git mergetool`
- Follow tool-specific instructions

**3. Abort Operation:**
- For rebase: `git rebase --abort`
- For merge: `git merge --abort`
- For stash: `git stash drop stash@{n}`

**4. Common Resolution Patterns:**
- **Keep ours**: Keep current branch changes, discard incoming
- **Keep theirs**: Keep incoming changes, discard current
- **Combine**: Manually merge both sets of changes
- **Use diff3**: `git diff3` to see common ancestor

### After Resolution
1. Verify build still works
2. Run tests
3. Check for unintended changes: `git diff --cached`

**Example Conflict Resolution:**
```
Conflicts detected in:
- src/index.js
- config.json

Conflict in src/index.js:
<<<<<<< HEAD
const version = '2.0';
=======
const version = '2.1';
>>>>>>> feature/new-version

Resolution options:
1. Keep '2.0' (current)
2. Keep '2.1' (incoming)
3. Use custom value

Select resolution for src/index.js: [1-3]
[User selects: 2]

File resolved. Continue rebase? (y/n)
```

---

## Step 5: Output Format

All responses follow this structure:

```markdown
## Git Operation: {operation}

**Context:**
- Current branch: {branch}
- Status: {clean/dirty}
- Changes: {files}

**Action:** {what will be done}

**Safety Check:** {pass/warning/block}

{operation-specific content}

**Next Steps:**
{what user should do next}
```

---

## Verification

Test with:
- [ ] `/git-workflow commit` on staged changes
- [ ] `/git-workflow commit` with no staged changes (should prompt)
- [ ] `/git-workflow branch` to create new branch
- [ ] `/git-workflow branch` with invalid name (should reject)
- [ ] `/git-workflow rebase` on local-only branch (should work)
- [ ] `/git-workflow rebase` on shared branch (should block without confirmation)
- [ ] `/git-workflow rebase` on protected branch (should block)
- [ ] `/git-workflow squash` on local-only branch (should work)
- [ ] `/git-workflow stash` with uncommitted changes
- [ ] `/git-workflow stash pop` with stashed changes
- [ ] `/git-workflow undo` to undo last commit
- [ ] `/git-workflow push` with no upstream (should offer to set)
- [ ] `/git-workflow push` with diverged branch (should warn)
- [ ] `/git-workflow` for general status and suggestions
- [ ] Natural language: "create a branch for fixing the login bug"
- [ ] Natural language: "generate a commit message for my changes"
- [ ] Natural language: "stash my changes"
- [ ] Natural language: "undo my last commit"

---

## Red Flags

Warn user about:
- Branch has been diverged from upstream for >3 days
- No `.gitignore` file in project
- Committing build artifacts (`node_modules/`, `dist/`, `.env`)
- Large uncommitted changes (>1000 lines)
- Vague commit messages ("fix", "update", "misc")
- Force pushing to shared branches
- Long-lived feature branches (>7 days)
