---
name: project-planner
description: Use for initial project planning, large feature scoping, architectural changes, and migrations. Maintains a living PLAN.md in the project directory. Triggers on explicit requests to plan a project, scope work, add features to the plan, or organize project development. Can invoke deep-research for complex topics requiring sustained investigation. For small, self-contained tasks, use the auto-task skill instead.
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - grep
  - bash
  - web_search
  - ask_user_question
  - skill
---

# Project Planner

## Overview

Maintains a living `PLAN.md` file in the project directory that serves as the central repository for all project planning artifacts. This skill handles initial project scoping, new feature planning, architectural changes, migrations, and major refactoring efforts.

The skill focuses on **iteratively gathering requirements with the user** and defining scope, producing structured but flexible planning documents that evolve with the project.

**Scope:** This skill is designed for large projects and architectural changes. For small, self-contained tasks, use the auto-task skill instead.

## When to Use

**Explicit triggers:**
- "plan a project"
- "create project plan"
- "scope this feature"
- "add to project plan"
- "plan migration"
- "architectural change plan"
- "break down this epic"
- "plan a refactor"
- "plan a refactoring"
- "break down this task"
- "create roadmap"
- "update project plan"

**When NOT to use:**
- Small, self-contained tasks (use auto-task skill)
- Bug fixes (use debugging workflow)
- Code review (use code-review skill)

## PLAN.md Location

- **Default:** `./PLAN.md` in project root
- **Override:** Specify alternative location in project-local `AGENTS.md`
- **Scope:** Single canonical PLAN.md file for the entire project (nested plans are not supported)

## PLAN.md Format

The format is **loose but structured**. The skill amends existing content in its existing format, and adds new content in a consistent format.

**Reasonable format definition:** A format with clear section headers (using `#`, `##`, etc.), identifiable planning items, and logical structure. The skill will adapt to and preserve existing reasonable formats.

### Minimal Section Structure

Each major planning item should have:

```markdown
## [Name] - [YYYY-MM-DD]

**Type:** feature | architecture | migration | refactor | research

**Description:** [What this accomplishes]

**Scope:** [High-level boundaries]

**Tasks:**
- [ ] [Task description]
- [ ] [Task description]

**Dependencies:** [What this depends on]

**Risks:** [Potential issues and mitigations]

**Status:** planned | in-progress | completed | blocked | deferred

**Notes:** [Additional context, decisions, or references]
```

## Workflow

### Step 1: Check for Existing Plan

- If `PLAN.md` does not exist: Proceed to **New Project Flow**
- If `PLAN.md` exists: Read it and display current plan to user
- If `PLAN.md` exists but is corrupted/malformed: Stop and ask user for action (delete, fix manually, or treat as new project)

### Step 2: Determine Action Type

Ask user what type of planning is needed:
- **New project** - Full initial scoping
- **New feature** - Feature breakdown and integration
- **Architectural change** - System design modification
- **Migration** - Data, library, or platform migration
- **Refactor** - Large-scale code restructuring

If user is unsure, the skill should suggest the most appropriate type based on the request context.

### Step 3: Gather Information Iteratively

For all action types, follow this pattern:

1. **Clarify the goal** - What problem does this solve?
2. **Define scope** - What's included? What's explicitly excluded?
3. **Identify constraints** - Technical limitations
4. **Research as needed** - Use `web_search` for specific questions, suggest invoking deep-research skill for complex domains
5. **Break into tasks** - Use vertical slicing, INVEST criteria
6. **Identify dependencies** - What must exist first?
7. **Assess risks** - What could go wrong? How to mitigate?

**Interactive approach:** Ask one clarifying question at a time. Do not assume - surface uncertainty early.

**Contradiction handling:** If user requests contradict existing plan, ask for explicit confirmation before proceeding.

### Step 4: New Project Flow

When no PLAN.md exists, gather:

- **Project name and purpose**
- **Primary goals** (3-5 key objectives)
- **Success criteria** (how we know we're done)
- **Technical constraints** (language, framework, platform requirements)
- **Initial feature set** (MVP scope)

Create PLAN.md with **Project Overview** section followed by feature sections.

### Step 5: Existing Project Flow

When PLAN.md exists:

1. **Read and understand** current plan
2. **Identify insertion point** - Where does this new work fit?
3. **Gather details** for the new item (see Step 3)
4. **Append or update section** using existing format, preserving structure
5. **Update priorities** if needed
6. **Update task statuses** if user requests (mark complete, revise descriptions)

### Step 6: Research Integration

**When to use research tools:**

- **web_search**: Specific factual questions ("What's the latest version of X?", "How does Y library handle Z?")
- **deep-research**: Complex topics requiring sustained investigation ("Survey existing solutions for problem X", "Compare frameworks A vs B")

**Research directory:** If `./research/` exists, check for relevant existing research (created by deep-research skill) for additional context. The project-planner skill only reads existing research; it does not create new research directories.

**Invocation suggestion:** The skill can suggest invoking the deep-research skill when a topic requires comprehensive analysis, but should ask for user confirmation first.

### Step 7: Amending Existing PLAN.md

**Strategy:**

1. Read existing file
2. If file has **recognizable sections** (headers with dates/types):
   - Find appropriate location for new content
   - Append or update section in existing format
3. If file is **freeform but has structure**:
   - Add separator (`---`)
   - Append or update section in minimal format
4. If file is **empty or malformed**:
   - Stop and ask user for action

**Content modification:** The skill can modify existing content to:
- Update task status (mark as completed, in-progress, blocked)
- Revise task descriptions based on user request
- Refine scope or add clarifications
- Update dependencies or risks
- Add notes or decisions

**Preservation:** Preserve all existing content that is not being explicitly updated. When in doubt, append rather than modify.

### Step 8: Finalize and Write

- Confirm all information with user
- Write PLAN.md with new/updated content
- Display summary of what was added or changed
- Suggest next steps
- **Remind user to commit changes** to git with a descriptive commit message referencing the plan updates

## Research Best Practices

### web_search Usage

Use for:
- Quick factual lookups
- API documentation
- Library versions
- Specific error messages
- "How to X in Y" questions

**Query guidelines:**
- Be specific: "React hooks performance optimization 2026" not "React best practices"
- Avoid relative time: Use years (2025, 2026) not "latest" or "current"
- Include technology context: "Python asyncio database connection pool"

### deep-research Usage

Use for:
- Prior art surveys
- Framework comparisons
- Complex technical decisions
- Broad domain research

**When to suggest invocation:**
- User explicitly requests comprehensive research
- Topic is complex and unfamiliar
- Multiple conflicting solutions exist
- Decision has long-term implications

**Check first:** If `./research/` directory exists, review existing reports before starting new research.

## Templates

### Project Overview Template

```markdown
# Project Plan: [Project Name]

## Project Overview

**Description:** [What this project does]

**Primary Goals:**
- [ ] [Goal 1]
- [ ] [Goal 2]
- [ ] [Goal 3]

**Success Criteria:**
- [ ] [Measurable outcome 1]
- [ ] [Measurable outcome 2]

**Technical Constraints:**
- Language: [Primary language]
- Framework: [Required framework]
- Platform: [Deployment target]
- Dependencies: [Key libraries]

## Planning History
```

### Feature Template

```markdown
## [Feature Name] - [YYYY-MM-DD]

**Type:** feature

**Description:** [User-facing description of what this delivers]

**Scope:**
- **Included:** [What's part of this feature]
- **Excluded:** [What's explicitly NOT included]

**Tasks:**
- [ ] [Task 1 - Small/Medium task with clear outcome]
- [ ] [Task 2]
- [ ] [Task 3]

**Dependencies:**
- [Dependency 1] - [Why it's needed]
- [Dependency 2]

**Risks:**
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk description] | High/Medium/Low | [Strategy] |

**Status:** planned

**Notes:** [Decisions, references, or additional context]
```

### Migration Template

```markdown
## [Migration Name] - [YYYY-MM-DD]

**Type:** migration

**Description:** [What system/data is being migrated and why]

**From -> To:** [Source] -> [Destination]

**Scope:**
- **Data:** [What data is affected]
- **Downtime:** [Expected/allowed downtime]
- **Rollback:** [How to reverse if needed]

**Phases:**
1. **Phase 1: Preparation** - [What needs to be done first]
2. **Phase 2: Execution** - [Migration steps]
3. **Phase 3: Validation** - [How to verify success]

**Tasks:**
- [ ] [Preparation task]
- [ ] [Execution task]
- [ ] [Validation task]

**Dependencies:**
- [Dependency 1]

**Risks:**
- **Data loss:** [Risk] - Mitigation: [Backup strategy]
- **Downtime:** [Risk] - Mitigation: [Minimization approach]

**Status:** planned

**Notes:** [Lessons learned, references]
```

### Architecture Change Template

```markdown
## [Architecture Change] - [YYYY-MM-DD]

**Type:** architecture

**Description:** [What architectural change and why it's needed]

**Current State:** [How things work now]

**Proposed State:** [How things will work after]

**Rationale:** [Why this change - performance, maintainability, scalability]

**Trade-offs:**
| Aspect | Current | Proposed | Impact |
|--------|---------|----------|--------|
| [Metric] | [Value] | [Value] | [+/-] |

**Tasks:**
- [ ] [Implementation task]
- [ ] [Testing task]
- [ ] [Documentation update]

**Dependencies:**
- [Dependency 1]

**Risks:**
- [Risk 1] - [Mitigation]

**Status:** planned

**Notes:** [Design decisions, alternatives considered]
```

## Quality Gates

Before finalizing any plan section, confirm:

- [ ] Goal is clearly defined and testable
- [ ] Scope boundaries are explicit (what's in AND what's out)
- [ ] Tasks are INVEST-compliant (Independent, Negotiable, Valuable, Estimable, Small, Testable)
- [ ] Each task has a clear outcome
- [ ] Dependencies are identified and ordered correctly
- [ ] Risks are documented with mitigations
- [ ] User has reviewed and approved the plan

## Examples

### Example: New Project Plan

```
User: "Let's plan a new e-commerce platform"

Skill: 
1. Asks: "What's the primary purpose of this platform?"
2. Gathers: Goals, constraints, initial feature set
3. Researches: Existing e-commerce solutions (using web_search)
4. Creates: PLAN.md with project overview and initial feature sections
5. Outputs: Full project plan document
6. Reminds: User to commit the new PLAN.md to git
```

### Example: Adding Feature to Existing Project

```
User: "Add user authentication to our app"

Skill:
1. Reads: Existing PLAN.md
2. Asks: "What authentication method? Social login, email/password, SSO?"
3. Gathers: Scope, security requirements, integration points
4. Researches: Best practices for chosen auth method (using web_search)
5. Appends: New feature section to PLAN.md
6. Outputs: Updated plan with authentication feature
7. Reminds: User to commit changes to git
```

### Example: Planning Database Migration

```
User: "Plan migration from SQLite to PostgreSQL"

Skill:
1. Reads: Existing PLAN.md
2. Asks: "What's the reason for migration? Scale, features, reliability?"
3. Gathers: Data volume, downtime tolerance, rollback requirements
4. Researches: PostgreSQL migration tools (using web_search)
5. Suggests: Invoking deep-research skill for comprehensive framework comparison
6. Appends: Migration plan section to PLAN.md
7. Outputs: Updated plan with migration details
8. Reminds: User to commit changes to git
```

### Example: Updating Task Status

```
User: "I've completed the authentication backend task"

Skill:
1. Reads: Existing PLAN.md
2. Locates: The authentication feature section
3. Updates: Task status from [ ] to [x] for backend task
4. Confirms: Change with user
5. Writes: Updated PLAN.md
6. Reminds: User to commit changes to git
```

## Notes

- **Format evolution:** PLAN.md format can evolve over time. The skill adapts to existing format while adding new content consistently.
- **Research directory:** Check `./research/` for existing research (created by deep-research skill) before conducting new searches. The project-planner skill only reads, never creates research files.
- **User approval:** Always confirm with user before writing significant plan changes.
- **Atomic changes:** Each invocation should make one coherent set of changes to PLAN.md.
- **Integration:** For codebase exploration during planning, the explorer subagent is available. The skill can suggest using the deep-research skill for complex research needs.
- **Git integration:** Always remind the user to commit PLAN.md changes to git with descriptive commit messages.
