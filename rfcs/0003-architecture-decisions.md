---
rfc: 0003
title: Architecture decisions for version 0.1
status: Draft
type: Standards Track
created: 2026-10-24
authors: OpenCheckpoints maintainers
---

# RFC 0003: Architecture decisions for version 0.1

## Abstract

This RFC records the design decisions behind the v0.1 data model, schema, repository, and
SDK strategy, with the alternatives considered and the reasons for each choice. It ends with
the known risks and open questions that reviewers are asked to weigh in on.

## Decisions

### D1. A complementary document format

OpenCheckpoints is a self-contained document format that existing protocols carry, not a
protocol, profile, or transport. RFC 0002 gives the evidence. Consequences: the specification
defines no RPC or storage API; session history stays in the systems that own it and is
referenced through `source.session_refs`.

### D2. JSON, described by JSON Schema Draft 2020-12

Alternatives: Protocol Buffers (A2A's normative source), TypeSpec/OpenAPI (Open Responses),
CDDL, or a TypeScript source of truth (MCP, ASP).

JSON Schema 2020-12 is chosen because it is language-neutral, is the format MCP and ACP
publish, has mature validators in every target language (Ajv for JavaScript,
`santhosh-tekuri/jsonschema` for Go, the `jsonschema` crate for Rust), and can express most of
the format's safety rules directly through `if`/`then`. Protocol Buffers would make JSON a
secondary encoding and lose conditional constraints. A TypeScript or Rust source of truth would
make one SDK's language the owner of the contract.

### D3. A hand-authored schema is the single source of truth

The schema in `spec/schema/` is written by hand, reviewed as part of the specification, and
consumed verbatim by every SDK. No SDK's types are allowed to redefine it. MCP and ACP generate
their schema from code; this project inverts that so that no implementation language owns the
format.

### D4. One statement type with a `kind`

Alternatives: separate arrays for findings, hypotheses, decisions, instructions, and so on.

A single `statements` array with a `kind` discriminator keeps provenance (`origin`,
`verification`, `evidence`) uniform, so compaction and security rules apply the same way to
everything, and keeps the number of object types small. Kind-specific rules (an instruction's
origin must be the user or system; a hypothesis cannot be verified; a decision needs a
rationale) are expressed as schema conditionals and tested by fixtures.

The kinds are the smallest set that keeps apart what a summary blurs and a destination must
treat differently: `instruction`, `constraint`, `decision`, `observation`, `hypothesis`,
`question`, `external`.

### D5. One namespace for local identifiers

All local objects share one id namespace, unique across the document. References need no type
tag, and `blocked_by` can point at a question, an operation, a resource, or a requirement. The
cost is that producers must avoid collisions between object types, which prefixes (`r-`,
`s-`, `op-`) make easy.

### D6. No blocker object

A blocker is always an open question, an awaiting or failed operation, an unavailable
resource, or an unmet requirement. Recording it as a `blocked_by` relation from a next step
avoids a second representation of the same fact.

### D7. Strict core objects, namespaced extensions

Alternatives: allow unknown properties everywhere (lenient), or prefix them (`x-`).

Core objects reject undefined properties so typos and invented fields are caught, and all
extension data lives in `extensions` maps keyed by reverse-DNS names (the convention MCP uses
for `_meta`). Consumers ignore unknown extensions and preserve them on re-serialization.
Forward compatibility comes from the version policy (D10), not from tolerating arbitrary
fields. An extension that is needed to interpret a document is declared as a continuation
requirement of kind `extension`, which serves the purpose of a "critical extensions" list
without a new field.

### D8. Operations carry side-effect semantics; approvals are records

Runtime checkpoints (LangGraph pending writes, OpenAI `RunState` interruptions) show that the
dangerous moment in resumption is a side effect whose outcome is unknown. Operations therefore
record `effect` (`none`, `idempotent`, `non_idempotent`, `unknown`) and a recommended `resume`,
and the schema rejects an uncertain, possibly non-idempotent operation that recommends
`retry`. An approval outcome must cite evidence in a system of record, and the specification
states that the record never authorizes the destination.

### D9. Application context is located, not modeled

Application context names the application, the view, selected and open resources, filters,
drafts, and application-defined `state` described by a `state_schema` URI. It does not define a
UI model. This captures state that never appeared in chat while leaving each application in
charge of its own semantics.

### D10. Version policy

`opencheckpoints` is a `MAJOR.MINOR` string. Before 1.0, every minor version may break and
consumers reject versions they do not implement. From 1.0, minor versions are additive. Each
version's schema is immutable at a stable URL.

### D11. Field naming

Field names are `snake_case`, as in Open Responses. MCP and A2A's JSON use `camelCase`. Either
works; one had to be chosen, and `snake_case` avoids ambiguity with acronyms and reads
naturally to people and models. This is listed as an open question because alignment with
carrier protocols has some value.

### D12. One repository

The specification, schema, fixtures, examples, documentation site, and (later) SDKs live in
one repository, so a change to the format and its tests, docs, and bindings lands in one
reviewed pull request. Normative material (`spec/`), process (`rfcs/`), documentation
(`docs/`), tests (`tests/`), and implementations (`sdks/`) stay in separate directories.

### D13. SDKs generate types from the schema and validate with the schema

Evaluated per language:

| Language   | Types                                                                                          | Schema validation                                           | Handwritten                                       |
| ---------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------- |
| TypeScript | Generated from the schema (e.g. `json-schema-to-typescript`).                                  | Ajv with the canonical schema file.                         | Builder helpers, semantic rules, error reporting. |
| Go         | Generated structs (e.g. `go-jsonschema`), reviewed for idiom; `map[string]any` for extensions. | `santhosh-tekuri/jsonschema` with the embedded schema file. | Constructors, semantic rules, typed errors.       |
| Rust       | Generated Serde types (e.g. `typify`), `serde_json::Map` for extensions.                       | `jsonschema` crate with the embedded schema file.           | Builders, semantic rules, error enums.            |

Generated types are reviewed and may be wrapped for idiom, but never edited to diverge from the
schema; CI regenerates and diffs them. Every SDK validates with the canonical schema rather
than re-encoding its rules, so level-1 behavior is identical by construction. The semantic
rules (§8.2 of the specification) are the only per-language logic, and the shared conformance
manifest tests them. Restoration into a particular runtime is the job of adapters, outside the
SDKs' core.

### D14. Documentation derives from the specification

The documentation site imports the specification, RFCs, governance files, and examples from
the repository at build time, and generates the schema reference from the schema. Pages that
explain concepts link to the normative text rather than restate it.

## Risks

- **Adoption.** A format with no producers is not a standard. Mitigation: keep the minimal
  checkpoint tiny; build converters from existing session formats (pi compaction summaries,
  ASP projections) as early demonstrations; seek reviewers from carrier-protocol communities.
- **Over-modeling.** Each field is a burden on producers. Mitigation: every object beyond
  `task` is optional; additions require evidence from the examples or from implementers.
- **Under-modeling application state.** `state` is opaque by design; destinations that do not
  know the application may get little from it. Mitigation: applications can publish
  `state_schema`; revisit after implementers report.
- **False sense of safety.** Implementers may treat schema validation as permission to resume.
  Mitigation: the five-level assurance model (specification §8.1) is normative, and
  validators must not describe valid documents as resumable.
- **Provenance can be forged.** `origin.type: user` is a claim by the source. Mitigation: the
  trust model treats it as such; signatures are a planned extension.
- **Model-written checkpoints may be wrong.** A producer that uses a model to fill fields can
  misclassify kinds. Mitigation: compaction rules, the `verification` model, and behavioral
  scenarios that test destinations against misleading checkpoints.

## Open questions

1. Should `statements` support relations beyond supersession (supports, contradicts,
   answers)? v0.1 uses `evidence` and `superseded_by` only.
2. Should operations be able to record partial completion (for example, 3 of 5 locations
   updated), or should that be modeled as separate operations? The business-operations
   example uses separate operations.
3. Is a separate `blocker` object worth its cost for readability, despite D6?
4. Should field names follow the `camelCase` convention of MCP and A2A (D11)?
5. Should checkpoints support multiple parents for merges, or is `derivation.inputs` enough?
6. What is the right signature extension: JWS over JCS, or a detached envelope such as DSSE?
7. Should `resource.kind` and other enums be open (accept unknown values) after 1.0, as ACP v2
   does for enum variants?
8. Should there be a size limit on whole documents, and should validators enforce it?
