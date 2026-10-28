# Checks for v0.1 rules the harness does not enforce yet

`tools/conformance.mjs` at `c46950e` accepts 36 documents that break a MUST in
`spec/versions/v0.1.md`. `checks/checks.mjs` runs the harness's `check()` unchanged, then adds
the checks below. With them all 36 fail, the 12 valid controls pass, and the repository's 45
manifest cases and four examples give the same results as before.

```sh
node contrib/checks/run.mjs
```

The runner shows each invalid case passing the harness alone, then failing with the checks.

| Spec        | Accepted today                                                                                                                                                                      | Cases | Code                    |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----: | ----------------------- |
| §9.2        | A compacted child drops or rewrites what it must keep: an active instruction, constraint, decision or question, an open operation, a stop condition or its scope, an origin         |    31 | OCP-S010, OCP-T003–T006 |
| §9.1, §10.2 | A constraint or decision whose origin is `tool` or `external`, so a tool result can plant a rule the destination treats as the user's. The schema blocks this only for instructions |     2 | OCP-S011                |
| §3          | Duplicate member names and unpaired surrogates. Parsers disagree on which duplicate wins, so two consumers read two different checkpoints                                           |     2 | schema                  |
| §6.5        | A statement changes kind between parent and child outside compaction                                                                                                                |     1 | OCP-T004                |

Codes are placeholders. Nothing outside `contrib/` changes.
