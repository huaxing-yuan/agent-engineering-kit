# Decision Register

Scan this register before proposing a feature or design change.

## Format

One durable ruling per file. IDs are date plus slug; they are never reused or renumbered.

```yaml
---
id: dec-YYYY-MM-DD-kebab-case-title
module: module-id
decision: accepted
date: YYYY-MM-DD
related: ""
enforced_by: []
superseded_by: ""
---
```

Decision values: `accepted | rejected | deferred | superseded`.

## Rules

1. Record accepted boundaries, explicit rejections, deferrals, and superseding rulings.
2. Do not record routine implementation progress.
3. Rejected decisions remain; supersede them with a link instead of deleting them.
4. A deferral names the evidence that would reopen it.
5. Prefer an `enforced_by` test or guard when the ruling can be protected.
6. Keep the entry short; link long-form analysis.

<!-- AENG:DECISIONS:START -->
<!-- AENG:DECISIONS:END -->
