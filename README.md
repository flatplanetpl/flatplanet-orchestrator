# Flatplanet Orchestrator

Cost-efficient multi-agent orchestration skill for OpenAI Codex.

The goal is simple:

- keep the expensive root model focused on planning, architecture and final integration,
- delegate long-running execution to cheaper worker models,
- avoid short `wait_agent` polling loops,
- avoid duplicate work between the root and subagents,
- choose the worker model per task with a simple execution profile.


## What you can gain

In a real before/after run on the same non-trivial implementation task, changing from an actively polling Astra orchestrator to Flatplanet Orchestrator produced:

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Root Astra responses | 455 | 21 | **-95.4%** |
| Root Astra tokens | 59.47M | 1.05M | **-98.2%** |
| All Astra tokens | 60.77M | 1.66M | **-97.3%** |
| Astra share of all tokens | 40.4% | 1.4% | **-39.0 pp** |
| Total tokens | 150.35M | 118.84M | **-21.0%** |
| Worker tokens | 89.58M | 117.18M | **+30.8%** |
| Visible primary allowance delta | +4 pp | 0 pp visible | see caveats |

The important shift is not merely "fewer tokens." It is **moving execution away from the expensive root model and into the worker model**, while keeping Astra for planning and review.


### At a glance

```text
ROOT ASTRA RESPONSES
Before  455 |██████████████████████████████████████████████████| 100%
After    21 |██                                                |   4.6%

ROOT ASTRA TOKENS
Before 59.47M |██████████████████████████████████████████████████| 100%
After   1.05M |█                                                 |   1.8%

ALL ASTRA TOKENS
Before 60.77M |██████████████████████████████████████████████████| 100%
After   1.66M |█                                                 |   2.7%

ASTRA SHARE OF ALL TOKENS
Before 40.4% |████████████████████                              |
After   1.4% |█                                                 |

TOTAL TOKENS
Before 150.35M |██████████████████████████████████████████████████| 100%
After  118.84M |███████████████████████████████████████           |  79%

WORK SHIFT
Before | Astra ████████████████████ 40.4% | Workers ██████████████████████████████ 59.6% |
After  | Astra █ 1.4%                  | Workers █████████████████████████████████████████████████ 98.6% |
```

The goal is not to eliminate worker compute. The goal is to make **expensive orchestration sparse** and let cheaper workers do the long-running execution.

The optimized run took longer wall-clock time (151m42s vs 106m56s), but the Astra root almost stopped consuming context while the worker was active.

Quality was not ignored: the independent Astra reviewer found **2 high + 4 medium** issues; all were fixed, with broad backend/frontend verification afterward.

> These numbers are one measured case study, not a guaranteed savings ratio. Codex allowance accounting is not publicly reducible to a simple token formula, and the secondary/weekly counter was unavailable in this run.

See **[Benchmark case study](docs/BENCHMARK-CASE-STUDY.md)** for the complete methodology, raw numbers, quality findings, tests, and limitations.

## Execution profiles

| Profile | Worker | Reasoning | Typical use |
|---|---|---|---|
| `cheap` | GPT-5.6 Luna | max | small, bounded, routine changes |
| `balanced` | GPT-5.6 Terra | high | default production development |
| `strong` | GPT-5.6 Sol | high | difficult debugging/refactors |
| `max` | GPT-6 Astra | medium | exceptional, high-risk tasks |

Fixed roles by default:

- root: GPT-6 Astra / medium
- explorer: GPT-5.6 Luna / max
- researcher: GPT-5.6 Luna / max
- tester: GPT-5.6 Luna / max
- reviewer: GPT-6 Astra / low

## Install in a repository

From the target repository:

```bash
mkdir -p .agents/skills
git clone https://github.com/flatplanetpl/flatplanet-orchestrator.git /tmp/flatplanet-orchestrator
cp -R /tmp/flatplanet-orchestrator/.agents/skills/flatplanet-orchestrator .agents/skills/
rm -rf /tmp/flatplanet-orchestrator
```

Then start a new Codex session from the repository root.

## Usage

Default profile (`balanced`):

```text
$flatplanet-orchestrator implement ticket GR-UX-01A
```

Cheap:

```text
$flatplanet-orchestrator profile=cheap fix the form validation
```

Strong:

```text
$flatplanet-orchestrator profile=strong redesign the data synchronization
```

Explicit worker override:

```text
$flatplanet-orchestrator worker=terra effort=high implement the ticket
```

## Why this exists

A root orchestrator can burn a large amount of usage by repeatedly waking while subagents are still working. This skill therefore enforces:

- explicit long `wait_agent(timeout_ms=...)` calls,
- no heartbeat polling,
- no progress-report chatter from workers,
- no root inspection of partial worker-owned diffs,
- batching correction passes,
- independent testing/review only when it materially improves confidence.

The preferred flow is:

```text
Astra root
  -> plan / decompose
  -> spawn worker(s)
  -> LONG WAIT
  -> integrate completed result
  -> optional tester
  -> optional Astra reviewer
  -> one correction pass
  -> final verification
```

## Benchmarking

When comparing orchestration strategies, track at least:

- root model responses,
- root cached input,
- root total tokens,
- worker total tokens,
- root share of total tokens,
- task wall time,
- Codex primary/secondary allowance delta when available.

A healthy run should move most execution tokens away from the expensive root and into the selected worker model.
