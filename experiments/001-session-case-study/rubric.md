# Rubric for continuation runs

Written and committed before any continuation run. Every check is automated by
[`score.py`](score.py) against the repository the destination leaves behind and the destination's
recorded tool calls.

## The held-out request

The user's actual next message at the interruption point:

> yes - but this is also all net new code. why do we already have this many RFCs? we should be
> operating on an MVP set of RFC(s) because they are draft before htye are accepted

"yes" answers the previous assistant's question: whether to accept the forking proposal (RFC 0006)
and apply it to the specification and schema with fixtures and a sibling-fork scenario. A
destination without context cannot know that.

## Task checks (what the user asked for)

| ID  | Check                                | Pass when                                                                                                                                                                                                                             |
| --- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T1  | RFCs reduced to a minimal set        | At most 2 numbered RFC files in `rfcs/` besides the template (there were 6).                                                                                                                                                          |
| T2  | Forking applied to the schema        | `derivation.method` in the schema includes `forked`.                                                                                                                                                                                  |
| T3  | Forking applied to the specification | The specification mentions `forked` and states that a side-effecting operation is actionable in at most one fork.                                                                                                                     |
| T4  | Forking covered by fixtures          | At least one fixture under `tests/fixtures/` has `"method": "forked"`.                                                                                                                                                                |
| T5  | Conformance suite passes             | `npm test` exits 0.                                                                                                                                                                                                                   |
| T6  | Documentation builds                 | `npm run docs:build` exits 0.                                                                                                                                                                                                         |
| T7  | Content preserved                    | The repository (outside `node_modules`) still contains each of: `Agent Session Protocol`, `Replay of side-effecting operations`, `Handoff Debt`, `Duplicate side effects`. Consolidating RFCs must move their content, not delete it. |

## Regression checks (preferences stated earlier in the session)

| ID  | Check                  | Pass when                                                                                           |
| --- | ---------------------- | --------------------------------------------------------------------------------------------------- |
| G1  | Singular project name  | No occurrence of `OpenCheckpoints` or `opencheckpoints` (baseline: 0).                              |
| G2  | No foundation material | No whole-word occurrence of `foundation`, `AAIF`, or `stewardship`, case-insensitive (baseline: 0). |
| G3  | Python SDK not built   | No `.py` files under `sdks/`.                                                                       |
| G4  | Nothing published      | No tool call runs `git push`, `gh repo create`, or `npm publish`.                                   |

The uv/ruff preference is not scored: both destinations load the operator's global instructions,
which state it, in every condition.

## Efficiency measures (reported, not scored)

Input, cached, and output tokens; cost where the CLI reports it; wall time; number of tool calls;
tool calls and seconds before the first file modification.

## Contamination

A run is marked contaminated and excluded if any tool call references a path outside its
workspace that contains `opencheckpoint`, `experiments/001`, or `.claude/projects`, since those
lead to the original repository's later commits or the session transcript.

## Conditions and repeats

Conditions A (bare), B2 (portable transcript, redacted), C (prose summary), and D (checkpoint),
each with the same wrapper (see `prompts/destination.md`). Destinations: Claude Code with Claude
Opus 5.5 at default effort, and Codex CLI with gpt-6-astra at medium reasoning effort. Three runs
per cell. Each run starts from a fresh copy of the repository at `7a1668c` with no git history
beyond one snapshot commit.
