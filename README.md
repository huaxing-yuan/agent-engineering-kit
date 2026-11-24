# Agent Engineering Kit

**Repository-native project memory and verification for coding agents.**

Agent Engineering Kit gives a coding agent the things a fresh session cannot infer from code alone: active plans, durable decisions, module maturity, verification routes, manual-test ownership, and a machine-checked definition of done.

It is harness-agnostic. Use it with any coding agent that can read repository files and run commands.

- English: this file
- Français: [README.fr.md](README.fr.md)
- 中文: [README.zh-CN.md](README.zh-CN.md)

## What it is

- A small set of Markdown contracts and templates.
- A Python CLI that discovers project structure, initializes safely, generates indexes, validates write-back, and reports progress.
- A verification model that separates unit, integration, headless, real-process, live, and manual evidence.
- Documentation impact analysis, traceability and screenshot checks, internal technical-note validation, and an opt-in Pulse baseline.
- An adoption path that preserves existing `AGENTS.md`, `CLAUDE.md`, instructions, and engineering artifacts.

## What it is not

- It is not an agent runtime, model, orchestrator, or task queue.
- It does not replace GitHub Issues, Jira, or Linear.
- It does not require a particular language, framework, or cloud.
- It does not make an agent autonomous or turn a green build into proof that a feature works.

## The core idea

> Code says what the system does. Repository memory says what the team intends, what it rejected, and what evidence is still missing.

| Artifact | Owns |
|---|---|
| `AGENTS.md` | Standing agent contract |
| `engineering/modules/` | Feature maturity, documentation, tests, roadmap |
| `engineering/plans/` | Active execution contracts and atomic slices |
| `engineering/decisions/` | Durable accepted, rejected, deferred, and superseded rulings |
| `engineering/manual-tests/` | Checks automation cannot exercise today |
| `engineering/verification/` | Test matrix and expiring known-failure allowlist |
| `aeng check` | Completion gate for missing or stale write-back |

## Requirements

- Python 3.10 or newer.
- PyYAML 6.x.
- Git for change-scoped test selection.
- GitHub CLI only if you explicitly want `aeng verify add --create-issue` or `--close-issue`.

No model API key is required.

## Quick start

### 1. Run the kit itself

```bash
git clone https://github.com/<your-account>/agent-engineering-kit.git
cd agent-engineering-kit

python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install -e .
aeng --version
aeng check
aeng report
```

Replace `<your-account>` with the account you forked from. For this repository, the canonical public location is:

```bash
git clone https://github.com/huaxing-yuan/agent-engineering-kit.git
```

### 2. Use it in an existing project

Install the CLI from your local fork, then run discovery inside the target project:

```bash
python -m pip install -e /path/to/agent-engineering-kit
cd /path/to/your-project

aeng discover --output .agent-engineering.yaml
```

Review the generated file before initializing. Discovery is a draft, not an architectural decision. Correct:

- project name, description, and languages;
- source roots and module boundaries;
- test, build, and lint commands;
- existing instruction files;
- documentation root and locales;
- whether UI/headless verification applies;
- whether GitHub issues are required for manual tests.

Then preview and apply:

```bash
aeng init --dry-run
aeng init
aeng check
aeng report
```

If documentation is configured:

```bash
aeng docs init --dry-run
aeng docs init
aeng docs check
aeng docs impact --base main
```

Pulse is optional and disabled by default:

```bash
aeng pulse
aeng pulse --write
```

`aeng init` never overwrites an existing `AGENTS.md`, `CLAUDE.md`, instruction file, module card, or engineering document. If `engineering/` already exists, use `--adopt-existing` to add only missing files.
Documentation templates are explicit: `aeng docs init` never overwrites an existing manual or style file.

## Let a coding agent initialize the project

After installing the CLI, give your agent this prompt:

```text
Initialize agent-engineering-kit in this repository.

1. Run `aeng discover --stdout` and inspect the actual manifests, source tree, tests, documentation, AGENTS.md, CLAUDE.md, and existing instruction files.
2. Create or update .agent-engineering.yaml with accurate languages, source roots, module boundaries, responsibilities, and test/build/lint commands.
3. Do not overwrite any existing agent rules or engineering artifacts.
4. Run `aeng init --dry-run` and show me the adoption plan and conflicts.
5. Wait for my approval, then run `aeng init` (use --adopt-existing only if I approve adopting an existing engineering/ directory).
6. Run `aeng check`. If documentation is configured, preview and run `aeng docs init`, then run `aeng docs check` and `aeng docs impact --base main`.
7. Run `aeng report`. Do not enable Pulse unless I approve it.
8. Summarize what was installed, what was preserved, what needs manual review, and which commands are still unknown.
```

The agent should inspect the repository rather than invent module boundaries or successful test commands.

## What initialization creates

```text
AGENTS.md                              # only if missing
CLAUDE.md                              # only if missing
.github/instructions/agent-engineering/
  README.md
  core-engineering.md
  testing.md
  ui.md
  documentation.md
  security.md
  git-and-sessions.md
engineering/
  README.md
  PROJECT.md                           # generated
  modules/<module-id>.md
  plans/INDEX.yaml                     # generated
  decisions/README.md                  # generated index
  manual-tests/README.md               # generated open backlog
  verification/test-matrix.yaml
  verification/known-failures.yaml
  technical/_TEMPLATE.md
  reports/_TEMPLATE.md
.agent-engineering/
  adoption-report.md
  integration-block.md                 # when an existing agent contract was preserved
```

Documentation templates are installed separately with `aeng docs init`:

```text
docs/
  STYLE.md
  TRACEABILITY.md
  screenshot-index.md
```

Existing instructions are not moved or rewritten. Kit instructions live in a namespaced directory so they can coexist with project- or host-specific rules.

## Plan lifecycle

Open a plan when work spans sessions or slices, crosses modules, changes a public contract, includes a migration, or needs ordered gates. Use a time-boxed `investigation` when the approach is still uncertain.

```text
draft -> in-progress -> dev-finished -> done -> retired
              |              |
           blocked       manual verification
              |
        superseded / abandoned
```

A plan contains atomic slices:

| ID | Scope | Verification | Status | Evidence |
|---|---|---|---|---|
| S1 | Domain contract | Unit + contract tests | landed | commit/test link |
| S2 | UI behavior | Headless test | in-progress | — |

Rules:

- Progress is derived from slice status; there is no hand-maintained percentage.
- A slice with an unfinished tail is not landed.
- `landed` requires evidence.
- `dev-finished` means every slice is landed and only required human verification or documentation remains.
- A plan retires only after tests, documentation impact, manual verification, and durable decisions are complete.
- Finished plans are deleted; Git history is the archive.

## Decisions

Write a decision when a durable direction is accepted, rejected, deferred, or superseded. Do not use decisions as a changelog.

Decision IDs use `dec-YYYY-MM-DD-kebab-case-title`, avoiding global-number races between parallel agents. A decision includes context, ruling, consequences, and the evidence that would reopen it. Use `enforced_by` to link a test or guard.

## Issues and manual tests

- External bug reports and independently triaged work belong in issues.
- A small fix inside an active plan does not need a duplicate issue.
- Add a manual-test entry when current automation cannot exercise the change.
- New manual tests require an issue by default. Set `github.issue_required: false` for a no-issue tracker.
- Only explicit human confirmation allows `verified`; record the exact build in `verified_in`.
- When a manual check becomes automatable, add the test and mark the entry `obsolete`.

## Verification model

| Layer | Use it for |
|---|---|
| Static/governance | Formatting, links, schemas, indexes, missing write-back |
| Unit | Pure logic and edge cases |
| Component/contract | Boundaries, serialization, compatibility |
| Integration | Multiple modules and ephemeral dependencies |
| Headless/in-process | Real application and UI behavior without OS chrome |
| Real-process E2E | Packaging, OS dialogs, focus, multiple windows, accessibility |
| Live external | Real providers, accounts, networks, paid models |
| Manual | Visual judgment, language nuance, hardware, real accounts |

Important rules:

1. Prove a regression test fails on the old behavior.
2. Test selection is an optimization, not proof of complete coverage.
3. Broad or infrastructure changes fall back to the fast/full gate.
4. `0 tests executed` is not success.
5. Wait for observable state, not fixed sleeps.
6. Use stable automation identifiers, not localized labels.
7. A screenshot is an artifact, not a behavioral assertion.
8. Known failures require an exact test ID, owner, issue, reason, and expiry date.

If the repository contains an agent product, add an orthogonal evaluation track for tool schemas, role visibility, permissions, confirmations, golden trajectories, and final artifacts. Software tests and agent evaluations answer different questions.

## Documentation governance

The kit separates user manuals, internal technical notes, and engineering tracking.

- User manuals are task-first and contain no internal implementation details.
- `aeng docs impact` maps changed source to candidate pages and doc gaps.
- `aeng docs check` validates links, traceability, screenshots, and technical-note frontmatter.
- `aeng docs audit` combines structural findings with a human semantic-review checklist.
- Current technical notes require a review date, commit, and resolvable source paths.
- Screenshots require build-specific human verification.
- Search indexes are release artifacts unless the project decides otherwise.

Read [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) and [docs/DOCUMENT_AUDIT.md](docs/DOCUMENT_AUDIT.md).

## Pulse

`aeng pulse` derives a progression snapshot from plans, module cards, decisions, manual tests, and documentation metrics.

- `latest.json` is the persistent comparison baseline.
- A dated Markdown report is generated for humans.
- A CI artifact is not a baseline until it is retained or committed.
- Pulse is opt-in and disabled by default.

Read [docs/PULSE.md](docs/PULSE.md).

## Which projects fit

- **Personal or prototype:** use the minimal profile; no scheduled Pulse.
- **Small team or maintained product:** use the standard profile with docs checks and optional weekly Pulse.
- **Multi-team or multi-repo:** add explicit ownership, retained baselines, and isolated worktrees.
- **Regulated or security-critical:** use the kit as supporting evidence, not as the compliance system of record.

Read [docs/APPLICABILITY.md](docs/APPLICABILITY.md).

## What you can reuse, and what needs care

### Reuse directly

- The plan/decision/manual-test lifecycle.
- Atomic slices with evidence.
- Generated indexes and completion checks.
- The test-layer routing model.
- Safe initialization that preserves existing files.
- Expiring known-failure allowlists.

### Adapt to the project

- Module boundaries and ownership.
- Test/build/lint commands.
- Documentation locations and locales.
- Maturity definitions and review thresholds.
- CI blocking policy.
- Issue labels and tracker integration.

### Use carefully

- **Existing `AGENTS.md`**: merge the integration block deliberately; do not replace working rules.
- **Existing `engineering/`**: adopt incrementally and migrate frontmatter before trusting the gate.
- **Headless UI tests**: framework support and OS coverage vary.
- **Live tests**: credentials, cost, rate limits, and nondeterminism require explicit controls.
- **Known failures**: an allowlist can become permanent debt; expiry is mandatory.
- **Global decision numbers**: do not introduce them for new repositories.
- **Historical decisions**: never publish private product decisions as generic examples.
- **Reports and screenshots**: scrub customer data, internal hostnames, tokens, and metadata.

Read [docs/ADOPTION_GUIDE.md](docs/ADOPTION_GUIDE.md) for the full migration checklist.

## CLI reference

| Command | Purpose |
|---|---|
| `aeng discover` | Draft project configuration from files and manifests |
| `aeng init --dry-run` | Preview creates/preserves without writing |
| `aeng init` | Install missing contracts and artifacts safely |
| `aeng init --adopt-existing` | Add missing files to an existing `engineering/` |
| `aeng check` | Fail on invalid or stale governance artifacts |
| `aeng index` | Regenerate indexes and `PROJECT.md` |
| `aeng report` | Print derived plan and verification progress |
| `aeng docs init` | Install missing documentation templates |
| `aeng docs impact` | Map source changes to documentation candidates |
| `aeng docs check` | Validate documentation structure and traceability |
| `aeng docs audit` | Write a structural audit and human review checklist |
| `aeng pulse` | Generate a progression snapshot |
| `aeng pulse --write` | Persist the baseline and dated report |
| `aeng plan new` | Create an active plan |
| `aeng plan add-slice` | Add an atomic slice |
| `aeng plan set-slice` | Update status and evidence |
| `aeng plan status` | Move a plan through its lifecycle |
| `aeng plan retire` | Delete a completed plan after gates pass |
| `aeng decision add` | Record a durable ruling |
| `aeng verify add` | Add a manual check, optionally creating an issue |
| `aeng verify close` | Record explicit human verification |
| `aeng test select` | Show likely affected tests and fallback reason |
| `aeng test select --run` | Execute selected configured commands |

Use `aeng <command> --help` for exact arguments. Use global `--root` before the command when operating on another directory.

## Documentation

- [Quick start](docs/QUICKSTART.md)
- [Agent initialization prompt](docs/AGENT_INITIALIZATION.md)
- [Adoption and migration guide](docs/ADOPTION_GUIDE.md)
- [Configuration reference](docs/CONFIGURATION.md)
- [Documentation governance](docs/DOCUMENTATION.md)
- [Documentation audit](docs/DOCUMENT_AUDIT.md)
- [Pulse](docs/PULSE.md)
- [Applicability](docs/APPLICABILITY.md)
- [Lifecycle and completion gate](docs/LIFECYCLE.md)
- [Testing strategy](docs/TESTING.md)
- [Security](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Current limitations

Version 0.2 is intentionally small:

- Test selection is path-based and conservative, not a dependency graph.
- Markdown slice parsing expects the documented table shape.
- GitHub integration uses the CLI and is optional; there is no hosted sync service.
- Pulse requires an explicitly retained baseline for continuous comparison.
- There is no GUI, dashboard service, or multi-repository `moved` workflow.
- JSON Schema files are not yet shipped; validation lives in the CLI and tests.
- The sample is synthetic and does not prove suitability for every stack.

These are explicit boundaries, not hidden promises.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Changes to lifecycle semantics need tests and a decision. Changes to templates need a clean-initialization test and an existing-project preservation test.

## License

[MIT](LICENSE).
