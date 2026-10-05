# Benchmark Harness

This document defines the benchmark procedure for comparing Flatplanet
Orchestrator profiles and explicit worker-model configurations.

The harness is intended to make repeated runs comparable and to prevent common
benchmark contamination such as different starting code, different
requirements, inherited fixes, reviewer anchoring, or historical test claims
being treated as fresh evidence.

## 1. Define the experiment

Before starting any implementation, record:

- task/ticket identifier
- source-of-truth requirement files
- frozen application baseline SHA
- benchmark variants to run
- expected root/worker/tester/reviewer models and reasoning efforts
- Codex CLI version
- ChatGPT plan when plan-level allowance is being measured

Change one primary variable at a time when causal interpretation matters.

For example, if the question is whether GPT-6 Luna improves on GPT-5.6 Luna,
keep the same:

- baseline
- skill version
- root model
- tester model
- reviewer model
- task
- acceptance criteria
- verification policy

If several variables change together, report the result as a workflow
comparison rather than attributing the difference to one model.

## 2. Freeze the application baseline

Resolve the exact baseline commit:

```bash
git rev-parse <baseline-ref>
```

Use a fresh branch or worktree for each run. Example:

```bash
git worktree add \
  -b <benchmark-branch> \
  ../<benchmark-worktree> \
  <baseline-sha>
```

Do not start a model-comparison run from another benchmark implementation unless
that inheritance is the explicit subject of the experiment.

Do not cherry-pick, merge, or copy code from previous benchmark variants.

## 3. Freeze the orchestrator input

Install or update Flatplanet Orchestrator before starting the Codex session.

Record:

```bash
git -C ~/flatplanet-orchestrator rev-parse HEAD
sha256sum .agents/skills/flatplanet-orchestrator/SKILL.md
codex --version
```

The installed `SKILL.md` hash matters because the source checkout may move
later.

If comparing model capability, all variants should normally use the same skill
commit. If the skill changed between runs, disclose that fact and avoid
attributing the full difference to the worker model.

## 4. Record the model topology

Record the exact requested and effective topology.

Example:

```text
root:     gpt-6-astra / medium
worker:   gpt-6-luna / max
tester:   gpt-5.6-luna / max
reviewer: gpt-6-astra / medium
```

For explicit model experiments, verify the effective worker model from session
or tool metadata when possible.

Do not infer the effective model solely from the natural-language prompt.
Separate requested settings, helper-export labels, and independently inspected
per-thread/per-event metadata. A summary label is not proof that every turn used
the same model or effort; preserve transitions and unknown attribution.

If the requested model cannot be selected, stop the benchmark run rather than
silently continuing with a fallback model.

## 5. Start from a clean benchmark branch

Before the implementation session:

```bash
git status --short
git rev-parse HEAD
git branch --show-current
```

The expected application baseline should be the only application code present
before the run, apart from the installed benchmark skill when it is intentionally
kept inside the application repository.

Record any unavoidable pre-existing changes.

## 6. Implementation-run rules

The implementation run should use the same task wording and source requirements
for every variant.

The root should:

1. derive material acceptance criteria;
2. select or honor the benchmark worker configuration;
3. delegate implementation;
4. use long waits instead of heartbeat polling;
5. require independent testing when the risk policy requires it;
6. perform independent review according to the skill;
7. batch corrections;
8. perform required re-review;
9. report unresolved acceptance criteria.

Do not prime the implementation worker with:
- another benchmark's implementation;
- another benchmark's defect list;
- previous branch-to-branch rankings;
- historical review conclusions.

When the goal is a clean model comparison, do not retrieve task-specific
memories or prior implementation summaries.

## 7. Capture final implementation identity

Before collecting final quality evidence, record the final implementation state.

Preferred:

```bash
git rev-parse HEAD
git status --short
```

If the run intentionally does not commit, record a reproducible snapshot
identifier and preserve the diff.

Do not compare a committed snapshot from one run with an unstable working tree
from another without explicitly documenting the difference.

## 8. Capture usage by pinned session ID

Usage collection belongs to the implementation run, not the later comparative
review. The usage helper is external to this repository. Record its exact local
revision, file hash and any modifications before changing or updating it.

Use its session list to locate the run, then resolve the **full root ID** and
verify the expected `cwd`. Do not select by recency alone: `--latest` can pick a
different project, canary, or later review. The terminal's current directory is
not a session filter.

```bash
python3 ~/codex-astra-luna-orchestrator/scripts/token_usage.py --list --limit 1000
```

After resolving the exact run, replace the placeholder before running:

```bash
HELPER="$HOME/codex-astra-luna-orchestrator/scripts/token_usage.py"
ROOT_SESSION_ID='REPLACE_WITH_FULL_ROOT_SESSION_ID'
sha256sum "$HELPER"
python3 "$HELPER" --root "$ROOT_SESSION_ID" --format md
python3 "$HELPER" --root "$ROOT_SESSION_ID" --format json
```

Save both exports, their exit status, generation timestamp, command arguments and
SHA-256 hashes in the private evidence directory. These commands report usage;
they are not a raw-log audit. Preserve the existing helper and exports before
any later parser change. Check local `--help` if supported options differ.

Do not apply a single-day filter to a run spanning midnight. Inventory all its
root/child segments and any archived or resumed logs actually used. Exclude the
routing canary and independent comparative-review sessions explicitly.

Record:

- full root ID, full child IDs and parent/root relationships
- cwd and run boundaries, including post-implementation turns if present
- Codex version(s) observed in relevant segments
- helper repository revision, local file hash and local modifications
- raw file inventory, hashes, lengths and completeness warnings
- number of threads and inclusion/exclusion policy
- elapsed session span; separately established active time only when measured
- plan primary/secondary observations, window duration/reset evidence and other account use
- each thread's role, model and reasoning effort, including changes or unknowns
- exported responses and the parser's definition of that counter
- uncached input, cached input, output, reasoning and total tokens
- per-thread and per-model totals and weighted input cache-hit rate
- arithmetic-check and raw-log-audit status, reported separately

### Usage validation gate

**Publishing an export is allowed before auditing it, but the confidence label
must state what was checked.** Do not replace uncertainty with a numerical
correction or silently promote an arithmetic check to a verified measurement.

| Status | Minimum evidence | Does not establish |
|---|---|---|
| REPORTED | Saved export and declared run identity | Correct parsing or arithmetic |
| ARITHMETIC CHECKED | Rows, subtotals and ratios recomputed from the export | Unique, complete, correctly attributed events |
| RAW LOG AUDITED | Exact helper and frozen relevant logs independently reconciled, with method and exceptions recorded | Backend billing certification, active time or model quality |

Keep allowance attribution, active-time measurement, model identity and final
quality as separate fields. A limitation in one does not automatically invalidate
all other measurements. Apply the same standards to every compared run.

For a raw-log audit:

1. **Freeze inputs without modifying them.** Record the helper's exact local bytes
   and revision, not just a link to upstream `main`. Preserve read-only copies of
   the relevant rollout files with hashes. Missing, malformed or truncated records
   must be reported rather than silently treated as zero. Restrict collection to
   this run; keep logs private because they may contain code, prompts or secrets.
2. **Establish membership and boundaries.** Use full thread IDs and actual metadata
   relationships. Do not group by eight-character prefixes or cwd alone. Identify
   resumed/forked histories, separate segments, child preflight and final-report
   turns. Exclude unrelated work. A shared prefix is not evidence of duplicate IDs.
3. **Check event semantics and overlap.** Determine which records are per-response
   deltas, cumulative snapshots or repeated notifications for the CLI version(s).
   Check duplicate files and repeated history across resumes before aggregating.
   Deduplicate only with supported event/response identity or verified overlap,
   and retain an exclusion ledger. Identical token counts are not proof of a
   duplicate; a real retry may represent new work. A 401 or resume alone proves
   neither double counting nor a billable successful request.
4. **Reconcile counters once.** Recompute per-thread/per-model totals independently.
   Do not add cumulative counters to the deltas they already summarize. Compare
   like-for-like boundaries, accounting for resets, inherited/forked history,
   compaction, missing records and fallback paths before expecting equality.
   Resolve discrepancies or leave the result provisional; do not force a match.
5. **Verify attribution.** Map usage to the model/effort active for that event where
   supported. A last-known thread setting must not silently label its entire past
   history. Check whether a fallback attributes all cumulative usage to the last
   model or skips earlier periods when record formats are mixed. Report unknown
   attribution instead of assigning it to the requested model.
6. **Retain the result and its limits.** Save original and reconciled exports,
   helper/log hashes, scope, exclusions, differences and audit notes. A conclusion
   of no counting defect requires completed checks; otherwise state NOT AUDITED.
   Do not edit historical figures in place without a sourced correction record.

For the input/output convention used by these supplied exports, check:

```text
input = uncached_input + cached_input
total = input + output
0 <= reasoning_output <= output
cache_hit_rate = sum(cached_input) / sum(input)
```

Cached input is already part of input; reasoning output is already part of
output. Neither is added twice. Calculate cache ratios from summed counts, not an
unweighted average of thread percentages. If the actual log schema differs,
document it instead of forcing these identities. `Responses` must retain its
parser-specific definition until reconciled; it is not automatically billable
API calls, useful implementation steps or successful task completions.

For general API terminology, OpenAI documents [prompt-cache reuse](https://developers.openai.com/api/docs/guides/prompt-caching)
and [reasoning within output usage](https://developers.openai.com/api/docs/guides/reasoning).
These references explain terminology, not the correctness of a particular Codex
CLI rollout parser or how this Pro account's allowance was charged.

### Time, allowance and cost boundaries

Publish elapsed log span separately from active execution time. Record known
interruptions and intervals only when supported by timestamps and events. Do not
invent active time by subtracting arbitrary idle thresholds, sum overlapping
thread durations, or rank model speed from an interrupted session span.

Do not assume backend labels such as `primary` and `secondary` have universal
semantics. Preserve observed window duration/reset details when available; leave
unknown mappings unresolved. Account percentages may be rounded, delayed, reset
or affected by other sessions. Without isolated attribution, label the change
**account observation only** and do not subtract other deltas mechanically.

Raw token sums across different models/cache categories are not monetary cost.
Any estimate needs a declared pricing basis and applicable rates; an API-rate
estimate is not a Pro allowance charge. Cache reuse also means aggregate tokens
do not measure unique input size or code produced.

## 9. Separate implementation findings from final-snapshot findings

A benchmark run may discover and fix many defects.

For example:

```text
implementation/review found:
  4 High
  5 Medium

after corrections:
  0 open known findings
```

That does not mean the final implementation contains zero defects.

For cross-profile quality comparison, count only findings independently
confirmed in the frozen final snapshot.

Maintain separate fields for:

- findings discovered during implementation
- findings fixed during implementation
- findings present in the final comparative review
- acceptance criteria not verified

## 10. Independent comparative quality review

After all candidate runs finish, freeze each branch to an exact SHA.

The quality review must evaluate each final snapshot independently against the
same source requirements before directly comparing branches.

First-pass reviewers should receive:

- the same source requirements
- the frozen source snapshot
- relevant tests
- the same review scope and evidence standard

They should not receive before forming findings:

- profile labels
- worker models
- token usage
- plan allowance usage
- previous ranking
- worker success narrative
- previous reviewer approval claims

When possible, use neutral snapshot identifiers such as `s1`, `s2`, `s3`.

Use the same reviewer model and reasoning effort for all candidate snapshots.

## 11. Comparable executable probes

Baseline test suites are necessary but insufficient.

Where practical, execute the same reviewer-authored scenarios against every
snapshot.

High-value classes include:

- source-value to operational-value semantics
- units and currencies
- null/special values
- delayed responses
- autosave and navigation
- optimistic concurrency
- retry/idempotency
- rollback
- migration/runtime normalization parity
- derived-key collision behavior
- authorization/tenant boundaries

Expected results must come from requirements or independently established
business invariants, not from the implementation under review.

For race conditions, prefer deterministic synchronization barriers,
interceptors, controlled callbacks, or equivalent mechanisms over timing-based
tests that merely hope to hit the problematic interleaving.

## 12. Evidence categories

Every verification item should be classified as one of:

- `PASS — executed`
- `FAIL — executed`
- `PASS — static`
- `PARTIAL`
- `NOT VERIFIED`
- `BLOCKED — environment`
- `HISTORICAL ONLY`

Do not convert historical statements such as "tests passed during
implementation" into fresh evidence for the final SHA.

## 13. Finding severity

Use consistent severity definitions across snapshots:

- **Critical** — severe security-boundary failure, major data loss/corruption,
  or fundamentally unusable required workflow
- **High** — substantial correctness, data-integrity, concurrency, or workflow
  defect
- **Medium** — meaningful defect or missing requirement with more limited
  impact
- **Low** — minor robustness, usability, or maintainability issue

Group related symptoms of one root cause instead of inflating counts.

Do not invent findings to equalize scrutiny between variants.

## 14. Minimum final comparison

Always present candidate implementations in a fixed declared order.

Include:

### Setup

| Field | Candidate A | Candidate B | Candidate C |
|---|---|---|---|
| Branch | | | |
| Final SHA | | | |
| Skill SHA/hash | | | |
| Root | | | |
| Worker | | | |
| Tester | | | |
| Reviewer | | | |

### Usage

| Metric | Candidate A | Candidate B | Candidate C |
|---|---:|---:|---:|
| Export / arithmetic / raw-log status | | | |
| Elapsed session span | | | |
| Active time and measurement basis, or NOT ESTABLISHED | | | |
| Root responses, as defined by parser | | | |
| Root tokens | | | |
| All premium/root-model tokens | | | |
| Worker tokens | | | |
| Total tokens | | | |
| Observed plan allowance and attribution | | | |

### Final-snapshot quality

| Severity | Candidate A | Candidate B | Candidate C |
|---|---:|---:|---:|
| Critical | | | |
| High | | | |
| Medium | | | |
| Low | | | |

### Acceptance matrix

| Requirement | Candidate A | Candidate B | Candidate C |
|---|---|---|---|

### Verification matrix

| Scenario | Candidate A | Candidate B | Candidate C |
|---|---|---|---|

Also report:

- merge blockers for every candidate
- evidence not obtained
- browser/manual/production acceptance still missing
- shared product ambiguities that require a human decision
- causal limitations of the experiment

## 15. Interpretation rules

Valid conclusion, with the measurement status made explicit:

> In the supplied exports, configuration X records fewer Astra root turns than
> configuration Y. Its final snapshot also had fewer independently confirmed
> High findings. The usage raw-log audit status is reported separately.

Invalid conclusion without stronger controls:

> Model X is 40% better than model Y.

Also avoid:

- "same quality at lower cost" unless final-snapshot evidence supports it;
- equating total tokens across different models with monetary cost;
- equating arithmetic consistency with correct, unique and complete event accounting;
- treating an interrupted elapsed span as model speed or a shared-account delta as a run-only charge;
- equating zero known findings with proof of correctness;
- treating a larger test suite as inherently higher quality;
- treating a newer implementation as inherently better.

## 16. Artifacts to retain

For every run retain:

- completed [RUN-TEMPLATE.md](RUN-TEMPLATE.md)
- exact final SHA or snapshot
- original usage exports, commands and export hashes
- exact local helper revision/hash and raw-log inventory/hashes, kept privately
- audit method, reconciled result and exclusion ledger when a raw-log audit is performed
- implementation summary
- independent tester/reviewer findings
- final re-review result when applicable

For every multi-run comparison retain:

- frozen input SHAs
- requirement revision
- independent review report
- executable probe results
- environment/tool versions
- limitations

The goal is not merely to reproduce a number. The goal is to preserve enough
evidence that another reviewer can explain why the number should be trusted.
