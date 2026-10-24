---
title: Security and trust
description: Why checkpoints are untrusted input, and what producers and consumers must do.
---

A checkpoint is **untrusted input** that is likely to be shown to a model and acted on. It may
come from a manipulated agent, be edited in transit, or be replayed. The normative requirements
are in [§10 and §11 of the specification](../specification/#10-consumer-requirements-security-and-trust);
[RFC 0005](../rfcs/0005-threat-model/) is the threat model.

## No transfer of authority

A checkpoint never grants the destination a capability, permission, credential, or authority it
does not already have. `origin.type: user`, approval records, and access requirements are claims
and descriptions, not proof or permission. The destination acts under its own policy, with its
own credentials, as if the checkpoint did not exist.

## Instructions and injected content

- Only the user or the operating system can issue an `instruction`; the schema rejects anything
  else.
- Text from tools, documents, web pages, emails, and other agents is recorded as `external`,
  however it is phrased.
- Consumers treat every text field as data. They never follow directives in external content,
  excerpts, drafts, extensions, or source fields.
- The destination's own operator policy always comes first.

## Side effects and approvals

- Restoring a checkpoint never executes pending operations.
- An `uncertain` action that may not be idempotent must be checked in the target system before it
  is retried; the schema forbids recommending a blind retry.
- An approval record must cite evidence in a system of record, and the destination must verify it
  there, including scope and expiry, before relying on it.
- An operation that is complete, cancelled, or rejected in one checkpoint cannot reappear as
  pending in a later one.

## Stale state

Resources change. Statements with `revalidate: before_use` or `before_action`, and resources with
recorded revisions or digests, must be re-checked, or the destination continues without them and
says so.

## Credentials and privacy

Checkpoints must not contain secrets of any kind: tokens, keys, cookies, signed URLs, or
credentials in URIs (a semantic error). Producers minimize personal data, prefer roles to names
and locators to excerpts, flag `sensitivity`, and record withheld content as an omission.

## Integrity

Version 0.1 defines no signatures. `parent.digest` gives tamper evidence across a lineage.
Detached signatures (JWS over a canonical form, or a DSSE envelope) are a planned extension, and
would establish who produced a checkpoint, not that its content is true.
