# Documentation governance

Agent Engineering Kit separates three kinds of documentation:

| Artifact | Audience | Owns |
|---|---|---|
| User manual | Product users | Tasks, exact labels, behavior, limitations |
| `engineering/technical/` | Maintainers | As-built architecture, evidence, invariants, failure modes |
| `engineering/` | Agents and project members | Plans, decisions, maturity, verification, doc gaps |

They may link to each other, but they must not duplicate one another.

## Configuration

```yaml
documentation:
  root: docs
  locales: [en]
  translation_policy: declared-only
  build_command: npm run docs:build
  pages:
    - path: docs/authentication.md
      source_patterns:
        - src/auth/**
        - src/ui/login*
    - path: docs/cli.md
      source_patterns:
        - src/cli/**
  screenshots:
    index: docs/screenshot-index.md
    required: true
  search_index:
    generated_at: release
    committed: false
```

All fields are optional except `root` when the `documentation` section exists.
`project.documentation_languages` describes the project's declared documentation languages; `documentation.locales` describes the manual tree checked by the docs commands.

### Translation policies

- `none`: no parity check.
- `declared-only`: report counts for configured locales without requiring every page to be translated.
- `readmes-only`: keep entry-point READMEs aligned while detailed guides use a primary language.
- `full`: use only when the project truly maintains full page parity.

The CLI reports structural counts. It does not fabricate missing translations or claim parity.

## Install templates explicitly

```bash
aeng docs init --dry-run
aeng docs init
```

This installs only missing files:

- `STYLE.md`
- `TRACEABILITY.md`
- `screenshot-index.md`

Normal `aeng init` does not add files to an existing documentation tree. Existing files are never overwritten.

## Check documentation

```bash
aeng docs check
aeng docs check --build
aeng docs check --json
```

Structural checks cover:

- configured pages exist;
- local Markdown links resolve;
- traceability source paths exist or match a glob;
- screenshot rows have valid statuses and assets;
- verified screenshots record `Verified in`;
- current technical notes have review metadata and resolvable source paths;
- superseded technical notes name a successor;
- the optional documentation build exits successfully.

`--build` executes the configured command with `shell=False`. Review the command before enabling it.

## Analyze change impact

```bash
aeng docs impact --base main
aeng docs impact --base main --json
aeng docs impact --base main --output engineering/reports/docs-impact.md
```

The command maps changed files to configured pages and reports:

- directly edited pages;
- pages whose source patterns matched;
- missing pages as doc gaps;
- screenshots that may need recapture;
- changed module source that no page mapping covers.

Path mapping finds candidates. It does not decide whether a change is user-visible or whether existing prose remains true.

## Audit documentation

```bash
aeng docs audit --base main
aeng docs audit --base main --output engineering/reports/docs-audit-2026-11-24.md
```

An audit combines structural findings with a mandatory human checklist:

- read impacted pages against current behavior;
- verify labels, defaults, limitations, and errors;
- confirm documented capabilities exist;
- verify screenshots against the target build;
- review only declared locales;
- correct stale prose in place.

An audit report is point-in-time evidence. It does not replace fixing the page.

## Traceability

Use HTML comments so the metadata remains portable across documentation tools:

```html
<!--
  UI Source: src/ui/login.ts (2026-11-24)
  Code Source: src/auth/session.ts (2026-11-24)
  Test Source: tests/test_session.py
  Decision Source: engineering/decisions/dec-2026-11-24-session-lifetime.md
-->
```

Optional `Workflow Source` points to a human-maintained workflow. Agents may read it but must not rewrite it.

## Screenshots

The screenshot index uses paths relative to the documentation root:

| Doc page | UI source | Asset | Status | Must show | Verified in |
|---|---|---|---|---|---|
| login.md | src/ui/login.ts | images/login-light.png | verified | Full form and error state | abc123 |

Statuses: `placeholder`, `captured`, `verified`, `stale`, `obsolete`.

Rules:

- placeholders do not require an asset;
- captured, verified, and stale entries require the asset to exist;
- verified requires a build;
- old screenshots are not reusable by default;
- automated capture does not replace human review.

## Internal technical notes

```yaml
---
id: session-architecture
status: current
updated: 2026-11-24
reviewed_against: abc123
owners: [backend]
source_paths: [src/auth/**]
related_decisions: []
superseded_by: ""
---
```

Use `proposed`, `current`, or `superseded`.
A plan may link to a proposed note. On retirement, move durable as-built knowledge into a current note.
Historical assessments belong in `engineering/reports/` or Git history, not in the current technical set.

## Search indexes and generated assets

Markdown is the source of truth. Generate search indexes and other large derived documentation assets at release time unless the project explicitly chooses another policy.
Do not commit a large generated index after every page edit.

## Completion rule

A user-visible change is not complete until documentation impact is reported and one of these is true:

- mapped pages are updated;
- a doc gap is recorded in the owning module card;
- documentation is explicitly not required with a reason.

Run `aeng check` as the final governance gate.
