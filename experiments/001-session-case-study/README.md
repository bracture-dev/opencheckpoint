# Experiment 001: session case study

A real working session (the one that produced this repository) is interrupted at a fixed point,
and the work is handed off under five conditions. This is a case study of one session, not a
benchmark; it establishes method and first numbers.

## Setup

- **Session:** a single Claude Code session building OpenCheckpoint v0.1.
- **Interruption point:** immediately before the user's request to consolidate the RFCs. The
  repository state at that point is commit `7a1668c`.
- **Next request (held out):** the user's actual next message.
- **Producer model:** Claude Opus 5.5 (`claude-opus-5-5`) via `claude -p`, no tools, fixed
  prompts in [`prompts/`](prompts/). Both producers receive the same rendered transcript and are
  told the destination will have the repository at `7a1668c`. The checkpoint producer also
  receives the v0.1 specification and schema as of that commit.
- **Token counts:** Claude counts are exact, from API usage (document call minus an empty-call
  baseline, which was stable at 6,201 before and after). OpenAI counts use `tiktoken`
  `o200k_base`, computed locally.

The transcript and generated handoffs are kept in `private/`, which is not committed, because the
transcript contains the operator's private configuration.

## Conditions

|     | Condition                | What the destination receives                                                                                                                                                 |
| --- | ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A   | Bare                     | The next request only.                                                                                                                                                        |
| B1  | Original session context | What the original Claude Code session carried at the interruption: transcript plus the harness's system prompt, tool definitions, images, and injected context. Not portable. |
| B2  | Portable transcript      | The transcript rendered as text: messages, tool calls, and tool results.                                                                                                      |
| C   | Prose summary            | A handoff summary written by the producer.                                                                                                                                    |
| D   | Checkpoint               | An OpenCheckpoint v0.1 document written by the producer.                                                                                                                      |

## Results: restore size

Tokens the destination reads at restore, excluding the next request (55 Claude tokens, 43 OpenAI).

| Condition                     | Claude tokens | OpenAI tokens (o200k) | Relative to B2 (Claude) |
| ----------------------------- | ------------: | --------------------: | ----------------------: |
| A. Bare                       |             0 |                     0 |                      0% |
| B1. Original session context  |       355,594 |                   n/a |                    170% |
| B2. Portable transcript       |       208,686 |               130,236 |                    100% |
| C. Prose summary              |         3,762 |                 2,391 |                    1.8% |
| D. Checkpoint, pretty-printed |        12,426 |                 8,494 |                    6.0% |
| D. Checkpoint, minified       |        10,324 |                 6,476 |                    4.9% |

## Results: capture cost

One fresh, uncached call per handoff. A producer working inside the live session would reuse its
cached context and cost less.

| Handoff          | Input tokens | Output tokens | Wall time |  Cost |
| ---------------- | -----------: | ------------: | --------: | ----: |
| C. Prose summary |      215,005 |         4,868 |      43 s | $1.82 |
| D. Checkpoint    |      238,678 |        17,839 |     152 s | $2.27 |

The checkpoint passed schema and semantic validation on the first attempt, with no warnings:
27 statements (6 instructions, 3 constraints, 5 decisions, 6 observations, 1 hypothesis,
6 questions), 18 resources, 3 operations.

## Results: facts captured

Ten facts that the user stated before the interruption and that the repository alone does not
reveal (for example the singular project name, the removal of foundation material, the Python
SDK being documentation only, and the DCO sign-off convention). A keyword check found all ten in
both the prose summary and the checkpoint. A keyword check is coarse; scoring continuation
behavior is the real test.

## Findings so far

1. **Restore size.** A checkpoint is about 5% of the portable transcript and about 3% of what the
   original session carried: roughly 20 to 34 times smaller.
2. **Checkpoint versus prose summary.** The prose summary is about a third of the checkpoint's
   size and captured the same ten facts. On size and fact capture alone, prose summary wins.
   Whatever the checkpoint adds must show up in continuation: provenance, explicit pending
   operations and preconditions, validation, and behavior across models.
3. **Capture cost.** Writing the checkpoint took about 3.7 times the output tokens and 3.5 times
   the wall time of the summary, mostly from structure and from reading the specification.
4. **Tokenizers differ.** The same documents cost 1.45 to 1.6 times more tokens in Claude's
   tokenizer than in `o200k_base`. Cross-model claims report both.

## Next

- **Continuation runs.** Give conditions A, B2, C, and D with the next request to Claude Code
  (`claude -p`) and Codex (`codex exec`) in a copy of the repository at `7a1668c`. Measure
  tokens, wall time, tool calls before the first edit, and score the result against a rubric
  written before the runs: the ten facts, what the user's actual next turn produced, and
  regressions (re-adding foundation material, plural naming, building SDK code).
- **Repeat** each run at least three times per destination to report spread.
- **Redaction** before anything from `private/` is published.
