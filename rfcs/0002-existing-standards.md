---
rfc: 0002
title: Existing standards and the case for a checkpoint artifact
status: Draft
type: Informational
created: 2026-10-24
authors: OpenCheckpoints maintainers
---

# RFC 0002: Existing standards and the case for a checkpoint artifact

## Abstract

This RFC surveys the protocols and runtimes that touch session history, task state, and
compaction, records what each one represents, and asks whether OpenCheckpoints should be an
independent specification, a profile of an existing session standard, or a complementary
artifact that existing standards carry. It recommends the third, and lists what OpenCheckpoints
reuses from each.

Facts below were checked against each project's repository or published specification on
2026-10-24. Versions and dates are as found that day. Where a point could not be verified it
says so.

## Survey

### Open Responses

- **Solves:** a vendor-neutral, multi-provider LLM API modeled on the OpenAI Responses API:
  items, the agentic loop, streaming events. Specification version 2026-04-24; a series of LF
  Projects, LLC, with a technical charter that names the Agentic AI Foundation as liaison.
  Defined in TypeSpec, published as OpenAPI 3.1. Apache-2.0.
- **State:** typed `Item`s (`message`, `function_call`, `function_call_output`, `reasoning`,
  `compaction`) inside a `Response` with `id`, `status`, `previous_response_id`, `output`.
- **Continuity:** `previous_response_id` makes the server reload earlier input and output.
  With `store=false` state lives only on one connection.
- **Application state:** none.
- **Portability:** the wire format is portable; the state is not. Response ids, encrypted
  reasoning, and compaction items are tied to one provider.
- **Compaction:** `POST /v1/responses/compact` returns a `compaction` item carrying only
  `encrypted_content`. No fidelity rules; unreadable by anyone but the issuing provider.
- **Reuse:** the `type` discriminator pattern; dated, immutable releases with each field
  tagged by the version that added it.

### Model Context Protocol (MCP)

- **Solves:** how applications expose tools, resources, and prompts to models. Version
  2026-07-28; a series of LF Projects, LLC, hosted by AAIF. TypeScript source of truth,
  generated JSON Schema 2020-12, JSON-RPC 2.0 transport. Code and specification moving from MIT
  to Apache-2.0; documentation CC-BY-4.0.
- **State:** `Resource {uri, name, title, description, mimeType, annotations, size}`;
  `ResourceLink`; `Annotations {audience, priority, lastModified}`. URIs per RFC 3986 with
  custom schemes allowed.
- **Continuity:** the 2026-07-28 revision removed protocol sessions and the `initialize`
  handshake. Servers that need state mint their own handles. Mid-request input uses an
  `input_required` result with opaque `requestState`. Tasks moved to an official extension
  with statuses `working`, `input_required`, `completed`, `failed`, `cancelled` (only the
  overview of that extension was reviewed).
- **Application state:** the MCP Apps extension lets an embedded app replace the model's
  context (`ui/update-model-context`). It stays inside one host.
- **Portability:** resource URIs travel; server state does not.
- **Compaction:** none.
- **Reuse:** resource identification by URI with custom schemes; reverse-DNS namespacing for
  extension keys (MCP's `_meta` convention); `input_required` as a model for operations
  awaiting input; JSON Schema 2020-12 as the published artifact.

### Agent2Agent (A2A)

- **Solves:** discovery and task delegation between independent agents. v1.0.0 (2026-03-12),
  with v1.0.1 in the changelog; Linux Foundation project, AAIF growth stage. `a2a.proto` is
  normative; JSON Schema is generated and non-normative. Apache-2.0.
- **State:** `Task {id, context_id, status, artifacts, history, metadata}`;
  `TaskState` (`SUBMITTED`, `WORKING`, `COMPLETED`, `FAILED`, `CANCELED`, `INPUT_REQUIRED`,
  `REJECTED`, `AUTH_REQUIRED`); `Message` and `Artifact` built from `Part`s (text, raw, url,
  data).
- **Continuity:** `contextId` groups tasks; `referenceTaskIds` links follow-ups; terminal
  tasks accept no new messages.
- **Application state:** none.
- **Portability:** the message format is portable; context and history stay on the serving
  agent, and the protocol defines no export or cross-agent handoff of a task's state.
- **Compaction:** none beyond `historyLength` truncation.
- **Reuse:** an A2A Artifact with a data part is a natural envelope for a checkpoint;
  `contextId` and task ids are natural session references; `INPUT_REQUIRED` and
  `AUTH_REQUIRED` confirm that "awaiting a person" deserves first-class representation.

### Agent Client Protocol (ACP)

(Zed's editor-to-agent protocol. IBM's Agent Communication Protocol, also abbreviated ACP, was
archived and folded into A2A.)

- **Solves:** the JSON-RPC protocol between an editor and a coding agent. Stable v1 (schema
  1.26.0) and v2 alpha, 2026-10-16; multi-vendor maintainers. JSON Schema 2020-12 generated
  from Rust. Apache-2.0.
- **State:** nothing persisted by the protocol. `session/update` notifications carry message
  chunks, tool calls (`status`: `pending`, `in_progress`, `completed`, `failed`), plans
  (`entries` with `content`, `priority`, `status`), and permission requests (`allow_once`,
  `allow_always`, `reject_once`, `reject_always`).
- **Continuity:** `session/load` replays history; `session/resume` restores without replay;
  persistence belongs to the agent and no on-disk format is defined.
- **Application state:** none as a structure; context reaches the agent as content blocks.
- **Portability:** session ids mean something only to the agent that issued them.
- **Compaction:** a `compaction_update` lifecycle with a display summary; no record of what was
  dropped.
- **Reuse:** plan entries map to `progress.next`; tool-call status confirms the need for an
  `uncertain` state at the boundary; ACP v2's rule that unknown enum variants are preserved
  matches our extension rule.

### Agent Session Protocol (ASP)

- **Solves:** durable storage and migration of agent session logs between harnesses. Draft
  (schema v1.0, projection v1.1), last updated 2026-09-01; steward not identified; early
  adoption. TypeScript reference contracts; JSON Schema on the roadmap. MIT.
- **State:** three layers: raw native blobs, a canonical append-only event log, and
  rebuildable projections. Event envelopes carry `authority`
  (`authoritative`, `self_reported`, `inferred`) and `confidence`; event families include
  `task.updated`, `approval.requested/resolved`, and `artifact.observed` (with `uri`,
  `digest`, `sizeBytes`).
- **Continuity:** a lineage graph with relation types `fork`, `resume`, `handoff`, `subagent`,
  `compact`. Exporters refuse to export when a target's required fields are missing.
- **Application state:** none beyond `cwd`.
- **Portability:** its purpose. Converters exist for several coding harnesses.
- **Compaction:** modeled only as a lineage relation. Fidelity is declared per axis
  (`preserved`, `partial`, `evidence-only`, `dropped`, `not-in-source`).
- **Reuse:** ASP event and session ids as session references; per-axis fidelity and "refuse
  rather than silently degrade" inform `derivation.omissions` and `necessity: required`;
  `authority` informs `origin` and `verification`.

### Pi session format and compaction

- **Solves:** native session persistence for the pi coding agent (`earendil-works/pi`,
  formerly `badlogic/pi-mono`). Session format v3; MIT.
- **State:** JSONL; a header line, then entries with `id` and `parentId` forming a tree
  (branching in place). Entry types include `message`, `compaction`, `branch_summary`,
  `context_edit`, and `custom`.
- **Compaction:** a `CompactionEntry` with `summary`, `firstKeptEntryId`, `tokensBefore`, and
  `details.readFiles` / `modifiedFiles`. The summary is markdown with fixed sections: Goal,
  Constraints & Preferences, Progress (Done / In Progress / Blocked), Key Decisions (with
  rationale), Next Steps, Critical Context. The raw log is kept; the summary replaces old
  entries only in what the model sees.
- **Application state:** none beyond `cwd`.
- **Portability:** native to pi.
- **Reuse:** the summary's sections map almost one to one onto `task`, `statements`
  (constraints, decisions), and `progress` (completed, focus, next). That an independently
  developed agent converged on these sections is evidence the data model fits practice. Read
  and modified file lists map to resources.

### LangGraph checkpointing

- **Solves:** durable execution, human-in-the-loop interrupts, and time travel for LangGraph
  graphs. MIT.
- **State:** `Checkpoint {v, id, ts, channel_values, channel_versions, versions_seen}`, with
  metadata (`source`: input, loop, update, fork; `step`; `parents`) and `pending_writes`.
  Interrupts carry an id, a payload, and optionally a response schema.
- **Continuity:** checkpoints chain by `parent_config` within a `thread_id`; `update_state`
  forks.
- **Portability:** none. Channel names and versions are meaningful only to the compiled graph,
  and the format may change between releases.
- **Reuse:** parent lineage; pending writes as the model for in-flight effects; the documented
  hazard that resumed nodes re-run from the start, so side effects must be idempotent, which
  motivates `effect` and `resume`.

### OpenAI Agents SDK

- **Solves:** sessions (stored Responses-format input items), handoffs between agents, and
  serializable run state for human approval. MIT.
- **State:** `RunState` (`$schemaVersion` 1.21) with the current agent, generated items, model
  responses, and serialized application context; `ToolApprovalItem` interruptions approved or
  rejected via the state.
- **Handoffs:** input filters and an optional beta that nests prior history into summary
  segments, which the documentation notes does not redact sensitive data.
- **Portability:** reloading a `RunState` requires the original agent object; the docs warn
  that model, prompt, or tool changes can break it, and to deserialize only from trusted
  storage.
- **Compaction:** the Responses API produces encrypted, opaque `compaction` items.
- **Reuse:** the shape of an approval (tool, arguments, decision); the warning that serialized
  context carries secrets, which motivates §10.5 of the specification.

### Claude API and Claude Code

- **Context editing** clears old tool results or thinking server-side. **Compaction** produces
  a summary block (readable plaintext with a signature for the on-demand variant; images and
  documents in the summarized range are lost). The **memory tool** gives the model a
  developer-owned file store. Claude Code keeps JSONL session transcripts and checkpoints file
  edits only, not remote side effects.
- **Portability:** summary text is readable by anyone; the signed blocks are for the same API.
- **Reuse:** the default summary categories (state, next steps, learnings) again match the
  data model; "checkpoints cover local files, not remote effects" is exactly the gap
  `operations` fills.

### Research

| Work                                                               | Takeaway for OpenCheckpoints                                                                                                                                                                                              |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Packer et al., _MemGPT_ (2023), arXiv:2310.08560                   | Tiered memory lets work exceed the context window; a checkpoint is a portable, inspectable tier.                                                                                                                          |
| Lindenbauer et al., _The Complexity Trap_ (2025), arXiv:2508.21433 | Masking old observations matches LLM summarization on SWE-bench Verified at about half the cost. Cheap structural reduction is a strong baseline; compaction needs measurement, not assumption.                           |
| Kang et al., _ACON_ (2025), arXiv:2510.00615                       | Compression guidelines can be optimized against task success and peak tokens.                                                                                                                                             |
| KC and Budathoki, _Handoff Debt_ (2026), arXiv:2606.02875          | On 181 handoff points from SWE-bench Verified, carrying context cut median agent events by 20–59% and prompt tokens by 42–63%; effects on solve rate were smaller and model-dependent. Repeated work is a primary metric. |
| Gulati, _ContinuityBench_ (ICML 2026 workshop)                     | Interruption cut success from 41.7% to 28.0%; a structured summary beat summary plus full action history in 11 of 18 settings. More context is not always better.                                                         |

These sources measure task success, tokens and cost, agent steps (a proxy for repeated work),
latency, and consistency. RFC 0004 adopts these metrics.

## Gap analysis

| Need                                                        | Open Responses  | MCP                 | A2A            | ACP                 | ASP                   | Pi         | LangGraph         | OpenAI SDK     |
| ----------------------------------------------------------- | --------------- | ------------------- | -------------- | ------------------- | --------------------- | ---------- | ----------------- | -------------- |
| Objective and status as data                                | —               | task status (ext.)  | task state     | —                   | `task.updated`        | prose      | developer-defined | —              |
| Completed work / next steps                                 | —               | —                   | —              | plan entries        | projections           | prose      | —                 | —              |
| Typed provenance (instruction vs. observation vs. external) | roles only      | —                   | roles only     | —                   | authority on events   | —          | —                 | —              |
| Decisions with rationale                                    | —               | —                   | —              | —                   | —                     | prose      | —                 | —              |
| Resource references with revision and digest                | —               | URI, size           | parts          | locations           | artifacts with digest | file lists | —                 | —              |
| Application state outside chat                              | —               | Apps ext., one host | —              | —                   | —                     | —          | channels          | context object |
| Pending approvals and uncertain side effects                | —               | input_required      | INPUT_REQUIRED | permission requests | approvals             | —          | interrupts        | approvals      |
| Readable by any vendor                                      | yes (state not) | yes                 | yes            | yes                 | yes                   | yes        | no                | no             |
| Survives runtime change                                     | no              | n/a                 | no             | no                  | yes                   | no         | no                | no             |
| Records what was dropped                                    | no              | —                   | —              | no                  | per-axis fidelity     | no         | —                 | no             |

Nothing in the survey offers a standalone, vendor-readable record of _working state_: what is
being attempted, what is known and how, what was decided, what is pending, and what must be
checked. Protocols move messages and expose live state; session formats preserve history;
runtime checkpoints preserve executable state for one engine; compaction outputs are prose or
encrypted. ASP comes closest on portability and fidelity, but it preserves the log, not a
distilled state, and it has no typed provenance for claims or application context.

## Options

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
  makes it a risky foundation. A profile would inherit those constraints and lose
  neutrality between protocols.

**C. Complementary checkpoint artifact.** A self-contained document format, independent of
transport, that existing protocols carry (as an MCP resource, an A2A artifact, an ACP content
block, alongside an ASP session) and that points back into their records.

- For: fills the gap without competing; usable from any protocol, runtime, or application;
  reuses existing conventions instead of redefining them; small surface.
- Against: needs its own governance and versioning; adoption depends on producers in several
  ecosystems.

## Recommendation

**C.** OpenCheckpoints is an independent _document_ specification (it needs its own schema and
versioning, as in A) whose design commitment is to complement, not replace, the protocols that
carry it. Concretely:

1. It defines no transport, RPC, or storage. §12 of the specification describes how each
   protocol carries a checkpoint.
2. It references session history kept by other standards (`source.session_refs`) instead of
   embedding it.
3. It reuses existing conventions: URIs per RFC 3986 with custom schemes (as MCP),
   reverse-DNS extension namespaces (as MCP `_meta`), JSON Schema 2020-12 (as MCP and ACP),
   RFC 3339 timestamps, IANA hash names, and status vocabularies aligned with A2A, MCP tasks,
   and ACP tool calls where meanings coincide.
4. It defines new structure only where the survey found a gap: typed statements with
   provenance, operations with side-effect semantics, application context, continuation
   requirements, and derivation records.

If a carrier protocol later wants a normative binding (for example an A2A extension URI for
checkpoint artifacts), that binding belongs to that protocol's process, with this
specification as the referenced format.
