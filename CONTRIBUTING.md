# Contributing

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m unittest discover -s tests -v
aeng check
```

## Change discipline

- One coherent change per pull request.
- Add tests for lifecycle or validation changes.
- Template changes require clean initialization and existing-file preservation coverage.
- Documentation changes must keep the English, French, and Chinese README entry points aligned.
- Do not add private product names, customer data, internal hostnames, or real credentials.
- Update the module card and record a decision when a standing rule changes.

## Pull request checklist

- [ ] Tests pass and prove the intended behavior.
- [ ] `aeng check` passes.
- [ ] Existing files are preserved by initialization.
- [ ] CLI help and documentation match the implementation.
- [ ] No secrets or private identifiers were introduced.
- [ ] User-visible behavior has documentation impact.

## Release checklist

- [ ] Version updated.
- [ ] Clean clone install succeeds.
- [ ] Sample application tests pass.
- [ ] English, French, and Chinese README links resolve.
- [ ] Public repository contains no private history or artifacts.
- [ ] Known limitations are stated accurately.
