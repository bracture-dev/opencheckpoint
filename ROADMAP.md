# Roadmap

| Phase                             | Deliverables                                                                                                                                                                         | Status                 |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------- |
| 0. Research and architecture      | Standards survey, scope and non-goals, architecture decisions, draft schema, risks and open questions.                                                                               | Done (RFCs 0001–0005). |
| 1. Specification and website      | Normative specification v0.1, JSON Schema, four examples, conformance fixtures, behavioral scenarios, documentation site, governance, CI.                                            | Done, pending review.  |
| 2. TypeScript SDK                 | Generated types, parser and serializer, schema validation, semantic rules, builders, unit and conformance tests, package configuration.                                              | Not started.           |
| 3. Go SDK                         | Equivalent capabilities in idiomatic Go, passing the shared conformance manifest.                                                                                                    | Not started.           |
| 4. Rust SDK                       | Equivalent capabilities with Serde types, passing the shared conformance manifest.                                                                                                   | Not started.           |
| 5. Python SDK                     | Equivalent capabilities with typed dictionaries generated from the schema, passing the shared conformance manifest.                                                                  | Not started.           |
| 6. Interoperability demonstration | A task starts in one agent, is checkpointed, and continues in a second, independently implemented agent without transcript replay, scored with the scenarios and RFC 0004's metrics. | Not started.           |
| 7. Community review               | Publish the RFCs, solicit review from carrier-protocol maintainers and runtime authors, recruit maintainers.                                                                         | Not started.           |

## Toward external implementations

The goal is independent implementations, not more code in this repository. Priorities:

1. **Converters from existing formats**, which give the format producers on day one: a pi
   compaction entry to checkpoint converter, and an Agent Session Protocol projection to
   checkpoint converter.
2. **Carrier bindings**: documented patterns, and eventually extensions proposed in each
   protocol's own process, for carrying checkpoints as MCP resources, A2A artifacts, and ACP
   content blocks.
3. **A reference destination** that implements the restoration procedure (§10.7) and runs the
   behavioral scenarios.
4. **A conformance report format**, so external implementations can publish results against the
   manifest.
