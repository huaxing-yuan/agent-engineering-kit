# Adoption and migration guide

## Reuse directly

These parts are stack-agnostic and usually safe to adopt as written:

- Root contract structure.
- Plan, decision, and manual-test lifecycles.
- Atomic slice table and evidence requirement.
- Generated indexes and `PROJECT.md`.
- Completion gate.
- Test-layer routing.
- Safe initialization and adoption report.
- Expiring known-failure format.

## Adapt deliberately

| Area | Why adaptation is needed |
|---|---|
| Modules | Directory names do not prove responsibility or ownership |
| Commands | Discovery is heuristic; manifests and CI are stronger evidence |
| Maturity | Team release and support policy may differ |
| Documentation | Root, locales, and publishing pipeline vary |
| Issue policy | Some teams use GitHub, some use another tracker, some use files only |
| UI verification | Framework headless support and OS coverage vary |
| Blocking tiers | Cost, flakiness, and release risk differ |

## Existing `AGENTS.md`

Default behavior: preserve it byte-for-byte.

Review `.agent-engineering/integration-block.md` and merge only the missing lifecycle and completion rules. Keep project-specific constraints. Remove duplicates after the merge.

Do not let two root files claim authority over the same rule.

## Existing `CLAUDE.md`

Preferred end state:

```markdown
# CLAUDE.md

Read and follow [AGENTS.md](AGENTS.md). It is the canonical agent contract.
Load only the area instructions relevant to the paths you change.
```

If the existing file contains useful host-specific rules, keep those rules and add the pointer. Do not duplicate the whole engineering contract.

## Existing instructions

Kit instructions are installed under `.github/instructions/agent-engineering/` to avoid name collisions.

Classify existing instructions:

- **Standing and still true**: keep.
- **Duplicated by the kit**: choose one owner and remove the duplicate after review.
- **Contradictory**: create a decision or ask the owner; do not let the agent choose silently.
- **Historical**: move to an archive or delete after confirming no current consumer.

## Existing `engineering/`

Use `--adopt-existing`. The CLI adds missing files but does not rewrite existing content.

Migration order:

1. Back up or commit the current state.
2. Map existing module IDs to `.agent-engineering.yaml`.
3. Add required Plan frontmatter: `manual_required`, `docs_impact`, `decisions_captured`.
4. Ensure every Plan has the documented `Slices` table.
5. Convert decision IDs to `dec-YYYY-MM-DD-slug` or keep a documented legacy namespace.
6. Ensure manual tests have `created`, `updated`, and an issue when required.
7. Add generated-section markers to existing index READMEs.
8. Run `aeng index`, inspect the diff, then `aeng check`.

Do not mass-rewrite history just to match the new format. Migrate active artifacts first.

## Existing decisions

Private product decisions should not be copied into a public example repository. In a private adoption, keep them in place and map their module IDs.

A decision belongs in the register only if it constrains future behavior. Routine implementation notes belong in module cards, technical docs, or Git history.

## Existing manual backlog

Classify each entry:

- Still manual: keep and assign an issue/build.
- Now automatable: add the test, then mark `obsolete` with a link.
- No longer relevant: mark `obsolete` with a reason.
- Duplicate: keep one canonical checklist and redirect the other.

Do not mark entries `verified` merely because code exists.

## CI adoption

Start with reporting mode if the repository has known failures, but record an expiry for every allowlisted failure. Then move to blocking mode.

A gate is credible only if it:

- propagates the runner exit code;
- proves tests were discovered and executed;
- blocks new failures;
- expires known-failure exceptions;
- validates governance write-back.

## Public release checklist

- New clean Git history; do not fork private history and delete names later.
- Synthetic examples only.
- No private hostnames, accounts, customer data, issue numbers, or tokens.
- Check screenshots, logs, HTML, fixtures, and metadata.
- Run tests and `aeng check` from a fresh clone.
- Verify all public links.
- Review dependency licenses and provenance.
