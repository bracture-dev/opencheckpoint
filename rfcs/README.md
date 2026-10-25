# RFCs

Changes to the OpenCheckpoint specification, and decisions about the project's direction, are
proposed and recorded as RFCs.

## When an RFC is needed

- Any change to the normative specification or the schema, other than editorial fixes.
- A new semantic rule, a new conformance requirement, or a change to the version policy.
- A change to governance or to the RFC process itself.
- A new extension that the project will maintain under the reserved `io.opencheckpoint`
  namespace.

Typos, clarifications that do not change meaning, documentation, examples, and tests do not need
an RFC. Open a pull request.

## Types

- **Standards Track:** changes the specification, schema, or conformance requirements.
- **Informational:** research, analysis, or guidance with no normative effect.
- **Process:** changes how the project works.

## Lifecycle

| Status    | Meaning                                                                                                                                                                                                                    |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Draft     | Open for discussion. Anyone may open one.                                                                                                                                                                                  |
| In review | A maintainer has agreed to shepherd it and scheduled it for decision.                                                                                                                                                      |
| Accepted  | Maintainers agreed to the change. A Standards Track RFC is merged into the specification only with fixtures that test it and, where it changes behavior an SDK implements, a reference implementation in at least one SDK. |
| Final     | Merged into a published specification version.                                                                                                                                                                             |
| Rejected  | Declined, with reasons recorded in the RFC.                                                                                                                                                                                |
| Withdrawn | Withdrawn by its authors.                                                                                                                                                                                                  |

## How to propose

1. Open a GitHub Discussion describing the problem, before writing the RFC. Link it from the RFC.
2. Copy `0000-template.md` to `NNNN-short-title.md`, using the next free number.
3. Open a pull request. Discussion happens on the pull request.
4. A maintainer who agrees to shepherd it moves it to In review. Only the shepherd changes its
   status.
5. Decisions follow `GOVERNANCE.md`.

## Index

| RFC                                        | Title                                                     | Type            | Status |
| ------------------------------------------ | --------------------------------------------------------- | --------------- | ------ |
| [0001](0001-problem-and-scope.md)          | Problem and scope                                         | Informational   | Draft  |
| [0002](0002-existing-standards.md)         | Existing standards and the case for a checkpoint artifact | Informational   | Draft  |
| [0003](0003-architecture-decisions.md)     | Architecture decisions for version 0.1                    | Standards Track | Draft  |
| [0004](0004-compaction-and-restoration.md) | Compaction and restoration                                | Informational   | Draft  |
| [0005](0005-threat-model.md)               | Threat model                                              | Informational   | Draft  |
| [0006](0006-forking-from-a-baseline.md)    | Forking from a baseline                                   | Standards Track | Draft  |
