---
title: Forking a baseline
description: Start several agents from one checkpoint to compare, test, explore, or delegate.
---

A fork is a new checkpoint derived from a parent and continued alongside other copies. With
forking, the costly part of a task (building context) happens once: an agent captures a
**baseline**, and any number of forks start from it. The normative rules are in
[§9.3 of the specification](../specification/#93-forking-a-checkpoint).

## How it works

1. An agent does the groundwork and captures a baseline checkpoint.
2. A producer creates N forks: new checkpoints whose `parent` is the baseline, each optionally
   varied (a different constraint, hypothesis, or instruction).
3. The same or different agents, runtimes, or models continue each fork independently.

## Uses

| Use                                                                                                                                                                                                                                                            | How the forks differ                                                                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Evaluating agents and models.** Several agents, runtimes, or models continue the same baseline and the results are compared. This is the [continuation measurement protocol](../compaction/#measuring-continuation); the behavioral scenarios are baselines. | The destination. The checkpoint is identical.                                                                                        |
| **Regression testing.** A library of baselines, versioned with the test suite, is run against each new agent release.                                                                                                                                          | The agent version.                                                                                                                   |
| **Adversarial testing.** A fork contains a forged approval, an instruction disguised as external content, or a stale resource, and tests how the destination responds. The [threat model](../security/#threat-model) becomes a set of executable cases.        | Injected content, labelled in `derivation.transformations`.                                                                          |
| **Parallel exploration.** One fork per hypothesis or approach runs at once, and the best result is kept.                                                                                                                                                       | The hypothesis or approach under investigation.                                                                                      |
| **Delegating to subagents.** A lead agent gives each subagent a fork with the same constraints and evidence and a narrower objective.                                                                                                                          | `task.objective` and `task.scope`.                                                                                                   |
| **What-if analysis.** A financial analysis is forked with a different materiality threshold, or an operations plan with a store reopened.                                                                                                                      | A constraint or decision, added as a new statement whose origin is the person who changed it.                                        |
| **Restarting from a known state.** A continuation that went wrong is abandoned and the baseline is forked again.                                                                                                                                               | Nothing; the new fork replaces the abandoned one. Operations the abandoned branch completed are reconciled before the new fork acts. |

## What a fork carries

A fork carries the baseline's knowledge: its findings, decisions, constraints, evidence, and
pending operations. It does not carry:

- **The environment.** Each fork needs its own repository checkout, database, or sandbox. Snapshot
  environments separately when they are expensive to rebuild.
- **The world's history.** Restarting from a baseline does not undo side effects a previous branch
  performed.
- **Freshness.** A baseline ages like any checkpoint. Forks created long after the baseline
  re-check the statements marked for revalidation. When you need the same starting state over
  weeks, capture a new baseline instead of reusing the old one, because a long-lived baseline behaves like
  [memory](../concepts/#checkpoints-and-memory).

## Cost

With a baseline that costs B to build, N forks, and a per-fork restore cost R, total groundwork is
B + N × R instead of N × B. The saving grows with B and N and is largest when the groundwork's
value is in conclusions (findings, decisions, ruled-out paths) rather than in environment setup.

Within one provider and model, prompt caching also makes replaying a shared transcript prefix
cheap for the cache's lifetime. Checkpoint forks extend the saving across models, vendors, and
longer intervals, and give each fork a smaller, structured context. The
[continuation metrics](../compaction/#measuring-continuation) measure both, with B amortized over N.

## How to fork

Each fork is a new checkpoint:

- a new `id`, with `parent.id` (and preferably `parent.digest`) set to the baseline;
- `derivation.method` set to `forked`, `derivation.inputs` naming the baseline, and
  `derivation.transformations` recording what the fork changed;
- changed statements added as new statements with their actual origin, superseding the baseline's
  rather than editing them.

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

Every fork inherits the baseline's pending operations, and forks act on the same external systems.
When there are several forks, each pending action with a side effect is actionable in one fork
only. The other forks either carry a stop condition that references it, or omit it and record the
omission in `derivation.omissions`. Validators warn (OCP-W004) when a fork carries such an action
with no stop condition guarding it.

`derivation.method: forked` also tells a destination that sibling forks may exist, so it does not
mistake a sibling for a stale replay of the baseline.

## Forking in other systems

Several runtimes fork within themselves: LangGraph forks threads with `update_state`, pi offers
`/fork` and `/clone`, Claude Code forks sessions, the OpenAI Agents SDK has a branching session
store, ACP defines an unstable `session/fork`, and the Agent Session Protocol records `fork` as a
lineage relation. Handoff research builds test sets the same way, continuing recorded trajectories
from fixed points ([Prior art](../prior-art/)). A checkpoint fork works across runtimes and models,
and a person can read and edit its baseline before anyone creates the forks.

## Not yet defined

- **Merging forks.** `derivation.method: merged` with several inputs exists, but the
  specification does not yet say how to reconcile forks that reach different decisions.
- **Forking environments.** Checkpoints reference resources and never contain them.
