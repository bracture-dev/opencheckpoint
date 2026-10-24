# Conformance suite

The conformance suite is language-neutral. Any implementation, in any language, can run it by
reading [`manifest.json`](manifest.json) and checking each case.

## Case format

```json
{
  "id": "semantic/dangling-reference",
  "description": "References resolve to an object in the document.",
  "file": "../fixtures/invalid/dangling-reference.json",
  "parent": "../fixtures/valid/transition-parent.json",
  "expect": { "result": "semantic", "errors": ["OCP-S002"], "warnings": [] }
}
```

- `file` is the document under test, relative to this directory.
- `parent`, when present, is the parent checkpoint; the transition rules (OCP-T001, OCP-T002)
  apply.
- `expect.result` is one of:
  - `valid`: passes the schema and all semantic and transition rules.
  - `schema`: fails JSON Schema validation (level 1).
  - `semantic`: passes the schema and fails the semantic or transition rules listed in
    `errors` (level 2). An implementation must report exactly those codes.
- `expect.warnings` lists the warning codes an implementation must report. Absent means none.

Schema failures are not matched by message or path, because validators word them differently.

## What an implementation must do

For each case:

1. Parse the file. Validate it against `spec/schema/v0.1/checkpoint.schema.json`.
2. If it passes, apply the semantic rules (specification §8.2) and, if `parent` is given, the
   transition rules.
3. Compare the outcome and codes with `expect`.
4. For every `valid` case, serialize the parsed document and parse it again. The result must be
   equal to the original as a JSON value: no fields added (including defaults), none removed
   (including unknown extensions), no values changed.

Coverage includes required fields, version handling, unknown extensions, round trips, provenance,
resource references, pending approvals, uncertain actions, invalid state transitions, stale
references, and credential leakage.

## Cross-language consistency

Every SDK runs this manifest in CI. Two implementations that pass it agree on validity and on
semantic error codes for every case. That is necessary for interoperability, not sufficient:
behavioral continuation is tested separately by [`tests/scenarios`](../scenarios/).

## Reference harness

`tools/conformance.mjs` runs the manifest with Ajv and a JavaScript implementation of the
semantic rules. It is test tooling, not an SDK.

```sh
npm test
```
