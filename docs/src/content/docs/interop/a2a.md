---
title: Agent2Agent (A2A)
description: Returning checkpoints as A2A artifacts and referencing A2A contexts and tasks.
sidebar:
  order: 2
---

## Returning a checkpoint as an artifact

An A2A agent that hands work to another agent, or pauses a task, can return the checkpoint as an
`Artifact` with a data part containing the document, and the part's media type set to
`application/vnd.opencheckpoint+json`. The receiving agent treats it as untrusted input and
follows the [restoration procedure](../../specification/#107-restoration-procedure).

## Referencing A2A records

```json
"session_refs": [
  { "protocol": "a2a", "id": "ctx-holiday-2026", "event": "task-holiday-hours-07" }
]
```

Use the `contextId` as `id` and the task id as `event`. A consumer with access to the originating
agent may retrieve history; one without it relies on the checkpoint alone.

## Mapping

| A2A                             | OpenCheckpoint                                                       |
| ------------------------------- | -------------------------------------------------------------------- |
| `TaskState.INPUT_REQUIRED`      | `task.status: awaiting_input`, and an `operation` of kind `input`    |
| `TaskState.AUTH_REQUIRED`       | an `operation` of kind `approval`, or a requirement of kind `access` |
| `Artifact` (deliverable)        | a `resource` of kind `artifact`                                      |
| `Part` with `url`               | a `resource` with `uri` and `media_type`                             |
| `contextId`, `referenceTaskIds` | `source.session_refs`                                                |

A checkpoint sits alongside A2A task history and holds the distilled state a different agent needs
to continue without that history.
