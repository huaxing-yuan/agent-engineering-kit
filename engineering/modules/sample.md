---
id: sample
name: Sample application
responsibility: A synthetic runnable example of the governance lifecycle.
updated: '2026-11-24'
---

# Sample application

## Features

| Feature | Maturity | Docs | Tests | Notes |
|---|---|---|---|---|
| Total calculation | stable | yes | yes | Empty, absent, and summed inputs |
| Governance lifecycle | stable | yes | yes | Clean init, plan, decision, check, report |
| Percentage discounts | planned | no | no | Draft plan intentionally remains unlanded |

## Active plans

- [Add percentage discounts](../../examples/sample-app/engineering/plans/add-percentage-discounts.md)

## KPI

- Documentation coverage: sample README and docs index.
- Test evidence: `examples/sample-app/tests/test_calculations.py`.
- Last maturity review: 2026-11-24.

## Roadmap

- Near-term: Keep the example small and deterministic.
- Mid-term: Add an optional UI example only if it teaches a distinct verification lesson.
- Long-term: No expansion without a concrete adoption need.

## Related technical docs

- `../../examples/sample-app/README.md`
