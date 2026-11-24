# Screenshot index

Release-time review list for screenshots required by the manual. Paths are relative to the documentation root.

Status values:

- `placeholder`: required, but no asset exists yet.
- `captured`: asset exists, but has not been reviewed.
- `verified`: a human verified it against the recorded build.
- `stale`: source or UI changed after verification.
- `obsolete`: the page or feature no longer needs the image.

## Screenshots

| Doc page | UI source | Asset | Status | Must show | Verified in |
|---|---|---|---|---|---|

## Rules

- A file that exists is not automatically current.
- `verified` requires `Verified in`.
- Re-check screenshots before release and after relevant UI changes.
- Use synthetic data and redact secrets, customer data, and internal hostnames.
- If an image is not needed, remove the row or mark it obsolete.
- Automated capture can produce an artifact; human review establishes visual and language correctness.
