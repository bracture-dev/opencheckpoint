---
title: Forking a baseline
description: Build expensive context once, then start several agents from it to test, compare, or explore.
---

Building context is often the costly part of a task. Once it is captured in a checkpoint, several
agents can start from the same **baseline** at once without each rebuilding it.
[RFC 0006](../rfcs/0006-forking-from-a-baseline/) audits the idea in full; this page is the
practical summary.

## When it pays off

Forking saves the groundwork cost once per extra fork. It pays when the groundwork's value is in
**conclusions** (findings, decisions, ruled-out paths) rather than in a warm environment, and it
pays most across models, vendors, or longer intervals, where you cannot just replay a cached
transcript.

| Good fit                                              | Poor fit                                                                                                          |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Comparing agents or models on the same starting state | Groundwork that is mostly environment setup (snapshot the environment instead)                                    |
| Regression fixtures for agent releases                | A baseline reused for weeks (it goes stale, and starts acting like [memory](../concepts/#checkpoints-and-memory)) |
| Injecting adversarial content to test a destination   | Forks that all write to the same external system without isolation                                                |
| Exploring several hypotheses in parallel, read-only   |                                                                                                                   |
| Briefing subagents with a narrowed objective          |                                                                                                                   |

## How to fork with v0.1

Create a new checkpoint for each fork:

- a new `id`, with `parent.id` (and ideally `parent.digest`) set to the baseline;
- `derivation.inputs` naming the baseline, and `derivation.transformations` recording what the
  fork changed;
- changed statements added as new statements with their real origin, superseding the baseline's,
  never edited in place.

```json
{
  "parent": { "id": "urn:uuid:…baseline" },
  "derivation": {
    "method": "authored",
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

## Pending operations: one owner

Every fork inherits the baseline's pending operations. If the baseline is waiting to refund a
charge, every fork may try to refund it. Before fanning out, give each pending operation that has
a side effect to **one** fork. In the others, add a stop condition that references it, or remove
it and record the removal in `derivation.omissions`.

RFC 0006 proposes making this a rule, and adding a `forked` derivation method so destinations
know sibling forks may exist.
