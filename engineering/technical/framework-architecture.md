---
id: framework-architecture
status: proposed
updated: 2026-11-24
reviewed_against: ""
owners: [cli, templates, docs]
source_paths:
  - aeng/cli.py
  - aeng/config.py
  - aeng/docs.py
  - aeng/pulse.py
  - aeng/validator.py
  - aeng/templates/project/**
related_decisions:
  - dec-2026-11-24-documentation-planes-stay-separate
  - dec-2026-11-24-documentation-impact-is-structural-not-semantic
  - dec-2026-11-24-pulse-requires-a-retained-baseline
superseded_by: ""
---

# Framework architecture

## Scope

The generic governance CLI, installable templates, documentation checks, and Pulse baseline.

## Evidence

The architecture is defined by the source paths above and protected by the framework test suite.
This note remains proposed until the v0.2 feature commit is available for review.

## Current design

- Configuration is optional and backward-compatible.
- Markdown artifacts remain usable without the CLI.
- Initialization creates missing files only.
- Documentation templates are installed explicitly.
- Documentation impact is path-based and conservative.
- Pulse persists a small JSON baseline and a dated Markdown report.
- Governance validation never executes a documentation build unless explicitly requested.

## Invariants

- No private product names, internal classes, or customer data appear in templates or examples.
- Existing project files are preserved.
- Structural checks do not claim semantic truth.
- A CI artifact is not a persistent Pulse baseline.

## Failure modes

- Path mappings can miss user-visible behavior; unmapped source is reported for review.
- Screenshot existence does not establish freshness.
- A stale Pulse baseline produces a warning, not a false progress claim.

## Related decisions and tests

- `tests/test_documentation.py`
- `tests/test_pulse.py`
