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
- [Case study](../docs/BENCHMARK-CASE-STUDY.md) — historical GR-UX-01 results

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
