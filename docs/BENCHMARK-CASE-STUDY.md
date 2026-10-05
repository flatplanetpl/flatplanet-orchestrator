# GR-UX-01 benchmark comparison

**Evidence update:** 2026-10-05  
**Order:** Old orchestration → Cheap profile → Balanced profile → GPT-6 Luna.

**Quick navigation:** [Evidence](#evidence-scope) · [Usage](#usage-comparison) · [Bars](#visual-comparison) · [Quality](#final-snapshot-quality) · [Luna 6](#gpt-6-luna-process-results) · [Limitations](#interpretation-limits) · [Historical study](BENCHMARK-CASE-STUDY-OLD-CHEAP.md) · [Harness](../benchmark/README.md) · [README](../README.md)

## Evidence scope

This page brings together the maintainer-supplied GR-UX-01A usage reports and review results. It adds the **GPT-6 Luna / max** run of 2026-09-25–26. No application code, build, test, or comparative review was rerun while preparing this documentation.

There are two different evidence layers:

1. **Session usage:** four supplied implementation-session exports, with different orchestration histories and verification workloads.
2. **Final-snapshot quality:** a later independent review of Old, Cheap and Balanced. Luna 6 currently has only its own implementation/closure report, not the same comparative review.

The original two-run article is preserved verbatim as the [historical Old/Cheap case study](BENCHMARK-CASE-STUDY-OLD-CHEAP.md). Its earlier quality counts are historical and were superseded by the subsequent three-snapshot review below. Review rounds are not additive.

The [Luna 6 run entry](../benchmark/runs/2026-09-25-GR-UX-01-luna6.md) contains the exact transcribed usage counts, source-attachment hash, reproducibility fields, process findings, acceptance matrix and evidence limitations.

## Usage comparison

All counts below come from the supplied exports. `M` means one million tokens. Model identifiers are those recorded for these runs, not a statement about current product availability or pricing.

| Metric | Old orchestration | Cheap profile | Balanced profile | GPT-6 Luna |
|---|---:|---:|---:|---:|
| Session prefix | `01a0c184` | `01a0c206` | `01a0c2d1` | `01a0d9c0` |
| Codex CLI in export | 0.155.1 | 0.155.1 | 0.155.1 | 0.157.0 |
| Threads counted | 7 | 3 | 4 | 4 |
| Root Astra responses | 455 | 21 | 37 | 105 |
| Root Astra cached input | 58,756,480 | 951,424 | 2,042,752 | 7,254,400 |
| Root Astra total tokens | 59,466,160 | 1,047,467 | 2,120,143 | 7,398,270 |
| All Astra tokens (root + reviewer) | 60,768,574 | 1,657,251 | 3,556,097 | 11,842,658 |
| GPT-5.6 Luna tokens, all roles | 89,580,751 | 117,179,887 | 41,027,409 | 44,671,233 |
| GPT-5.6 Terra tokens | — | — | 24,360,298 | — |
| GPT-6 Luna tokens | — | — | — | 130,353,100 |
| All responses | 1,124 | 806 | 530 | 1,320 |
| **All-model total tokens** | **150,349,325** | **118,837,138** | **68,943,804** | **186,866,991** |
| Astra share of total tokens | 40.42% | 1.39% | 5.16% | 6.34% |
| Input cache-hit rate | 98.2% | 98.2% | 97.0% | 97.3% |
| Reported elapsed session span | 106m56s | 151m42s | 172m00s | 1158m06s* |

`—` means the model has no row in that supplied export. Total tokens include cached input; they do not measure unique source size. Reported reasoning counts are not added again to the exported totals.

*Luna 6's span is 19h18m06s and includes an unquantified interruption after a 401 error and subsequent continuation. Active coding time has not been established. Do not rank model speed using this elapsed span, or sum thread durations as wall time.

The original usage exports for Old, Cheap and Balanced were supplied in the benchmark discussion; the Old/Cheap values are also preserved in the historical study. Balanced's export recorded 2,120,143 root Astra + 1,435,954 reviewer Astra + 24,360,298 Terra + 41,027,409 Luna tokens. The Luna 6 export is reproduced in the linked run entry. Raw rollout logs were not audited for this publication.

### Arithmetic changes, not cost estimates

| Luna 6 compared with | Root Astra token change | All-model token change |
|---|---:|---:|
| Old orchestration | -87.6% | +24.3% |
| Cheap profile | +606.3% | +57.2% |
| Balanced profile | +249.0% | +171.0% (2.71× total) |

These ratios do not isolate worker capability or monetary cost. In particular, the Cheap run has no separate tester thread, whereas the Luna 6 run includes 44,671,233 GPT-5.6 Luna tester tokens. Its GPT-6 Luna worker used 130,353,100 tokens versus Cheap's 117,179,887 worker tokens: +11.2%, not the whole-workflow +57.2%.

### Plan-level allowance

All runs were reported on **ChatGPT Pro**. The maintainer identified the `primary` field as the weekly window for this account. This mapping is recorded as account-specific context, not a universal meaning of `primary`.

| Observation | Old orchestration | Cheap profile | Balanced profile | GPT-6 Luna |
|---|---|---|---|---|
| Primary percentage in export | 19% → 23% | 23% → 23% | 24% → 25% | 30% → 46% |
| Interpretation | +4 pp observed | 0 pp visible, not proof of zero usage | +1 pp observed | **Account delta only; NOT ISOLATED** |
| Secondary field | Unavailable | Unavailable | Unavailable | Unavailable |

An unrelated `daycomplet` session on the same account was separately reported with 38% → 46%. The supplied records do not establish a complete chronology. Do not charge Luna 6 with all 16 points, subtract 8 points mechanically, or present an exact percentage saving. Displayed values can also be rounded or delayed. The unrelated session's token totals are excluded completely.

## Visual comparison

Root Astra tokens relative to Old = 100%. Bars are rounded to 30 cells; exact ratios are shown alongside. These are **token bars, not quality scores**.

```text
ROOT ASTRA TOKENS — RELATIVE TO OLD
Old       59.47M |##############################| 100.0%
Cheap      1.05M |#.............................|   1.8%
Balanced   2.12M |#.............................|   3.6%
Luna 6     7.40M |####..........................|  12.4%
```

Low root activity does not guarantee low whole-workflow usage: Luna 6 records the largest total token count in this set, despite using far fewer root Astra tokens than Old. The varying verification workloads and model mixes must remain visible.

## Final-snapshot quality

The later three-branch review supplied by the maintainer evaluated these exact commits using separate GPT-6 Astra / medium reviewer contexts, neutral snapshot labels, baseline builds/tests and equivalent adversarial probes. It excluded unsupported hypotheses from confirmed counts. The following is a transcription of that review, not a new review or a model-quality score.

| Field | Old orchestration | Cheap profile | Balanced profile | GPT-6 Luna |
|---|---|---|---|---|
| Branch | `old-skill-GR-UX-01` | `new-skill-GR-UX-01` | `ballanced-skill-GR-UX-01` | `gpt6-luna-skill-GR-UX-01` |
| Reviewed final commit | `97366ca586f86f354e08ab5ffc7852e0c83359b6` | `58386ae2a9d6cfd0ce0e773d5fa7e026e5dcc5fb` | `3df2af045dc0dc30fbabc880e78ebc3b40d3faf6` | **Not supplied; final work was uncommitted** |
| Critical | 0 | 0 | 0 | NOT EVALUATED |
| High | 1 | 6 | 3 | NOT EVALUATED |
| Medium | 4 | 5 | 3 | NOT EVALUATED |
| Low | 2 | 2 | 2 | NOT EVALUATED |
| Comparative merge assessment | Not ready | Not ready | Not ready | PENDING; own acceptance is PARTIAL |

`ballanced` is the actual reported branch spelling. These findings were present in the frozen snapshots, not defects already corrected during their implementation runs.

That review selected **Old orchestration as the strongest starting point**, with material blockers in all three. Old preserved operational pricing/currency and pending edits better, but rejected signed source lines in its frontend and retained other defects. Balanced improved several editor, recovery and mapping behaviors relative to Cheap, yet retained operational unit-price/currency defects and navigation loss. Passing baseline tests did not eliminate those findings.

The review also found that 22 of 32 source/test/migration files changed by Cheap were byte-identical in Balanced, including generated files and main mutation tests. Git ancestry alone did not establish how that content was introduced. This restricts causal claims about independent implementations and worker-model capability.

**Luna 6 is deliberately not ranked.** Its own reviewer closed known findings, but an equivalent independent comparison of its final code has not been supplied. The earlier Old/Cheap finding counts in the archived study remain historical evidence, not competing current totals.

## GPT-6 Luna process results

The supplied implementation report separates **7 High and 6 Medium failure modes**, all reported closed after corrections by the same Luna 6 worker. No Critical defect was established; a complete Low count was not supplied. Four review passes included new failures found during re-review, followed by a final 4/4 reproduction pass.

| Evidence | Reported result | Boundary |
|---|---|---|
| Final components | 93/93 PASS | Worker and independent tester; no full application browser acceptance |
| Workspace component subset | 31/31 PASS | Included in the component coverage, not an extra disjoint total |
| Final independent reproductions | 4/4 PASS | Closure of tested findings, not proof of no remaining defects |
| Root synthetic DB tests | 49/49 PASS | 25 rules + 8 forward + 10 mutations + 6 consumers; performed by root |
| Fresh migration / bootstrap | PASS | Synthetic disposable database only |
| Typecheck / lint / npm test / frontend build | Reported PASS after final correction | Not rerun for this documentation |
| Earlier broad backend suite | 787 passed, 342 skipped, 1 failure | Not rerun as a whole; not a final global PASS |
| Independent tester DB execution | Blocked | Later root checks do not replace its provenance |
| Full acceptance | **PARTIAL** | Browser/mobile/keyboard, cross-tab, <=60-second measurement, exact-SHA CI and owner approval missing |

The broad-suite failure was `assistant_probe_limit_wait_timeout` in an assistant-coordinator test; its cause was not established. It must remain visible instead of being reclassified as an environment-only issue.

The implementation report initially could not verify effective child identity through its tools. The separately supplied corrected usage export records the requested model/effort topology. This is additional log-derived evidence, not retroactive independent certification of runtime identity.

## Interpretation limits

- **Different workflow, not a controlled model-only experiment.** Skills, CLI versions, tester presence, reviewer effort and correction history changed. Older runs used CLI 0.155.1; Luna 6 used 0.157.0 and the pinned orchestrator commit documented in its run entry.
- **No active-time ranking.** Luna 6's 401 interruption and idle span were not measured separately.
- **No isolated Luna 6 allowance charge.** Other account usage was documented; no token-to-weekly conversion is inferred.
- **No four-way final-code verdict yet.** Luna 6's final snapshot identifier and equal-scope comparative review remain missing.
- **No test-count quality score.** Suites cover different scopes; baseline passing tests coexisted with independently reproduced defects in the three earlier snapshots.
- **No same-quality-at-lower-cost claim.** Accepted-solution cost would include implementation, review, correction, regression and final acceptance at the same evidence threshold.

The defensible observation is narrower: orchestration changes reduced recorded root Astra activity relative to Old, while whole-workflow token totals and remaining implementation quality varied. The [Luna 6 entry](../benchmark/runs/2026-09-25-GR-UX-01-luna6.md) adds another measured workflow, not a new quality winner.

## Source map and preserved history

| Evidence | Scope |
|---|---|
| [Historical Old/Cheap case study](BENCHMARK-CASE-STUDY-OLD-CHEAP.md) | Original two-run usage, early quality review, and prior interpretation; preserved verbatim |
| Maintainer-supplied Balanced usage export, session `01a0c2d1` | Four-thread model totals transcribed above |
| Maintainer-supplied three-snapshot comparison, beginning “A. Executive summary.” | Later Old/Cheap/Balanced final findings and frozen SHAs above; original probes retained outside this repo, not rerun here |
| [GPT-6 Luna run entry](../benchmark/runs/2026-09-25-GR-UX-01-luna6.md) | Implementation report, attachment fingerprint, corrected session export, setup fields and limitations |
| [Benchmark harness](../benchmark/HARNESS.md) | Procedure for future comparable runs; not evidence that every historical run satisfied it |

Unknown fields remain unknown. This publication adds documentation only; it does not commit the application implementation, certify a final source snapshot, or perform deployment/acceptance.
