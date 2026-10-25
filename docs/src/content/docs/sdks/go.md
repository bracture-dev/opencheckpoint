---
title: Go SDK
description: Status and planned scope of the OpenCheckpoint Go SDK.
---

**Status: not started.** The Go SDK is Phase 3 of the [roadmap](../../project/roadmap/). This page
describes its planned scope so that implementers and reviewers can comment before code exists. It
documents no API, because none has been designed.

## Planned scope

Idiomatic exported structs generated from the schema and reviewed for idiom, `encoding/json` round trips that keep unknown extensions, validation with a Draft 2020-12 validator (such as `santhosh-tekuri/jsonschema`) against the embedded canonical schema, and typed errors. The module path will follow the repository: `github.com/opencheckpoint/opencheckpoint/sdks/go`.

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

[RFC 0003, decision D13](../../rfcs/0003-architecture-decisions/#d13-sdks-generate-types-from-the-schema-and-validate-with-the-schema)
explains why types are generated from the schema while builders, semantic rules, and errors are
handwritten.

Want to help build it? See [contributing](../../project/contributing/).
