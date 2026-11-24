---
id: dec-2026-11-24-documentation-planes-stay-separate
module: docs
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_documentation.py
superseded_by: ''
---

# Documentation planes stay separate

## Context

User manuals and internal architecture notes serve different readers

## Decision

User manuals describe product tasks; engineering technical notes describe as-built system facts; engineering tracking records work and rulings

## Consequences

Traceability links the planes without copying internal details into user prose

## Reopen only if

A project has a single combined documentation system with no distinct maintainer audience
