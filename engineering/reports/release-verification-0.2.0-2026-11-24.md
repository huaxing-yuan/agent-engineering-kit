# Version 0.2 local release verification — 2026-11-24

- Author: maintainer
- Scope: Documentation governance and Pulse release candidate
- Method: automated tests, isolated wheel installation, documentation checks, static repository audit

## Findings

- 33 framework tests passed.
- 3 sample-application tests passed.
- Package compilation passed.
- Wheel build passed and contained all required documentation templates.
- An isolated wheel install completed discover, init, docs init, docs check, Pulse preview, and governance check.
- Framework and sample documentation checks passed with 0 errors and 0 warnings.
- Governance checks passed with 0 errors and 0 warnings.
- 85 local Markdown links resolved.
- 13 YAML files parsed.
- No private product names, internal class names, internal source structures, or configured secret patterns were found.
- The first persistent Pulse baseline was generated.

## Evidence

- `python -m unittest discover -s tests -v`
- `python -m unittest discover -s examples/sample-app/tests -v`
- `python -m compileall -q aeng tools`
- `python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist`
- `python tools/verify_wheel.py dist`
- `aeng docs check`
- `aeng --root examples/sample-app docs check`
- `aeng check`
- `aeng pulse --write`

## Recommended next actions

- Publish the v0.2 commit.
- Confirm hosted CI on the published commit.
- Record the hosted result in a separate publication report.

## Limitations

- Hosted CI had not run at the time of this report.
- Documentation impact is path-based and does not certify semantic truth.
- Pulse continuity requires the committed or externally retained baseline.
