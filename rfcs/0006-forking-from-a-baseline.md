---
rfc: 0006
title: Forking from a baseline
status: Draft
type: Standards Track
created: 2026-10-24
authors: OpenCheckpoint maintainers
---

# RFC 0006: Forking from a baseline

## Abstract

Building context is often the expensive part of a task: reading a codebase, loading and
reconciling a ledger, ruling out explanations. Once that context is captured in a checkpoint,
several agents can start from it at once to test, compare, or explore different paths without
each paying to rebuild it. This RFC audits that idea, lists the scenarios where it does and does
not hold, shows how to express a fork with v0.1 as it stands, and proposes two small changes:
a `forked` derivation method and a rule for who owns pending operations after a fork.

## The idea

1. An agent does the costly groundwork and captures a **baseline** checkpoint.
2. A producer creates **N forks**: new checkpoints whose `parent` is the baseline, each
   optionally varied (a different constraint, hypothesis, or instruction).
3. Each fork is continued independently, possibly by different agents, runtimes, or models.

The claimed benefit is efficiency: pay for the groundwork once instead of N times.

## Audit

### Does forking already exist?

Yes, inside single runtimes. LangGraph forks a thread by writing a new checkpoint with
`update_state`, and supports returning to earlier checkpoints. pi branches sessions in place and
offers `/fork` and `/clone`. Claude Code can fork a session. ACP has a `session/fork` method in
its unstable schema. The OpenAI Agents SDK has a branching session store. The Agent Session
Protocol records `fork` as a lineage relation. Research on agent handoffs builds its test sets
the same way: the _Handoff Debt_ study derived 181 handoff points from recorded trajectories and
continued each under different conditions (RFC 0002).

None of these forks crosses runtimes or models, and none produces a readable baseline that a
person can inspect or edit before fanning out. That is what OpenCheckpoint adds. The idea is
not new; making it portable is.

### Does the efficiency claim hold?

Partly. With a baseline costing B to build, N forks, and a per-fork restore cost R:

- Without forking, total groundwork is N × B.
- With forking, it is B + N × R.
- Forking saves roughly (N − 1) × B − N × R. It pays when B is much larger than R.

The claim holds when **the groundwork's value is in conclusions**: findings, decisions, ruled-out
paths, a reconciled number. It weakens in four cases:

1. **The world is not forked.** A checkpoint carries knowledge about resources, not the resources.
   Each fork still needs its own repository checkout, database, or sandbox. When B is mostly
   environment setup, forking a checkpoint saves little; snapshot the environment instead.
2. **Same provider, same model, run soon.** Provider prompt caching already makes replaying a
   shared transcript prefix cheap within the cache lifetime. There the checkpoint's advantage is
   smaller context and less distraction, not raw token cost. The cost advantage is largest across
   models, vendors, and longer intervals.
3. **Compression loses nuance.** Forks start from a summary. For tests that is a feature (every
   fork starts from the same controlled state). For real work, a fork may lack detail the
   baseline's agent had.
4. **Baselines age.** A baseline reused days later has stale evidence. The verification and
   precondition machinery handles this, but re-validation is a per-fork cost that grows with age.

The claim should be measured, not assumed. RFC 0004's metrics apply, with B amortized over N.

### What breaks

The serious risk is **side effects in shared systems**. If the baseline has a pending,
non-idempotent operation (post the credit memo, refund the charge), every fork inherits it, and
each destination's reconciliation step may conclude it should act. Forks also act on the same
external systems as each other: two forks updating the same schedule collide.

A second risk is **replay detection**. Specification §10.3 tells a destination to check for a
newer checkpoint in the lineage. Sibling forks are all "newer" than the baseline, so that check
cannot tell a stale replay from a legitimate sibling.

## Scenarios

| Scenario                                                                                                                                                           | Holds?                | Notes                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Evaluating agents or models.** The same checkpoint is continued by several agents, runtimes, or models, and the results are compared.                            | Strong                | This is RFC 0004's measurement protocol, and the behavioral scenarios are baselines. Read-only or sandboxed.                                                                                                                                                         |
| **Regression fixtures.** A library of frozen baselines; each new agent version is run from each one.                                                               | Strong                | Treat baselines as test data, versioned with the suite. Pair them with environment snapshots.                                                                                                                                                                        |
| **Adversarial testing.** Fork a baseline and inject a forged approval, an instruction disguised as external content, or a stale resource, to test the destination. | Strong                | The threat model (RFC 0005) becomes executable. Mark injected content in the fork's `derivation.transformations`.                                                                                                                                                    |
| **Parallel exploration.** One fork per hypothesis or approach, explored at once; the best result is kept.                                                          | Strong when read-only | Investigation, analysis, and drafting fork well. Forks that write to shared systems need isolation (see below).                                                                                                                                                      |
| **Delegating to subagents.** A lead agent hands each subagent a narrowed fork: same constraints and evidence, a smaller objective.                                 | Strong                | Today such briefs are prose. A fork keeps provenance and constraints intact. Narrow `task.objective` and `scope`.                                                                                                                                                    |
| **What-if analysis.** Fork a financial analysis with a different materiality threshold, or an operations plan with a store reopened.                               | Holds with care       | The varied statement must be recorded honestly. If a person changes a constraint in the fork, the new statement's origin is that person, and the edit is recorded in `derivation.transformations`. A fork must not silently rewrite the baseline user's instruction. |
| **Rolling back.** A continuation goes wrong; restart from the baseline instead.                                                                                    | Partly                | Works for knowledge. Does not undo side effects the failed branch performed. The failed branch's completed operations must be reconciled, not forgotten.                                                                                                             |
| **Reusable starting points.** A "month-end close" baseline re-instantiated every month.                                                                            | Weak                  | This drifts into memory (specification §1.3): stale by design. Capture a fresh baseline each time, or use a template outside this format.                                                                                                                            |

## Expressing a fork in v0.1

A fork is a new checkpoint:

- a new `id`;
- `parent.id` set to the baseline's id, and preferably `parent.digest`;
- `derivation.inputs` naming the baseline;
- `derivation.transformations` recording what the fork varied, with `affected` naming the changed
  objects;
- changed statements recorded as new statements with their real origin, superseding the
  baseline's where appropriate, never edited in place.

Pending operations can be isolated with existing fields: in every fork except one, add a stop
condition that names the operation ("Do not act on op-refund; it is owned by another branch"),
or remove the operation and record the removal in `derivation.omissions`.

v0.1 has no value of `derivation.method` that says "forked", so a fork today uses `authored`
(edited) or `captured` (unchanged copy). That is the first gap.

## Proposed changes

### 1. A `forked` derivation method

Add `forked` to `derivation.method`: "a copy of the parent, possibly varied, intended to be
continued alongside other copies." Consumers then know siblings may exist, which fixes the
replay-detection ambiguity: a destination that finds sibling forks is not looking at a stale
replay.

### 2. Operation ownership after a fork

Add a normative rule:

> When a producer creates more than one fork of a checkpoint, each non-terminal operation whose
> `effect` is not `none` MUST remain actionable in at most one fork. In every other fork, the
> producer MUST either remove it, recording the removal in `derivation.omissions`, or add a stop
> condition that references it.

Add a semantic warning: a checkpoint with `derivation.method: forked` that carries a
non-terminal operation with a side effect and no stop condition referencing it (OCP-W004). It
is a warning rather than an error because a single fork is legitimate.

### Considered and deferred

- **A `fork_of` relation separate from `parent`.** `parent` plus `derivation.method` is enough.
- **Merging forks back.** `derivation.method: merged` with several `inputs` already exists, but
  conflict semantics (two forks reach different decisions) are undefined. Defer until an
  implementation needs it.
- **Forking environments.** Out of scope; a checkpoint references resources and never contains
  them.

## Compatibility

Both changes are additive. Pre-1.0 they ship in the next minor version.

## Security

Forking multiplies the side-effect risk and weakens replay detection; the ownership rule and the
`forked` method address both. Forks used for adversarial testing contain deliberately hostile
content and must be labelled in `derivation.transformations` and kept out of production use.
RFC 0005 gains a threat: duplicate side effects across sibling forks.

## Conformance

If accepted: a valid fixture for a fork with an isolated operation; a fixture producing OCP-W004;
a scenario in which two destinations continue sibling forks of the customer-support example and
exactly one refund is issued.
