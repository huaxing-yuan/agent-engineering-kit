---
id: dec-2026-11-24-documentation-impact-is-structural-not-semantic
module: cli
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_documentation.py
superseded_by: ''
---

# Documentation impact is structural not semantic

## Context

Path mapping can find candidate pages but cannot prove prose is true

## Decision

aeng docs impact reports candidates and gaps; aeng docs audit requires human semantic review

## Consequences

Automation never certifies documentation correctness

## Reopen only if

A reliable behavior-to-prose proof system is implemented and validated
