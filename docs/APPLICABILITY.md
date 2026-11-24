# Applicability

Agent Engineering Kit is a governance layer, not a mandatory ceremony. Adopt the smallest profile that solves a real problem.

## Profiles

### Minimal

Use for personal projects, prototypes, and short-lived experiments.

- Root `AGENTS.md`.
- `engineering/plans/` for multi-session work.
- `engineering/decisions/` only for durable rulings.
- `aeng check`.
- No Pulse schedule.
- No module maturity matrix unless it helps.
- Manual tests only for behavior automation cannot cover.

Avoid: full documentation asset tracking, scheduled reports, multi-repository rollups.

### Standard

Use for small teams and maintained products.

- Minimal profile.
- Module cards and generated `PROJECT.md`.
- Documentation impact and `aeng docs check`.
- Technical notes for durable architecture.
- Manual-test issue linkage.
- Weekly Pulse if several plans are active.
- Expiring known-failure allowlists.

### Multi-team

Use for multiple modules, repositories, or long-lived programs.

- Standard profile.
- Explicit owners and single-writer artifacts.
- Isolated worktrees for parallel agents.
- Stable date+slug decision IDs.
- Retained Pulse baselines.
- Cross-repository links with an explicit system of record.
- Separate mechanism repositories from product repositories.

Cautions:

- The current kit does not provide a hosted multi-repo database.
- Cross-repository guards cannot be validated by a single repository's `aeng check`.
- Do not create global decision-number allocators unless an external compliance system requires them.

### Regulated or security-critical

The kit can support evidence discipline, but it is not sufficient on its own.

Add:

- controlled system of record;
- access control and approval workflow;
- signed artifacts and immutable audit logs;
- requirement-to-test traceability;
- independent review and release authorization;
- retention and legal-hold policy;
- secret scanning and supply-chain controls.

Do not treat Markdown plus CI as a compliance certification.

## Project types where the full system is usually excessive

- Throwaway scripts and demos.
- One-person projects with one small active task.
- Early research where the design changes daily.
- Design-only explorations with no code contract.
- Projects where the team already has a mature external system and the repository would become a duplicate.

Use a time-boxed investigation or a single Plan instead.

## Project types where it pays off

- Agent-heavy development with frequent fresh sessions.
- Long-lived products with many small changes.
- UI plus backend plus CLI or automation surfaces.
- Teams that repeatedly re-propose rejected designs.
- Projects where manual verification is easy to forget.
- Public SDKs or APIs with compatibility constraints.
- Multi-agent or parallel-session development.

## Adoption rule

Start with the root contract and one real task. Add module cards, docs checks, Pulse, and issue automation only after the basic lifecycle proves useful.

Governance overhead should make completion more truthful, not merely create more files.
