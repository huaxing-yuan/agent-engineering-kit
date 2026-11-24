# Agent initialization

The safest initialization is agent-assisted but human-approved. The agent surveys the repository; the CLI performs only explicit, non-destructive writes.

## Copyable prompt

```text
Initialize agent-engineering-kit in this repository.

Rules:
- Do not overwrite existing AGENTS.md, CLAUDE.md, instructions, engineering artifacts, tests, or product code.
- Do not invent module responsibilities, test commands, or successful verification.
- Stop and ask if the adoption plan would replace an existing rule.

Steps:
1. Run `aeng discover --stdout`.
2. Inspect manifests, directory structure, test configuration, documentation, AGENTS.md, CLAUDE.md, and all existing instruction files.
3. Write `.agent-engineering.yaml` with accurate project name, description, languages, source roots, modules, responsibilities, commands, and tracker policy.
4. Run `aeng init --dry-run`.
5. Present the create/preserve plan, conflicts, unknown commands, and any existing engineering directory.
6. Wait for approval.
7. Run `aeng init`. Use `--adopt-existing` only for an explicitly approved existing engineering/ directory.
8. Run `aeng check`.
9. If documentation is configured, preview and run `aeng docs init`, then run `aeng docs check` and `aeng docs impact --base main`.
10. Run `aeng report`. Do not enable Pulse unless the user approves it.

Final response:
- Installed files.
- Preserved files.
- Rules that need manual merging.
- Unknown or uncertain commands.
- Documentation or test gaps.
```

## What the agent should inspect

| Evidence | What it tells the agent |
|---|---|
| Manifest files | Languages, package manager, likely test/build commands |
| Source roots | Candidate modules, not final boundaries |
| Existing tests | Actual runner and invocation |
| Existing instructions | Rules that must be preserved |
| Existing plans/decisions | Current lifecycle vocabulary and migration cost |
| CI configuration | Real blocking gates and external dependencies |
| Documentation tree | User-doc root and locales |

## Approval boundary

The following require explicit approval:

- Merging text into an existing `AGENTS.md` or `CLAUDE.md`.
- Adopting a non-empty `engineering/` directory.
- Replacing a discovered command with a different one.
- Enabling Issue creation.
- Deleting or moving existing project artifacts.

`aeng init` generates `.agent-engineering/integration-block.md` instead of modifying an existing root contract.

## After initialization

Ask the agent to run one small, real task through the lifecycle:

1. Create an investigation or plan.
2. Add atomic slices.
3. Prove a regression test red when relevant.
4. Land a slice with evidence.
5. Regenerate indexes and run `aeng check`.
6. Produce `aeng report`.

This validates the workflow better than inspecting files alone.
