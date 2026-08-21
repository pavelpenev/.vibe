Use `task` to launch a subagent that handles a complex, multi-step task autonomously.

Usage:
- Specify the `agent` (subagent type) that best fits the work; see the available subagents in your system prompt.
- Provide a detailed, self-contained task description and state exactly what the subagent should return, since it runs autonomously and its only output is a final message.
- Launch multiple subagents in parallel for independent work; once delegated, do not duplicate that work yourself.
- The subagent's result is not shown to the user — summarize it back to them yourself.

Subagent capabilities:
- Subagents cannot use `ask_user_question` for conversational clarification, and cannot spawn other subagents.
- Subagents run on their own context with their pinned model. Each generic subagent loads a role skill (implementor, reviewer, advisor, etc.) to specialize. Permission prompts do not occur — safe tools are set to always, dangerous commands are denylisted (silent skip).
- Some roles can modify files (e.g., `implementor`, `lisp-implementor`); check the delegation table in your system prompt for each role's returns and capabilities. Read-only roles (reviewer, advisor, explorer, finder, summarizer, verifier) are instructed not to write even though write tools are available.

Delegation guidance:
- Delegate for parallelism (fan-out searches, multi-subsystem investigation) and bulk isolation (large explorations that would crowd working memory).
- Read directly when the task needs raw code evidence, when verifying specific behavioral claims, or when the read count is small enough to hold in context.
- For verifying specific behavioral claims about code (e.g., "does X propagate to Y?"), read the raw source directly — subagent summaries compress away the exact lines that are the evidence.