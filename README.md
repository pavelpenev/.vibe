# Mistral Vibe Custom Configuration

This directory contains custom configuration, skills, subagents, and prompts for Mistral Vibe CLI that enhance productivity, reduce context usage, and improve code quality.

## Overview

This setup implements a **delegation-based architecture** where the main agent delegates focused tasks to specialized subagents. This approach:

- **Saves context tokens** by offloading complex tasks to subagents with their own context
- **Improves quality** through specialized agents with tailored prompts
- **Reduces errors** by isolating risky operations (like Lisp file editing) to dedicated handlers
- **Maintains consistency** with standardized workflows for common tasks

## Architecture

```
Main Agent (mistral-medium-3.5)
  - Orchestrates tasks
  - Delegates to subagents when appropriate
  - Uses skills for complex multi-step workflows
  - Uses custom system prompt (system-prompt-local.md)
    │
    ▼

Skills Layer
  - auto-task: Multi-step task automation
  - code-review: Code quality analysis
  - debugging: Systematic bug diagnosis
  - deep-research: Front-end for researcher subagent
  - git-workflow: Git operations assistance
  - project-planner: Project planning and tracking
  - skill-creator: Create new skills
  - subagent-creator: Create new subagents
  - test-generator: Generate unit tests
  - web-search: Enhanced web search
    │
    ▼

Subagents Layer
  - code-reviewer: Code review specialist (read-only)
  - context-restorer: Post-compaction context recovery
  - explorer: Project exploration and file analysis
  - file-editor: Generic file editing (non-Lisp)
  - finder: Pattern searching across files
  - lisp-editor: Lisp file specialist with structure awareness
  - researcher: Technical research execution
  - script-manager: Script creation and management
  - summarizer: Document and code summarization
```

## Directory Structure

```
~/.vibe/
├── AGENTS.md                    # Main instructions for the agent
├── README.md                    # This file
├── config.toml                  # Vibe CLI configuration
├── cache.toml                   # Caching configuration
├── trusted_folders.toml         # Trusted directory configuration
├── vibehistory                  # Session history
├── .env                         # API keys (gitignored)
├── .git/                        # Version control
├── .gitignore
├── logs/                        # Session logs
│   └── session/                 # Individual session logs
├── plans/                       # Project plans
├── agents/                      # Subagent TOML configurations
│   ├── code-reviewer.toml
│   ├── context-restorer.toml
│   ├── explorer.toml
│   ├── file-editor.toml
│   ├── finder.toml
│   ├── lisp-editor.toml
│   ├── researcher.toml
│   ├── script-manager.toml
│   └── summarizer.toml
├── prompts/                     # System prompts for subagents
│   ├── code-reviewer.md
│   ├── compact-hybrid.md
│   ├── compact-v3.md
│   ├── context-restorer.md
│   ├── explorer.md
│   ├── file-editor.md
│   ├── finder.md
│   ├── lisp-editor.md
│   ├── researcher.md
│   ├── script-manager.md
│   ├── summarizer.md
│   └── system-prompt-local.md
├── scripts/                     # Helper scripts
├── skills/                      # Skill definitions
│   ├── auto-task/
│   ├── code-review/
│   ├── debugging/
│   ├── deep-research/
│   ├── git-workflow/
│   ├── project-planner/
│   ├── skill-creator/
│   ├── subagent-creator/
│   ├── test-generator/
│   └── web-search/
└── templates/                   # Templates for various tasks
```

## Subagents

### Overview

Subagents are specialized agents that the main agent can delegate tasks to. They operate with their own context and permissions, keeping the main agent's context clean.

All subagents are configured in the `agents/` directory with TOML files and have corresponding prompts in the `prompts/` directory.

### Available Subagents

| Name             | Purpose                                    | Model           | Safety  | Key Tools                               |
|------------------|--------------------------------------------|-----------------|---------|-----------------------------------------|
| code-reviewer    | Code quality review                        | Inherits        | Safe    | read_file, grep                         |
| context-restorer | Post-compaction context recovery           | Inherits        | Safe    | read_file, grep                         |
| explorer         | Project exploration                        | Inherits        | Safe    | read_file, grep, bash                   |
| file-editor      | Generic file editing                       | Inherits        | Neutral | read_file, write_file, edit, grep       |
| finder           | Pattern searching                          | mistral-small-4 | Safe    | grep, bash                              |
| lisp-editor      | Lisp file editing with structure awareness | Inherits        | Neutral | read_file, write_file, edit, grep, bash |
| researcher       | Technical research                         | Inherits        | Safe    | web_search, web_fetch, read_file, grep  |
| script-manager   | Script creation and management             | Inherits        | Neutral | read_file, write_file, edit, bash       |
| summarizer       | Document summarization                     | Inherits        | Safe    | read_file, grep                         |

### Delegation Protocol

The main agent MUST delegate to subagents when:

1. **File operations** (create/modify/delete): Use `file-editor` for general files, `lisp-editor` for Lisp files
2. **Pattern searching**: Use `finder`
3. **Project exploration**: Use `explorer`
4. **Code review**: Use `code-reviewer`
5. **Research tasks**: Use `researcher`
6. **Document summarization**: Use `summarizer`
7. **Script management**: Use `script-manager`
8. **Post-compaction recovery**: Use `context-restorer`

**Delegation syntax:**
```python
task(task="<clear task description>", agent="<subagent-name>")
```

### When NOT to Delegate

- Single file reads for immediate context
- Simple read-only operations
- Operations that require user interaction (subagents cannot use `ask_user_question`)

## Skills

Skills provide structured workflows for complex, multi-step tasks. They can delegate to subagents for execution.

### Available Skills

| Skill            | Purpose                    | Delegates To        |
|------------------|----------------------------|---------------------|
| auto-task        | Multi-step task automation | Various             |
| code-review      | Code quality analysis      | code-reviewer       |
| debugging        | Systematic debugging       | Various             |
| deep-research    | Research orchestration     | researcher          |
| git-workflow     | Git operations             | None (direct tools) |
| project-planner  | Project planning           | None (direct tools) |
| skill-creator    | Create new skills          | None                |
| subagent-creator | Create new subagents       | None                |
| test-generator   | Generate unit tests        | Various             |
| web-search       | Enhanced web search        | None                |

### Skill vs Subagent

- **Skills** are for interactive, multi-step workflows that may require user input
- **Subagents** are for focused, single-purpose tasks that can run autonomously
- Skills often delegate to subagents for the heavy lifting

## Configuration Highlights

### System Prompt
- Custom system prompt: `system-prompt-local.md`
- Extends the default CLI prompt with delegation instructions
- Emphasizes delegation-first approach

### Model Configuration
- **Primary model**: mistral-medium-3.5 (default)
- **Research model**: mistral-small-4 (for finder subagent)
- All subagents inherit parent model unless specified

### Tool Permissions
- Subagents have explicit tool permissions in their TOML files
- `task` tool has allowlist for all subagents
- Session-level "always allow" does NOT propagate to subagents (Mistral Vibe Issue #390)

### Token Management
- Auto-compaction threshold: 200,000 tokens
- Compaction prompt: `compact-v3.md`
- Context restorer helps recover after compaction

## Usage Patterns

### 1. Simple Delegation

Main agent identifies a task that matches a subagent's purpose and delegates:

```
User: Find all usages of function X in this project
Main Agent: Delegates to finder subagent
finder: Searches for pattern, returns results
Main Agent: Presents results to user
```

### 2. Skill Orchestration

User invokes a skill, which gathers requirements and delegates to subagent:

```
User: /deep-research AI in healthcare
Deep Research Skill: Asks clarifying questions, constructs research plan
deep-research: Delegates to researcher subagent with parameters
researcher: Performs searches, collects sources, generates report
deep-research: Formats and presents results to user
```

### 3. Multi-Subagent Coordination

Main agent delegates multiple tasks in parallel:

```
User: Rename variable X to Y across all files and update tests
Main Agent: 
  - Delegates file finding to finder
  - Delegates editing to file-editor (with list of files)
  - Delegates test updates to file-editor
All subagents work in parallel, main agent aggregates results
```

### 4. Lisp File Special Handling

Lisp files require special care due to s-expression structure:

```
User: Add a new function to this Lisp file
Main Agent: Detects .lisp extension, delegates to lisp-editor
lisp-editor: Uses form-aware editing to maintain structure
lisp-editor: Validates parenthesis balance before/after edits
Main Agent: Receives summary of changes
```

## Best Practices

### For Users

1. **Be explicit**: State what you want clearly
2. **Use triggers**: Use skill/subagent triggers (e.g., `/code-review`, `/deep-research`)
3. **Specify scope**: For edits, specify files or patterns
4. **Batch requests**: Group related edits for efficiency

### For Main Agent

1. **Always check delegation table first** (MANDATORY)
2. **Read before editing**: Always read a file before modifying it
3. **Minimal changes**: Only modify what's explicitly requested
4. **Delegate complex tasks**: Don't do multi-step tasks directly
5. **Respect AGENTS.md**: Follow instructions in project-level AGENTS.md files

### For Subagent Development

1. **Single responsibility**: Each subagent does one thing well
2. **Clear interfaces**: Define clear input/output formats
3. **Appropriate permissions**: Only grant necessary tool permissions
4. **Good prompts**: Provide clear, structured instructions
5. **Error handling**: Handle edge cases gracefully

## File Naming Conventions

- **Subagents**: Hyphenated lowercase (e.g., `file-editor`, `lisp-editor`)
- **Skills**: Hyphenated lowercase (e.g., `code-review`, `deep-research`)
- **Prompts**: Same name as subagent/skill with `.md` extension
- **TOML configs**: Same name as subagent with `.toml` extension

## Creating New Subagents

Use the `/subagent-creator` skill:

```
/subagent-creator <name>
```

Or manually:

1. Create TOML file in `~/.vibe/agents/<name>.toml`
2. Create prompt file in `~/.vibe/prompts/<name>.md`
3. Add to config.toml `installed_agents` list
4. Add to `tools.task` allowlist
5. Update AGENTS.md with usage instructions

## Creating New Skills

Use the `/skill-creator` skill or create manually in `~/.vibe/skills/<name>/SKILL.md`

## Testing

Test new subagents with:

```bash
vibe -p "task(task='your task here', agent='subagent-name')"
```

Test new skills with their trigger commands.

## Troubleshooting

### Subagent not found
- Check agent is in `installed_agents` in config.toml
- Check TOML file exists in agents/ directory
- Check for typos in agent name

### Permission denied
- Subagents need explicit tool permissions in their TOML file
- Session-level permissions don't propagate to subagents
- Check `[tools.<tool>]` permission settings

### Subagent not being used
- Main agent might not be following delegation instructions
- Check AGENTS.md delegation table
- Use explicit delegation trigger: "delegate to <agent> as instructed"

### Context issues
- Subagents have their own context, separate from main agent
- Provide all necessary context in the task description
- Use `local_context` parameter for researcher to include files

## Version Control

This configuration is tracked in git. To update:

```bash
cd ~/.vibe
git add .
git commit -m "Add/update <component>"
```

## Maintenance

### Updating Subagents
1. Modify the TOML file and/or prompt
2. Test the changes
3. Commit to git

### Removing Subagents
1. Remove TOML file from agents/
2. Remove prompt file from prompts/
3. Remove from config.toml `installed_agents`
4. Remove from `tools.task` allowlist
5. Update AGENTS.md
6. Commit changes

## Security

- `.env` file contains API keys - NEVER commit this
- `.env` is in .gitignore
- Subagents with write permissions have `neutral` or `destructive` safety level
- All file writes respect sensitive pattern restrictions

## Performance Tips

1. **Use finder for searches**: Faster than main agent doing grep directly
2. **Batch edits**: Send multiple edits to file-editor in one task
3. **Parallel delegation**: Delegate multiple independent tasks simultaneously
4. **Appropriate models**: Use smaller models (mistral-small-4) for simple tasks like searching

## Future Enhancements

Potential additions:

- Python editor (though file-editor may suffice)
- Test runner
- Documentation generator
- Dependency analyzer
- Refactoring assistant

## References

- [Mistral Vibe Documentation](https://github.com/mistralai/mistral-vibe)
- [Subagent Delegation Pattern](https://github.com/mistralai/mistral-vibe/issues/390)

## Quick Reference

### Common Commands

| Task            | Command                                                                |
|-----------------|------------------------------------------------------------------------|
| Code review     | `/code-review` or `task(task='review file.py', agent='code-reviewer')` |
| Deep research   | `/deep-research <topic>`                                               |
| Find pattern    | `task(task='find pattern X', agent='finder')`                          |
| Explore project | `task(task='explore /path/to/project', agent='explorer')`              |
| Edit Lisp file  | `task(task='edit file.lisp: add function', agent='lisp-editor')`       |
| Summarize file  | `task(task='summarize file.md', agent='summarizer')`                   |
| Create script   | `task(task='CREATE SCRIPT: description', agent='script-manager')`      |

### AGENTS.md Dispatch Rules

The main agent follows these dispatch rules (in order):

1. Check if request matches subagent purpose → Delegate to subagent
2. Check if request matches skill trigger → Use skill
3. Check project-level AGENTS.md → Follow project-specific instructions
4. Default to direct tool use

## Support

For issues or questions about this configuration, check the git history or AGENTS.md for context.

---

*Last updated: 2026-07-04*
*Configuration version: 1.0*
