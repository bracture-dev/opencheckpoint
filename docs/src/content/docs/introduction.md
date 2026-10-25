---
title: Introduction
description: What OpenCheckpoint is, what it is not, and where to start.
---

OpenCheckpoint lets you pick up where you left off with any AI, without starting over or
explaining everything again.

It defines a **checkpoint**: a JSON document that records the working state of an unfinished
AI-assisted task at a well-defined boundary. Another agent, runtime, model, or person can read it,
check it against the world, and continue the work with their own tools.

## What a checkpoint answers

1. What is the user or system trying to accomplish?
2. What work is already done?
3. What was being worked on?
4. What has been learned, and on what evidence?
5. Which decisions, instructions, and constraints still apply, and who made them?
6. Which files, records, documents, and application objects are involved?
7. Which approvals, requests, and actions are pending or blocked?
8. What should happen next?
9. What must be verified before anyone continues?

## What a checkpoint is not

- **Not a transcript.** It can point to one kept elsewhere, but it does not contain it.
- **Not model state.** No KV caches, hidden reasoning, or provider-specific blobs.
- **Not memory.** It describes one task at one point, not everything an assistant knows
  across tasks. [Core concepts](../concepts/#checkpoints-and-memory) explains the difference.
- **Not a permission slip.** Nothing in a checkpoint authorizes the destination to do anything.
- **Not a protocol.** It travels inside MCP, A2A, ACP, or any other channel.

## Where to go next

- [Why OpenCheckpoint](../why/) explains the problem and the alternatives.
- [Core concepts](../concepts/) walks through the parts of a checkpoint.
- [The specification](../specification/) is the normative definition, with the
  [schema reference](../reference/schema/) beside it.
- [Examples](../examples/) show complete checkpoints from four domains.
