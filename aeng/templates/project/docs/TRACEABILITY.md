# Traceability

Traceability links a user-facing page to the source that defines its behavior. It is metadata for maintainers and agents, not prose for readers.

Use an HTML comment near the top of the page:

```html
<!--
  UI Source: src/ui/example.ts (2026-01-01)
  Code Source: src/application/example.ts (2026-01-01)
  Test Source: tests/test_example.py
  Decision Source: engineering/decisions/dec-2026-01-01-example-contract.md
-->
```

## Source tags

| Tag | Points to | Owner |
|---|---|---|
| `UI Source` | View, template, or interaction definition | Agent or maintainer |
| `Code Source` | Behavior, controller, or service implementation | Agent or maintainer |
| `Test Source` | Test that protects the documented contract | Agent or maintainer |
| `Decision Source` | Durable ruling that constrains the behavior | Decision register |
| `Workflow Source` | Optional human-maintained workflow and screenshot intent | Human |

## Rules

- Paths are relative to the project root.
- Dates on source tags record when the link was reviewed.
- A source path must exist or match a configured glob.
- Do not put internal names in visible prose.
- `Workflow Source` is optional and human-owned; agents must not rewrite it.
- When a page changes behavior, review its source tags in the same task.
- A traceability comment proves a link exists, not that the prose is semantically correct.
