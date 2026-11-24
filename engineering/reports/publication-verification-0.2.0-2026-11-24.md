# Version 0.2 publication verification — 2026-11-24

- Author: maintainer
- Scope: Published documentation governance and Pulse release
- Method: GitHub metadata, fresh clone, hosted CI

## Findings

- Commit `9f34683739bd37b58f93b9a1a9e1a66ed981d434` is published on `main`.
- Hosted CI run `45462940506` passed all four jobs:
  - Ubuntu / Python 3.10
  - Ubuntu / Python 3.12
  - Windows / Python 3.10
  - Windows / Python 3.12
- Every job passed framework tests, wheel build, wheel template verification, governance, documentation, Pulse preview, sample governance, sample documentation, and sample tests.
- A fresh clone passed 33 framework tests, 3 sample tests, both documentation checks, governance, and Pulse preview.
- No private product identifiers, internal class names, internal source structures, or configured secret patterns were found.

## Evidence

- Repository: https://github.com/huaxing-yuan/agent-engineering-kit
- CI: https://github.com/huaxing-yuan/agent-engineering-kit/actions/runs/45462940506
- Clean-clone verification used the published `main` branch.

## Non-blocking annotation

GitHub reports that `actions/checkout@v4` and `actions/setup-python@v5` target Node.js 20, which the runner promotes to Node.js 24. All jobs succeeded. Action upgrades remain a separate dependency change.

## Limitations

- No external user has completed an adoption walkthrough yet.
- Documentation impact remains path-based.
- Pulse continuity depends on retaining `latest.json`.
