# Documentation audit guide

A documentation audit compares four surfaces:

1. What the manual promises.
2. What the UI or CLI exposes.
3. What the code actually does.
4. What tests and decisions establish as the contract.

## Automated scope

`aeng docs check` can establish:

- files and links exist;
- traceability paths resolve;
- screenshot rows and assets are structurally valid;
- current technical notes have review metadata;
- configured documentation builds complete.

It cannot establish that a sentence is true.

## Human review procedure

1. Run `aeng docs impact --base <base>` and list candidate pages.
2. Read each whole page, not only the changed lines.
3. Open the referenced UI, command, API, or workflow.
4. Compare exact labels, defaults, persistence scope, errors, and limitations.
5. Check product copy and onboarding text for the same promise.
6. Verify screenshots against the target build.
7. Correct stale claims in place.
8. Sweep sibling pages for the same class of error.
9. Update module-card doc status and record any remaining gap.
10. Run `aeng docs check` and the documentation build.

## Defect classes

| Class | Example |
|---|---|
| Documented but absent | Manual describes a control that does not exist |
| Implemented but undocumented | UI exposes behavior with no manual page |
| Wrong default | Manual states a different value from code |
| Contradictory page | Two sections describe different persistence or scope |
| Stale terminology | Page, UI, and release notes use different names |
| Broken contract | Exit code, error, or serialization differs from the manual |
| Stale screenshot | Image exists but predates the current UI |
| False localization claim | A language is listed but content falls back silently |

## Evidence

Record exact source paths, test names, commands, build identifiers, and dates in the audit report.
Do not put secrets, customer data, internal hostnames, or private product details in a public report.

## Close-out

An audit is complete only when findings are fixed, explicitly deferred with a decision, or recorded as owned doc gaps.
The report itself is not the fix.
