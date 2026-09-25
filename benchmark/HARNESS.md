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

## 8. Capture usage immediately

Usage collection belongs to the implementation run, not the later comparative
review.

With the existing external usage helper:

```bash
python3 ~/codex-astra-luna-orchestrator/scripts/token_usage.py --latest
```

Record:

- session ID
- cwd
- Codex version
- number of threads
- wall time
- plan primary/secondary allowance change when available
- each thread's role
- model and reasoning effort
- responses
- uncached input
- cached input
- output
- reasoning
- total tokens
- duration
- totals per model
- totals across all models
- input cache-hit rate

Do not assume backend labels such as `primary` and `secondary` have universal
semantics. Record the observed window/account interpretation separately.

Displayed allowance percentages may be rounded or delayed. Treat them as a
plan-level signal, not an exact token-to-percent conversion.

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
| Wall time | | | |
| Root responses | | | |
| Root tokens | | | |
| All premium/root-model tokens | | | |
| Worker tokens | | | |
| Total tokens | | | |
| Visible plan allowance delta | | | |

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

Valid conclusion:

> In this benchmark, configuration X used fewer Astra root turns and its final
> snapshot had fewer independently confirmed High findings than configuration Y.

Invalid conclusion without stronger controls:

> Model X is 40% better than model Y.

Also avoid:

- "same quality at lower cost" unless final-snapshot evidence supports it;
- equating total tokens across different models with monetary cost;
- equating zero known findings with proof of correctness;
- treating a larger test suite as inherently higher quality;
- treating a newer implementation as inherently better.

## 16. Artifacts to retain

For every run retain:

- completed [RUN-TEMPLATE.md](RUN-TEMPLATE.md)
- exact final SHA or snapshot
- usage report
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
