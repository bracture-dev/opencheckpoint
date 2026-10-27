---
title: Agent Client Protocol (ACP)
description: Passing checkpoints between editors and coding agents.
sidebar:
  order: 3
---

ACP connects editors to coding agents. It defines no on-disk session format, and a session id
means something only to the agent that issued it, so ACP leaves moving work between agents out of
scope; a checkpoint covers that case.

## Passing a checkpoint to an agent

When an editor starts a session with a new agent to continue earlier work, it can include the
checkpoint as a resource content block in the first prompt, with media type
`application/vnd.opencheckpoint+json`. The agent restores it as untrusted input.

## Producing a checkpoint from an ACP session

An editor or agent can build a checkpoint from what ACP already exposes:

| ACP                                                  | OpenCheckpoint                                                                                                              |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Plan entries (`content`, `priority`, `status`)       | `progress.completed` for completed entries, `progress.focus` for the in-progress entry, `progress.next` for pending entries |
| Tool call with `status: in_progress` at the boundary | `operation` with `status: uncertain` and an explicit `effect`                                                               |
| Tool call `locations`                                | `resource` entries for the files, with `application_context` selections for line ranges                                     |
| Permission request awaiting a response               | `operation` with `kind: approval`, `status: awaiting`                                                                       |
| Session id                                           | `source.session_refs` with `protocol: acp`                                                                                  |

The [software development example](../../examples/software-development/) shows the result.
