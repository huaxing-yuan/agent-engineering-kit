---
id: dec-2026-11-24-decision-ids-do-not-use-global-sequence-numbers
module: cli
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_framework.py
superseded_by: ''
---

# Decision ids do not use global sequence numbers

## Context

Parallel agents can allocate the same next number

## Decision

New decision ids use date plus slug and are never renumbered

## Consequences

References use stable Git paths instead of a shared counter

## Reopen only if

A repository requires numeric ids for an external compliance system
