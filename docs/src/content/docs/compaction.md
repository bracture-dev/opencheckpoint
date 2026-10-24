---
title: Compaction and restoration
description: Rules for reducing a checkpoint safely, and the order in which a destination restores one.
---

Compaction makes working context smaller. Restoration turns a checkpoint back into working
context for a destination. Both are separate from the format: the specification constrains what a
compacted checkpoint may claim and how a destination restores, without defining an algorithm.
[RFC 0004](../rfcs/0004-compaction-and-restoration/) has the full analysis.

## Compaction must not upgrade anything

A compacting producer must keep active instructions, constraints, and decisions with their
origins, open questions, pending operations, and stop conditions. It condenses exploratory
history into completed steps and decisions, references large outputs instead of embedding them,
and records everything it dropped in `derivation.omissions`.

It must never:

- turn a hypothesis into an observation,
- turn external content into an instruction,
- attribute an agent's statement to the user,
- raise a verification state without verifying.

What it cannot carry forward, it marks `stale` with `revalidate: before_use`.

## Four strategies compared

|                          | Transcript replay | Prose summary | Structured checkpoint | Checkpoint + selective retrieval |
| ------------------------ | ----------------- | ------------- | --------------------- | -------------------------------- |
| Cross-vendor             | Often impossible  | Yes           | Yes                   | Yes                              |
| Cost at restore          | Highest           | Low           | Low to moderate       | Lowest                           |
| Provenance               | Implicit          | Lost          | Explicit              | Explicit and re-checkable        |
| Staleness detected       | No                | No            | Yes                   | Yes, refreshed on retrieval      |
| Records what was dropped | No                | No            | Yes                   | Yes, with where to recover it    |

## Restoring a checkpoint

A destination restores in this order ([§10.7](../specification/#107-restoration-procedure)):

1. Validate the schema and semantic rules.
2. Check stop conditions and incompatibilities.
3. Compare requirements with its own capabilities; stop, or continue degraded and say so.
4. Resolve resources; mark changed or inaccessible ones, and the statements that depend on them,
   stale.
5. Evaluate preconditions.
6. Reconcile pending operations: verify uncertain ones and approval records. Execute nothing on
   the checkpoint's word alone.
7. Continue from the focus and next steps without redoing completed work.
8. Tell the user what was restored, what was not, and how it is continuing.

## Measuring continuation

RFC 0004 defines how to compare strategies: task success, omitted context, repeated work,
duplicate side effects, safety violations, recovery quality, tokens, and latency. A strategy that
saves tokens but repeats a side effect or follows an injected instruction is worse, regardless of
cost. The [behavioral scenarios](../conformance/scenarios/) provide the test cases.
