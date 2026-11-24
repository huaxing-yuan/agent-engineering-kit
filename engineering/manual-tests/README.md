# Manual Verification Register

Use this register only for checks that current automation cannot exercise.

## Lifecycle

`pending -> verified | failed | blocked | obsolete`

- `verified` requires explicit human confirmation, `verified_in`, and evidence.
- Open entries require an issue when `github.issue_required` is true.
- Verified and obsolete files remain as evidence but leave the generated index.
- When a check becomes automatable, add the test and mark the entry `obsolete` with a link.

## Format

One file per check. Include why manual, prerequisites, numbered steps, expected results, evidence, and related links.

<!-- AENG:MANUAL:START -->
| Entry | Module | Status | Created | Updated | Issue |
|---|---|---|---|---|---|
<!-- AENG:MANUAL:END -->
