# Engineering Management

This directory is the project's durable management memory. It is independent of any agent host.

| Artifact | Owns | Must not duplicate |
|---|---|---|
| `PROJECT.md` | Generated overview | Hand-maintained status |
| `modules/` | Feature maturity, evidence, roadmap | Full implementation plans |
| `plans/` | Active execution contracts | Finished history |
| `decisions/` | Durable accepted/rejected/deferred rulings | Routine change logs |
| `manual-tests/` | Checks automation cannot exercise today | Already automated behavior |
| `verification/` | Test matrix and expiring known failures | Secret values |
| `technical/` | As-built architecture knowledge | Active task checklists |
| `reports/` | Point-in-time audits and handoffs | Standing rules |

## Rules

1. One artifact has one writer. Parallel agents must not edit the same file concurrently.
2. Plan, decision, and manual-test indexes are generated. Never hand-edit their marked sections.
3. `PROJECT.md` is generated from module cards and lifecycle metadata.
4. Every active plan names its next slice and any blocker.
5. `done` plans retire immediately. Git history is the archive.
6. A rejected or deferred feature gets a decision in the same task.
7. A user-visible change reports documentation impact.
8. A change that automation cannot exercise gets a manual-test entry in the same task.
9. Run `aeng check` at the completion gate.
10. Keep active artifacts short. Move long-form design and as-built knowledge to `technical/`.

## Plan lifecycle

`draft -> in-progress -> dev-finished -> done -> retired`

- `blocked` requires a named blocker and exit condition.
- `dev-finished` means only required manual verification or documentation remains.
- `superseded` links the successor.
- `abandoned` records why work stopped.
- A plan without manual verification may retire directly after all other gates pass.

## Retirement checklist

- All slices are landed with evidence.
- Required tests and builds pass.
- Documentation impact is complete or explicitly not required.
- Required manual tests are verified or obsolete.
- Durable rulings are captured as decisions.
- As-built knowledge has a home outside the plan.
- The plan file is deleted and indexes are regenerated.

## Manual verification lifecycle

`pending -> verified | failed | blocked | obsolete`

Only explicit human confirmation permits `verified`. Record the exact build in `verified_in`.
Open entries appear in the generated index. Verified and obsolete files remain as evidence but leave the work list.

## Documentation governance

User manuals live in the configured documentation root. Internal technical notes live in `technical/`.

- User pages are task-first and contain no internal implementation details.
- Current technical notes require a review date, commit, and resolvable source paths.
- User-visible changes report documentation impact in the same task.
- `aeng docs impact` maps source changes to candidate pages; it does not decide semantic truth.
- `aeng docs check` validates links, traceability, screenshots, and technical-note frontmatter.
- `aeng docs audit` writes structural findings and a human review checklist.
- Screenshots require build-specific human verification.
- Search indexes are release artifacts unless the project explicitly decides otherwise.

## Pulse

`aeng pulse` derives a snapshot from plans, module cards, decisions, manual tests, and documentation metrics.
`aeng pulse --write` updates `engineering/pulse/latest.json` and a dated Markdown report.

The latest JSON is the persistent comparison baseline. A CI artifact is not a baseline until it is retained or committed.
Pulse shows movement and aging; it cannot prove code completeness, semantic documentation accuracy, or runtime verification.

## Suggested budgets

- Root `AGENTS.md`: 120–150 lines.
- Active plan: about 200 lines; deeper design belongs in `technical/`.
- Decision: about 30 lines.
- Module card: about 80 lines.
- Manual test: one screenful plus evidence.

These are review triggers, not reasons to hide necessary detail.
