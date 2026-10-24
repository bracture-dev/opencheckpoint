# SDKs

No SDK exists yet. The canonical format is the specification and schema in [`spec/`](../spec/);
SDKs are conveniences around it and never redefine it.

Order: TypeScript (Phase 2), Go (Phase 3), Rust (Phase 4). Each will live in its own directory
here and must pass the shared [conformance manifest](../tests/conformance/) in CI.

## Responsibilities in v0.1

Every SDK will:

- Parse and serialize checkpoints without adding, dropping, or changing fields, including unknown
  extensions.
- Validate against the canonical schema file, embedded verbatim, and report structured errors.
- Apply the semantic rules (§8.2) and transition rules, reporting their codes.
- Offer an idiomatic way to construct checkpoints.
- Expose the continuation requirements and resource references so a destination can compare
  them with its capabilities.
- Reject unsupported versions as the version policy (§5) requires.

No SDK will call a network service, a model, or a database, and no validation method will hide a
model call. No SDK will offer a generic "resume" function: restoring work into a particular
runtime is the job of runtime-specific adapters built on top.

## Generated versus handwritten

RFC 0003, decision D13, records the evaluation. In short: types are generated from the schema and
checked in CI by regenerating and diffing; validation uses the canonical schema through each
language's 2020-12 validator; builders, semantic rules, and error types are handwritten and
idiomatic.
