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
| ID | Title | Module | Decision | Date |
|---|---|---|---|---|
| [dec-2026-11-24-decision-ids-do-not-use-global-sequence-numbers](dec-2026-11-24-decision-ids-do-not-use-global-sequence-numbers.md) | Decision ids do not use global sequence numbers | cli | accepted | 2026-11-24 |
| [dec-2026-11-24-documentation-impact-is-structural-not-semantic](dec-2026-11-24-documentation-impact-is-structural-not-semantic.md) | Documentation impact is structural not semantic | cli | accepted | 2026-11-24 |
| [dec-2026-11-24-documentation-planes-stay-separate](dec-2026-11-24-documentation-planes-stay-separate.md) | Documentation planes stay separate | docs | accepted | 2026-11-24 |
| [dec-2026-11-24-files-are-the-portable-contract](dec-2026-11-24-files-are-the-portable-contract.md) | Files are the portable contract | cli | accepted | 2026-11-24 |
| [dec-2026-11-24-initialization-preserves-existing-rules](dec-2026-11-24-initialization-preserves-existing-rules.md) | Initialization preserves existing rules | templates | accepted | 2026-11-24 |
| [dec-2026-11-24-pulse-requires-a-retained-baseline](dec-2026-11-24-pulse-requires-a-retained-baseline.md) | Pulse requires a retained baseline | cli | accepted | 2026-11-24 |
<!-- AENG:DECISIONS:END -->
