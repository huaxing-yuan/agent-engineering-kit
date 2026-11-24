# Testing

## Before coding

- Classify the affected layers.
- For a defect, write a regression test and prove it fails on the old behavior.
- Identify whether the test is deterministic, live, paid, visual, or manual.

## Selection

- Use `aeng test select` for likely affected tests.
- Selection is an optimization, not proof of complete coverage.
- Shared contracts, build configuration, fixtures, and broad changes use the fast/full gate.
- Include untracked files in the change set.
- Never treat `0 tests executed` as success.

## Test design

- Assert observable behavior and artifacts, not private implementation details unless the contract is the implementation.
- Isolate filesystem, settings, clocks, network, and process-global state.
- Wait for observable state; avoid fixed sleeps.
- Preserve and propagate the test runner's exit code.
- Keep live external tests explicit and secret values out of logs.

## UI and headless

- Use stable automation identifiers, not localized labels.
- Execute real commands; a synthetic click event may bypass them.
- Assert the effect after every action.
- Use per-scenario workspaces and reset global state.
- Screenshots support diagnosis and documentation; they do not replace assertions.

## Known failures

`engineering/verification/known-failures.yaml` is an expiring allowlist, not a place to hide regressions.
Every entry needs an exact test ID, owner, issue, reason, and expiry date.
New failures block. Expired entries block.
