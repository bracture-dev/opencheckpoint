---
title: TypeScript SDK
description: Status and planned scope of the OpenCheckpoint TypeScript SDK.
---

**Status: not started.** The TypeScript SDK is Phase 2 of the [roadmap](../../project/roadmap/). This page
describes its planned scope so that implementers and reviewers can comment before code exists. It
documents no API, because none has been designed.

## Planned scope

Targets modern Node.js, Bun, and browsers. Types will be generated from the schema; validation will use Ajv with the canonical schema file. Proposed package name, subject to registry availability: `@opencheckpoint/sdk`.

Like every OpenCheckpoint SDK, it will:

- Parse and serialize checkpoints without adding, dropping, or changing fields.
- Validate against the canonical schema and report structured errors.
- Apply the semantic and transition rules and report their codes.
- Offer an idiomatic way to construct checkpoints.
- Expose continuation requirements and resource references for capability checks.
- Reject unsupported versions.
- Pass the shared [conformance manifest](../../conformance/) in CI.

It will not call a network service, a model, or a database, and it will not offer a generic
"resume" function. Restoring work into a specific runtime is the job of adapters built on top.

## Design notes

[RFC 0001, decision D13](../../rfcs/0001-opencheckpoint/#d13-sdks-generate-types-from-the-schema-and-validate-with-the-schema)
explains why types are generated from the schema while builders, semantic rules, and errors are
handwritten.

Want to help build it? See [contributing](../../project/contributing/).
