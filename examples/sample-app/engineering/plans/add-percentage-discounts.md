---
id: add-percentage-discounts
module: core
type: plan
status: draft
owner: maintainer
updated: '2026-11-24'
manual_required: false
docs_impact: pending
decisions_captured: false
blocked_by: ''
superseded_by: ''
---

# Add percentage discounts

## Outcome

Apply a validated percentage discount to a total

## Non-goals

No UI or persistence

## Current evidence

`src/sample_app/__init__.py` currently exposes only `total`. `tests/test_calculations.py` pins empty, absent, and summed totals.

## Related decisions

- [An empty total is zero](../decisions/dec-2026-11-24-an-empty-total-is-zero.md).

## Slices

| ID | Scope | Verification | Status | Evidence |
|---|---|---|---|---|
| S1 | Specify valid percentages, rounding, and rejection behavior | Red-first unit tests | planned | — |
| S2 | Implement the pure discount function | S1 tests plus boundary cases | planned | — |

## Gates

- G1: S1 tests fail for the missing behavior before implementation.
- G2: S2 passes all unit tests without changing total semantics.

## Documentation impact

`pending`

Update the sample README when the function becomes available.

## Manual verification

Not required: this is a pure function with deterministic unit coverage.

## Risks and rollback

- Risk: Rounding policy is ambiguous; settle it in S1 before implementation.
- Rollback: Remove the new function and tests; `total` remains unchanged.

## Landing log

- 2026-11-24 — Plan created.
