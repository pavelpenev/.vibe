---
name: main-git-workflow
description: Git workflow assistance - commit messages, branch management, rebase/squash guidance (history rewrites are handoff-only, never agent-executed)
user-invocable: true
allowed-tools:
  - bash
  - read_file
  - grep
  - ask_user_question
---

# Git Workflow

Provides conversation-driven git workflow assistance with safety-first operations. Use for commit message generation, branch creation, and rebase/squash guidance — history-rewriting operations are explained and handed off to the user, never executed by the agent.

## Tools

Available: `bash`, `read_file`, `grep`, `ask_user_question`

**Usage Guidelines:**
- `bash`: Ask before running (allow: safe git commands only — never history-rewriting ones; see Core Principles)
- `read_file`: Always for reading files
- `grep`: Always for searching
- File edits (e.g., conflict resolution) are done by the main agent's normal editing flow, not by this skill

## When to Use

Activates when user requests git assistance:
- `/main-git-workflow` - General git workflow help
- `/main-git-workflow commit` - Generate commit message from changes
- `/main-git-workflow branch` - Create and checkout a new branch
- `/main-git-workflow rebase` - Assist with rebase operation
- `/main-git-workflow squash` - Assist with squash operation
- `/main-git-workflow stash` - Stash uncommitted changes
- `/main-git-workflow stash pop` - Restore stashed changes
- `/main-git-workflow undo` - Undo last commit or operation
- `/main-git-workflow push` - Push branch with safety checks
- Natural language: "create a git branch for...", "generate git commit message", "help me with git rebase", "squash my git commits", "stash my changes", "undo my commit", "push my branch"

## Core Principles

### 1. Safety First
- **Handoff-only history rewriting**: The agent never executes history-rewriting operations — rebase, squash via reset, amend, any reset that moves existing commits, force push — even with explicit user confirmation. The agent explains the operation, prepares exact commands, and the user runs them in their own terminal.
- **Warning**: Alert user before any history-rewriting operation
- **Detection**: Check if current branch is shared/protected before advising on dangerous operations
- **Shared safety ban**: The shared AGENTS rules prohibit destructive checkout, reset, clean, and history-rewrite operations by the agent. This skill never loosens that ban, and user confirmation does not lift it. Operations the agent must not run itself (`git rebase`, `git reset` that moves history, `git commit --amend`, `git push --force*`, `git reset --hard`, `git clean`, discarding changes) are handled handoff-only: prepare exact commands and guidance, and the user runs them in their own terminal.

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

**For rebase/squash (handoff-only — these checks inform the guidance, the agent never runs the rebase/squash itself):**
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
        echo "BLOCKED: Rebase/squash of protected branch is not advised"
        exit 1
    fi
done
```

---

## Step 3: Execute Operation

Safe operations (commit, branch, stash, normal push) are executed by the agent with user approval. History-rewriting operations (rebase, squash, amend, any history-moving reset, force push) are NEVER executed here — they follow the handoff-only protocol in their sections and in Step 4.

### Operation: Commit Message Generation (`/main-git-workflow commit` or "generate commit message")

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

### Operation: Branch Creation (`/main-git-workflow branch` or "create a branch")

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
5. Create and checkout branch: `git checkout -b <branch-name>` (branch creation only — this does not discard any files; if uncommitted changes would conflict with the switch, warn and get approval first)
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

### Operation: Rebase Assistance (`/main-git-workflow rebase` or "rebase onto")

**Workflow (guidance and handoff — the agent never runs the rebase itself):**
1. **Safety Check**: Verify current branch is NOT shared and NOT protected
   ```bash
   current_branch=$(git branch --show-current)

   # Check if branch is shared (exists on remote)
   git ls-remote --heads origin | grep -q "refs/heads/$current_branch"

   # Check if branch is protected
   protected_patterns=("main" "master" "develop" "release/")
   for pattern in "${protected_patterns[@]}"; do
       if [[ "$current_branch" == "$pattern" || "$current_branch" == "$pattern"* ]]; then
           echo "BLOCKED: Rebase of protected branch is not advised"
           exit 1
       fi
   done
   ```
   - If shared: **BLOCK** and warn: "This branch exists on remote. Rebasing will rewrite shared history. Use with caution."
   - If protected: **BLOCK** and warn: "Do not rebase protected branch (main/master/develop/release/*)"
   - Rebase rewrites history, so it is handoff-only regardless of confirmation: the agent never runs it.

2. Determine target branch (default: main or develop)

3. Check for conflicts before starting (read-only checks the agent may run):
   ```bash
   git fetch origin
git merge-base HEAD origin/<target-branch>
   git diff $(git merge-base HEAD origin/<target-branch>)..HEAD --name-only
   ```

4. Hand the rebase to the user:
   - Provide the exact commands: `git rebase origin/<target-branch>`
   - Explain each step: checkout conflicted files, resolve, `git add`, `git rebase --continue`
   - The user runs the rebase in their own terminal; the agent assists with conflict analysis and resolution guidance (file edits via the normal editing flow)

5. After the user completes the rebase, explain force-push implications (with warning):
   - Only suggest `git push --force-with-lease` (safer than `--force`)
   - Force push rewrites remote history — handoff-only: provide the command; the user runs it themselves

**Example Output:**
```
WARNING: Branch 'feature/user-auth' exists on remote.

Rebasing will rewrite history visible to others.
This can cause issues for collaborators who have based work on this branch.

The agent does not run rebase commands. Run this yourself in a terminal:

  git rebase origin/main

If conflicts occur, tell me and I'll help you resolve them:
1. Open the file and resolve the conflict markers (<<<<<<<, =======, >>>>>>>)
2. Stage the resolved file: git add src/auth.ts
3. Continue rebase: git rebase --continue

After the rebase, pushing requires --force-with-lease (rewrites remote history) —
I'll give you the exact command to run yourself.
```

---

### Operation: Squash Assistance (`/main-git-workflow squash` or "squash my commits")

**Workflow (guidance and handoff — the agent never runs the squash itself):**
1. **Safety Check**: Same as rebase - verify branch is not shared and not protected
   - See Step 2.5 Pre-Operation Validation for protected branch patterns

2. Show commit history to squash (read-only, agent may run):
   ```bash
   git log --oneline HEAD~5..HEAD  # Show last 5 commits
   ```

3. Determine squash point:
   - Ask: "Squash all commits since branch from main? (y/n)"
   - Or: "Squash last N commits?" with interactive selection

4. Hand the squash to the user — both variants rewrite history, so the agent never runs them:
   - **Non-interactive squash**: provide the exact commands:
     ```bash
     git reset --soft HEAD~N   # N = number of commits to squash; work stays staged
     git commit -m "<combined message>"
     ```
     - Generate the combined commit message from the squashed commits (Conventional Commits format) and present it for the user's approval
     - Note for the user: `git reset --soft` is non-destructive (all changes remain staged; recover via `git reflog` if needed), but it still moves existing history, so it is handoff-only under the shared AGENTS ban — the user runs it themselves
   - **Selective squash or reordering** (keeping some commits, squashing others): also hand off:
     "Selective squashing needs an interactive rebase. Run this yourself in a terminal: `git rebase -i HEAD~N`, mark commits to combine as `squash`, save and close. Tell me when done and I'll verify the result."
5. After the user completes the squash, explain force-push implications (with warning) — force push is handoff-only too

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

Combined commit message:

feat: add password reset flow

Adds reset endpoint, email service, and supporting refactors.

Squash with this message? (y/n/Edit)

[User selects: y]

The agent does not run squash commands (they rewrite history). Run this yourself
in a terminal:

  git reset --soft HEAD~5 && git commit -m "feat: add password reset flow"

Tell me when done and I'll verify the result with: git log --oneline -3
```

---

### Operation: Stash (`/main-git-workflow stash` or "stash my changes")

**Workflow:**
1. Check for uncommitted changes: `git status --porcelain`
2. If no changes: "No changes to stash"
3. Check for staged changes: `git diff --cached --stat`
4. Prompt: "Stash staged changes only, unstaged only, or both? (staged/unstaged/both)"
5. Execute appropriate stash:
   - Both: `git stash push -u -m "<auto-generated message>"`
   - Staged only: `git stash push -S -m "<auto-generated message>"`
   - Unstaged only: `git stash push -u --keep-index -m "<auto-generated message>"`
6. Confirm: "Changes stashed. Use `/main-git-workflow stash pop` to restore."

**Example Output:**
```
Uncommitted changes:
 M  src/index.js
?? config.tmp

Stash both staged and unstaged changes? (y/n)
[User: y]

Changes stashed as: WIP on feature/user-auth: 5a6b7c8 Add new feature
To restore: /main-git-workflow stash pop
```

---

### Operation: Stash Pop (`/main-git-workflow stash pop` or "restore stashed changes")

**Workflow:**
1. List stashes: `git stash list`
2. If no stashes: "No stashes found"
3. If one stash: Prompt "Apply stash? (y/n)"
4. If multiple stashes: Prompt "Which stash? [0, 1, 2...]"
5. Apply: `git stash apply stash@{<n>}` (preferred — keeps the stash entry; `git stash pop` also drops the entry, so use `apply` unless the user explicitly wants the entry removed, in which case dropping requires approval)
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

### Operation: Undo (`/main-git-workflow undo` or "undo my last commit")

**Workflow:**
1. Check if user wants to undo commit, rebase, or other operation
2. **Undo last commit (keep changes staged):** any reset that moves existing history is handoff-only — provide the command; the user runs it:
   - `git reset --soft HEAD~1`
3. **Undo last commit (keep changes unstaged):** same — handoff-only:
   - `git reset HEAD~1`
4. **Undo last commit (discard changes):**
   - **HANDOFF-ONLY**: The agent does not run `git reset --hard`. Provide the command and require the user to run it themselves after explicit confirmation "Type 'DISCARD' to permanently discard changes"
5. **Undo rebase (in-progress only):**
   - `git rebase --abort` — HANDOFF-ONLY: the user executes this to abort a rebase the USER started; the agent never runs it or starts a rebase
6. **Undo merge (in-progress only):**
   - `git merge --abort`
7. **Find lost commits:**
   - `git reflog`
   - Guide user to find and restore lost commits

**Example Output:**
```
Last commit: feat: add login form (a1b2c3d)

Undo options:
1. Undo commit, keep changes staged (soft reset) - handoff-only: the agent provides the command; the user runs it
2. Undo commit, keep changes unstaged (mixed reset) - handoff-only: the agent provides the command; the user runs it
3. Undo commit, DISCARD all changes (hard reset) - DANGEROUS, handoff-only: the agent provides the command; the user runs it
4. Undo rebase/merge
5. Find lost commits with reflog

Select option: [1-5]
```

---

### Operation: Push (`/main-git-workflow push` or "push my branch")

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
   - **BLOCK**: Explain that force push overwrites remote history — handoff-only: provide the `git push --force-with-lease` command; the user runs it themselves
   - Suggest `--force-with-lease` instead of `--force`
6. Execute push: `git push` (normal fast-forward push only). Force pushes are never executed by the agent — handoff-only.

**Example Output:**
```
Branch: feature/user-auth
Upstream: origin/feature/user-auth
Status: 2 commits ahead, 1 commit behind

Your branch has diverged from remote. Options:
1. Pull and merge (recommended)
2. Rebase onto remote and force push (handoff-only: I provide the commands, you run them)
3. Force push (overwrites remote) - DANGEROUS, handoff-only: I provide the command, you run it

Select option: [1-3]
```

---

### Operation: General Git Help (`/main-git-workflow` or "help with git")

**Workflow:**
1. Show current git status: branch, uncommitted changes, recent commits
2. Suggest next actions based on context:
   - Uncommitted changes → suggest commit or stash
   - On main branch → suggest create feature branch
   - Diverged from main → suggest pull, or rebase guidance (handoff-only)
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
3. Commit: /main-git-workflow commit
4. Push: git push
5. Rebase onto main: /main-git-workflow rebase (guidance + handoff; you run the rebase)

What would you like to do?
```

---

## Step 4: Safety Layer (CRITICAL)

### Handoff-Only Operations (never executed by the agent, even with user confirmation)
These operations rewrite history. The agent explains them, prepares exact commands, and the user runs them in their own terminal:

```bash
# Force push (overwrites remote history)
git push --force
git push --force-with-lease  # Still dangerous, just safer

# Any reset that moves existing history (soft, mixed, or hard)
git reset --soft HEAD~N
git reset HEAD~N
git reset --hard

# Rebase (rewrites commit history)
git rebase origin/main

# Amend (rewrites the last commit)
git commit --amend

# Squash merge (rewrites history)
git merge --squash

# Discard untracked files
git clean
```

**Handoff Protocol:**
1. Detect that the requested operation rewrites history
2. Check if branch is shared (exists on remote) and warn about shared-history consequences
3. Display clear warning of consequences
4. Provide the exact commands and step-by-step guidance
5. The user runs the commands in their own terminal; the agent verifies results afterward (read-only: `git log`, `git status`)

### Safe Operations
These can be executed directly (read-only or additive, no history rewrite):
- `git status`
- `git diff`
- `git log`
- `git branch`
- `git add`
- `git commit` (new commits only, with generated message)
- `git pull` (without rebase)
- `git fetch`
- `git push` (normal fast-forward push only)

`git checkout` is NOT blanket-safe: switching branches is fine, but `git checkout <file>`/`git checkout -- <path>` discards unsaved work — state the action and get user approval every time. `git stash drop` and `git stash clear` permanently discard stashed work — user approval every time.

---

## Conflict Resolution

When merge or rebase conflicts occur, guide user through resolution:

### Identifying Conflicts
- Check for conflict markers: `git diff --check | grep -q "^<<<<<<<"`
- List conflicted files: `git status --porcelain | grep "^UU"`
- Show conflict details: `git diff` on each conflicted file

### Resolution Strategies

**1. Agent-Assisted Resolution (default):**
- Read each conflicted file to find markers: `<<<<<<< HEAD`, `=======`, `>>>>>>> branch-name`
- Show the user both sides and ask which to keep (or how to combine)
- Apply the chosen resolution with the edit tool, removing the markers
- Stage resolved file: `git add <file>`
- Continue operation: for a rebase the USER is running, provide `git rebase --continue` for the user to run; for a merge, `git commit` may be run by the agent with approval. The agent never starts or drives a rebase itself.

**2. User's Own Merge Tool:**
- If the user prefers a visual tool, hand off: "Run `git mergetool` in your terminal, then tell me when done and I'll continue." (Merge tools require an interactive editor the agent cannot drive.)

**3. Abort Operation:**
- For rebase: `git rebase --abort` — HANDOFF-ONLY: the user executes this to abort a rebase the USER started; the agent never runs it or starts a rebase
- For merge: `git merge --abort`
- For stash: `git stash drop stash@{n}` permanently discards that stash — state the action and get user approval every time before running it

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
- [ ] `/main-git-workflow commit` on staged changes
- [ ] `/main-git-workflow commit` with no staged changes (should prompt)
- [ ] `/main-git-workflow branch` to create new branch
- [ ] `/main-git-workflow branch` with invalid name (should reject)
- [ ] `/main-git-workflow rebase` on local-only branch (should hand off commands to user, not execute)
- [ ] `/main-git-workflow rebase` on shared branch (should block with shared-history warning, then hand off)
- [ ] `/main-git-workflow rebase` on protected branch (should block)
- [ ] `/main-git-workflow squash` on local-only branch (should hand off commands to user, not execute)
- [ ] `/main-git-workflow stash` with uncommitted changes
- [ ] `/main-git-workflow stash pop` with stashed changes
- [ ] `/main-git-workflow undo` to undo last commit (should hand off reset commands to user, not execute)
- [ ] `/main-git-workflow undo` with discard option (should hand off to user, not run `git reset --hard`)
- [ ] `/main-git-workflow push` with no upstream (should offer to set)
- [ ] `/main-git-workflow push` with diverged branch (should warn and hand off force-push command, not execute it)
- [ ] `/main-git-workflow` for general status and suggestions
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
