# Publication verification — 2026-11-24

- Author: maintainer
- Scope: First public publication of Agent Engineering Kit 0.1.0
- Method: GitHub metadata inspection, fresh clone, hosted CI

## Findings

- Repository is public under the maintainer's personal account.
- Default branch is `main`; MIT license is detected.
- Commit `975a4b571b90ce3bffcec3f14192ad05dd882c39` is published.
- Hosted CI run `45295892661` passed all four matrix jobs:
  - Windows / Python 3.10
  - Windows / Python 3.12
  - Ubuntu / Python 3.10
  - Ubuntu / Python 3.12
- A fresh clone from GitHub passed 18 framework tests, 3 sample tests, both governance checks, and the no-change test-selection path.
- The `manual testing` issue label exists.

## Evidence

- Repository: https://github.com/huaxing-yuan/agent-engineering-kit
- CI: https://github.com/huaxing-yuan/agent-engineering-kit/actions/runs/45295892661
- Clean-clone commands:
  - `python -m unittest discover -s tests -v`
  - `python -m unittest discover -s examples/sample-app/tests -v`
  - `python -m aeng check`
  - `python -m aeng --root examples/sample-app check`
  - `python -m aeng test select --run`

## Non-blocking annotation

GitHub reported that `actions/checkout@v4` and `actions/setup-python@v5` target Node.js 20, which the runner promotes to Node.js 24. All jobs completed successfully. Action upgrades should be evaluated as a separate dependency change.

## Limitations

- No external user has completed an adoption walkthrough yet.
- The sample remains intentionally small and synthetic.
