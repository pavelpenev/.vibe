---
name: subagent-creator
description: Create subagent TOML configuration files with proper permissions and settings
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit
  - bash
  - grep
  - ask_user_question
---

# Subagent Creator

## Purpose
Generate subagent TOML configuration files that enable the main agent to delegate focused tasks. This skill mirrors the skill-creator workflow but creates delegation-capable subagents instead of skills.

## Triggering Conditions
Activates when user requests subagent creation:
- `/subagent-creator` - Interactive subagent creation
- `/subagent-creator <name>` - Create subagent with specified name
- "create a subagent for..."
- "make a subagent that..."
- "I need a subagent to..."

## Workflow

### Step 1: Parse Request
Extract from user input:
- **Name**: Subagent identifier (single word or hyphenated)
- **Purpose**: What the subagent should do
- **Tools**: Which tools it needs access to
- **Permissions**: Read-only or write-enabled
- **Model**: Which model to use (optional)
- **Prompt**: Custom system prompt (optional)

If user provides only a name:
```
/subagent-creator code-reviewer
```
Proceed to Step 2 with that name and prompt for remaining details.

If user provides partial information:
```
create a subagent for code review
```
Extract intent and prompt for missing details.

If user provides no information:
```
/subagent-creator
```
Start interactive workflow from Step 2.

### Step 2: Gather Subagent Details
Ask the user in order (skip if already provided):

1. **What is the subagent's name?** (single word or hyphenated, e.g., "code-review", "test-generator")
   - Validate: not empty, only alphanumeric and hyphens
   - Check: subagent doesn't already exist in `~/.vibe/agents/` or `./.vibe/agents/`
   - Suggest: based on purpose if name is unclear

2. **What is its purpose/description?** (e.g., "Reviews code for quality and security issues")
   - Validate: not empty
   - Use: for `description` field in TOML

3. **What agent type?**
   - Default: `subagent` (delegation-only)
   - Option: `agent` (user-facing, selectable via `--agent`)
   - Recommend: `subagent` for focused task delegation

4. **What safety level?**
   - `safe`: Read-only or non-destructive operations
   - `neutral`: May modify files with approval
   - `destructive`: Can perform destructive operations
   - `yolo`: Minimal restrictions (use with caution)
   - Recommend: `safe` for read-only, `neutral` for write-enabled

5. **What tools should it have access to?**
   - Present common tool sets based on purpose:
     - **Research/Exploration**: `read_file`, `grep`
     - **Code Analysis**: `read_file`, `grep`, `bash` (read-only commands)
     - **Code Generation**: `read_file`, `write_file`, `edit`
     - **Full Access**: `read_file`, `write_file`, `edit`, `grep`, `bash`
   - Allow custom list
   - Validate: all tools are valid Mistral Vibe tools

6. **Permission level for each tool?**
   - For each selected tool, ask: should this be `always`, `ask`, or `never`?
   - Default: `always` for core tools, `ask` for potentially destructive tools
   - Special handling: warn that session-level "always allow" does NOT propagate to subagents (Issue #390)

7. **Which model should it use?** (optional)
   - Default: inherit from parent agent
   - Options: `mistral-medium-latest`, `mistral-small-latest`, etc.
   - Note: model must be available in user's configuration

8. **Should it have a custom system prompt?** (y/n)
   - If yes: specify prompt ID (filename without .md extension)
   - Will create file in `~/.vibe/prompts/` or `./.vibe/prompts/`
   - Offer to generate prompt based on purpose

### Step 3: Validate Configuration
Before creating files, validate:
1. **Name uniqueness**: No existing subagent with this name
2. **Tool validity**: All specified tools exist in Mistral Vibe
3. **Permission consistency**: Write tools (write_file, edit) shouldn't have `always` permission without warning
4. **Safety level**: Matches the subagent's actual capabilities
5. **Single responsibility**: Description must focus on one clear purpose (reject if it describes multiple distinct tasks)
6. **Tool boundary alignment**: Tools must logically support the stated purpose

If validation fails, inform user and return to Step 2.

### Step 4: Create Subagent TOML File

**Location Priority:**
1. If in a trusted project directory with `.vibe/agents/` → create there
2. Otherwise → create in `~/.vibe/agents/`

**TOML Template:**
```toml
agent_type = "{agent_type}"
display_name = "{Display Name}"
description = "{description}"
safety = "{safety_level}"
{active_model_line}{system_prompt_line}enabled_tools = [{tools_list}]

{permissions_block}
```

**Field Mapping:**
- `{agent_type}`: from Step 2.3 (default: "subagent")
- `{Display Name}`: Capitalized version of name (e.g., "code-review" → "Code Review")
- `{description}`: from Step 2.2
- `{safety_level}`: from Step 2.4
- `{active_model_line}`: `active_model = "{model}"` if specified, else omit
- `{system_prompt_line}`: `system_prompt_id = "{prompt_id}"` if specified, else omit
- `{tools_list}`: comma-separated quoted tool names
- `{permissions_block}`: per-tool permission stanzas

**Example Output:**
```toml
# ~/.vibe/agents/code-review.toml
agent_type = "subagent"
display_name = "Code Review"
description = "Reviews code for quality, security, and best practices"
safety = "safe"
system_prompt_id = "code-review"
enabled_tools = ["read_file", "grep"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

### Step 5: Create System Prompt (if requested)

If user requested custom system prompt:
1. Determine location: `~/.vibe/prompts/{prompt_id}.md` or `./.vibe/prompts/{prompt_id}.md`
2. Generate prompt based on purpose:

**Prompt Templates by Purpose:**

**Research Subagent:**
```markdown
# {Display Name} Subagent

You are a {purpose} subagent. Your tasks:
1. Analyze files and code provided in the task
2. Return a comprehensive report with findings
3. Do NOT modify any files
4. Be thorough and cite specific locations (file:line)
5. Return results in markdown format

Task: {task}
```

**Code Generation Subagent:**
```markdown
# {Display Name} Subagent

You are a {purpose} subagent. Your tasks:
1. Generate code based on the task requirements
2. Create or modify files as needed
3. Follow best practices and existing code style
4. Return a summary of what was created/modified
5. Return results in markdown format

Task: {task}
```

**Code Review Subagent:**
```markdown
# {Display Name} Subagent

You are a {purpose} subagent. Your tasks:
1. Review all files specified in the task
2. Check for: bugs, security issues, style violations, anti-patterns
3. Provide specific, actionable feedback
4. Do NOT modify files (read-only)
5. Return a structured report with categories (Bugs, Security, Style, etc.)

Task: {task}
```

3. Create the prompt file
4. Inform user: "Created prompt file at {path}"

### Step 6: Update System Prompt Dispatch Rules

**Purpose:** Automatically update the custom system prompt's delegation table so the main agent knows when to use this new subagent.

**Check if custom system prompt is in use:**
1. Use `read_file` to read `~/.vibe/config.toml`
2. Extract `system_prompt_id` value
3. If `system_prompt_id` == "cli" (default) → skip this step, inform user:
   "Note: Using default system prompt. To enable auto-dispatch, create a custom system prompt and set system_prompt_id in config.toml"
4. If custom prompt → proceed to update

**Update delegation table in custom system prompt:**
1. Identify the system prompt file: `~/.vibe/prompts/{system_prompt_id}.md`
2. Use `read_file` to read the current content
3. Create backup: use `write_file` to copy to `~/.vibe/prompts/{system_prompt_id}-backup-{YYYYMMDD}-{HHMMSS}.md`
4. **Derive delegation triggers from subagent purpose/description:**
   - Extract key action verbs (review, search, create, edit, explore, etc.)
   - Extract key nouns (code, files, patterns, scripts, etc.)
   - Generate 2-3 concrete example trigger phrases
   - Examples:
     - Purpose: "Reviews code for quality and security issues" → Triggers: "Review this code", "Check for bugs", "Audit security"
     - Purpose: "Search for patterns across files" → Triggers: "Find usages of X", "Search for pattern Y", "Where is Z used"
     - Purpose: "Create and manage scripts" → Triggers: "Write a script", "Create helper.py", "Update script"
5. **Generate new table row:**
   ```markdown
   | [Task description derived from purpose] | `{name}` | [Trigger 1], [Trigger 2], [Trigger 3] |
   ```
   Example: `| Code review and security auditing | `code-reviewer` | "Review this code", "Check for bugs", "Audit security" |`
6. Find the delegation table in the prompt (look for the line containing "| Request involves... | Delegate to | Example triggers |")
7. Find the end of the table (next line starting with `|` that has different content, or the end of the table marker)
8. Insert the new row before the end of the table
9. Use `edit` to add the new row to the system prompt file
10. Validate the table markdown formatting is correct by reading the modified file

**If update fails or custom prompt not found:**
- Inform user: "Could not update system prompt dispatch rules. Please manually add to {system_prompt_file}:"
  ```markdown
  | [Task description] | `{name}` | [Trigger examples] |
  ```
- Continue with subagent creation (this is NOT blocking)

**If update succeeds:**
- Inform user: "Updated {system_prompt_file} dispatch rules to include {name}"

**Required tools:** `read_file`, `write_file`, `edit`

### Step 7: Confirm and Test

After creation:
1. Display the created TOML content
2. Display the prompt content (if created)
3. Display the dispatch rule update status
4. Suggest testing:
   ```
   Test your new subagent with: vibe -p "task(task='your task here', agent='{name}')"
   ```
5. Ask: "Does this configuration look correct? (y/n/Edit)"
   - If "Edit": return to Step 2
   - If "n": delete files and cancel
   - If "y": confirm success and **add the agent to the `[tools.task]` allowlist** in `~/.vibe/config.toml` so delegating to it does not prompt:
     ```toml
     [tools.task]
     allowlist = [..., "{name}"]
     ```
     - Inform user: "Added {name} to the task allowlist"
     - Note: the delegation table in the system prompt (updated in Step 6) is the single registry - AGENTS.md does not list subagents

### Step 8: Output

**Success Output:**
```markdown
## Subagent Created: {name}

**Type:** {agent_type}
**Location:** {file_path}
**Safety Level:** {safety_level}
**Enabled Tools:** {tools_list}

**Dispatch Rule Status:** {updated/skipped/failed - details}

**TOML Configuration:**
```toml
{content}
```

**Next Steps:**
- Reload config for changes to take effect
- Test: `vibe -p "task(task='test task', agent='{name}')"`
- Use: The main agent can now delegate tasks using this subagent
- Modify: Edit {file_path} to adjust configuration

**Note:** Remember that session-level "always allow" permissions do NOT propagate to subagents. Each subagent respects only its own TOML-defined permissions.
```

## Configuration Reference

### Agent Types
- `subagent`: Delegation-only. Spawned by main agent via `task` tool. Not user-selectable.
- `agent`: User-facing. Selectable via `vibe --agent <name>` or `Shift+Tab`.

### Safety Levels
- `safe`: Visual indicator only (green). Use for read-only or non-destructive.
- `neutral`: Visual indicator only (yellow). Use for agents that may modify files.
- `destructive`: Visual indicator only (red). Use for agents with destructive capabilities.
- `yolo`: Visual indicator only (purple). Use with extreme caution.

**Important:** Safety level is a visual hint only and does NOT enforce permissions. Always pair with appropriate tool permissions.

### Common Tool Sets

**Read-Only Research:**
```toml
enabled_tools = ["read_file", "grep"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"
```

**Code Analysis:**
```toml
enabled_tools = ["read_file", "grep", "bash"]

[tools.read_file]
permission = "always"

[tools.grep]
permission = "always"

[tools.bash]
permission = "ask"
allowlist = ["wc -l", "grep -r", "find . -name"]
```

**Code Generation:**
```toml
enabled_tools = ["read_file", "write_file", "edit", "grep"]

[tools.read_file]
permission = "always"

[tools.write_file]
permission = "always"

[tools.edit]
permission = "always"

[tools.grep]
permission = "always"
```

## Known Limitations

1. **Permission Propagation**: Session-level "always allow" does NOT apply to subagents (Mistral Vibe Issue #390). Each subagent respects only its own TOML permissions.

2. **No User Interaction**: Subagents cannot use `ask_user_question` or any interactive tools.

3. **Text-Only Returns**: Subagents return text results only to the parent agent.

4. **No Nesting**: Subagents cannot spawn other subagents.

## Verification

Test with:
- [ ] `/subagent-creator` with no arguments (interactive mode)
- [ ] `/subagent-creator code-review` (name only)
- [ ] `/subagent-creator` with full description
- [ ] Creating a read-only subagent
- [ ] Creating a write-enabled subagent
- [ ] Creating a subagent with custom prompt
- [ ] Attempting to create duplicate subagent (should warn)
- [ ] Verify dispatch rules are updated in system prompt

## Red Flags

Warn user about:
- Granting write permissions without restrictions
- Using `permission = "always"` for bash tool without allow/deny lists
- Creating subagents with overly broad tool access
- Using `agent_type = "agent"` when they meant `subagent`
- Dispatch rules update failing silently