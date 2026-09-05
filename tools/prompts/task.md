Use `task` to launch a subagent that handles an independent task autonomously.

Usage:
- Specify the `agent` profile that best fits the work and provide a detailed, self-contained task description.
- State exactly what the subagent should return; it runs autonomously and cannot ask the user or spawn another subagent.
- Launch multiple subagents in parallel only for independent work, then synthesize their results.

Subagent capabilities:
- Each generic subagent loads its named role skill and uses its pinned model.
- Some roles modify files; read-only roles report findings without writing.
- Tool permissions, denylists, and sensitive-pattern protections remain active for subagents.

The `usage-tool` is not part of task dispatch. Use it only when the user explicitly requests usage or allowance information.
