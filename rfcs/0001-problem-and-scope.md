---
rfc: 0001
title: Problem and scope
status: Draft
type: Informational
created: 2026-10-24
authors: OpenCheckpoints maintainers
---

# RFC 0001: Problem and scope

## Abstract

OpenCheckpoints lets a person pick up unfinished AI-assisted work with a different AI, agent,
or application without starting over or explaining everything again. This RFC states the
problem, who has it, what a solution must and must not do, and the boundary of version 0.1.

## The problem

AI-assisted work increasingly spans more than one session, agent, model, or application:

- A financial analyst starts a variance analysis in one assistant, runs out of context, and
  has to re-explain the ledger structure, the materiality threshold, and the three accounts
  already ruled out.
- An operations manager hands a half-finished multi-location scheduling change from a chat
  assistant to an agent embedded in the scheduling tool. The second agent cannot see which
  locations were already updated or which change is waiting on a regional manager.
- A support case moves from an AI triage agent to a human, then to a different vendor's
  agent. Each re-asks the customer for information already given.
- A developer switches coding agents mid-refactor. The new agent re-reads the codebase,
  re-runs the failing test, and re-discovers the root cause the first agent found an hour ago.

In each case the work has state: an objective, completed steps, findings, decisions, open
questions, pending approvals, unsaved drafts. Today that state lives in a transcript, in a
runtime's internal format, or in someone's head. Moving it means one of:

1. **Replaying the transcript.** Expensive, often impossible across vendors (reasoning and
   compaction items are encrypted or runtime-specific), and noisy: the next agent must
   re-derive what matters from everything that happened.
2. **Writing a prose summary.** Cheap, but it loses provenance. A summary does not say which
   sentences the user said, which the agent guessed, and which came from a web page. It
   silently promotes hypotheses to facts and quoted text to instructions, and it does not say
   what was left out.
3. **Starting over.** The person re-explains, and the agent redoes work, sometimes including
   side effects such as sending an email twice.

Research on handoffs between coding agents quantifies the cost: carrying context cut agent
events by 20–59% and prompt tokens by 42–63% (RFC 0002). The same research shows that more
context is not automatically better, which argues for structure over volume.

## Principle

**Preserve the state of the work, not just the conversation that produced it.**

A checkpoint lets another system understand: what is being accomplished; what is done; what
is in progress; what is known and with what evidence; which decisions, instructions, and
constraints still apply; which resources and application objects are involved; which
operations are pending or blocked; what to do next; and what to verify first.

## Users

- **Agent and runtime developers** who want their agent to export and import work.
- **Application developers** who embed AI and want application state (selections, drafts,
  filters) to travel with the task.
- **Platform and infrastructure providers** who route work between agents and need a neutral
  handoff format.
- **People using AI**, who benefit indirectly: they do not re-explain, and work is not
  silently redone or lost.

## Requirements

A solution must:

1. Be independent of model, provider, runtime, framework, programming language, application
   type, cloud, storage system, and domain.
2. Represent the task, the progress, the knowledge with its provenance, the resources, the
   application context, the pending operations, and the continuation requirements.
3. Keep instructions, decisions, observations, hypotheses, questions, and third-party content
   distinguishable.
4. Make unsafe states explicit: side effects whose outcome is unknown, approvals that are only
   records, evidence that may be stale, capabilities the destination lacks.
5. Never transfer authority. A checkpoint describes; it does not authorize.
6. Support degraded continuation when the destination lacks some capabilities or resources.
7. Be small and simple enough that a producer can emit a useful checkpoint with a few fields,
   and complete enough that a careful producer can record everything a destination needs.
8. Be extensible without forks, and versioned so that consumers know what they can rely on.
9. Distinguish what validation proves (well-formed, consistent) from what it does not
   (resources available, actions authorized, continuation successful).

## Scope of version 0.1

In scope:

- A JSON document format with a normative specification and a JSON Schema.
- Semantic validation rules with stable codes.
- Producer and consumer requirements, including a restoration procedure.
- A security and trust model, and privacy guidance.
- Compaction rules that constrain how a checkpoint may be reduced, without defining the
  reduction algorithm.
- Language-neutral conformance fixtures and behavioral continuation scenarios.

Out of scope (non-goals), now and possibly permanently: KV caches and hidden model state;
private chain-of-thought; prompt formats; full transcripts; long-term memory; in-flight process
migration; distributed transaction recovery; credentials; authorization transfer; UI document
models; runtime internals; transports and storage APIs; an automatic "resume anything" API.

## Boundary

Checkpoints are captured at **well-defined execution boundaries**: points where nothing is
mid-write from the producer's point of view. The format does not attempt to capture a process
in flight. Anything started and unconfirmed at the boundary is recorded as uncertain, with
what repeating it would do.

## Success

Version 0.1 succeeds if:

- Independent implementers can read the specification and produce and consume checkpoints
  that pass the shared conformance suite.
- Checkpoints from the four example domains carry enough state that a second agent continues
  without transcript replay, measured by the method in RFC 0004.
- Reviewers from at least two unaffiliated organizations find the model sound or propose
  concrete changes.

The ultimate measure is independent implementations adopting the format.
