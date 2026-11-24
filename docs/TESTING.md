# Testing strategy

## Route by the question

| Layer | Question | Default gate |
|---|---|---|
| Static/governance | Are contracts, links, and write-back consistent? | Every change |
| Unit | Is pure logic correct? | Affected change |
| Component/contract | Are boundaries and wire/persisted formats compatible? | Affected change |
| Integration | Do modules and ephemeral dependencies cooperate? | Affected change |
| Headless/in-process | Does real application/UI behavior work without OS chrome? | UI behavior change |
| Real-process E2E | Do packaging, OS integration, focus, windows, and accessibility work? | Critical journeys/pre-release |
| Live external | Does a real provider/account/network behave correctly? | Explicit opt-in |
| Manual | Does rendering, language, hardware, or real-account behavior need human judgment? | Same task as the change |

## Bottom-up delivery

For a cross-layer feature:

1. Prove the domain or contract without UI.
2. Prove adapters and non-UI consumers.
3. Prove headless/CLI flows.
4. Add UI behavior.
5. Add rendered/manual verification.
6. Smoke-test the real artifact.

Do not start a UI slice while the layer below is only assumed to work.

## Regression tests

For a defect:

1. Reproduce the symptom.
2. Add a test at the lowest layer that can observe it.
3. Run it against the old behavior and confirm failure.
4. Fix the cause.
5. Confirm the same test passes.
6. Run affected neighboring tests.

A test that was green before and after the fix may not protect the defect.

## Selection

`aeng test select` includes tracked and untracked changes. It maps files to configured areas and prints the reason and command.

Fallback occurs for broad paths, too many files, too many modules, or unmapped source changes.

Selection is not a dependency graph. Review shared contracts and transitive behavior manually.

## Headless rules

- Stable automation IDs, not display text.
- Real command execution.
- State-based waits.
- Effect assertions after actions.
- Isolated workspaces/settings/global state.
- No screenshot-only success criteria.

## Real-process E2E

Keep this layer thin. Use it for what headless cannot prove: installed artifact startup, native dialogs, focus, multiple windows, DPI, accessibility exposure, and OS integration.

## Live and paid tests

Never make live external tests the silent default. Require explicit configuration, secret injection, cost awareness, timeouts, and diagnostic artifacts. Treat provider outage separately from product regression.

## Known failures

```yaml
failures:
  - test_id: tests.test_example
    owner: team
    issue: "123"
    reason: Temporary external fixture limitation
    expires: 2026-12-31
```

Expired entries fail `aeng check`. The CI test runner must separately enforce the same allowlist; the governance checker does not parse test results.

## Agent evaluation

If the project includes an agent, test separately:

- tool schema validity;
- registry visibility by role;
- permission and confirmation boundaries;
- deterministic fake-model trajectories;
- final artifacts and state transitions;
- host tool parity.

Use real-model evaluations as sampled evidence, not as the only deterministic gate.
