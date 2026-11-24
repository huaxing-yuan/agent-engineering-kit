# Core engineering

- Preserve the module boundary declared in `.agent-engineering.yaml`.
- Dependencies point inward: contracts/domain must not depend on UI or host adapters.
- Change the smallest coherent surface. Do not combine unrelated cleanup.
- Reuse existing abstractions before adding a new one.
- Default to the narrowest visibility that satisfies the actual consumer.
- Validate untrusted input at system boundaries; trust internal invariants.
- Keep async operations non-blocking where the stack supports concurrency.
- Add a dependency only when existing libraries cannot reasonably solve the problem.
- Do not add compatibility shims for hypothetical future requirements.
- Record a durable boundary in `engineering/decisions/`; record ordinary progress in the owning plan.

## Layer routing

| Change | Start with | Required evidence |
|---|---|---|
| Domain rule | Unit test | Edge cases and regression proof |
| Public contract | Contract test | Producer/consumer or round-trip fixtures |
| Adapter | Integration test | Reproducible ephemeral dependency |
| UI behavior | Headless/component test | State and command effects |
| Visual/localization | Rendered check | Human review when judgment remains |
| Agent tool | Schema + registry test | Permissions and golden trajectory |
| Release | Artifact smoke test | Real installed/packaged process |
