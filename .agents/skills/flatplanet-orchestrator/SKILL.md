---
name: flatplanet-orchestrator
description: Cost-efficient multi-agent orchestration for Codex. GPT-6 Astra is used as a low-activity planner/integrator, while execution workers are selected dynamically with cheap/balanced/strong/max profiles. Optimized to minimize root-agent wakeups, polling, duplicated work, and Astra context usage.
---

# Flatplanet Orchestrator — Parametrized Cost/Quality Profiles

The user's explicit instructions take precedence over this skill.

# Primary goal

Use GPT-6 Astra only for work that materially benefits from Astra-level reasoning.

Delegate routine execution to cheaper models.

The root Astra should:

1. understand the task
2. choose architecture and work boundaries
3. select or honor the requested execution profile
4. delegate bounded execution
5. WAIT while workers execute
6. integrate completed results
7. perform only high-value final review

The root Astra must NOT behave like an active implementation worker or continuously monitor workers.


# Execution profiles

The user may select the implementation profile directly in the request.

Supported syntax:

- `profile=cheap`
- `profile=balanced`
- `profile=strong`
- `profile=max`

Explicit model overrides are also supported:

- `worker=luna`
- `worker=terra`
- `worker=sol`
- `worker=astra`

Optional effort override:

- `effort=medium`
- `effort=high`
- `effort=max`

Examples:

`$flatplanet-orchestrator profile=cheap fix the form validation`

`$flatplanet-orchestrator profile=balanced implement GR-UX-01A`

`$flatplanet-orchestrator profile=strong redesign the data synchronization`

`$flatplanet-orchestrator worker=terra effort=high implement the ticket`

Explicit `worker=` and `effort=` values override the selected profile.

If the user provides no profile and no explicit worker model, use:

`profile=balanced`


## Profile: cheap

Use:

- worker: `gpt-5.6-luna`
- worker reasoning: `max`

Use for:

- small and well-bounded features
- mechanical refactors
- routine CRUD
- straightforward validation
- test fixes
- repetitive repository work
- low-risk implementation


## Profile: balanced

Use:

- worker: `gpt-5.6-terra`
- worker reasoning: `high`

This is the DEFAULT profile.

Use for:

- normal production feature development
- multi-file implementation
- backend + frontend changes
- migrations
- moderate business logic
- state management
- API changes
- tasks requiring stronger reasoning than Luna but not premium reasoning


## Profile: strong

Use:

- worker: `gpt-5.6-sol`
- worker reasoning: `high`

Use for:

- complex debugging
- difficult refactors
- complicated concurrency
- distributed state
- subtle correctness issues
- difficult migrations
- complicated architectural implementation
- tasks where Terra is likely to require multiple correction passes


## Profile: max

Use:

- worker: `gpt-6-astra`
- worker reasoning: `medium`

Use only when:

- the user explicitly requests maximum capability
- previous cheaper workers failed materially
- the implementation itself requires Astra-level reasoning
- the task is unusually high-risk or conceptually difficult

Do NOT select `max` merely because the task is large.

Large but well-structured tasks should normally use `balanced` or `strong`.


# Fixed role models

Unless the user explicitly overrides them:

- root: GPT-6 Astra / medium
- explorer: GPT-5.6 Luna / max
- researcher: GPT-5.6 Luna / max
- tester: GPT-5.6 Luna / max
- reviewer: GPT-6 Astra / low

Only implementation workers change according to the execution profile.

This is intentional.

Routine exploration, research, and validation should remain cheap.


# Profile selection behavior

If the user explicitly provides a profile:

honor it.

Do not silently upgrade the worker model.

If no profile is specified:

use `balanced`.

The root may recommend a different profile only when there is strong evidence that the selected profile is unsuitable.

If the user selected `cheap`, do not automatically upgrade to Terra merely because the task is moderately difficult.

If a worker encounters a genuine reasoning blocker, return the blocker to root.

The root may then decide whether escalation is justified.


# Risk-aware profile floor

Before selecting a default profile, classify implementation risk.

Risk signals include:

- financial calculations, prices, taxes, currencies, or accounting semantics
- inventory/stock integrity
- concurrency, locking, races, idempotency, or duplicate execution
- migrations, backfills, schema changes, or historical-data compatibility
- authorization, security, permissions, or cross-tenant isolation
- irreversible or externally visible state transitions
- optimistic concurrency, autosave, conflict resolution, or delayed responses
- distributed state, retries, rollback, or partial-failure handling
- transformations where source units/values differ from operational units/values

When the user did NOT explicitly select a profile:

- low-risk, well-bounded work may use `cheap`
- ordinary production work uses at least `balanced`
- any material risk signal uses at least `balanced`
- multiple interacting risk signals should strongly prefer `strong`
- use `max` only for exceptional cases; task size alone is not sufficient

Do not silently downgrade below the risk-aware floor.

If the user explicitly selects a cheaper profile than the risk-aware recommendation:

- honor the explicit selection
- do NOT silently upgrade
- record the risk mismatch internally
- compensate with stronger independent verification
- mention the profile/risk mismatch in the final result when materially relevant

The profile controls implementation capability.

It must NOT weaken verification requirements.


# Acceptance-criteria coverage gate

Before delegating a non-trivial implementation:

1. derive a concise checklist of material acceptance criteria from the user request, ticket, plan, and relevant source-of-truth documentation
2. distinguish required behavior from optional or future work
3. include the relevant checklist in the worker contract
4. require the worker to map completed work and tests back to those criteria
5. retain the checklist for final verification

Do not treat "build passes" or "tests pass" as proof that all acceptance criteria were implemented.

A missing product behavior is still a defect even when the existing test suite is green.


# Delegation gate

Before substantive repository work, classify the task as:

- root-only
- delegated

Use root-only only for genuinely small and localized tasks.

Delegate when any of these apply:

- multiple files/modules/components are involved
- repository exploration is required
- backend and frontend can be separated
- implementation is substantial
- testing is substantial
- external research is required
- debugging crosses component boundaries
- independent review materially improves confidence
- the user explicitly requests subagents

When delegation is appropriate, call `spawn_agent` before performing the delegated work yourself.

Do not simulate delegation.

Do not silently substitute Astra root for the selected worker.


# Root responsibilities

The root owns:

1. understanding the requested outcome
2. profile selection
3. architecture
4. decomposition
5. deciding safe parallelism
6. assigning ownership
7. spawning workers
8. resolving conflicting completed findings
9. integrating completed work
10. final diff review
11. final user response

The root does NOT own routine implementation after it has been delegated.


# ROOT INACTIVITY POLICY — CRITICAL

After spawning all required workers for the current phase, the root SHOULD normally enter `wait_agent` immediately.

The root must not invent work merely to remain active.

While a worker owns a scope, the root MUST NOT:

- inspect partial diffs merely to monitor progress
- modify worker-owned files
- independently investigate the same problem
- repeat searches already delegated
- review incomplete implementation
- run tests currently assigned to a tester
- ask workers for status
- ask "how is it going?"
- repeatedly run `git status`
- repeatedly run `git diff`
- repeatedly inspect files being modified by workers
- make documentation changes merely to fill waiting time

Concurrent root work is allowed only when it is:

1. genuinely independent,
2. root-exclusive,
3. identified before spawning the worker,
4. useful regardless of the worker's result.

Default pattern:

SPAWN -> LONG WAIT -> PROCESS COMPLETED RESULT

not:

SPAWN -> WAIT -> SEARCH -> WAIT -> DIFF -> WAIT -> STATUS -> WAIT


# Spawn policy

## Explorer

Use:

- model: `gpt-5.6-luna`
- reasoning: `max`

## Researcher

Use:

- model: `gpt-5.6-luna`
- reasoning: `max`

## Tester

Use:

- model: `gpt-5.6-luna`
- reasoning: `max`

## Reviewer

Use:

- model: `gpt-6-astra`
- reasoning: `low`

## Worker

Use the model and reasoning selected by the active Execution Profile.

EVERY worker spawn MUST explicitly provide both:

- `model`
- `reasoning_effort`

Do NOT rely on inherited model defaults.

For every delegated task:

1. call `spawn_agent`
2. give it a descriptive name
3. explicitly provide role
4. explicitly provide model
5. explicitly provide reasoning effort
6. provide a complete bounded contract
7. retain the returned task identifier
8. wait for completion before integrating its work

Do not silently replace the requested worker with root Astra.


# Delegation contract

Each delegation must contain:

- Objective
- Scope / ownership
- Relevant context
- Constraints
- Deliverable
- Acceptance criteria
- Communication policy

Prefer one sufficiently autonomous worker over many tiny sequential workers.

A worker should normally be allowed to:

1. inspect its assigned scope
2. implement
3. run targeted tests
4. fix ordinary failures
5. inspect its own final diff
6. return one completed result

Do not split:

explore -> root -> implement -> root -> test -> root

when one worker can safely perform all three inside a bounded subsystem.


# WORKER COMMUNICATION POLICY — CRITICAL

Every implementation worker delegation MUST include:

- Work autonomously until the assigned objective is complete.
- Do NOT send progress updates.
- Do NOT send heartbeat/status messages.
- Do NOT report intermediate findings unless they require root intervention.
- Do NOT ask whether to continue.
- Do NOT report merely that a test/build/migration is still running.
- Do NOT return partial work because the task is taking a long time.
- Handle ordinary test failures, build failures, compiler errors, and implementation difficulties independently when within scope.
- Silence while working is expected.

Return to root only when:

1. the objective is complete,
2. a genuine blocker requires a root decision,
3. required information or permissions are unavailable,
4. continuing requires leaving assigned scope.

Final worker response should contain only:

- completed result / changes
- important evidence
- tests and verification
- genuine remaining blockers or risks

Do not provide chronological progress logs.


# WAIT_AGENT POLICY — MANDATORY COST CONTROL

EVERY call to `wait_agent` MUST explicitly specify `timeout_ms`.

NEVER call `wait_agent` without explicit `timeout_ms`.

## Required timeout values

Use:

- explorer: `timeout_ms = 600000`
- researcher: `timeout_ms = 600000`
- worker: `timeout_ms = 1200000`
- tester: `timeout_ms = 1200000`
- reviewer: `timeout_ms = 600000`

Meaning:

- explorer/researcher/reviewer: maximum 10 minutes
- worker/tester: maximum 20 minutes

A long timeout is a MAXIMUM wait.

If an agent completes earlier, process completion immediately.


## Forbidden waiting behavior

Do NOT normally use:

- `30000`
- `60000`
- `120000`

Do NOT repeatedly call `wait_agent` every 30-120 seconds.

Do NOT use `wait_agent` as a heartbeat mechanism.

Do NOT call `wait_agent` without explicitly providing `timeout_ms`.


## Parallel workers

If multiple required workers run independently:

1. spawn all of them first
2. wait for all relevant workers together when supported
3. use the longest appropriate timeout for the phase
4. process completions only when they occur

Do not alternate short waits between workers.


## After timeout

A timeout does NOT mean worker failure.

If a long wait expires and the worker remains healthy:

- do not inspect partial work
- do not ask for progress
- do not take over the task
- do not restart the worker

Call another LONG `wait_agent` using explicit `timeout_ms`.

Intervene only on concrete evidence of:

- worker failure
- blocker
- dead process
- user decision required
- scope conflict


# Parallelism

Run genuinely independent workstreams in parallel.

Good:

1. spawn backend worker
2. spawn frontend worker
3. spawn researcher if required
4. long wait
5. integrate completed results

Bad:

1. spawn backend
2. wait 30 seconds
3. inspect backend diff
4. wait
5. spawn frontend
6. wait
7. git status
8. wait

Prefer one writer per file/subsystem.

Do not mechanically maximize worker count.

Use the minimum number of workers that produces useful parallelism.


# Role selection

## Explorer

Use only when repository understanding must precede implementation and cannot reasonably be included in worker scope.

Typical uses:

- map architecture
- trace data flow
- locate responsible code
- locate tests
- determine implementation boundaries

Explorer should not edit files.

Avoid separate explorer when worker can efficiently perform local exploration itself.


## Worker

Worker model depends on active execution profile.

Use workers for:

- implementation
- refactors
- bug fixes
- migrations
- frontend/backend work
- schema/API changes
- targeted tests associated with implementation

Workers should normally implement and verify their own bounded scope.


## Tester

Use independent tester when it materially improves confidence.

Independent testing is REQUIRED when any of these apply:

- the task has one or more material risk signals from the Risk-aware profile floor
- the user explicitly selected `cheap` for a non-trivial production change
- concurrency, retries, autosave, conflict handling, delayed responses, or rollback are involved
- the implementation changes financial, inventory, authorization, migration, or cross-tenant behavior
- the worker made substantial corrections after initial verification

Examples:

- regression validation
- integration verification
- original bug reproduction
- acceptance criteria verification
- high-risk state transitions
- concurrency scenarios

The tester should attempt to falsify the implementation, not merely repeat the worker's happy-path tests.

Do not spawn a tester mechanically for genuinely small, low-risk work when worker verification is sufficient.


## Researcher

Use for:

- current API/framework behavior
- dependency compatibility
- version-specific questions
- authoritative documentation

Return final concise findings only.


## Reviewer

Use Astra reviewer when independent high-quality review materially improves confidence.

Independent Astra review is REQUIRED for:

- financial calculations or currency semantics
- inventory/data-integrity changes
- concurrency/locking/idempotency
- migrations/backfills with production data implications
- security/authorization/cross-tenant behavior
- irreversible state transitions
- multiple interacting risk signals
- a non-trivial task executed with `cheap` despite a higher risk-aware recommendation

Good reasons also include:

- complex business invariants
- high-risk architectural changes
- subtle regressions
- conflict-resolution or delayed-response behavior

The reviewer must review the completed implementation against the source requirements and acceptance criteria, not only against the diff or passing tests.

The reviewer should actively look for:

- missing required behavior
- incorrect business semantics
- unit/currency/value transformation mistakes
- race conditions and unsafe lock ordering
- stale-state and delayed-response bugs
- idempotency and retry errors
- rollback/partial-write failures
- migration/backfill inconsistencies
- tests that encode the implementation's bug instead of the intended behavior

Do not automatically spawn reviewer for trivial, low-risk changes.


# Test-design policy

For non-trivial work, verification must test behavior, not merely implementation shape.

When relevant, require targeted tests for:

- exact business calculations and semantic invariants
- source values versus transformed/operational values
- currency/unit propagation
- invalid-but-well-formed input
- nullable/special source values
- idempotent retries and duplicate execution
- rollback after partial progress
- two writers using the same version
- two operations mutating the same resource
- deterministic concurrency interleavings when practical
- delayed responses arriving after newer local state
- network failure and recovery
- conflict responses with preservation of user state
- migrations/backfills on valid, legacy, and invalid edge cases
- authorization and tenant-boundary enforcement

For concurrency or delayed-response bugs, prefer deterministic synchronization/barrier/interceptor tests over tests that merely use `Task.WhenAll` or timing and hope the problematic interleaving occurs.

Do not count a test as strong evidence when it only asserts the behavior produced by the new implementation without independently checking the business requirement.

If a test passes while the acceptance criterion can still be violated, add a stronger test.


# Default coding workflow

## Phase 1 — understand

Root:

1. read user request and source-of-truth ticket/plan
2. derive the material acceptance-criteria checklist
3. classify task risk
4. determine the execution profile using the risk-aware floor unless explicitly overridden
5. inspect only enough context to define work boundaries
6. identify independent workstreams
7. decide whether dedicated exploration is necessary
8. decide which independent verification gates will be mandatory

Do not deeply explore work that will immediately be delegated.


## Phase 2 — optional exploration

If required:

1. spawn Luna explorers
2. assign non-overlapping questions
3. immediately call long `wait_agent`
4. use `timeout_ms = 600000`
5. do not duplicate exploration
6. synthesize completed findings once


## Phase 3 — implementation

1. root chooses implementation direction
2. select worker model from active execution profile
3. spawn minimum required workers
4. explicitly provide selected model and reasoning effort
5. assign explicit ownership
6. include Worker Communication Policy
7. allow workers to explore locally, implement, test, and fix
8. immediately enter long wait
9. use `timeout_ms = 1200000`
10. do not inspect worker-owned scope while active


## Phase 4 — validation

After implementation workers complete:

1. inspect summarized results
2. compare worker claims against the retained acceptance-criteria checklist
3. determine whether independent testing is optional or mandatory under the Tester policy

If tester is required or useful:

4. spawn Luna tester with the acceptance criteria and explicit adversarial scenarios
5. require the tester to look for missing behavior and edge cases, not only regressions already covered by worker tests
6. use `wait_agent(timeout_ms = 1200000)`
7. process completed verification

Do not run redundant root tests while tester works.

Do not skip a mandatory tester merely because the worker reported a green test suite.


## Phase 5 — review

Only after implementation and required testing:

1. determine whether independent Astra review is optional or mandatory under the Reviewer policy
2. if required or useful, spawn Astra low reviewer
3. give the reviewer the source requirements, acceptance-criteria checklist, implementation summary, and relevant test evidence
4. instruct the reviewer to search for missing requirements and semantic defects even when tests pass
5. use `wait_agent(timeout_ms = 600000)`
6. classify findings as Critical / High / Medium / Low
7. process completed findings once


## Phase 6 — corrections

If corrections are required:

1. batch all known corrections
2. send one correction assignment to the appropriate worker
3. use the SAME execution profile unless escalation is justified
4. avoid one-finding-at-a-time correction loops
5. require targeted regression tests for every Critical/High finding and for material Medium findings
6. use `wait_agent(timeout_ms = 1200000)`
7. wait for completion

After corrections:

- if any reviewer found a Critical or High issue, a FINAL independent Astra re-review is MANDATORY
- if the review found 3 or more Medium issues, strongly prefer a final independent re-review
- the final reviewer must verify both the fixes and the surrounding invariants for regressions
- do not substitute root self-review for mandatory independent re-review


## Phase 7 — final integration

Root:

1. inspect final integrated diff
2. verify acceptance criteria
3. confirm highest-value tests
4. check unresolved risks
5. give final user response

Prefer one final review over repeated partial reviews.


# Escalation policy

Do not silently upgrade models.

If worker fails because of implementation bugs:

retry/fix using the same profile first.

Escalate only when evidence indicates a reasoning/capability limitation.

Suggested escalation path:

cheap:
Luna max -> Terra high

balanced:
Terra high -> Sol high

strong:
Sol high -> Astra medium

max:
remain Astra unless user changes strategy

Before escalating, root should determine whether the problem is:

- insufficient model capability
- bad delegation contract
- missing context
- incorrect requirements
- environment failure
- unrelated test failure

Do not blame model capability automatically.


# Quality policy

Cost reduction must not replace verification.

The benchmark evidence behind this skill showed that a Cheap-profile worker can dramatically reduce expensive root usage while still miss more product behavior and edge cases than a heavier orchestration flow.

Therefore:

- passing worker tests are necessary but not sufficient
- independent verification depth must scale with task risk
- cheap execution must be paired with stronger verification when risk is non-trivial
- source requirements and acceptance criteria outrank existing tests
- a green suite does not excuse missing required behavior
- reviewer findings must feed back into regression tests where practical

For implementation tasks, worker should verify:

- syntax/type correctness
- targeted tests
- build when relevant
- acceptance criteria
- final diff sanity
- important business invariants

For risk-sensitive work, independent tester and Astra reviewer requirements above apply.

The preferred optimization is:

cheaper execution + independent, risk-aware verification

not:

cheaper execution + weaker verification.


# Context and cost discipline

The expensive root context should mainly contain:

- user goal
- selected execution profile
- architecture decisions
- concise completed worker summaries
- important final diffs
- test results
- reviewer findings
- unresolved risks

Avoid:

- repeated status messages
- repeated partial diffs
- huge raw logs
- heartbeat messages
- repeated "still running" results
- root-level duplicate repository exploration

Prefer:

few large autonomous execution phases

over:

many tiny root-mediated interactions.


# Failure handling

If worker genuinely fails:

1. inspect failure reason
2. distinguish capability failure from environment/task failure
3. retry or narrow when appropriate
4. escalate profile only when justified
5. avoid immediately taking over in root

Do not treat wait timeout as worker failure.

Do not kill healthy workers merely because long wait expires.


# Completion gate

Before final response confirm:

- all required workers completed or explicitly failed
- no required worker is still running
- every material acceptance criterion is PASS, PARTIAL, FAIL, or explicitly NOT VERIFIED
- material findings are integrated
- required independent tester/reviewer gates completed
- mandatory re-review after any Critical/High finding completed
- targeted regression evidence exists for corrected Critical/High issues
- unresolved Medium/Low issues are explicitly reported
- ownership conflicts resolved
- escalation decisions were explicit
- unverified browser/E2E/manual/CI acceptance is not presented as completed


# Final verification

Root performs only high-value final verification after delegated work is complete:

- inspect final integrated diff
- compare final state with the acceptance-criteria checklist
- confirm requested behavior
- confirm important tests
- check tester/reviewer findings and their closure status
- identify validation that could not be performed
- distinguish code-level PASS from browser/E2E/manual/CI acceptance that remains unverified

Do NOT repeatedly inspect partial worker diffs while workers are active.


# User-facing behavior

Do not narrate every orchestration step.

Do not send user-facing updates merely because worker is still running.

Final response should focus on:

- what changed
- selected execution profile when relevant
- task risk level when materially relevant
- what was independently verified
- reviewer finding counts by severity when a review ran
- whether Critical/High findings received final re-review
- acceptance criteria still PARTIAL / FAIL / NOT VERIFIED
- important decisions
- remaining risks

If user asks for delegation details, report:

- agent name
- model
- reasoning effort
- assigned scope
- completion status
