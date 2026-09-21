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

- ChatGPT plan: Pro
- Codex CLI: `0.155.1`
- Same repository and feature area
- Root model: GPT-6 Astra / medium
- Old orchestration worker strategy: Luna subagents with an actively polling root
- Cheap profile worker strategy: one long-running GPT-5.6 Luna / max worker plus GPT-6 Astra / low reviewer
- Token accounting source: `scripts/token_usage.py --latest`
- Prompt cache hit rate:
  - before: 98.2%
  - after: 98.2%

The runs were not laboratory-identical. The optimized run took longer and used a different orchestration topology, so the result should be treated as an engineering case study rather than a controlled scientific benchmark.

## Raw results

### Old orchestration

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

weekly allowance (backend `primary` on this Pro account):
  19.0% -> 23.0%  (+4 percentage points)

secondary window:
  unavailable
```

### Cheap profile (Luna Max)

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

weekly allowance (backend `primary` on this Pro account):
  23.0% -> 23.0%  (no visible increase)

secondary window:
  unavailable
```

## Old orchestration vs Cheap profile

| Metric | Old orchestration | Cheap profile | Change |
|---|---:|---:|---:|
| Wall time | 106m56s | 151m42s | +41.9% |
| Root Astra responses | 455 | 21 | **-95.4%** |
| Root Astra cached input | 58.76M | 0.95M | **-98.4%** |
| Root Astra total | 59.47M | 1.05M | **-98.2%** |
| All Astra total | 60.77M | 1.66M | **-97.3%** |
| Luna total | 89.58M | 117.18M | +30.8% |
| All-model total | 150.35M | 118.84M | **-21.0%** |
| Astra share of total tokens | 40.4% | 1.4% | **-39.0 pp** |
| Visible weekly allowance delta (Pro) | +4 pp | 0 pp visible | displayed percentage |

The key result is the collapse in expensive root activity. The Cheap profile intentionally allowed the cheaper worker to do more work, yet overall tokens still fell by about 21%.


## Visual comparison

### Expensive root activity

```text
Root Astra responses
Old    455  ██████████████████████████████████████████████████  100.0%
Cheap   21  ██                                                    4.6%
             └──────────────────────────────────────────────────┘
             95.4% reduction
```

```text
Root Astra total tokens
Old    59.47M  ██████████████████████████████████████████████████  100.0%
Cheap   1.05M  █                                                     1.8%
                └──────────────────────────────────────────────────┘
                98.2% reduction
```

```text
Root Astra cached input
Old    58.76M  ██████████████████████████████████████████████████  100.0%
Cheap   0.95M  █                                                     1.6%
                └──────────────────────────────────────────────────┘
                98.4% reduction
```

### Where the tokens went

```text
OLD ORCHESTRATION

Astra   40.4%  ████████████████████
Workers 59.6%  ██████████████████████████████


CHEAP PROFILE

Astra    1.4%  █
Workers 98.6%  █████████████████████████████████████████████████
```

### Total compute

```text
All-model tokens
Old   150.35M  ██████████████████████████████████████████████████  100%
Cheap 118.84M  ███████████████████████████████████████             79%

Despite the worker doing MORE work:
Luna before   89.58M  ██████████████████████████████████████
Luna after   117.18M  ██████████████████████████████████████████████
```

This is the core optimization:

```text
OLD ORCHESTRATION
┌─────────────────────────────────────────────────────────────────┐
│ ASTRA ROOT                                                      │
│ plan -> wait -> wake -> inspect -> wait -> wake -> diff -> ... │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                       frequent expensive turns
                                │
                                ▼
                         Luna subagents


CHEAP PROFILE
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
Old:   4.26 root responses/min  ██████████████████████████████████████████████████
Cheap: 0.15 root responses/min  ██

Approximate reduction: 96.5%
```

## Root wake-up behavior

The original root produced approximately:

```text
455 responses / 106m56s
≈ 4.26 root responses per minute
```

The Cheap profile root produced:

```text
21 responses / 141m49s root-thread duration
≈ 0.15 root responses per minute
```

That is roughly a 96.5% reduction in root response frequency.

The Cheap profile trace showed the desired pattern:

```text
Started worker
Waiting for agents
...long-running worker activity...
worker completes
root resumes
```

instead of repeated short `wait_agent` wake-ups.

## Independent quality comparison

A separate branch-to-branch review was performed after both implementations were complete.

The reviewer evaluated each branch independently against the same ticket/specification before comparing them directly. The branch labels used during review were neutralized to reduce naming bias.

The result:

> **Old orchestration was technically stronger by a moderate margin. Neither branch was considered ready to merge without additional fixes.**

Both implementations had a sound transactional foundation: persistent line snapshots, tenant-scoped APIs, transactional finalization, idempotent retry behavior, and separation of invoice source amounts from stock-increase quantity.

### Findings

| Severity | Old orchestration | Cheap profile |
|---|---:|---:|
| Critical | 0 | 0 |
| High | **0** | **1** |
| Medium | **5** | **8** |
| Low | **1** | **2** |

```text
QUALITY FINDINGS
(lower is better)

Old orchestration
Critical  0
High      0
Medium    5  █████
Low       1  █

Cheap profile
Critical  0
High      1  █
Medium    8  ████████
Low       2  ██
```

### Where Old orchestration was stronger

The Old orchestration implementation was stronger in:

- warehouse unit-price semantics and purchase-price currency
- nullable/non-numeric source VAT handling
- real ISO 4217 currency validation
- mixed-currency behavior
- contextual supplier creation
- editor recovery and conflict handling
- concurrency coverage
- delayed-response/autosave coverage

It also had substantially stronger editor and concurrency-oriented tests.

### Where Cheap profile was stronger

The Cheap profile implementation had several useful strengths:

- reused a shared receipt-creation path instead of duplicating as much receipt/stock logic
- preserved more accurate business error messages during finalization
- returned only open drafts in the "to receive" list
- refreshed current suggestions when reading a draft
- changed fewer non-generated source lines overall

### Most important Cheap-profile defect

The independent review found one High-severity issue in the Cheap profile: incorrect warehouse purchase-price semantics when source quantity/unit and stock quantity/unit differed.

Example:

```text
Source: 1 case for 100 EUR
Stock:  20 bottles

Correct operational stock unit price: 5 EUR / bottle
Cheap-profile behavior could preserve UnitNetPrice=100 on Quantity=20
```

The source financial total remained correct, but the stored/consumed operational purchase price could be wrong and could lose its currency semantics.

### Test-quality comparison

| Area | Old orchestration | Cheap profile |
|---|---:|---:|
| Editor component tests | **12** | 3 |
| Dedicated autosave queue tests | **Yes** | No |
| Changes during in-flight save | **Covered** | No dedicated test |
| Two writes with same version | **Covered** | No dedicated independent-context test |
| Concurrent finalization of same draft | **Covered** | No dedicated test |
| Two drafts updating same stock | Covered | Covered |
| Retry finalization | Covered | Covered |
| Rollback | Covered | Covered |
| Delayed response / commit race | **Barrier/interceptor test** | No |

The independent review concluded that Old orchestration had clearly stronger coverage around concurrency and delayed responses.

### Interpretation

The Cheap profile delivered the dramatic usage reduction measured in this case study, but the quality comparison shows that **lower orchestration cost did not preserve identical implementation quality** on this high-risk ticket.

That is why Flatplanet Orchestrator uses:

- `cheap` / Luna Max for bounded, lower-risk tasks
- `balanced` / Terra High as the default production profile
- `strong` / Sol High for difficult debugging/refactoring
- `max` / Astra for exceptional cases

For tasks involving multiple of the following, use at least `balanced`:

- financial calculations
- inventory integrity
- concurrency
- migrations
- authorization/security
- cross-tenant isolation
- irreversible state transitions

If an independent reviewer reports any High-severity finding, perform a final independent re-review after corrections.

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
Old orchestration: Astra = 40.4% of all tokens
Cheap profile:     Astra =  1.4% of all tokens
```

The worker consumed more tokens, but on the cheaper model. This is intentional.

The root's cached input dropped from 58.76M to 0.95M, strongly indicating that repeated context-heavy root wake-ups were the dominant inefficiency in the original workflow.

### What did not become free

The Cheap profile still used substantial worker compute:

```text
117.18M Luna tokens
```

Flatplanet Orchestrator is not a "use fewer tokens at all costs" strategy. It is primarily a **model-routing and orchestration-efficiency strategy**:

- expensive reasoning stays sparse,
- cheap execution can be extensive,
- expensive review is used selectively.

### Quality trade-off

The Cheap profile did not match the implementation quality of the Old orchestration branch in the later independent branch-to-branch review.

That result supports the profile model used by Flatplanet Orchestrator:

- `cheap` / Luna: suitable for bounded low-risk implementation
- `balanced` / Terra: preferred default for normal production work
- `strong` / Sol: complex debugging/refactors
- `max` / Astra: exceptional cases

For work involving concurrency, money, inventory integrity, migrations, authorization/security, or cross-tenant isolation, using at least `balanced` is prudent unless the user explicitly chooses `cheap`.

## Allowance caveats

The allowance observations in this case study are specific to the **ChatGPT Pro plan** used for the benchmark.

For this ChatGPT Pro account, the backend `primary` rate-limit window represented the **7-day / weekly allowance**. The benchmark therefore observed:

```text
old:   weekly (primary) 19.0% -> 23.0%   (+4 pp)
cheap: weekly (primary) 23.0% -> 23.0%   (0 pp visible)
```

The backend labels `primary` and `secondary` should not be treated as universal semantic names across all Codex configurations; the relevant interpretation is the window duration/account configuration. In this benchmark, `primary` was the weekly window.

This should NOT be interpreted as proof that the Cheap profile consumed exactly zero allowance.

Reasons:

- displayed percentages may be rounded
- usage reporting may lag
- Codex plan allowance is not publicly documented as a simple token-to-percent formula
- the secondary window was unavailable in both reports
- account-wide concurrent usage could affect the same counters

The weekly percentage is useful as an observed plan-level signal, but the most granular evidence still comes from the per-thread model/token measurements and the observed root wake-up reduction.

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

In this case study, the Cheap profile changed the workload from:

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
- independent branch comparison still found the Old orchestration implementation technically stronger

The primary lesson is that **orchestration behavior can dramatically reduce expensive usage, but worker-model choice and independent verification still materially affect implementation quality**.
