---
id: cli
name: CLI and validation
responsibility: Discovery, safe initialization, lifecycle commands, validation, reports, and test selection.
updated: '2026-11-24'
---

# CLI and validation

## Features

| Feature | Maturity | Docs | Tests | Notes |
|---|---|---|---|---|
| Project discovery | stable | yes | yes | Language/module/command drafts; human review required |
| Safe initialization | stable | yes | yes | Existing files preserved; explicit adoption boundary |
| Plan lifecycle | stable | yes | yes | Evidence required for landed slices and retirement |
| Decision register | stable | yes | yes | Date+slug IDs; guard paths validated |
| Manual verification | stable | yes | yes | Explicit human confirmation and build required |
| Governance check | stable | yes | yes | Frontmatter, indexes, links, expiry, stale warnings; first public CI 4/4 green |
| Progress report | stable | yes | yes | Derived next slice and backlog |
| Test selection | preview | yes | yes | Path-based; conservative fallback; no dependency graph |
| Documentation impact | stable | yes | yes | Source-to-page mapping with explicit semantic-review boundary |
| Documentation check | stable | yes | yes | Links, traceability, screenshots, and technical-note metadata |
| Documentation audit | stable | yes | yes | Structural findings plus mandatory human checklist |
| Pulse | stable | yes | yes | Persistent latest.json baseline and dated Markdown report |

## Active plans

None.

## KPI

- Documentation coverage: all CLI commands have README/help coverage.
- Test evidence: `tests/test_framework.py`.
- Last maturity review: 2026-11-24.

## Roadmap

- Near-term: JSON Schemas and package-build verification.
- Mid-term: Dependency-aware test selection.
- Long-term: Optional tracker adapters without a hosted service.

## Related technical docs

- `technical/`
