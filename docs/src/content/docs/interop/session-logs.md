---
title: Session logs and runtimes
description: How checkpoints relate to session formats, runtime checkpoints, and provider compaction.
sidebar:
  order: 4
---

## Agent Session Protocol

ASP stores and migrates complete session logs between harnesses. OpenCheckpoint holds the distilled
working state. A handoff can carry an ASP session alongside a checkpoint, and a checkpoint can
reference ASP session and event ids:

```json
{ "protocol": "asp", "id": "6f0d2c1e9b", "event": "evt-a91f" }
```

ASP's per-axis fidelity declarations correspond to `derivation.omissions`, and its
`approval.requested` and `task.updated` events map to operations and task status.

## pi compaction summaries

pi's compaction summaries use fixed sections that map onto checkpoint fields:

| pi summary section                     | OpenCheckpoint                                                            |
| -------------------------------------- | ------------------------------------------------------------------------- |
| Goal                                   | `task.objective`                                                          |
| Constraints & Preferences              | `statements` of kind `constraint` or `instruction`                        |
| Progress: Done / In Progress / Blocked | `progress.completed`, `progress.focus`, `progress.next` with `blocked_by` |
| Key Decisions                          | `statements` of kind `decision` with `rationale`                          |
| Next Steps                             | `progress.next`                                                           |
| Read and modified files                | `resources`                                                               |

A converter from pi compaction entries is a planned early producer.

## Runtime checkpoints (LangGraph, OpenAI Agents SDK)

Runtime checkpoints serialize execution state for one engine: graph channels, run state, the
current agent object. They suit resuming in the same runtime and do not carry over to another
one. A runtime can emit an OpenCheckpoint document alongside its own checkpoint when work
must leave the runtime. Pending writes and approval interruptions become `operations`; thread ids
become `session_refs`.

## Open Responses and provider compaction

Provider compaction produces encrypted or signed items that only the issuing provider can use.
Any consumer can read an OpenCheckpoint document, so the two complement each other. A checkpoint may reference a
response id in `session_refs` so the same provider can use its own state when available.
