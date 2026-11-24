# Lifecycle and completion gate

## When to open a plan

Open a plan when work:

- spans sessions or independently verifiable slices;
- crosses modules or architecture layers;
- changes a public contract or persisted format;
- includes migration, deletion, or release;
- needs ordered gates such as domain -> adapter -> headless -> UI.

Do not open a plan for a small, understood fix. Use an `investigation` when the first deliverable is evidence rather than implementation.

## Plan frontmatter

```yaml
id: kebab-case-id
module: core
type: plan
status: in-progress
owner: maintainer
updated: 2026-11-24
manual_required: false
docs_impact: pending
decisions_captured: false
blocked_by: ""
superseded_by: ""
```

- `type`: `plan | investigation | design | migration`.
- `status`: `draft | in-progress | dev-finished | blocked | superseded | abandoned`.
- `done` is transient; the file must be retired.
- `docs_impact`: `pending | complete | not-required`.
- `decisions_captured`: explicit acknowledgment that durable rulings have a home.

## Atomic slices

A slice is independently verifiable. It has an ID, scope, verification, status, and evidence.

A slice is not landed if it contains a known unfinished tail. Split the tail into another slice.

`aeng` computes progress from this table. Do not add a second manual percentage.

## Status transitions

- `draft -> in-progress`: execution started.
- `in-progress -> dev-finished`: every slice landed; required manual verification remains.
- `in-progress -> blocked`: blocker and exit condition recorded.
- `in-progress -> superseded`: successor named.
- `in-progress -> abandoned`: stop reason recorded in the plan.
- A plan with no manual requirement may retire directly after all other gates pass.

## Retirement

`aeng plan retire` checks:

1. Every slice is landed with evidence.
2. Documentation impact is complete or not required.
3. `decisions_captured` is true.
4. Required manual tests are verified or obsolete.

The CLI cannot prove that the right decisions were written or the documentation is correct. Those remain review responsibilities.

After retirement:

- rulings live in `engineering/decisions/`;
- as-built knowledge lives in `engineering/technical/`;
- user behavior lives in user documentation;
- execution history lives in Git.

## Decisions

Create a decision for a durable accepted boundary, explicit rejection, deferral, or supersession.

Required content:

- Context.
- Decision and decision-maker.
- Consequences.
- Reopen condition.

Do not delete a rejected decision. Supersede it with a link.

## Manual tests

Statuses:

- `pending`: not run.
- `verified`: human ran it and recorded the build.
- `failed`: reproduced a defect.
- `blocked`: cannot run; blocker named.
- `obsolete`: rolled back or automated.

Only explicit human confirmation permits `verified`. An agent may record that confirmation, but may not infer it.

## Completion gate

`aeng check` fails on:

- invalid configuration or frontmatter;
- unknown modules and statuses;
- unretired `done` plans;
- missing slice evidence;
- invalid `dev-finished` contracts;
- missing decision guards;
- missing required issues or `verified_in`;
- expired known failures;
- stale generated indexes;
- dead Markdown links;
- missing root contract.

Warnings cover stale plans, stale pending manual tests, and a `CLAUDE.md` that does not point to `AGENTS.md`.

A passing check proves consistency, not product correctness.
