# Documentation

## User manual

- Write for the person performing the task, not for the implementer.
- Use exact current UI labels, commands, defaults, and limitations.
- Lead with the quickest successful scenario; add alternatives and reference later.
- Describe what the product does, not internal architecture or design rationale.
- Do not invent features, shortcuts, parameters, or behavior.
- Use synthetic examples and redact secrets, customer data, and internal hostnames.
- Keep source paths, class names, config keys, and decision numbers in traceability comments, not visible prose.
- Read the whole page against current behavior before editing it.

## Internal technical notes

- Use `engineering/technical/` for as-built architecture, measurements, constraints, and failure modes.
- A current note requires `updated`, `reviewed_against`, and resolvable `source_paths`.
- Move durable as-built knowledge out of a plan before retiring the plan.
- Mark replaced notes `superseded`; do not silently rewrite history.

## Traceability

- Link pages to UI, code, tests, and decisions with HTML comments.
- `Workflow Source` is optional and human-owned; never rewrite it as an agent.
- A valid source link does not prove the prose is semantically correct.

## Screenshots

- Track required images in `docs/screenshot-index.md`.
- A file that exists is not automatically current.
- `verified` requires a build in `Verified in`.
- Use placeholders instead of inventing images.
- Automated capture is not human visual or language verification.

## Documentation impact

- Every user-visible change reports documentation impact.
- Run `aeng docs impact` to find mapped pages and unmapped source requiring review.
- If no page covers the behavior, record a doc gap and propose a category and title.
- Run `aeng docs check`; use `--build` only when a build command is configured.

## Translation and generated assets

- Update UI strings with behavior changes.
- Translate stable manuals after behavior settles.
- Check parity only for declared locales.
- Generate search indexes at release time unless the project explicitly chooses another policy.
