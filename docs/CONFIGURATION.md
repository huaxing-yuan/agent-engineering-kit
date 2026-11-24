# Configuration reference

Configuration lives in `.agent-engineering.yaml` at the project root.

## Minimal example

```yaml
version: 1
project:
  name: sample-app
  description: A small task API
  languages: [python]
  documentation_languages: [en]
  source_roots: [src]
  docs_root: docs
modules:
  - id: core
    name: Core
    paths: [src/core/**]
    responsibility: Domain rules and public contracts
  - id: api
    name: API
    paths: [src/api/**]
    responsibility: HTTP adapter and request validation
test:
  default_command: python -m unittest discover -s tests -v
  fast_command: python -m unittest discover -s tests -v
  full_command: python -m unittest discover -s tests -v
  areas:
    core: [src/core/**]
    api: [src/api/**]
  area_commands:
    core: python -m unittest tests.test_core -v
    api: python -m unittest tests.test_api -v
  broad_change:
    paths: [pyproject.toml, tests/**, "*.sln", "*.slnx"]
    max_files: 30
    max_modules: 4
verification:
  stale_days: 30
  ui: false
existing:
  agent_files: [AGENTS.md, CLAUDE.md]
  instruction_files: [.github/instructions/project.md]
  preserve_existing: true
github:
  issue_required: true
  manual_test_label: manual testing
commands:
  build: python -m compileall src
  lint: python -m ruff check .
```

## Project

- `name`: required display name.
- `description`: human summary; discovery leaves a reminder.
- `languages`: required non-empty list. Use `unknown` until reviewed.
- `documentation_languages`: locales maintained by the project.
- `source_roots`: top-level code roots.
- `docs_root`: user-documentation directory.

## Modules

Each module needs a unique `id`, display `name`, one or more path globs, and a responsibility.

Path globs are used for test selection, not for enforcing architecture. The architecture rule lives in instructions and review.

Avoid modules named only after directories when the actual boundary is different.

## Test commands

- `default_command`: required string; may be empty while unknown.
- `fast_command`: deterministic local/CI gate.
- `full_command`: broad safety net.
- `areas`: module/test-area path globs.
- `area_commands`: optional per-area commands.

`aeng test select --run` executes configured commands with `shell=False`. Do not put shell pipelines, environment assignments, or secrets in these strings. Use a project script when composition is needed.

## Broad-change fallback

Selection falls back when:

- a configured broad path changes;
- changed source files exceed `max_files`;
- touched areas reach `max_modules`;
- source changes match no area.

Fallback is conservative. It prevents a heuristic from silently skipping the fast/full gate.

## Existing files

`existing` records what discovery found. It does not grant permission to overwrite those files. `preserve_existing` should remain true.

## Verification

- `stale_days`: warning threshold for inactive plans and pending manual tests.
- `ui`: declaration used by initialization guidance; it does not run UI tests automatically.

## GitHub

- `issue_required`: require an issue on non-obsolete manual tests.
- `manual_test_label`: label used only by explicit `--create-issue`.

Set `issue_required: false` when the project intentionally has no issue tracker.

## Documentation

Optional section:

```yaml
documentation:
  root: docs
  locales: [en]
  translation_policy: declared-only
  build_command: ""
  pages:
    - path: docs/api.md
      source_patterns: [src/api/**]
  screenshots:
    index: docs/screenshot-index.md
    required: false
  search_index:
    generated_at: release
    committed: false
```

- `pages` maps source changes to documentation candidates.
- `locales` are the manual locales reported by docs commands.
- `translation_policy` accepts `none`, `declared-only`, `readmes-only`, or `full`.
- `build_command` runs only with `aeng docs check --build`.
- Screenshot paths are relative to the documentation root.
- `search_index` records policy; it does not generate an index.

See [DOCUMENTATION.md](DOCUMENTATION.md).

## Pulse

```yaml
pulse:
  enabled: true
  stale_days: 7
```

Disabled by default. When enabled, `aeng check` warns if `engineering/pulse/latest.json` is missing or stale.
See [PULSE.md](PULSE.md).

## Discovery metadata

`discovery` is informational. Remove it or keep it; the validator does not treat it as architecture evidence.
