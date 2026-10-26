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

## Results: continuation

Scored with the pre-registered [rubric](rubric.md) by [`score.py`](score.py). Per-run numbers are
in [`results.json`](results.json). Token figures are totals across every turn of the run,
including each CLI's own system prompt and tool definitions; compare conditions within an agent,
not across agents. Cost is reported by Claude Code; Codex reports none.

| Agent       | Condition        |   n | Task (of 7) | Regressions | Uncached input | Cached input | Output |  Cost | Wall time | Tool calls | Calls before first edit |
| ----------- | ---------------- | --: | ----------: | ----------: | -------------: | -----------: | -----: | ----: | --------: | ---------: | ----------------------: |
| Claude Code | A. Bare          |   3 |         3.0 |           0 |         27,345 |      103,082 |  2,845 | $0.30 |      31 s |          3 |                no edits |
| Claude Code | B2. Transcript   |   3 |         7.0 |           0 |        255,429 |    5,157,569 | 19,817 | $3.47 |     206 s |         21 |                     4.0 |
| Claude Code | C. Prose summary |   3 |         7.0 |           0 |        119,325 |    3,667,468 | 35,234 | $2.39 |     371 s |         41 |                    11.0 |
| Claude Code | D. Checkpoint    |   3 |         7.0 |           0 |        125,381 |    3,298,129 | 36,366 | $2.39 |     366 s |         36 |                    13.7 |
| Codex       | A. Bare          |   3 |         4.0 |           0 |         34,620 |      322,901 |  3,640 |   n/a |     111 s |         11 |                     5.3 |
| Codex       | B2. Transcript   |   3 |         7.0 |           0 |        150,659 |    1,553,109 |  6,164 |   n/a |     176 s |         11 |                     3.7 |
| Codex       | C. Prose summary |   3 |         7.0 |           0 |         43,492 |      580,395 |  6,621 |   n/a |     183 s |         13 |                     4.3 |
| Codex       | D. Checkpoint    |   3 |         7.0 |           0 |         48,829 |      567,296 |  6,318 |   n/a |     173 s |         13 |                     6.0 |

No run regressed on any of the four earlier preferences, in any condition, including bare. The
repository at the interruption point already reflects those preferences, so these checks did not
discriminate between conditions on this task.

### What the runs show

1. **A handoff is necessary.** Without one, neither agent knew that the user's "yes" accepted the
   forking proposal. Claude explained the problem and proposed a plan without editing (3 of 7);
   Codex consolidated the RFCs and deferred forking (4 of 7). With any handoff, both agents
   completed all seven checks in every run.
2. **Summaries and checkpoints cost less than replay.** With Claude, both cost $2.39 per run
   against $3.47 for transcript replay (31% less), and read about half as many uncached input
   tokens. With Codex, a checkpoint or summary read about 3 times fewer uncached input tokens
   than the transcript (44,000 to 49,000 against 151,000).
3. **Replay was faster here.** With Claude, transcript runs finished in 206 s with 21 tool calls
   and made their first edit after 4 calls; summary and checkpoint runs took about 370 s and
   37 to 41 calls, with the first edit after 11 to 14. The transcript contains the previous
   assistant's exact plan, so the destination executes it; with a summary or checkpoint it
   re-reads the repository first. The checkpoint's explicit preconditions encourage that
   verification. With Codex, wall time was equal across handoff conditions.
4. **Checkpoint and prose summary performed alike on this task.** Same task score, same cost,
   similar time. This task has no pending side effects, approvals, or injected content, which is
   where typed provenance and operations are designed to matter. Experiment 3 (business
   scenarios) tests those.
5. **The same checkpoint worked on both agents.** Claude Code and Codex each completed all seven
   checks from it in every run.
6. **Transcript replay carried live paths into the original environment.** Two of three Claude
   transcript runs listed the original repository's absolute path, taken from the transcript.
   Redaction had replaced the username, so the path did not exist. Without redaction the agent
   would have reached the original repository and its later commits. A checkpoint references
   resources deliberately; a transcript references whatever the session touched.

### Deviations from the pre-registered plan

- **Codex usage limit.** The operator's ChatGPT plan reached its usage limit twice during the
  batch. Twelve attempts across eight runs ended on the limit error; each of those runs was rerun
  from a fresh workspace until it completed, and only completed runs are scored. Every cell has n=3.
- **Contamination rule narrowed after the runs.** The registered rule also flagged four Claude
  runs that touched a non-existent redacted path or their own spilled tool output under
  `~/.claude/projects/<run>`. Their tool calls were inspected: none reached the original
  repository or transcript. The rule now matches only those.
- **T3 matching corrected after the runs.** The registered phrase match missed correct statements
  of the one-owner rule that wrapped across lines or used equivalent wording ("at most one of
  them"). Five runs failed T3 on this alone; all five state the rule. Before the correction, the
  summary and checkpoint conditions averaged 6.3 of 7 with Claude, and Codex scored 6 with the
  checkpoint.
- **Pilot runs.** The bare-condition pilots (repeat 0) ran before the rubric was committed. The one
  rubric change made then (whole-word matching for G2) came from baseline counts, not from pilot
  results.
- **Global instructions.** Both CLIs load the operator's global instructions and skills in every
  condition; Codex also read a global workspace skill. This is constant across conditions.

## Next

- **Experiment 3:** business scenarios with pending side effects, approvals, and injected content,
  where structure is expected to matter.
- **Redaction** before anything from `private/` is published.
