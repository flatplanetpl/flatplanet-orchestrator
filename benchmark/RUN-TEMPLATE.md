# Benchmark Run Manifest

Copy this file for each benchmark run. Suggested name:

```text
benchmark/runs/YYYY-MM-DD-<task>-<variant>.md
```

Do not overwrite previous manifests.

## Identity

- Date:
- Task/ticket:
- Variant/display name:
- Benchmark branch:
- Application repository:
- Starting application SHA:
- Final application SHA or snapshot:
- Source requirement files:

## Orchestrator

- Flatplanet Orchestrator source commit:
- Installed `SKILL.md` SHA-256:
- Install/update method:
- Local skill modifications: yes / no
- Codex CLI version:
- ChatGPT plan:

## Model topology

| Role | Requested model / effort | Exported model / effort | Full session/thread ID | Independent metadata evidence or NOT VERIFIED |
|---|---|---|---|---|
| Root | | | | |
| Worker | | | | |
| Tester | | | | |
| Reviewer | | | | |
| Re-reviewer | | | | |

Requested worker configuration:

```text

```

Effective worker configuration verified from (or NOT VERIFIED):

```text

```

Record model/effort changes within each thread. A helper summary label is not
proof that every response used the same settings.

## Clean-start evidence

```text
git branch --show-current
git rev-parse HEAD
git status --short
```

Output:

```text

```

## Run prompt

Record the exact implementation prompt or a stable file/reference containing it.

```text

```

## Usage

- Full root session ID:
- Expected and exported cwd:
- Export generation timestamp / exact command / exit status:
- Export file SHA-256 (Markdown and JSON, if available):
- Usage helper repository / revision:
- Exact local helper SHA-256 / local modifications:
- CLI versions observed in relevant segments:
- Elapsed session span:
- Active execution time: NOT ESTABLISHED / value with measurement method
- Interruptions, idle periods, resumes and post-implementation turns:
- Threads counted / exclusion policy:
- Input cache hit rate and weighted calculation:
- Primary allowance observation:
- Secondary allowance observation:
- Window duration / reset / account-specific interpretation evidence:
- Other account usage:
- Allowance attribution: NOT ISOLATED / evidence supporting isolation
- Monetary cost: NOT ESTABLISHED / explicit applicable pricing basis and limitations

### Measurement validation

Follow the [usage validation gate](HARNESS.md#usage-validation-gate). When copying
this manifest into `benchmark/runs/`, change that link to
`../HARNESS.md#usage-validation-gate`.

Leave missing evidence as NOT RECORDED or NOT AUDITED, not zero or PASS.

| Layer | Status | Evidence / method / remaining limitations |
|---|---|---|
| Export retained and correct run selected | REPORTED / NOT RECORDED | |
| Export arithmetic | NOT CHECKED / ARITHMETIC CHECKED / DISCREPANCY | |
| Exact local helper provenance | NOT RECORDED / RECORDED | |
| Full thread membership and log completeness | NOT AUDITED / result | |
| Duplicate files or overlapping resumed history | NOT AUDITED / result | |
| Delta versus cumulative-counter reconciliation | NOT AUDITED / result | |
| Per-event model/effort attribution | NOT AUDITED / result | |
| Overall raw-log audit | PENDING / RAW LOG AUDITED / UNRESOLVED DISCREPANCIES | |

- Private raw-log inventory/hashes and full parent/root IDs:
- Original versus reconciled totals, if an audit was performed:
- Exclusions and evidence justifying each deduplication:
- Audit timestamp, method, tool revision and retained notes:
- Changes from prior published counts (do not overwrite the original):

Do not publish raw rollouts or secrets in this repository. Share only the scoped,
reviewed evidence needed for the benchmark.

| Thread | Role | Model / effort | Responses | Uncached in | Cached in | Output | Reasoning | Total | Duration |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | | | |

| Model | Threads | Responses | Uncached in | Cached in | Output | Reasoning | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | |

`Responses` and `Duration` retain the export's definitions; document them.
Reasoning is not added a second time to output/total, and cached input is not
added a second time to input. Arithmetic consistency alone does not certify
completeness, uniqueness, attribution, active time or billing.

Raw usage report:

```text

```

## Findings during implementation

These findings are process evidence only. Do not use these counts as the final
cross-profile quality score.

| Severity | Found | Fixed | Remaining known |
|---|---:|---:|---:|
| Critical | | | |
| High | | | |
| Medium | | | |
| Low | | | |

Summary:

```text

```

## Final-state verification

List only checks actually executed against the final state.

| Check | Result | Evidence |
|---|---|---|
| Typecheck | | |
| Lint | | |
| Frontend tests | | |
| Frontend production build | | |
| API build | | |
| Backend tests | | |
| Fresh migration/bootstrap | | |
| Forward migration | | |
| Concurrency/retry/rollback | | |
| Browser E2E | | |
| Manual acceptance | | |

## Acceptance criteria

| Requirement | Status | Evidence |
|---|---|---|
| | PASS / PARTIAL / FAIL / NOT VERIFIED | |

## Final implementation status

- Critical findings still known:
- High findings still known:
- Medium findings still known:
- Low findings still known:
- Merge blockers:
- Browser/manual acceptance missing:
- Production migration/deployment verified: yes / no
- Exact-SHA CI verified: yes / no

## Comparative-review fields

Fill these only after the independent final-snapshot comparison.

- Frozen comparative-review SHA:
- Neutral snapshot ID:
- Independent reviewer model/effort:
- Critical findings:
- High findings:
- Medium findings:
- Low findings:
- Merge-ready according to comparative review: yes / no

## Limitations / contamination

Record anything that weakens causal interpretation:

- different skill version
- different CLI version
- inherited implementation
- previous benchmark code visible to worker
- reviewer not fully blinded
- different test infrastructure
- different requirements revision
- account-wide concurrent usage
- unresolved parser provenance, event overlap or incomplete log capture
- unmeasured interruption/idle time
- missing tool/infrastructure
- other:

## Notes

