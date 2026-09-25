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

| Role | Model | Reasoning | Session/thread ID |
|---|---|---|---|
| Root | | | |
| Worker | | | |
| Tester | | | |
| Reviewer | | | |
| Re-reviewer | | | |

Requested worker configuration:

```text

```

Effective worker configuration verified from:

```text

```

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

- Session ID:
- Wall time:
- Threads:
- Input cache hit rate:
- Primary allowance:
- Secondary allowance:
- Interpretation of plan window:

| Thread | Role | Model / effort | Responses | Uncached in | Cached in | Output | Reasoning | Total | Duration |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | | | |

| Model | Threads | Responses | Uncached in | Cached in | Output | Reasoning | Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | |

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
- missing tool/infrastructure
- other:

## Notes

