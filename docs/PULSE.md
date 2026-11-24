# Pulse

Pulse is an opt-in progression snapshot derived from repository facts. It is not a task board or a productivity score.

## Generate

```bash
aeng pulse
aeng pulse --json
aeng pulse --write
aeng pulse --write --output-dir engineering/pulse
```

`--write` produces:

```text
engineering/pulse/
  latest.json
  progression-YYYY-MM-DD.md
```

`latest.json` is the persistent comparison baseline. The dated Markdown file is the human report.

## What it measures

- new, retired, and changed plans;
- plan status and landed/total slices;
- next slice and blockers;
- open manual checks;
- durable decision count;
- module maturity snapshots;
- documentation page counts by locale;
- module-card doc gaps;
- screenshot status counts;
- current/proposed/superseded technical notes.

## Baseline persistence

A CI artifact is not a baseline. If a scheduled job uploads `latest.json` only as an artifact, the next local run cannot diff against it.

Choose one explicit policy:

1. **Local or bot commit**: commit `latest.json` at a regular cadence.
2. **External retained artifact**: download the retained baseline before the next run.
3. **No scheduled baseline**: run Pulse manually and accept point-in-time comparisons.

Do not claim continuous measurement without a retained baseline.

## Enable staleness warnings

```yaml
pulse:
  enabled: true
  stale_days: 7
```

`aeng check` warns when the baseline is missing or older than the threshold.
Pulse is disabled by default for small projects.

## Scheduled CI

A weekly workflow may run `aeng pulse --write` and upload `engineering/pulse/` as an artifact.
Do not let the workflow commit generated reports on every run unless the repository explicitly wants bot commits.
If the workflow is the baseline writer, grant the minimum required permission and prevent recursive runs.

## Limits

Pulse cannot know:

- whether remaining code is implemented but not recorded;
- whether documentation prose is semantically true;
- whether a screenshot matches the current build;
- whether a feature works in the running product;
- whether an Agent used the best approach.

Those require tests, documentation review, manual verification, and decisions.

## When to use it

- Personal projects: optional, usually manual.
- Small teams: useful weekly if at least several plans are active.
- Multi-team repositories: useful with ownership and retained baselines.
- Regulated environments: supplementary only; not an audit system of record.
