# Quick start

## 1. Install from a fork

```bash
git clone https://github.com/<your-account>/agent-engineering-kit.git
cd agent-engineering-kit
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
aeng check
```

Python 3.10+ and PyYAML 6.x are required. Git is required for test selection. GitHub CLI is optional.

## 2. Configure a target project

```bash
python -m pip install -e /path/to/agent-engineering-kit
cd /path/to/project
aeng discover --output .agent-engineering.yaml
```

Open `.agent-engineering.yaml`. Discovery finds languages by file count, common source roots, candidate modules, test commands, and existing instruction files. It cannot understand responsibility or architecture for you.

Review at least:

1. `project.languages`
2. `project.source_roots`
3. `modules[].paths` and `modules[].responsibility`
4. `test.default_command`, `fast_command`, and `full_command`
5. `test.areas` and `test.area_commands`
6. `existing.agent_files` and `existing.instruction_files`
7. `verification.ui`
8. `github.issue_required`

## 3. Preview before writing

```bash
aeng init --dry-run
```

Every action is `create` or `preserve`. Resolve unexpected preserves or creates before continuing.

## 4. Initialize

```bash
aeng init
aeng check
aeng report
```

For an existing `engineering/` directory:

```bash
aeng init --adopt-existing --dry-run
aeng init --adopt-existing
```

Adoption adds missing files only. It does not translate legacy frontmatter or rewrite existing indexes. Run `aeng check` to see the exact migration work.

## 5. Create the first plan

```bash
aeng plan new "Add request validation" \
  --module core \
  --outcome "Reject malformed payloads with a stable error" \
  --non-goals "No UI redesign"

aeng plan add-slice --plan add-request-validation \
  --id S1 --scope "Validate at the boundary" --verification "Unit + contract tests"

aeng plan set-slice --plan add-request-validation --id S1 --status in-progress
aeng plan set-slice --plan add-request-validation --id S1 --status landed \
  --evidence "tests/test_validation.py; commit abc123"
```

Progress is now derived from the slice table.

## 6. Run the completion gate

```bash
aeng test select
aeng test select --run
aeng check
```

If selection falls back, run the configured fast/full command. Do not treat a path-based selection as proof that every affected behavior is covered.

## No CLI workflow

The Markdown files remain usable without the CLI. Copy the templates from `aeng/templates/project/`, map `agent-instructions/agent-engineering/` to `.github/instructions/agent-engineering/`, and fill the placeholders. Maintain the documented table/frontmatter shapes. The CLI adds generation, validation, and reporting; it is not required to understand the method.
