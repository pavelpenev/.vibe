---
name: skill-creator
description: Use to create or update Skills for Mistral Vibe CLI. Guides through defining, researching, creating, enabling, and testing skills in ~/.vibe/skills/.
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - grep
  - web_search
---

# Skill Creator

Guides users through the complete process of creating, validating, and enabling new Mistral Vibe skills. Use for creating focused, reusable agent capabilities that follow best practices.

## When to Use

**Explicit triggers:**
- `/skill-creator` - Start interactive skill creation
- `/skill-creator <name>` - Create skill with specified name
- `/skill-creator <name> for <purpose>` - Create skill with name and purpose

**Natural language triggers:**
- "create a skill for..."
- "make a new skill that..."
- "I need a skill to..."
- "create skill <name>"
- "build a skill for <task>"

**When NOT to use:**
- For creating subagents (use `/subagent-creator`)
- For one-off tasks that don't need reusability
- When a similar skill already exists (adapt existing instead)

---

## Step 1: Parse Request

Extract from user input:
- **Name**: Skill identifier (single word or hyphenated)
- **Purpose/Description**: What the skill should accomplish
- **Trigger phrases**: Natural language patterns that should activate it
- **Tools needed**: Which tools the skill requires

If user provides only a name:
```
/skill-creator code-review
```
Extract the name and proceed to Step 2 for remaining details.

If user provides partial information:
```
create a skill for reviewing python code
```
Extract intent (code review, python focus) and prompt for missing details.

If user provides no information:
```
/skill-creator
```
Start interactive workflow from Step 2.

---

## Step 2: Gather Skill Details

Ask the user in order (skip if already provided):

1. **What is the skill's name?**
   - Validate: only lowercase alphanumeric characters and hyphens
   - Validate: not empty
   - Check: no existing skill with this name in `~/.vibe/skills/`
   - Suggest: based on purpose if name is unclear

2. **What is its purpose/description?** (e.g., "Review Python code for PEP 8 compliance")
   - Validate: not empty
   - Validate: describes a specific, focused capability
   - Use: for `description` field in frontmatter

3. **What specific user requests should trigger it?**
   - Natural language patterns (e.g., "review my python", "/python-review")
   - Direct invocation command
   - Multiple trigger options are fine

4. **What task should it perform?** (detailed instructions)
   - Be concise but comprehensive
   - Include workflow steps
   - Specify what it should NOT do

5. **Should it be user-invocable?** (y/n)
   - Default: `true` for most skills
   - `false` for internal/system skills

6. **What tools should it have access to?**
   - Present common tool sets:
     - **Research/Read-only**: `read_file`, `grep`
     - **Code Analysis**: `read_file`, `grep`, `bash`
     - **Code Generation**: `read_file`, `write_file`, `edit`, `grep`
     - **Full Access**: `read_file`, `write_file`, `edit`, `grep`, `bash`, `web_search`
   - Allow custom list
   - Validate: all tools are valid Mistral Vibe tools

7. **Research similar skills?** (y/n)
   - If yes, proceed to Step 3
   - If no, skip to Step 4

---

## Step 3: Research (Optional)

If user requested research:

**Search locally first:**
```bash
find ~/.vibe/skills/ -name "SKILL.md" -type f
```
Search for skills with similar purpose or tools.

**Search patterns:**
- Keywords from the skill's purpose
- Similar tool combinations
- Related domains

**Web search for external patterns:**
```
web_search query: "site:github.com Mistral Vibe skill {keywords}"
web_search query: "{task} agent skill example"
web_search query: "AI agent skill for {domain}"
```

**Present findings:**
- List similar local skills with brief descriptions
- Summarize external patterns found
- Ask: "Would you like to adapt any of these patterns? (y/n/Which one)"

If user wants to adapt: incorporate relevant workflow elements, tool choices, or structure.

---

## Step 4: Validate Configuration

Before creating files, validate:

1. **Name validation:**
   - Only contains: `a-z`, `0-9`, `-`
   - Length: 2-40 characters
   - Not a reserved name (skill-creator, subagent-creator, etc.)

2. **Uniqueness check:**
   ```bash
   test -d ~/.vibe/skills/{name} && echo "ERROR: Skill already exists" && exit 1
   ```

3. **Tool validation:**
   - All specified tools exist in Mistral Vibe
   - Common valid tools: `read_file`, `write_file`, `edit`, `bash`, `grep`, `web_search`, `web_fetch`, `task`, `todo`, `ask_user_question`, `skill`

4. **Description validation:**
   - Not empty
   - Describes a specific capability
   - Not overly vague ("help with things", "do stuff")

5. **Trigger validation:**
   - At least one trigger pattern provided
   - Triggers are specific enough to avoid false positives

If validation fails, inform user of specific issues and return to Step 2.

---

## Step 5: Create Skill File

**Location:**
- Default: `~/.vibe/skills/{name}/SKILL.md`
- If in a project with `.vibe/skills/` directory, offer to create there instead

**Template structure:**
```markdown
---
name: {name}
description: {description}
user-invocable: {user_invocable}
allowed-tools:
{tools_list}
---

# {Display Name}

{instructions}

## When to Use

{trigger_conditions}

## Workflow

{workflow_steps}
```

**Display Name:** Capitalized, space-separated version of name (e.g., "code-review" -> "Code Review")

**Tools list formatting:**
```yaml
allowed-tools:
  - {tool1}
  - {tool2}
```

**Example output:**
```markdown
---
name: python-review
description: Review Python code for PEP 8 compliance and common anti-patterns
user-invocable: true
allowed-tools:
  - read_file
  - grep
  - bash
---

# Python Review

Reviews Python files for PEP 8 style compliance, common bugs, and anti-patterns.

## When to Use

Activates when user requests Python code review:
- `/python-review`
- `/python-review <file>`
- "review my python code"
- "check PEP 8 compliance"

## Workflow

1. Identify Python files to review (specified or from git status)
2. Check each file for PEP 8 violations
3. Look for common anti-patterns
4. Report findings with specific line references
```

---

## Step 6: Enable Skill

Instruct the user to manually add the skill to their config file:

**Tell the user:**
```
Skill created at: ~/.vibe/skills/{name}/SKILL.md

To enable this skill, manually add it to ~/.vibe/config.toml:

1. Open ~/.vibe/config.toml in your editor
2. Add "{name}" to the top-level `enabled_skills` array (this is a root-level key, not under any `[skills]` table)
3. Save the file

Example:
```toml
enabled_skills = [
    "...",
    "{name}",
]
```

**Note:** Only add each skill once to avoid duplicates.
```
---

## Step 7: Test Skill

**Suggest manual testing:**
```bash
vibe -p "/{name} {test-prompt}"
```

**Generate test prompt based on skill purpose:**
- For code review skills: review a sample file
- For generation skills: generate sample output
- For research skills: answer a test question

**Ask user:**
```
Skill created successfully at ~/.vibe/skills/{name}/SKILL.md

Test with:
vibe -p "/{name} {suggested-test-prompt}"

Does this work as expected? (y/n/Edit)
```

- If "Edit": return to Step 2
- If "n": offer to delete files and cancel
- If "y": confirm success

---

## Step 8: Finalize

**Success output:**
```markdown
## Skill Created: {name}

**Location:** ~/.vibe/skills/{name}/SKILL.md

**Configuration:**
```yaml
name: {name}
description: {description}
user-invocable: {user_invocable}
allowed-tools:
{tools_list}
```

**Trigger Patterns:**
{trigger_patterns}

**Next Steps:**
1. Test: `vibe -p "/{name} {test-prompt}"`
2. Use: The skill is now available for invocation
3. Modify: Edit ~/.vibe/skills/{name}/SKILL.md to refine
4. Reload: Restart vibe or wait for skill cache to refresh

**Note:** After modifying SKILL.md, you may need to restart vibe for changes to take effect.
```

---

## Skill Structure Best Practices

### 1. Naming
- Use lowercase with hyphens: `python-review`, `git-helper`
- Be specific: `typescript-lint` not `code-check`
- Avoid generic names: `helper`, `utility`, `assistant`

### 2. Description
- Start with action verb: "Review", "Generate", "Analyze"
- Specify domain: "Python code", "git commits", "markdown files"
- State purpose: "for PEP 8 compliance", "for security issues"

### 3. Tool Selection
- **Principle of least privilege**: Only include tools the skill actually needs
- Prefer read-only tools for analysis skills
- Include write tools only for generation/modification skills
- `bash` with `permission = "ask"` for potentially destructive operations

### 4. Trigger Design
- Include both direct invocation (`/{name}`) and natural language
- Make natural language patterns specific to avoid false positives
- Include 2-4 trigger patterns minimum

### 5. Workflow
- Break into clear, numbered steps
- Include error handling for each step
- Specify what to do when things go wrong
- Include validation where appropriate

---

## Templates

### Minimal Skill Template
```markdown
---
name: minimal-skill
description: Performs a single focused task
user-invocable: true
allowed-tools:
  - read_file
---

# Minimal Skill

Performs [specific task] on [specific target].

## When to Use

- `/minimal-skill`
- "[natural language trigger]"

## Workflow

1. [Step 1]
2. [Step 2]
```

### Research Skill Template
```markdown
---
name: research-helper
description: Research information about specific topics
user-invocable: true
allowed-tools:
  - web_search
  - read_file
---

# Research Helper

Researches [domain] topics using web search and local files.

## When to Use

- `/research-helper <topic>`
- "research [topic]"
- "look up [information]"

## Workflow

1. Parse research topic from user input
2. Use web_search to find current information
3. Summarize findings
4. Present with sources
```

### Code Generation Skill Template
```markdown
---
name: code-generator
description: Generate boilerplate code for common patterns
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - grep
---

# Code Generator

Generates [type] code based on user specifications.

## When to Use

- `/code-generator <type>`
- "generate [type] code"

## Workflow

1. Ask for required parameters
2. Validate inputs
3. Generate code
4. Create or modify files
5. Confirm with user before writing
```

---

## Error Handling

### Common Errors and Responses

| Error | Detection | Response |
|-------|-----------|----------|
| Skill already exists | `test -d ~/.vibe/skills/{name}` | "Skill '{name}' already exists at [path]. Overwrite? (y/n)" |
| Invalid name | Regex: `^[a-z0-9-]+$` | "Invalid name. Use only lowercase letters, numbers, and hyphens." |
| Invalid tool | Check against known tool list | "Unknown tool: {tool}. Valid tools: [list]" |
| Config file missing | `! -f ~/.vibe/config.toml` | "Config file not found at ~/.vibe/config.toml. Create it first." |
| Duplicate in config | `grep -q "\"{name}\""` | "Skill already enabled in config.toml." |
| File write failure | Check return code | "Failed to write skill file. Check permissions." |

### Recovery
- For file write failures: Suggest checking directory permissions
- For config issues: Offer to create config file if missing
- For duplicate skills: Offer to overwrite or choose new name

---

## Red Flags

Warn user about:

1. **Overly broad tool access**
   - Granting all tools without justification
   - `bash` with `permission = "always"` and no restrictions

2. **Vague purpose**
   - Descriptions like "help with coding", "do tasks"
   - No clear trigger conditions

3. **Missing error handling**
   - Workflow steps without failure handling
   - No validation of inputs

4. **Duplicate functionality**
   - Creating a skill when similar one already exists
   - Reinventing existing capabilities

5. **Complex skills**
   - Skills trying to do too much (should be split)
   - Long, unstructured workflows (>10 steps)

---

## Verification

Basic checks (user helps with manual testing):

- [ ] `/skill-creator` with no arguments starts interactive mode
- [ ] `/skill-creator <name>` with valid name proceeds to details
- [ ] `/skill-creator` with invalid name (spaces, uppercase) shows error
- [ ] `/skill-creator` with duplicate name warns and asks to overwrite
- [ ] Creating a skill with valid inputs generates proper SKILL.md
- [ ] Created skill appears in config.toml enabled list (no duplicates)
- [ ] Created skill can be invoked with its trigger
- [ ] Invoking created skill works as expected

**Note:** Manual testing with the user is required for full verification, as skill behavior depends on the specific use case.

---

## Known Limitations

1. **Manual enablement required**: Skills must be manually added to config.toml. Automatic enablement was removed to avoid complex configuration logic.

2. **Skill caching**: After creating/modifying a skill, vibe may need to be restarted for changes to take effect.

3. **Permission propagation**: Session-level "always allow" permissions do NOT apply to skills. Each skill respects only its own TOML-defined permissions.

4. **No automatic updates**: Updating a skill file does not automatically update already-spawned agents using that skill.
