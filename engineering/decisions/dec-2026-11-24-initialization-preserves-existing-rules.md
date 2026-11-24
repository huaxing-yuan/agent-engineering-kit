---
id: dec-2026-11-24-initialization-preserves-existing-rules
module: templates
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_framework.py
superseded_by: ''
---

# Initialization preserves existing rules

## Context

Projects already have agent instructions and engineering artifacts

## Decision

Init creates missing files only and requires explicit adoption for a non-empty engineering directory

## Consequences

Integration text is proposed in a separate block instead of appended automatically

## Reopen only if

The user explicitly requests a destructive migration mode
