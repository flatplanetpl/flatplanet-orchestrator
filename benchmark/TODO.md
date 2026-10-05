# Benchmark evidence and tooling backlog

**Open work carried forward from 2026-10-05.** Relocated from the project README without closing any item. Unchecked items are not completed features, verified results, or release commitments.

[Project README](../README.md) · [Benchmark index](README.md) · [Harness](HARNESS.md) · [Four-run comparison](../docs/BENCHMARK-CASE-STUDY.md)

## Priority 1 — validate the existing benchmark evidence

- [ ] **Freeze the final Luna 6 implementation.** Preserve tracked changes and relevant untracked source/test files, record a commit or source-tree/archive checksum, and attach that identity to the [run entry](runs/2026-09-25-GR-UX-01-luna6.md). The baseline HEAD is not the completed implementation.
- [ ] **Audit usage against the exact local helper and raw logs.** Reconcile full thread IDs, run boundaries, resumed history, counters and model/effort attribution under the [usage validation gate](HARNESS.md#usage-validation-gate). Keep raw logs private. Retain reported counts unless a counting defect is demonstrated; arithmetic consistency alone does not close this item.
- [ ] **Complete the independent four-way quality comparison.** Evaluate frozen snapshots in the order **Old → Cheap → Balanced → Luna 6**, using specification-first reviews and equivalent executable probes. Count defects remaining in each final snapshot, not findings already fixed during implementation. Publish the evidence and merge blockers before ranking Luna 6.

## Priority 2 — make future runs repeatable

- [ ] **Retain independent probes as regression tests.** Preserve reviewer-authored scenarios and their requirement-derived expectations in the benchmark application or an appropriate test harness. Reapply equivalent scenarios across candidates; do not turn ticket-specific assertions into mandatory global skill rules.
- [ ] **Automate the manual harness steps with tested local scripts.** Add run preflight, reproducible snapshot capture, pinned-root usage export and manifest validation. Include checks for effective model settings and isolated test-infrastructure access; test resumed/overlapping log handling before relying on automated accounting. Keep private source, credentials and raw rollouts out of published artifacts.
- [ ] **Run controlled follow-up comparisons, including GPT-6 Sol.** Freeze the same application baseline, requirements, skill, CLI and verification policy; keep root/tester/reviewer settings constant when comparing workers. Repeat reference configurations and record variability. Compare effort through the same acceptance threshold, including corrections and re-review; keep token totals, active time and account allowance separate.

## Benchmark application acceptance — not orchestrator features

GR-UX-01A still needs independent DB-layer verification, investigation and rerun of the unresolved broad backend failure, browser/mobile/keyboard and cross-tab checks, the <=60-second measurement, exact-SHA CI and owner acceptance. Representative historical-data migration also remains unverified. These are application acceptance gaps documented in the [Luna 6 report](runs/2026-09-25-GR-UX-01-luna6.md), not missing orchestrator features or claims that existing skill policies are absent. Existing-database operations, deployment and live-system checks require separate authorization.

## What to record in future comparisons

Use [HARNESS.md](HARNESS.md) for the procedure and [RUN-TEMPLATE.md](RUN-TEMPLATE.md) for per-run evidence. Track at least:

- root model responses, cached input and total tokens;
- worker totals, root share and whole-workflow usage;
- elapsed session span and separately established active time, if available;
- primary/secondary allowance observations and attribution limits;
- exact application/skill SHAs, full session/thread IDs, local helper hash, export hashes and raw-log audit status;
- final-snapshot quality findings and unverified acceptance criteria.

Move execution away from the expensive root without weakening the evidence required for final implementation quality. Token totals, actual cost, account allowance and product acceptance are different measurements.

**Completion rule:** close an item only when its linked artifact, test result or audit report supports closure. Preserve earlier evidence and update the run/comparison status explicitly; zero known findings is not proof of correctness.
