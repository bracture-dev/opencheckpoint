---
title: Core concepts
description: The parts of a checkpoint and how they fit together.
---

This page explains the model informally. The [specification](../specification/) is normative.

## The smallest checkpoint

```json
{
  "opencheckpoint": "0.1",
  "id": "urn:uuid:0b6f2f1e-4d3a-4c8e-9a51-2f6b7c1d0e01",
  "created_at": "2026-10-20T18:30:00Z",
  "source": { "producer": { "name": "example-agent" } },
  "task": {
    "objective": "Reconcile the October vendor invoices against purchase orders.",
    "status": "active"
  }
}
```

Everything else is optional. Producers add what the destination needs.

## Task

`task` holds the objective, the desired outcome, the status (`active`, `blocked`,
`awaiting_input`, `paused`, `completed`, `abandoned`), success criteria with their state, and
what is in and out of scope.

## Progress

`progress.completed` lists work already done, so the destination does not redo it.
`progress.focus` says what was in hand at the boundary. `progress.next` lists recommended next
steps, each of which can say what blocks it.

There is no separate "blocker" object. A blocker is always an open question, a pending
operation, an unavailable resource, or an unmet requirement, referenced from `blocked_by`.

## Statements

Statements record what is known about the work and what governs it. Each has a `kind`:

| Kind          | Example                                                              |
| ------------- | -------------------------------------------------------------------- |
| `instruction` | "Only break out drivers over $50k." (from the user)                  |
| `constraint`  | "Read-only access to finance systems." (from policy)                 |
| `decision`    | "Compare against budget B2, not the reforecast," with its rationale. |
| `observation` | "14 of 212 invoices have no PO number," with evidence.               |
| `hypothesis`  | "The missing POs come from the new portal's export."                 |
| `question`    | "Do freight surcharges count toward the threshold?"                  |
| `external`    | A vendor email asking to "skip the usual approval."                  |

Each statement has an `origin` (`user`, `system`, `agent`, `tool`, `application`, `external`)
and can carry `verification` (`verified`, `unverified`, `disputed`, `stale`) with a rule for when
to re-check it.

The schema enforces the safety-critical combinations: an instruction can only come from the user
or the system, a hypothesis can never be marked verified, and external content can never be
attributed to the user.

## Resources

A resource is anything outside the checkpoint that the task involves: a file, repository,
document, database record, business object, web page, artifact, tool output, dataset, or
message. It is identified by a `uri` in any scheme or by a `locator` (system, type, key) for
objects without one. `revision`, `digest`, and `observed_at` let a destination detect that a
resource changed after capture. A resource does not need to be public, and a reference never grants
access.

## Application context

Application context carries state from the applications the user works in: the current view,
selected or open objects, filters, unsaved drafts, and application-defined state. Much of it
never appeared in conversation. OpenCheckpoint records what a destination needs to understand,
not a full UI model.

## Operations

Operations are unfinished work involving someone or something outside the agent: an `approval`,
a request for `input`, a side-effecting `action`, or a `wait`. Each has a status, and actions say
what repeating them would do (`effect`) and what the source recommends (`resume`). An action
that was started and not confirmed is `uncertain`, and if it might not be idempotent, the schema
forbids recommending a blind retry. An action can also record the `call` it stands for, the
tool and its arguments, so software in front of the tools can refuse to repeat a completed
payment without asking a model.

An approval's outcome is a record backed by evidence in a system of record, and it never gives
the destination permission to act.

## Continuation

`continuation` lists the tools, capabilities, access, and extensions the work needs, each
`required`, `recommended`, or `optional` with a fallback; preconditions to check first; stop
conditions under which no one should continue; recommended recovery steps; and known
incompatibilities. A destination that lacks some of them can use the fallbacks and continue in
degraded form.

A stop condition can name the operations it forbids (`applies_to`) and what lifts it (`until`),
for example "refund nothing until approval RA-1192 is approved". An operation's `record` says
where its status lives, so a guard can hold the refund and release it once the billing system,
not the checkpoint, shows the approval.

## Derivation

`derivation` records how the checkpoint was produced (`captured`, `compacted`, `merged`,
`converted`, `authored`), from which inputs, what was deliberately left out and why, and what
was condensed. A compacted checkpoint that does not say what it dropped is not conforming.

## Checkpoints and memory

Memory is what an assistant keeps about you, your projects, and your
preferences across many tasks, retrieved a piece at a time when it seems relevant. A checkpoint
is the state of one task at one moment, read whole when the work changes hands, and replaced by
the next checkpoint.

|          | Checkpoint                                                             | Memory                             |
| -------- | ---------------------------------------------------------------------- | ---------------------------------- |
| Scope    | One task                                                               | Many tasks, a user, a project      |
| Shape    | Snapshot at a capture time                                             | Accumulates over time              |
| Use      | Read whole, at a handoff                                               | Retrieved by relevance             |
| Lifetime | Superseded; done when the task ends                                    | Persists until edited or forgotten |
| Carries  | Provenance, verification, staleness, pending operations, preconditions | Usually remembered facts           |

They meet at the edges: a producer can draw on memory when writing a checkpoint, and lessons from
a finished task can be saved to memory. A checkpoint should not become a long-lived store updated
across tasks. If you reuse the same starting state over weeks, capture it again so its timestamps
and verification states stay true. See [§1.3 of the specification](../specification/#13-checkpoints-and-memory).

## Extensions

Domain-specific data goes in `extensions` maps keyed by reverse-DNS names such as
`com.example.crm`. Consumers ignore keys they do not understand and preserve them when
re-serializing. Core objects reject undefined fields, so the schema catches typos.
