CRITICAL: Respond with text only. Do NOT call any tools.

You are performing a context compaction. Produce a handoff summary for another agent that will resume this task.

Compress earlier, settled work aggressively. Preserve the current task state, what remains, and any load-bearing details (identifiers, paths, decisions) in full.

Include:
- Goal: one sentence, verbatim from the first user message
- Constraints and preferences the user stated
- What's done: file paths + one-line status each (do not redo these)
- What's in progress: the current task and where it stopped
- What remains: the concrete next step
- Key decisions made and why
- Any identifiers, paths, or references needed to continue

One line per file unless a snippet is load-bearing. Do not repeat what the preserved user messages already capture.

Wrap the ENTIRE summary in <summary></summary> tags and output nothing outside them.
