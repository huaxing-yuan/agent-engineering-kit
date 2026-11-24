---
id: dec-2026-11-24-pulse-requires-a-retained-baseline
module: cli
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_pulse.py
superseded_by: ''
---

# Pulse requires a retained baseline

## Context

CI artifacts are ephemeral and cannot provide continuous comparison by themselves

## Decision

latest.json is the persistent baseline; dated reports and CI artifacts are derived output

## Consequences

Continuous Pulse claims require a committed or externally retained baseline

## Reopen only if

The kit gains a supported hosted baseline store
