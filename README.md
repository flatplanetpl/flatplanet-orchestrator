# Flatplanet Orchestrator

Cost-efficient multi-agent orchestration skill for OpenAI Codex.

**Quick navigation:** [Results](#what-you-can-gain) · [Quality](#cost-vs-quality) · [Profiles](#execution-profiles) · [Install](#install-in-a-repository) · [Update](#update-an-existing-installation) · [Usage](#usage) · [Benchmark harness](benchmark/README.md) · [Comparison](docs/BENCHMARK-CASE-STUDY.md) · [Luna 6 run](benchmark/runs/2026-09-25-GR-UX-01-luna6.md) · [TODO](#todo-and-roadmap)

The goal is simple:

- keep the expensive root model focused on planning, architecture and final integration,
- delegate long-running execution to cheaper worker models,
- avoid short `wait_agent` polling loops,
- avoid duplicate work between the root and subagents,
- choose the worker model per task with a simple execution profile.

## What you can gain

The GR-UX-01A evidence now includes four implementation runs, in a fixed order: **Old orchestration → Cheap profile → Balanced profile → GPT-6 Luna**. The Luna 6 run was performed on 2026-09-25–26 and documented here on 2026-10-05.

**Benchmark plan:** ChatGPT Pro. These are maintainer-supplied session exports, not a new test execution or a guaranteed savings ratio.

> **Measurement confidence:** Luna 6's exported sums are **ARITHMETIC CHECKED**; the local helper version/hash, underlying rollout files, duplicate-history handling and per-event model attribution have **NOT** been independently audited. Treat the figures as a consistent session export, not verified billing or a certified model-only benchmark. No counting error has been established, so the reported numbers are retained unchanged. See the [usage validation gate](benchmark/HARNESS.md#usage-validation-gate).

| Metric | Old orchestration | Cheap profile | Balanced profile | GPT-6 Luna |
|---|---:|---:|---:|---:|
| Root Astra responses | 455 | 21 | 37 | **105** |
| Root Astra tokens | 59.47M | 1.05M | 2.12M | **7.40M** |
| All Astra tokens | 60.77M | 1.66M | 3.56M | **11.84M** |
| Total tokens, all models | 150.35M | 118.84M | 68.94M | **186.87M** |
| Astra share of all tokens | 40.42% | 1.39% | 5.16% | **6.34%** |
| Reported elapsed session span | 106m56s | 151m42s | 172m00s | **1158m06s*** |
| Observed primary allowance | 19% → 23% | 23% → 23% | 24% → 25% | **30% → 46%; not isolated** |

*The Luna 6 span is 19h18m06s, with an unquantified 401 interruption and continuation. It is not verified active coding time and must not be used for a model-speed ranking. Other work on the same account was also documented, so the 30% → 46% change is not a Luna-6-only allowance charge. The maintainer identified `primary` as weekly on this account; this is not a universal mapping of that backend label. Zero visible change is not proof of zero usage.

The important distinction is between **root activity, whole-workflow usage, and final quality**. In the supplied exports, Luna 6 records 87.6% fewer root Astra tokens than Old, but 24.3% more total tokens. These are descriptive ratios pending a raw-log audit. Different models, tester workloads, review rounds and CLI/skill versions prevent a clean model-only or monetary-cost comparison.

**186.87M is the whole workflow:** 130.35M attributed to the GPT-6 Luna worker, 44.67M to the GPT-5.6 Luna tester, and 11.84M to Astra root/reviewer. Cached input is included; reasoning is not added a second time. `Responses` is the helper's exported count, not independently reconciled billable requests. Arithmetic consistency alone cannot detect duplicated or omitted history.

See the [four-run comparison](docs/BENCHMARK-CASE-STUDY.md) for exact counts and limitations, and the [Luna 6 run entry](benchmark/runs/2026-09-25-GR-UX-01-luna6.md) for provenance and reported verification.

### At a glance

Exported root Astra tokens relative to Old = 100%. The 30-cell bars are rounded; percentages are descriptive token ratios, not quality scores or independently audited charges.

```text
ROOT ASTRA TOKENS
Old       59.47M |##############################| 100.0%
Cheap      1.05M |#.............................|   1.8%
Balanced   2.12M |#.............................|   3.6%
Luna 6     7.40M |####..........................|  12.4%
```

The [original Old/Cheap chart](docs/assets/benchmark-at-a-glance.svg) and [historical two-run study](docs/BENCHMARK-CASE-STUDY-OLD-CHEAP.md) remain available. They do not include the later runs.

### Cost vs quality

The later independent final-snapshot comparison evaluated Old, Cheap and Balanced. **Luna 6 has not yet received that same comparative review.** Its in-process closure report must not be treated as a zero-defect result in this table.

| Finding severity | Old orchestration | Cheap profile | Balanced profile | GPT-6 Luna |
|---|---:|---:|---:|---|
| Critical | 0 | 0 | 0 | NOT EVALUATED |
| High | 1 | 6 | 3 | NOT EVALUATED |
| Medium | 4 | 5 | 3 | NOT EVALUATED |
| Low | 2 | 2 | 2 | NOT EVALUATED |

This later review preferred Old as a starting point, with material blockers in all three assessed snapshots. It supersedes the earlier Old/Cheap quality counts preserved in the historical study. It does not establish a causal ranking of the worker models.

For Luna 6, the supplied implementation report closes **7 High and 6 Medium failure modes** within its tested scope. It reports **93/93 component tests** and **49/49 focused synthetic DB checks performed by root**, plus four review passes. Acceptance is still **PARTIAL**: browser/mobile/keyboard, cross-tab runtime, the <=60-second measurement, exact-SHA CI and owner approval remain unverified. An earlier broad backend suite had one unresolved failure and was not rerun as a whole. The application changes were left uncommitted; a final source-snapshot identity has not been supplied.

**These data do not support “same quality at lower cost.”** Profile selection and independent verification remain separate controls. `balanced` is the configured default below, not a quality winner demonstrated by this experiment.

## Execution profiles

| Profile | Worker | Reasoning | Typical use |
|---|---|---|---|
| `cheap` | GPT-5.6 Luna | max | small, bounded, routine changes |
| `luna6` | GPT-6 Luna | max | explicit cost-sensitive GPT-6 / benchmark profile |
| `balanced` | GPT-5.6 Terra | high | default production development |
| `strong` | GPT-5.6 Sol | high | difficult debugging/refactors |
| `max` | GPT-6 Astra | medium | exceptional, high-risk tasks |

Fixed roles by default:

- root: GPT-6 Astra / medium
- explorer: GPT-5.6 Luna / max
- researcher: GPT-5.6 Luna / max
- tester: GPT-5.6 Luna / max
- reviewer: GPT-6 Astra / dynamic effort (`low` for low-risk review, `medium` for high-risk review and final re-review after High/Critical findings)

## Install in a repository

Use Bash, Git, and GNU coreutils on Linux. Finish any active Codex task before replacing its skill files. Keep a local clone of this repository; the scripts copy the skill from that checkout into your application repository.

### First installation

Clone once, then pass your application's directory to [install.sh](scripts/install.sh):

```bash
git clone --depth 1 --branch main https://github.com/flatplanetpl/flatplanet-orchestrator.git ~/flatplanet-orchestrator
bash ~/flatplanet-orchestrator/scripts/install.sh /path/to/application-repo
```

If you already have the source clone, skip cloning. The installer refuses to overwrite an existing installation. The target must be an existing Git working tree; a subdirectory is resolved to its repository root. Omit the path to use your current repository.

### Update an existing installation

Pull the source changes, then run [update.sh](scripts/update.sh) to refresh the installed copy:

```bash
git -C ~/flatplanet-orchestrator pull --ff-only &&
bash ~/flatplanet-orchestrator/scripts/update.sh /path/to/application-repo
```

**Update behavior:** a full backup is created first; matching files inside `.agents/skills/flatplanet-orchestrator/` are replaced, not merged. New files are added and local-only files are retained. Reapply local customizations from the backup and review obsolete helper files yourself.

Backups are stored outside both repositories at `${XDG_STATE_HOME:-$HOME/.local/state}/flatplanet-orchestrator/backups/`. The updater prints the backup path and source commit SHA. If the source skill has local edits, the scripts explicitly report that those edits were copied too.

Neither script changes `.codex/config.toml`, `AGENTS.md`, or other skills, and neither stages or commits changes. Symlinked skill installations and conflicting file/directory types are rejected. An update copy failure may leave a partial update; the error points to the complete backup.

A `git pull` alone updates only the source clone. `update.sh` copies that checkout into the application. The scripts themselves do not access the network.

### Verify the installation or update

Review the application repository diff and newly added files, then start a new Codex session from its root:

```bash
cd /path/to/application-repo
git status --short -- .agents/skills/flatplanet-orchestrator
git diff -- .agents/skills/flatplanet-orchestrator
codex
```

For script options, run `bash scripts/install.sh --help` or `bash scripts/update.sh --help` from the source clone. Offline installer tests can be run there with:

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

## Usage

Default profile (`balanced`):

```text
$flatplanet-orchestrator implement ticket GR-UX-01A
```

Cheap:

```text
$flatplanet-orchestrator profile=cheap fix the form validation
```

GPT-6 Luna / max:

```text
$flatplanet-orchestrator profile=luna6 implement the ticket
```

`luna6` is explicit and non-default. It uses `gpt-6-luna` with `max` reasoning while keeping the same independent tester/reviewer rules as the other profiles.

Strong:

```text
$flatplanet-orchestrator profile=strong redesign the data synchronization
```

Explicit worker override:

```text
$flatplanet-orchestrator worker=terra effort=high implement the ticket
```

### Blind / adversarial review

Independent reviewers are intentionally **not primed by the worker's success narrative**.

The first review pass follows:

```text
spec / acceptance criteria
          ↓
final implementation
          ↓
test code
          ↓
adversarial review
          ↓
test/build evidence
```

The reviewer is asked to **falsify correctness**: find missing behavior, semantic mistakes, stale-state/concurrency failures, and tests that may simply encode the implementation's bug.

Worker model/profile and worker claims are withheld from the first-pass reviewer when possible to reduce anchoring bias.

After fixes, re-review verifies previous findings **and** performs a fresh regression scan.

### Dynamic reviewer effort

Reviewer cost also scales with risk:

```text
low-risk change                         -> Astra reviewer / low
money, inventory, concurrency,
migrations, security, cross-tenant     -> Astra reviewer / medium
Cheap profile below risk-aware floor   -> Astra reviewer / medium
fix after Critical/High finding        -> final Astra reviewer / medium
```

This keeps routine review inexpensive while using stronger reasoning where the quality benchmark showed it matters.

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

The reproducible benchmark procedure lives under **[benchmark/](benchmark/README.md)**.

Use:

- [benchmark/HARNESS.md](benchmark/HARNESS.md) for the full run and review procedure,
- [usage validation gate](benchmark/HARNESS.md#usage-validation-gate) for session selection, helper provenance and raw-log reconciliation,
- [benchmark/RUN-TEMPLATE.md](benchmark/RUN-TEMPLATE.md) for per-run evidence,
- [docs/BENCHMARK-CASE-STUDY.md](docs/BENCHMARK-CASE-STUDY.md) for the current four-run comparison,
- [benchmark/runs/2026-09-25-GR-UX-01-luna6.md](benchmark/runs/2026-09-25-GR-UX-01-luna6.md) for the Luna 6 entry and its limitations.

When comparing orchestration strategies, track at least:

- root model responses,
- root cached input,
- root total tokens,
- worker total tokens,
- root share of total tokens,
- elapsed session span and separately established active time, if available,
- Codex primary/secondary allowance observations and attribution limits,
- exact application/skill SHAs,
- full session/thread IDs, local helper hash, export hashes and raw-log audit status,
- final-snapshot quality findings and unverified acceptance criteria.

A healthy run should move most execution tokens away from the expensive root and into the selected worker model without weakening the evidence required for final implementation quality.

## TODO and roadmap

**Open work as of 2026-10-05.** The checklist separates missing evidence from proposed tooling improvements. Unchecked items are not completed features, verified results, or release commitments.

### Priority 1 — validate the existing benchmark evidence

- [ ] **Freeze the final Luna 6 implementation.** Preserve tracked changes and relevant untracked source/test files, record a commit or source-tree/archive checksum, and attach that identity to the [run entry](benchmark/runs/2026-09-25-GR-UX-01-luna6.md). The baseline HEAD is not the completed implementation.
- [ ] **Audit usage against the exact local helper and raw logs.** Reconcile full thread IDs, run boundaries, resumed history, counters and model/effort attribution under the [usage validation gate](benchmark/HARNESS.md#usage-validation-gate). Keep raw logs private. Retain reported counts unless a counting defect is demonstrated; arithmetic consistency alone does not close this item.
- [ ] **Complete the independent four-way quality comparison.** Evaluate frozen snapshots in the order **Old → Cheap → Balanced → Luna 6**, using specification-first reviews and equivalent executable probes. Count defects remaining in each final snapshot, not findings already fixed during implementation. Publish the evidence and merge blockers before ranking Luna 6.

### Priority 2 — make future runs repeatable

- [ ] **Retain independent probes as regression tests.** Preserve reviewer-authored scenarios and their requirement-derived expectations in the benchmark application or an appropriate test harness. Reapply equivalent scenarios across candidates; do not turn ticket-specific assertions into mandatory global skill rules.
- [ ] **Automate the manual harness steps with tested local scripts.** Add run preflight, reproducible snapshot capture, pinned-root usage export and manifest validation. Include checks for effective model settings and isolated test-infrastructure access; test resumed/overlapping log handling before relying on automated accounting. Keep private source, credentials and raw rollouts out of published artifacts.
- [ ] **Run controlled follow-up comparisons, including GPT-6 Sol.** Freeze the same application baseline, requirements, skill, CLI and verification policy; keep root/tester/reviewer settings constant when comparing workers. Repeat reference configurations and record variability. Compare effort through the same acceptance threshold, including corrections and re-review; keep token totals, active time and account allowance separate.

### Benchmark application acceptance — separate from orchestrator features

GR-UX-01A still needs independent DB-layer verification, investigation and rerun of the unresolved broad backend failure, browser/mobile/keyboard and cross-tab checks, the <=60-second measurement, exact-SHA CI and owner acceptance. Representative historical-data migration also remains unverified. These are application acceptance gaps documented in the [Luna 6 report](benchmark/runs/2026-09-25-GR-UX-01-luna6.md), not missing orchestrator features or claims that existing skill policies are absent. Existing-database operations, deployment and live-system checks require separate authorization.

**Completion rule:** close an item only when its linked artifact, test result or audit report supports closure. Preserve earlier evidence and update the run/comparison status explicitly; zero known findings is not proof of correctness.
