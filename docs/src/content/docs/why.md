---
title: Why OpenCheckpoints
description: The problem with transcripts and summaries, and why a structured checkpoint helps.
---

## Work outlives sessions

An analyst runs out of context halfway through a variance analysis. An operations manager starts
a change in a chat assistant and needs to finish it inside the scheduling tool. A support case
moves from one vendor's agent to a person to another vendor's agent. A developer switches coding
agents mid-refactor.

Each time, the work has state: an objective, completed steps, findings, decisions, open
questions, approvals in flight, unsaved drafts. Today that state is trapped in a transcript, a
runtime's private format, or someone's memory.

## The usual options fall short

| Option                | What goes wrong                                                                                                                                                                                      |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Replay the transcript | Expensive, grows with history, and often impossible across vendors because reasoning and compaction data are encrypted or runtime-specific. The next agent must re-derive what matters.              |
| Write a prose summary | Cheap, but provenance disappears. A summary does not say what the user said, what the AI guessed, or what came from a web page. Guesses become facts and quoted text becomes instructions, silently. |
| Start over            | The person re-explains, the agent redoes work, and side effects can happen twice.                                                                                                                    |

Research on handoffs between coding agents found that carrying context cut agent steps by 20–59%
and prompt tokens by 42–63%, while also showing that _more_ context is not automatically better.
Structure matters more than volume. [RFC 0002](../rfcs/0002-existing-standards/) has the
sources.

## What existing standards cover

MCP exposes tools and resources. A2A delegates tasks between agents. ACP connects editors to
coding agents. Open Responses standardizes model APIs. The Agent Session Protocol stores and
migrates session logs. Runtimes such as LangGraph and the OpenAI Agents SDK checkpoint their own
execution state.

None of them defines a standalone, vendor-readable record of _working state_ with typed
provenance, pending side effects, and application context. OpenCheckpoints fills that gap and is
designed to travel inside those protocols rather than compete with them.
[RFC 0002](../rfcs/0002-existing-standards/) compares them in detail.

## Design commitments

- **Preserve the state of work, not the conversation.**
- **Keep provenance.** Instructions, decisions, observations, hypotheses, questions, and external
  content stay distinct through capture and compaction.
- **Make unsafe states explicit.** Uncertain side effects, unverified approvals, stale evidence,
  and missing capabilities are first-class.
- **Never transfer authority.**
- **Stay small.** A useful checkpoint needs five fields.
