---
rfc: 0001
title: OpenCheckpoint v0.1
status: Draft
type: Standards Track
created: 2026-10-24
authors: OpenCheckpoint maintainers
---

# RFC 0001: OpenCheckpoint v0.1

## Abstract

OpenCheckpoint lets a person pick up unfinished AI-assisted work with a different AI, agent, or
application without starting over or explaining everything again. This RFC proposes version 0.1
of the format: the problem, who has it, the scope, the design decisions behind the
[specification](../spec/versions/v0.1.md), and the risks and open questions reviewers are asked
to weigh in on. It is the only RFC until v0.1 is accepted; until then the specification changes
directly by pull request.

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
events by 20–59% and prompt tokens by 42–63% ([Prior art](../docs/src/content/docs/prior-art.md)). The same research shows that more
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

## Decisions

### D1. A complementary document format

OpenCheckpoint is a self-contained document format that existing protocols carry, not a
protocol, profile, or transport. [Prior art](../docs/src/content/docs/prior-art.md) gives the evidence. Consequences: the specification
defines no RPC or storage API; session history stays in the systems that own it and is
referenced through `source.session_refs`.

#### Alternatives considered

**A. Independent specification.** A new format with its own model, governance, and transport
bindings.

- For: full control over the model; no dependency on another project's release cycle.
- Against: risks duplicating concepts (resources, task states, extension conventions) that
  existing standards already define; a new transport would compete rather than complement.

**B. Profile or extension of an existing session standard.** For example, an ASP projection,
an A2A extension, or an MCP extension.

- For: inherits a community and transport.
- Against: each candidate represents something else. ASP is a log format and its projections
  are derived from events; a checkpoint must be authorable without a log, by hand or by an
  application with no agent session at all. A2A and MCP are transports; binding the format to
  one excludes users of the others. ASP is also early (draft, unidentified steward), which
  makes it a risky base. A profile would inherit those constraints and lose
  neutrality between protocols.

**C. Complementary checkpoint artifact.** A self-contained document format, independent of
transport, that existing protocols carry (as an MCP resource, an A2A artifact, an ACP content
block, alongside an ASP session) and that points back into their records.

- For: fills the gap without competing; usable from any protocol, runtime, or application;
  reuses existing conventions instead of redefining them; small surface.
- Against: needs its own governance and versioning; adoption depends on producers in several
  ecosystems.

### D2. JSON, described by JSON Schema Draft 2020-12

Alternatives: Protocol Buffers (A2A's normative source), TypeSpec/OpenAPI (Open Responses),
CDDL, or a TypeScript source of truth (MCP, ASP).

JSON Schema 2020-12 is chosen because it is language-neutral, is the format MCP and ACP
publish, has mature validators in every target language (Ajv for JavaScript,
`santhosh-tekuri/jsonschema` for Go, the `jsonschema` crate for Rust, `jsonschema` for Python), and can express most of
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

`opencheckpoint` is a `MAJOR.MINOR` string. Before 1.0, every minor version may break and
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

| Language   | Types                                                                                                               | Schema validation                                           | Handwritten                                       |
| ---------- | ------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------- |
| TypeScript | Generated from the schema (e.g. `json-schema-to-typescript`).                                                       | Ajv with the canonical schema file.                         | Builder helpers, semantic rules, error reporting. |
| Go         | Generated structs (e.g. `go-jsonschema`), reviewed for idiom; `map[string]any` for extensions.                      | `santhosh-tekuri/jsonschema` with the embedded schema file. | Constructors, semantic rules, typed errors.       |
| Rust       | Generated Serde types (e.g. `typify`), `serde_json::Map` for extensions.                                            | `jsonschema` crate with the embedded schema file.           | Builders, semantic rules, error enums.            |
| Python     | Generated typed dictionaries (e.g. `datamodel-code-generator`), plain `dict` documents so round trips are lossless. | `jsonschema` with the packaged schema file.                 | Builder, semantic rules, exception types.         |

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

### D15. Forks are first-class

A checkpoint can be forked: several new checkpoints share one parent and are continued
independently, to compare agents, run regression or adversarial tests, explore hypotheses in
parallel, or brief subagents. Forking within one runtime is common; a readable, portable
baseline is what this format adds. Forks set `derivation.method` to `forked`, so a destination
knows siblings may exist, and each pending action with a side effect stays actionable in at most
one fork (specification §9.3), because every fork inherits the baseline's pending operations.
The [Forking a baseline](../docs/src/content/docs/forking.md) page records the audit behind this
decision, including where forking does not pay off.

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

## Success

Version 0.1 succeeds if:

- Independent implementers can read the specification and produce and consume checkpoints
  that pass the shared conformance suite.
- Checkpoints from the four example domains carry enough state that a second agent continues
  without transcript replay, measured by the method on the [Compaction and restoration](../docs/src/content/docs/compaction.md) page.
- Reviewers from at least two unaffiliated organizations find the model sound or propose
  concrete changes.

The ultimate measure is independent implementations adopting the format.
