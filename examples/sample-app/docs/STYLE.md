# Documentation style

This is a product manual, not an engineering note. Write for the person performing the task.

## Audience

- Explain what the reader sees and what happens.
- Use the reader's vocabulary, not internal class or module names.
- Keep implementation, architecture, design rationale, and repository paths out of user-facing prose.

## Page structure

1. Page title.
2. One short paragraph: what this area is for and where to start.
3. **Before you start** only when a prerequisite blocks the task.
4. Task sections that match the product's UI or command structure.
5. Numbered steps for tasks; tables only for enumerations or comparisons.
6. **See also** with a few related pages.

## Task-first rules

- Lead with the quickest successful scenario.
- Put non-blocking alternatives after the main path.
- Put exhaustive reference material last.
- Use exact current UI labels and commands.
- State defaults and limitations only when they affect the task.
- Do not invent features, shortcuts, parameters, or behavior.

## Settings and reference pages

- Explain where a settings page lives once.
- Use one section per UI group.
- For each setting, state what it controls, its choices and default, and when to change it.
- Do not repeat the same navigation path for every setting.
- Drop table columns that repeat the row label or add no information.

## Internal details

User-facing pages must not contain class names, methods, file paths, binding names, config keys, decision numbers, or design trade-offs.
Use traceability comments for source links. Put measurements, architecture, and evidence in `engineering/technical/`.

## Voice

- Plain, specific, active.
- No filler, marketing adjectives, or claims that the page "explains" itself.
- Do not repeat one fact as a three-bullet synonym list.

## Deep read

- Read the whole page against the current UI, CLI, or API before editing.
- When one section is wrong, sweep the page and sibling pages for the same class of error.
- Correct stale claims in place; do not append a correction paragraph that leaves the original claim active.

## Screenshots

- Use screenshots for UI, diagrams for concepts.
- A screenshot must match the target build.
- File existence does not mean the image is current.
- Track required images in `screenshot-index.md`.
- Use placeholders instead of inventing images.
- Screenshots support documentation; they are not behavioral test assertions.

## Translation

- Update user-visible strings with the behavior change.
- Translate stable documentation after the product behavior settles.
- Check parity only for declared locales.
- Do not claim a language is supported because a placeholder README exists.

## Close-out

- Run `aeng docs check`.
- Build the documentation site when a build command is configured.
- Report documentation impact for user-visible changes.
- Record a doc gap when no page covers the behavior.
- Verify screenshots against the target build.
- Generate search indexes at release time unless the project explicitly chooses another policy.
