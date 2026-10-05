# Benchmark

This directory documents the reproducible benchmark harness used to evaluate
Flatplanet Orchestrator execution profiles.

The benchmark has two separate goals:

1. measure orchestration and model usage;
2. compare final implementation quality against the same requirements.

Do not mix these two measurements. Lower token usage does not imply higher
quality, and a larger finding count during implementation does not imply a worse
final snapshot.

## Files

- [HARNESS.md](HARNESS.md) — benchmark procedure and evidence rules
- [RUN-TEMPLATE.md](RUN-TEMPLATE.md) — manifest to copy for each benchmark run
- [Current comparison](../docs/BENCHMARK-CASE-STUDY.md) — Old, Cheap, Balanced and GPT-6 Luna usage, with quality-evidence boundaries
- [Historical two-run study](../docs/BENCHMARK-CASE-STUDY-OLD-CHEAP.md) — preserved Old/Cheap article and earlier review

## Published run entries

| Run dates | Variant | Entry | Evidence status |
|---|---|---|---|
| 2026-09-25 to 2026-09-26 | GPT-6 Luna / max (`luna6`) | [GR-UX-01A run](runs/2026-09-25-GR-UX-01-luna6.md) | Corrected session export recorded; implementation closure reported; acceptance PARTIAL; comparative review PENDING |

The Luna 6 entry was added on 2026-10-05 from maintainer-supplied reports. Its
186,866,991 tokens belong to root session
`01a0d9c0-89b9-7220-a0f9-73998acb7704`. The routing canary and the unrelated
`daycomplet` export are excluded. The final implementation was uncommitted;
its final source-snapshot identifier has not been supplied.

The comparison order remains **Old orchestration → Cheap profile → Balanced
profile → GPT-6 Luna**. Do not insert zeros for Luna 6 into final comparative
finding counts: its own closure report is a different evidence layer.

## Core benchmark rule

Every implementation run should start from the same frozen application baseline
and source requirements whenever the experiment is intended to compare worker
models or orchestration profiles.

Record at minimum:

- application repository and starting commit SHA
- benchmark branch name
- installed Flatplanet Orchestrator commit and `SKILL.md` hash
- Codex CLI version
- root, worker, tester, and reviewer model + reasoning effort
- session/thread identifiers
- wall time
- per-model and per-thread token usage
- plan allowance delta when available
- final implementation commit or reproducible snapshot identifier
- tests actually executed against the final state
- findings still present in the final snapshot
- acceptance criteria still not verified

## Current profile vocabulary

| Profile | Worker | Reasoning |
|---|---|---|
| `cheap` | GPT-5.6 Luna | max |
| `luna6` | GPT-6 Luna | max |
| `balanced` | GPT-5.6 Terra | high |
| `strong` | GPT-5.6 Sol | high |
| `max` | GPT-6 Astra | medium |

The harness also supports explicit worker/model overrides. When an override is
used, record the exact model ID instead of treating the run as evidence about a
different named profile.

## Recommended experiment shape

```text
frozen application baseline
        |
        +--> run A --> final snapshot A --+
        +--> run B --> final snapshot B --+--> independent quality comparison
        +--> run C --> final snapshot C --+
        +--> run D --> final snapshot D --+
```

Implementation runs and the final comparative review should be separate
sessions. Comparative reviewers should not receive token usage, profile labels,
worker success narratives, or previous quality rankings before producing their
first-pass findings.

See [HARNESS.md](HARNESS.md) for the full procedure.
