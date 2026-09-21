# Benchmark Case Study: Reducing Astra Orchestration Usage

## Summary

This case study compares two executions of the same non-trivial Codex implementation task:

```text
implement the first executable file from:
docs/plans/goods-receipts/GR-UX-01-GOODS-RECEIPTS-REDESIGN.md
```

The target work was the GR-UX-01A goods-receipt/KSeF draft flow in a production application repository. It included backend logic, persistence/migrations, frontend editing/autosave behavior, tests, and review.

Both runs used Codex CLI `0.155.1`.

The purpose was to test whether an orchestrator could preserve high-quality planning/review while dramatically reducing repeated GPT-6 Astra root invocations during long-running worker execution.

## The problem

The original orchestration pattern repeatedly woke the Astra root while workers were still running.

Typical behavior looked like:

```text
spawn worker
wait
wake Astra
worker still running
inspect/search/diff
wait
wake Astra
worker still running
...
```

Each wake-up could reprocess a very large cached root context. Even with a high prompt-cache hit rate, repeated Astra turns accumulated substantial usage.

Flatplanet Orchestrator changes the control flow to:

```text
Astra root
  -> understand / plan
  -> spawn worker
  -> LONG wait_agent(timeout_ms=...)
  -> process completed result
  -> optional independent review
  -> batch corrections
  -> final verification
```

The root is explicitly told not to poll, inspect partial worker-owned changes, or invent work merely to stay active.

## Benchmark environment

- Codex CLI: `0.155.1`
- Same repository and feature area
- Root model: GPT-6 Astra / medium
- Before worker strategy: Luna subagents with an actively polling root
- After worker strategy: one long-running GPT-5.6 Luna / max worker plus GPT-6 Astra / low reviewer
- Token accounting source: `scripts/token_usage.py --latest`
- Prompt cache hit rate:
  - before: 98.2%
  - after: 98.2%

The runs were not laboratory-identical. The optimized run took longer and used a different orchestration topology, so the result should be treated as an engineering case study rather than a controlled scientific benchmark.

## Raw results

### Before: original orchestration

```text
wall time: 106m56s
threads: 7

root Astra / medium:
  responses:      455
  uncached input: 648,750
  cached input:   58,756,480
  output:         60,930
  total:          59,466,160

all Astra:
  responses:      474
  total:          60,768,574

all Luna:
  responses:      650
  total:          89,580,751

all models:
  responses:      1,124
  total:          150,349,325

primary allowance:
  19.0% -> 23.0%  (+4 percentage points)

secondary allowance:
  unavailable
```

### After: Flatplanet Orchestrator

```text
wall time: 151m42s
threads: 3

root Astra / medium:
  responses:      21
  uncached input: 93,727
  cached input:   951,424
  output:         2,316
  total:          1,047,467

Luna worker / max:
  responses:      774
  total:          117,179,887

Astra reviewer / low:
  responses:      11
  total:          609,784

all Astra:
  responses:      32
  total:          1,657,251

all models:
  responses:      806
  total:          118,837,138

primary allowance:
  23.0% -> 23.0%  (no visible increase)

secondary allowance:
  unavailable
```

## Before vs after

| Metric | Before | After | Change |
|---|---:|---:|---:|
| Wall time | 106m56s | 151m42s | +41.9% |
| Root Astra responses | 455 | 21 | **-95.4%** |
| Root Astra cached input | 58.76M | 0.95M | **-98.4%** |
| Root Astra total | 59.47M | 1.05M | **-98.2%** |
| All Astra total | 60.77M | 1.66M | **-97.3%** |
| Luna total | 89.58M | 117.18M | +30.8% |
| All-model total | 150.35M | 118.84M | **-21.0%** |
| Astra share of total tokens | 40.4% | 1.4% | **-39.0 pp** |
| Visible primary allowance delta | +4 pp | 0 pp visible | not directly convertible to weekly usage |

The key result is the collapse in expensive root activity. The optimized run intentionally allowed the cheaper worker to do more work, yet overall tokens still fell by about 21%.


## Visual comparison

### Expensive root activity

```text
Root Astra responses
Before  455  ██████████████████████████████████████████████████  100.0%
After    21  ██                                                    4.6%
             └──────────────────────────────────────────────────┘
             95.4% reduction
```

```text
Root Astra total tokens
Before  59.47M  ██████████████████████████████████████████████████  100.0%
After    1.05M  █                                                     1.8%
                └──────────────────────────────────────────────────┘
                98.2% reduction
```

```text
Root Astra cached input
Before  58.76M  ██████████████████████████████████████████████████  100.0%
After    0.95M  █                                                     1.6%
                └──────────────────────────────────────────────────┘
                98.4% reduction
```

### Where the tokens went

```text
BEFORE

Astra   40.4%  ████████████████████
Workers 59.6%  ██████████████████████████████


AFTER

Astra    1.4%  █
Workers 98.6%  █████████████████████████████████████████████████
```

### Total compute

```text
All-model tokens
Before 150.35M  ██████████████████████████████████████████████████  100%
After  118.84M  ███████████████████████████████████████             79%

Despite the worker doing MORE work:
Luna before   89.58M  ██████████████████████████████████████
Luna after   117.18M  ██████████████████████████████████████████████
```

This is the core optimization:

```text
BEFORE
┌─────────────────────────────────────────────────────────────────┐
│ ASTRA ROOT                                                      │
│ plan -> wait -> wake -> inspect -> wait -> wake -> diff -> ... │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                       frequent expensive turns
                                │
                                ▼
                         Luna subagents


AFTER
┌────────────────────┐
│ ASTRA ROOT         │
│ plan + delegate    │
└─────────┬──────────┘
          │
          │ one long wait
          ▼
┌─────────────────────────────────────────────────────────────────┐
│ WORKER                                                          │
│ explore -> implement -> test -> fix -> verify                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │ completed result
                                ▼
                         ┌───────────────┐
                         │ ASTRA REVIEW  │
                         │ selective     │
                         └───────────────┘
```

### Root wake-up frequency

```text
Before: 4.26 root responses/min  ██████████████████████████████████████████████████
After : 0.15 root responses/min  ██

Approximate reduction: 96.5%
```

## Root wake-up behavior

The original root produced approximately:

```text
455 responses / 106m56s
≈ 4.26 root responses per minute
```

The optimized root produced:

```text
21 responses / 141m49s root-thread duration
≈ 0.15 root responses per minute
```

That is roughly a 96.5% reduction in root response frequency.

The optimized trace showed the desired pattern:

```text
Started worker
Waiting for agents
...long-running worker activity...
worker completes
root resumes
```

instead of repeated short `wait_agent` wake-ups.

## Quality results

Cost optimization is only useful if implementation quality remains acceptable.

The independent GPT-6 Astra / low reviewer reported:

- Critical: 0
- High: 2
- Medium: 4
- Low/minor: 0

All six reviewer findings were fixed.

### High findings

1. **Concurrent stock update risk**
   - A tracked stock record was loaded before acquiring the relevant lock.
   - Concurrent finalizations could lose stock updates.
   - Fixed; a concurrency regression test passed.

2. **Incorrect financial totals when warehouse quantity differed from KSeF quantity**
   - Warehouse quantity was multiplied by the KSeF source unit price.
   - This could change source financial totals when units differed.
   - Fixed; source amounts are now preserved independently from stock quantity.

### Medium findings

1. Autosave could restart after a network error or HTTP 409 and bypass explicit conflict resolution.
2. EUR receipts/lines were rendered using PLN formatting.
3. Manual receipts still modified `OperationalIssue`, contrary to the plan.
4. Public manual-receipt input exposed financial overrides that could create inconsistent totals.

All were fixed.

The root later identified and fixed two additional concerns:

- mapping keys containing `|`
- concurrent mapping creation

The sixth reviewer finding and the two root-review concerns did not receive another full independent reviewer pass.

## Verification performed

Reported passing verification included:

- API build: zero errors or warnings
- test-project build: passed, with two pre-existing CS8602 warnings in `AssistantChatAccessTests.cs`
- fresh isolated PostgreSQL migrations and bootstrap
- forward migrations: 4 tests
- database mutation / cross-tenant suite: 248 tests
- backend contracts: 13 tests
- final targeted backend checks: 9 tests covering receipts, KSeF, rollback, and concurrency
- frontend tests
- 64 component tests
- typecheck
- lint
- production build
- `git diff --check`

No outstanding failed test or build was reported.

## Verification still missing

The following were not fully verified:

- full unfiltered `dotnet test PubApp.slnx`
- full database-compatibility suite
- browser E2E
- exact committed-SHA CI verification
- complete broad-suite rerun after the final backend correction

Acceptance criteria still requiring manual/end-to-end validation included:

- previously mapped 1-5 line invoice completed within 60 seconds
- real desktop/mobile browser workflow
- keyboard interaction
- reopening a persisted draft
- owner/manager acceptance
- full A7 acceptance

The ticket therefore remained `IN_PROGRESS`.

## Interpretation

### What worked

The orchestration change successfully moved almost all execution activity away from the expensive Astra root:

```text
Before: Astra = 40.4% of all tokens
After:  Astra =  1.4% of all tokens
```

The worker consumed more tokens, but on the cheaper model. This is intentional.

The root's cached input dropped from 58.76M to 0.95M, strongly indicating that repeated context-heavy root wake-ups were the dominant inefficiency in the original workflow.

### What did not become free

The optimized run still used substantial worker compute:

```text
117.18M Luna tokens
```

Flatplanet Orchestrator is not a "use fewer tokens at all costs" strategy. It is primarily a **model-routing and orchestration-efficiency strategy**:

- expensive reasoning stays sparse,
- cheap execution can be extensive,
- expensive review is used selectively.

### Quality trade-off

The Luna worker did not produce a flawless first pass. Two high-severity and four medium-severity issues were discovered by independent review.

That result supports the profile model used by Flatplanet Orchestrator:

- `cheap` / Luna: suitable for bounded low-risk implementation
- `balanced` / Terra: preferred default for normal production work
- `strong` / Sol: complex debugging/refactors
- `max` / Astra: exceptional cases

For work involving concurrency, money, inventory integrity, migrations, authorization/security, or cross-tenant isolation, using at least `balanced` is prudent unless the user explicitly chooses `cheap`.

## Allowance caveats

The script reported:

```text
before: primary 19.0% -> 23.0%
after:  primary 23.0% -> 23.0%
```

This should NOT be interpreted as proof that the optimized run consumed exactly zero allowance.

Reasons:

- displayed percentages may be rounded
- usage reporting may lag
- Codex plan allowance is not publicly documented as a simple token-to-percent formula
- the secondary/weekly value was unavailable in both reports
- account-wide concurrent usage could affect the same counters

The most reliable conclusions from this case study are therefore the per-thread model/token measurements and the observed root wake-up reduction.

## Practical recommendation

For production use:

```text
$flatplanet-orchestrator profile=balanced <task>
```

is the recommended default.

Use `cheap` when the implementation is well bounded and low risk.

Use independent review for changes involving:

- concurrency
- data integrity
- financial calculations
- migrations
- security/authorization
- cross-tenant behavior
- complex business invariants

If a reviewer reports a high-severity finding, a final independent re-review after corrections is recommended.

## Bottom line

In this case study, Flatplanet Orchestrator changed the workload from:

```text
expensive Astra root continuously orchestrating
```

to:

```text
Astra plans
-> cheaper worker executes autonomously
-> Astra reviews selectively
```

Measured result:

- **95.4% fewer Astra root responses**
- **98.2% fewer Astra root tokens**
- **97.3% fewer Astra tokens overall**
- **21.0% fewer total tokens**
- **Astra share reduced from 40.4% to 1.4%**
- quality issues were found by independent review and corrected

The primary lesson is that **orchestration behavior can matter as much as model choice**.
