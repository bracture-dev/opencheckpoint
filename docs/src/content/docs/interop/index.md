---
title: Overview
description: How OpenCheckpoints relates to, and travels inside, other agent standards.
sidebar:
  order: 0
---

OpenCheckpoints is a document format, not a protocol. It defines no transport, RPC, or storage,
so it can travel inside whatever channel already connects the systems involved, and it points
back into the session records those systems keep.

Two mechanisms connect it to other standards:

- **Carrying a checkpoint.** A protocol transports the document, using the proposed media type
  `application/vnd.opencheckpoints+json`.
- **Referencing history.** `source.session_refs` points to sessions, tasks, or events in another
  protocol's records, so a consumer that can read them may, and one that cannot still understands
  the checkpoint.

The guides below describe patterns for each. They are informative. A normative binding, such as
an extension identifier in another protocol, belongs to that protocol's own process.

| Guide                                      | Covers                                                                    |
| ------------------------------------------ | ------------------------------------------------------------------------- |
| [MCP](mcp/)                                | Exposing checkpoints as resources; referencing MCP resources.             |
| [A2A](a2a/)                                | Returning checkpoints as artifacts; referencing contexts and tasks.       |
| [ACP](acp/)                                | Passing checkpoints to coding agents; mapping plans and tool calls.       |
| [Session logs and runtimes](session-logs/) | Agent Session Protocol, pi, LangGraph, OpenAI Agents SDK, Open Responses. |
