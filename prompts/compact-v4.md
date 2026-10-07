CRITICAL: Respond with text only. Do NOT call any tools.

You are performing a context compaction. Produce a handoff summary for another agent that will resume this task.

Compress earlier, settled work aggressively. Preserve the current task state, what remains, and any load-bearing details (identifiers, paths, decisions) in full.

Include:
- Goal: one sentence, verbatim from the first user message
- Constraints and preferences the user stated
- Task classification: trivial, implementation, review-only, design-only, or plan-only
- Current workflow phase: which phase (0-6) the task is at, and whether design/plan have been accepted by the user
- What's done: file paths + one-line status each (do not redo these)
- Authorship: the author set for the actual review scope (agents that authored or materially contributed to in-scope changes); preserve earlier contributors after retries and fixes, and report unknown provenance rather than assuming. Record the scope and selected review composition so authorship exceptions survive compaction.
- What's in progress: the current task and where it stopped
- What remains: the concrete next step
- Key decisions made and why
- Any identifiers, paths, or references needed to continue

One line per file unless a snippet is load-bearing. Do not repeat what the preserved user messages already capture.

Wrap the ENTIRE summary in <summary></summary> tags and output nothing outside them.
