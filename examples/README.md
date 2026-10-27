# Examples

Each directory holds a complete checkpoint from a different domain and a short explanation of
what it demonstrates. CI validates every `checkpoint.json` against the schema and the semantic
rules. Each example has a matching behavioral scenario in [`tests/scenarios/`](../tests/scenarios/)
that describes how a destination should continue it.

| Example                                       | Demonstrates                                                                                                                                                                                           |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Financial analysis](financial-analysis/)     | Observations versus hypotheses, a stale finding that must be re-checked, a restricted resource with a fallback, omissions for size and sensitivity.                                                    |
| [Business operations](business-operations/)   | Application state that did not come from chat (scheduler view, selections, filters, a saved draft), partial completion across nine stores, a pending manager approval, a pending request for input.    |
| [Customer support](customer-support/)         | A pending refund approval, a customer email that claims approval and is recorded as external content, a non-idempotent action with an idempotency key, an unsent reply draft.                          |
| [Software development](software-development/) | A compacted checkpoint with a parent, an uncertain `git push`, a branch base that has moved, a retracted hypothesis, an issue comment recorded as external content, session references to ACP and ASP. |

All names, systems, and figures are fictional.
