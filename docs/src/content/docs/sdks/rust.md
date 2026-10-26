---
title: Rust SDK
description: Status and planned scope of the OpenCheckpoint Rust SDK.
---

**Status: not started.** The Rust SDK is part of Phase 5 of the [roadmap](../../project/roadmap/),
built when runtime authors need native integration. This page
describes its planned scope so that implementers and reviewers can comment before code exists. It
documents no API, because none has been designed.

## Planned scope

Serde-compatible types generated from the schema (for example with `typify`), `serde_json::Map` for extensions so unknown data round-trips, validation with the `jsonschema` crate against the embedded canonical schema, and structured error enums. Core types stay separate from any runtime integration so the crate can be embedded in agent runtimes.

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
