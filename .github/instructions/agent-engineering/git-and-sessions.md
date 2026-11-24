# Git and parallel sessions

- Inspect `git status` before any operation that could discard work.
- Use isolated worktrees for parallel agents; never share one dirty working tree.
- One writer per artifact. Generated indexes are regenerated, not hand-edited.
- One coherent commit per logical change; do not commit per tool call.
- Do not push, force-push, rewrite history, delete branches, or modify shared infrastructure without explicit approval.
- If a hook fails, fix the cause; do not bypass it.
- Verify delegated results against the actual diff before reporting completion.
- A green build does not prove references resolved, tests executed, or the feature works.
- When another session changes the branch, re-check HEAD and your exact files before committing.
