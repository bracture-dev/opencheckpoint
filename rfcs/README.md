# RFCs

## Before v0.1 is accepted

[RFC 0001](0001-opencheckpoint.md) proposes version 0.1 as a whole. Until it is accepted, it
is the only RFC: the specification, schema, and fixtures change directly by pull request, and
design decisions are recorded in RFC 0001 itself.

## After v0.1 is accepted

Contributors propose changes to an accepted specification as RFCs, which also record the
decision.

### When an RFC is needed

- Any change to the normative specification or the schema, other than editorial fixes.
- A new semantic rule, a new conformance requirement, or a change to the version policy.
- A change to governance or to the RFC process itself.
- A new extension maintained under the reserved `io.opencheckpoint` namespace.

Typos, clarifications that do not change meaning, documentation, examples, and tests do not need
an RFC. Open a pull request.

### Lifecycle

| Status    | Meaning                                                                                                                                                  |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Draft     | Open for discussion. Anyone may open one.                                                                                                                |
| In review | A maintainer has agreed to shepherd it and scheduled it for decision.                                                                                    |
| Accepted  | Maintainers agreed. A normative change merges only with fixtures that test it and, where it changes SDK behavior, an implementation in at least one SDK. |
| Final     | Merged into a published specification version.                                                                                                           |
| Rejected  | Declined, with reasons recorded in the RFC.                                                                                                              |
| Withdrawn | Withdrawn by its authors.                                                                                                                                |

### How to propose

1. Open a GitHub Discussion describing the problem, and link it from the RFC.
2. Copy `0000-template.md` to `NNNN-short-title.md`, using the next free number.
3. Open a pull request. Discussion happens on the pull request.
4. A maintainer who agrees to shepherd it moves it to In review. Only the shepherd changes its
   status.
5. Decisions follow `GOVERNANCE.md`.

## Index

| RFC                            | Title               | Status |
| ------------------------------ | ------------------- | ------ |
| [0001](0001-opencheckpoint.md) | OpenCheckpoint v0.1 | Draft  |
