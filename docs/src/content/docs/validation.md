---
title: Validation and compatibility
description: The five levels of assurance, semantic rules, and the version policy.
---

## Valid is not the same as safe to resume

A checkpoint can pass every check and still be impossible, or dangerous, to continue. The
specification separates five properties, each established by a different party:

| Level                    | Question                                                                      | Who establishes it                                  |
| ------------------------ | ----------------------------------------------------------------------------- | --------------------------------------------------- |
| 1. Syntactic validity    | Does it match the JSON Schema?                                                | Any validator.                                      |
| 2. Semantic consistency  | Do references resolve, ids stay unique, and the semantic rules hold?          | Any conforming validator.                           |
| 3. Resource availability | Can the destination reach the referenced resources at the recorded revisions? | The destination, at restore time.                   |
| 4. Authorization         | May the destination take the next actions?                                    | The destination's own policy. Never the checkpoint. |
| 5. Continuation success  | Did the destination actually continue correctly?                              | Behavioral evaluation.                              |

Validators report levels 1 and 2 and must not describe a valid document as "safe to resume".

## Semantic rules

The schema cannot check everything. Semantic rules have stable codes so every implementation
reports the same thing:

- **OCP-S001–S008** (errors): unique ids, resolvable references of the right type, no
  self-parent, no observation timestamps after creation, no open operations on a completed task,
  supersession within a kind, no credentials in URIs.
- **OCP-W001–W003** (warnings): a blocked task that does not say why, an agent observation without
  evidence, an awaiting operation that already expired.
- **OCP-T001–T002** (between a parent and child): terminal operations stay terminal, and lineage
  and timestamps are consistent.

The authoritative table is in [§8.2 of the specification](../specification/#82-semantic-rules).

## Unknown extensions

Consumers ignore extension keys they do not understand and preserve them when they write the
document back out. An extension that is needed to interpret a document is declared as a
continuation requirement of kind `extension`; a consumer that does not implement a required one
must not claim full understanding.

## Versions

The `opencheckpoint` field holds `MAJOR.MINOR`.

- **Before 1.0**, any minor version may break compatibility, and consumers reject versions they
  do not implement.
- **From 1.0**, minor versions only add optional fields and warnings. A consumer may process a
  newer minor version at reduced understanding, preserves unknown fields, and says so. Unknown
  major versions are rejected.

Each version's schema is published once, at a stable URL, and never edited.

## Running the checks

The [conformance suite](../conformance/) is a manifest of fixtures with expected outcomes that
any implementation can run. In this repository:

```sh
npm install
npm test
```
