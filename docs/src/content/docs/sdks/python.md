---
title: Python SDK
description: Status and planned scope of the OpenCheckpoint Python SDK.
---

**Status: not started.** The Python SDK is part of Phase 5 of the [roadmap](../../project/roadmap/),
built when runtime authors need native integration. This
page describes its planned scope so that implementers and reviewers can comment before code
exists. It documents no API, because none has been designed.

## Planned scope

Documents stay plain `dict`s, typed with `TypedDict` definitions generated from the schema, so
parsing and serializing are lossless and unknown extensions round-trip untouched. Validation will
use the `jsonschema` library's Draft 2020-12 validator against the canonical schema shipped in the
package. Exceptions will be specific and catchable. Proposed package name, subject to registry
availability: `opencheckpoint`.

Like every OpenCheckpoint SDK, it will:

- Parse and serialize checkpoints without adding, dropping, or changing fields.
- Validate against the canonical schema and report structured errors.
- Apply the semantic and transition rules and report their codes.
- Offer an idiomatic way to construct checkpoints.
- Expose continuation requirements and resource references for capability checks.
- Reject unsupported versions.
- Pass the shared [conformance manifest](../../conformance/) in CI.

It will not call a network service, a model, or a database, and it will not offer a generic
"resume" function. Adapters built on top of it will restore work into a specific runtime.

## Design notes

[RFC 0001, decision D13](../../rfcs/0001-opencheckpoint/#d13-sdks-generate-types-from-the-schema-and-validate-with-the-schema)
explains why types are generated from the schema while builders, semantic rules, and errors are
handwritten.

To help build it, see [contributing](../../project/contributing/).
