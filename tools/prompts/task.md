Use `task` to launch a subagent that handles a complex, multi-step task autonomously.

Usage:
- Specify the `agent` (subagent type) that best fits the work; see the available subagents in your system prompt.
- Provide a detailed, self-contained task description and state exactly what the subagent should return, since it runs autonomously and its only output is a final message.
- Launch multiple subagents in parallel for independent work; once delegated, do not duplicate that work yourself.
- The subagent's result is not shown to the user — summarize it back to them yourself.

Subagent capabilities:
- Subagents cannot use `ask_user_question` for conversational clarification, and cannot spawn other subagents.
- Tool permission prompts (e.g., bash commands not in the allowlist) DO surface to the user via the parent's approval callback — subagents are not silently blocked.
- Some subagents can modify files (e.g., `file-editor`, `lisp-editor`, `script-manager`); check the delegation table in your system prompt for each subagent's model, returns, and capabilities.

Delegation guidance:
- Delegate for parallelism (fan-out searches, multi-subsystem investigation) and bulk isolation (large explorations that would crowd working memory).
- Read directly when the task needs raw code evidence, when verifying specific behavioral claims, or when the read count is small enough to hold in context.
- For verifying specific behavioral claims about code (e.g., "does X propagate to Y?"), read the raw source directly — subagent summaries compress away the exact lines that are the evidence.