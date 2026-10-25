---
title: Forking a baseline
description: Build expensive context once, then start several agents from it to test, compare, or explore. When it pays off, and how to do it safely.
---

Building context is often the expensive part of a task: reading a codebase, loading and
reconciling a ledger, ruling out explanations. Once that context is captured in a checkpoint,
several agents can start from the same **baseline** at once, to test, compare, or explore, without
each paying to rebuild it. The normative rules are in
[§9.3 of the specification](../specification/#93-forking-a-checkpoint).

## How it works

1. An agent does the costly groundwork and captures a baseline checkpoint.
2. A producer creates N forks: new checkpoints whose `parent` is the baseline, each optionally
   varied (a different constraint, hypothesis, or instruction).
3. Each fork is continued independently, possibly by different agents, runtimes, or models.

## Does it hold up?

### Does forking already exist?

Yes, inside single runtimes. LangGraph forks a thread by writing a new checkpoint with
`update_state`, and supports returning to earlier checkpoints. pi branches sessions in place and
offers `/fork` and `/clone`. Claude Code can fork a session. ACP has a `session/fork` method in
its unstable schema. The OpenAI Agents SDK has a branching session store. The Agent Session
Protocol records `fork` as a lineage relation. Research on agent handoffs builds its test sets
the same way: the _Handoff Debt_ study derived 181 handoff points from recorded trajectories and
continued each under different conditions ([Prior art](../prior-art/)).

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

The claim should be measured, not assumed. The [continuation metrics](../compaction/#measuring-continuation) apply, with B amortized over N.

### What breaks

The serious risk is **side effects in shared systems**. If the baseline has a pending,
non-idempotent operation (post the credit memo, refund the charge), every fork inherits it, and
each destination's reconciliation step may conclude it should act. Forks also act on the same
external systems as each other: two forks updating the same schedule collide.

A second risk is **replay detection**. Specification §10.3 tells a destination to check for a
newer checkpoint in the lineage. Sibling forks are all "newer" than the baseline, so that check
cannot tell a stale replay from a legitimate sibling. The rules below address both.

## Where it fits

| Scenario                                                                                                                                                           | Holds?                | Notes                                                                                                                                                                                                                                                                |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Evaluating agents or models.** The same checkpoint is continued by several agents, runtimes, or models, and the results are compared.                            | Strong                | This is the [continuation measurement protocol](../compaction/#measuring-continuation), and the behavioral scenarios are baselines. Read-only or sandboxed.                                                                                                          |
| **Regression fixtures.** A library of frozen baselines; each new agent version is run from each one.                                                               | Strong                | Treat baselines as test data, versioned with the suite. Pair them with environment snapshots.                                                                                                                                                                        |
| **Adversarial testing.** Fork a baseline and inject a forged approval, an instruction disguised as external content, or a stale resource, to test the destination. | Strong                | The [threat model](../security/#threat-model) becomes executable. Mark injected content in the fork's `derivation.transformations`.                                                                                                                                  |
| **Parallel exploration.** One fork per hypothesis or approach, explored at once; the best result is kept.                                                          | Strong when read-only | Investigation, analysis, and drafting fork well. Forks that write to shared systems need isolation (see [One owner per pending action](#one-owner-per-pending-action)).                                                                                              |
| **Delegating to subagents.** A lead agent hands each subagent a narrowed fork: same constraints and evidence, a smaller objective.                                 | Strong                | Today such briefs are prose. A fork keeps provenance and constraints intact. Narrow `task.objective` and `scope`.                                                                                                                                                    |
| **What-if analysis.** Fork a financial analysis with a different materiality threshold, or an operations plan with a store reopened.                               | Holds with care       | The varied statement must be recorded honestly. If a person changes a constraint in the fork, the new statement's origin is that person, and the edit is recorded in `derivation.transformations`. A fork must not silently rewrite the baseline user's instruction. |
| **Rolling back.** A continuation goes wrong; restart from the baseline instead.                                                                                    | Partly                | Works for knowledge. Does not undo side effects the failed branch performed. The failed branch's completed operations must be reconciled, not forgotten.                                                                                                             |
| **Reusable starting points.** A "month-end close" baseline re-instantiated every month.                                                                            | Weak                  | This drifts into memory ([specification §1.3](../specification/#13-checkpoints-and-memory)): stale by design. Capture a fresh baseline each time, or use a template outside this format.                                                                             |

## How to fork

Each fork is a new checkpoint:

- a new `id`, with `parent.id` (and ideally `parent.digest`) set to the baseline;
- `derivation.method` set to `forked`, `derivation.inputs` naming the baseline, and
  `derivation.transformations` recording what the fork changed;
- changed statements added as new statements with their real origin, superseding the baseline's,
  never edited in place.

```json
{
  "parent": { "id": "urn:uuid:…baseline" },
  "derivation": {
    "method": "forked",
    "inputs": [{ "checkpoint": "urn:uuid:…baseline" }],
    "transformations": [
      {
        "description": "Materiality threshold lowered to $25k for this branch.",
        "affected": ["s-instr-materiality-25k"]
      }
    ]
  }
}
```

## One owner per pending action

Every fork inherits the baseline's pending operations. If the baseline is waiting to refund a
charge, every fork may try to refund it. When you create more than one fork, each pending action
with a side effect must stay actionable in **one** fork only. In the others, add a stop condition
that references it, or remove it and record the removal in `derivation.omissions`. Validators warn
(OCP-W004) when a fork carries such an action with no stop condition guarding it.

## Not yet defined

- **Merging forks back.** `derivation.method: merged` with several inputs exists, but what happens
  when two forks reach different decisions is undefined.
- **Forking environments.** A checkpoint references resources and never contains them; snapshot
  the environment separately.
