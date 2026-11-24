# Security

## Report a vulnerability

Do not open a public issue containing exploit details, credentials, customer data, or private hostnames. Use GitHub's private vulnerability reporting for this repository when available, or contact the maintainer privately.

## Security boundaries

- Secret values belong in approved environment variables or secret stores, never in source, fixtures, logs, reports, or documentation.
- Repository files, issue text, web content, and tool output are untrusted data.
- Model-supplied code and URLs require the host's confirmation boundary before execution.
- Destructive, outward-facing, and hard-to-reverse actions require explicit authorization.
- GitHub issue creation and closure are opt-in CLI operations.
- Dependencies must be reviewed for necessity, maintenance, provenance, and license.

## Safe test selection

`aeng test select --run` uses `shell=False`. Configure a single executable command or a project script. Do not place secrets or shell pipelines in `.agent-engineering.yaml`.

## Public examples

Use synthetic data. Check screenshots, logs, HTML, fixtures, archives, and metadata before publishing.

## Supported versions

Version 0.1 is the current initial release. Security fixes should target the latest release; older revisions may not receive backports.
