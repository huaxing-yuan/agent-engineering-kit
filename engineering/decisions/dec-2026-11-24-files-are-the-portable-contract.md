---
id: dec-2026-11-24-files-are-the-portable-contract
module: cli
decision: accepted
date: '2026-11-24'
related: ''
enforced_by:
- tests/test_framework.py
superseded_by: ''
---

# Files are the portable contract

## Context

Agent hosts and memory systems change

## Decision

Markdown artifacts remain usable without the CLI; tooling generates and validates them

## Consequences

Templates are packaged resources and documented as the fallback workflow

## Reopen only if

A supported host cannot read repository files
