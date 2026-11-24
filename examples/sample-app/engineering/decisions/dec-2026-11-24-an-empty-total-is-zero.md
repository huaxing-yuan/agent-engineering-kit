---
id: dec-2026-11-24-an-empty-total-is-zero
module: core
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_calculations.py
superseded_by: ''
---

# An empty total is zero

## Context

Callers need a deterministic result for empty input

## Decision

None and an empty collection both produce zero

## Consequences

Boundary tests pin this behavior

## Reopen only if

A caller needs absent and empty to be distinguishable
